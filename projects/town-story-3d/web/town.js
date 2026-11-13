// ============================================================================
// TOWN.JS — "The Town That Counts To Ten" environment builder
// Stylized blocky town: colored facades with window grids, real doors on the
// hero houses, number plates, trees, streetlights with aim-able heads,
// a parked blocky car, clouds and stars. Day/night via facade texture swap.
// ============================================================================
import * as THREE from 'three';

const cv = (w, h) => {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  return [c, c.getContext('2d')];
};
const tex = (c) => {
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
};
export const box = (w, h, d, color, opts = {}) => {
  const m = new THREE.Mesh(
    new THREE.BoxGeometry(w, h, d),
    new THREE.MeshLambertMaterial({ color, ...(opts.map ? { map: opts.map } : {}) })
  );
  m.position.set(opts.x || 0, opts.y || 0, opts.z || 0);
  if (opts.ry) m.rotation.y = opts.ry;
  if (opts.rx) m.rotation.x = opts.rx;
  if (opts.rz) m.rotation.z = opts.rz;
  return m;
};

// Deterministic seeded RNG so every render is identical
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// ---------------------------------------------------------------- facades
// facade texture: wall + window grid + door + roofline. Two variants:
// day (windows dark blue) and night (random windows warm-lit).
function makeFacade({ wall, trim, floors, cols, door, lit, seed }) {
  const W = 320, H = 384;
  const [c, g] = cv(W, H);
  const [cn, gn] = cv(W, H);
  const rnd = mulberry32(seed);
  const paint = (g2, night) => {
    g2.fillStyle = wall; g2.fillRect(0, 0, W, H);
    // subtle wall panel lines
    g2.strokeStyle = 'rgba(0,0,0,0.10)'; g2.lineWidth = 3;
    for (let y = 0; y < H; y += 48) { g2.beginPath(); g2.moveTo(0, y); g2.lineTo(W, y); g2.stroke(); }
    // windows
    const winW = 44, winH = 52;
    const mx = (W - cols * winW - (cols - 1) * 26) / 2;
    for (let f = 0; f < floors; f++) {
      for (let cI = 0; cI < cols; cI++) {
        const x = mx + cI * (winW + 26);
        const y = 34 + f * 78;
        g2.fillStyle = trim; g2.fillRect(x - 5, y - 5, winW + 10, winH + 10);
        const isLit = night && rnd() < 0.62;
        g2.fillStyle = isLit ? (lit || '#ffd98a') : (night ? '#101826' : '#8fd0f0');
        g2.fillRect(x, y, winW, winH);
        // window cross bars
        g2.strokeStyle = 'rgba(0,0,0,0.35)'; g2.lineWidth = 3;
        g2.beginPath();
        g2.moveTo(x + winW / 2, y); g2.lineTo(x + winW / 2, y + winH);
        g2.moveTo(x, y + winH / 2); g2.lineTo(x + winW, y + winH / 2);
        g2.stroke();
        if (!night) { // day sky reflection glint
          g2.fillStyle = 'rgba(255,255,255,0.22)';
          g2.beginPath(); g2.moveTo(x, y + winH); g2.lineTo(x + 16, y); g2.lineTo(x + 28, y); g2.lineTo(x + 8, y + winH); g2.fill();
        }
      }
    }
    // door at street level (centered)
    const dW = 54, dH = 92, dx = (W - dW) / 2, dy = H - dH - 12;
    g2.fillStyle = 'rgba(0,0,0,0.30)'; g2.fillRect(dx - 6, dy - 6, dW + 12, dH + 12);
    g2.fillStyle = door; g2.fillRect(dx, dy, dW, dH);
    g2.fillStyle = 'rgba(255,255,255,0.75)'; g2.beginPath(); g2.arc(dx + dW - 12, dy + dH / 2, 4, 0, 7); g2.fill();
    // roofline band
    g2.fillStyle = 'rgba(0,0,0,0.22)'; g2.fillRect(0, 0, W, 14);
  };
  paint(g, false);
  paint(gn, true);
  return { day: tex(c), night: tex(cn) };
}

function makePlateTex(numStr) {
  const [c, g] = cv(256, 128);
  g.fillStyle = '#141a26'; g.fillRect(0, 0, 256, 128);
  g.strokeStyle = '#f0ecdf'; g.lineWidth = 10; g.strokeRect(9, 9, 238, 110);
  g.fillStyle = '#ffffff'; g.font = '900 86px Arial, sans-serif';
  g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText(numStr, 128, 68);
  return tex(c);
}

// ---------------------------------------------------------------- builder
export function buildTown(scene) {
  const rng = mulberry32(20260911);
  const town = new THREE.Group();
  scene.add(town);

  const buildings = [];   // {group, mat, facadeDay, facadeNight, x, side, num}
  const heroDoors = {};   // name -> {pivot, baseRot}
  const plates = [];      // {mesh, num}
  const lamps = [];       // {group, head, lens, light, baseAim}
  const trees = [];
  let stars, clouds = [], carGroup;

  // ---- ground / road / sidewalks -------------------------------------
  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(220, 160),
    new THREE.MeshLambertMaterial({ color: '#74b856' })
  );
  ground.rotation.x = -Math.PI / 2; ground.position.y = -0.02;
  town.add(ground);

  // road texture: asphalt with dashed centerline + crosswalk at x~0
  const [rc, rg] = cv(1024, 256);
  rg.fillStyle = '#3c4048'; rg.fillRect(0, 0, 1024, 256);
  rg.fillStyle = 'rgba(255,255,255,0.05)';
  for (let i = 0; i < 400; i++) rg.fillRect(rng() * 1024, rng() * 256, 3, 3);
  rg.fillStyle = '#e8d75a';
  for (let x = 40; x < 1024; x += 120) rg.fillRect(x, 122, 56, 12);
  const roadTex = tex(rc); roadTex.wrapS = THREE.RepeatWrapping; roadTex.repeat.x = 6;
  const road = new THREE.Mesh(
    new THREE.PlaneGeometry(180, 6.4),
    new THREE.MeshLambertMaterial({ map: roadTex })
  );
  road.rotation.x = -Math.PI / 2; road.position.set(0, 0.005, 0);
  town.add(road);
  // crosswalk stripes near x=0
  for (let i = -3; i <= 3; i++) {
    const st = box(0.42, 0.012, 4.6, '#e9e6da', { x: i * 0.95, y: 0.012, z: 0 });
    town.add(st);
  }
  // sidewalks
  for (const zs of [4.35, -4.35]) {
    const sw = new THREE.Mesh(
      new THREE.PlaneGeometry(180, 2.4),
      new THREE.MeshLambertMaterial({ color: '#b9b3a4' })
    );
    sw.rotation.x = -Math.PI / 2; sw.position.set(0, 0.018, zs);
    town.add(sw);
    // curb
    town.add(box(180, 0.14, 0.16, '#9d9788', { y: 0.07, z: zs + (zs > 0 ? -1.24 : 1.24) }));
  }

  // ---- buildings ------------------------------------------------------
  // Right row (z=+9.6, doors face -z toward street): hero houses.
  // Left row (z=-9.6, doors face +z): mixed shops/apartments.
  const rightRow = [
    { x: -22, num: '121', wall: '#f2b56b', door: '#7a3b2e', floors: 2, cols: 3, seed: 11 },
    { x: -14, num: '127', wall: '#7cc4f0', door: '#31465e', floors: 3, cols: 3, seed: 12 },
    { x: -6, num: '131', wall: '#f28b8b', door: '#5e3146', floors: 2, cols: 2, seed: 13 },
    { x: 2, num: '135', wall: '#9fdd7a', door: '#44583a', floors: 3, cols: 3, seed: 14 },
    { x: 6, num: '143', wall: '#f7d774', door: '#6e5a3a', floors: 2, cols: 2, seed: 15 },
    { x: 10, num: '145', wall: '#c99bf5', door: '#5a3d63', floors: 2, cols: 2, seed: 16 },
    { x: 14, num: '147', wall: '#9fbef0', door: '#3d5266', floors: 2, cols: 3, seed: 17 }, // FINCH
    { x: 18, num: '149', wall: '#ffd98a', door: '#7d5b33', floors: 2, cols: 3, seed: 18, doorway: true }, // KID
    { x: 26, num: '153', wall: '#f09a8f', door: '#6e3a34', floors: 3, cols: 3, seed: 19 },
  ];
  const leftRow = [
    { x: -26, num: '120', wall: '#8fd8a8', door: '#3f5647', floors: 3, cols: 4, seed: 21 },
    { x: -18, num: '126', wall: '#f7c489', door: '#63513c', floors: 2, cols: 3, seed: 22 },
    { x: -10, num: '132', wall: '#c9a2f0', door: '#4e3f61', floors: 3, cols: 3, seed: 23 },
    { x: -2, num: '138', wall: '#ffe066', door: '#8a6d20', floors: 2, cols: 3, seed: 24 },
    { x: 6, num: '140', wall: '#8cc4f0', door: '#3a4a63', floors: 3, cols: 4, seed: 25 },
    { x: 14, num: '144', wall: '#f5b8a5', door: '#5f4c41', floors: 2, cols: 3, seed: 26 },
    { x: 22, num: '148', wall: '#8fe8c4', door: '#3e5a50', floors: 3, cols: 3, seed: 27 },
  ];
  // Real window material for the hero doorway house (day glass / night lit)
  const heroWinMat = new THREE.MeshLambertMaterial({ color: '#2b3f66' });
  const buildHouse = (spec, side) => {
    if (spec.doorway) {
      // Hero house with a REAL doorway: panels around an opening + dark interior
      // backdrop so the kid can peek out through the door gap at night.
      const g = new THREE.Group();
      const h = 3.0 + (spec.floors - 1) * 1.45;
      const w = 3.6, d = 3.4;
      const wallM = new THREE.MeshLambertMaterial({ color: spec.wall });
      const openW = 0.85, openH = 1.66;
      const sideW = (w - openW) / 2;
      // left/right front panels
      g.add(box(sideW, h, 0.22, spec.wall, { x: -(openW / 2 + sideW / 2), y: h / 2, z: -d / 2 }));
      g.add(box(sideW, h, 0.22, spec.wall, { x: (openW / 2 + sideW / 2), y: h / 2, z: -d / 2 }));
      // header above the opening
      g.add(box(openW, h - openH, 0.22, spec.wall, { y: openH + (h - openH) / 2, z: -d / 2 }));
      // side walls + back
      g.add(box(0.22, h, d, spec.wall, { x: -w / 2 + 0.11, y: h / 2, z: 0 }));
      g.add(box(0.22, h, d, spec.wall, { x: w / 2 - 0.11, y: h / 2, z: 0 }));
      g.add(box(w, h, 0.22, spec.wall, { y: h / 2, z: d / 2 - 0.11 }));
      // dark interior backdrop just behind the doorway
      const inner = new THREE.Mesh(
        new THREE.PlaneGeometry(openW + 0.3, openH + 0.3),
        new THREE.MeshBasicMaterial({ color: '#07080d' })
      );
      inner.position.set(0, (openH + 0.3) / 2, -d / 2 + 0.5);
      inner.rotation.y = Math.PI;
      g.add(inner);
      // windows (real boxes: day glass -> night lit via shared material)
      for (const wx of [-(openW / 2 + sideW / 2), (openW / 2 + sideW / 2)]) {
        const win = box(0.52, 0.62, 0.06, '#ffffff', { x: wx, y: 3.35, z: -d / 2 - 0.02 });
        win.material = heroWinMat;
        g.add(win);
        g.add(box(0.62, 0.72, 0.04, '#5c5648', { x: wx, y: 3.35, z: -d / 2 + 0.01 }));
      }
      // roof + chimney
      g.add(box(w + 0.5, 0.34, d + 0.5, '#b0533f', { y: h + 0.17 }));
      g.add(box(0.42, 0.9, 0.42, spec.wall, { x: w / 2 - 0.6, y: h + 0.8, z: d / 2 - 0.7 }));
      g.position.set(spec.x, 0, side * 9.6);
      town.add(g);
      const plate = new THREE.Mesh(
        new THREE.PlaneGeometry(0.92, 0.46),
        new THREE.MeshBasicMaterial({ map: makePlateTex(spec.num) })
      );
      plate.position.set(spec.x, 2.06, side * (9.6 - d / 2) - side * 0.13);
      plate.rotation.y = side > 0 ? Math.PI : 0;
      town.add(plate);
      plates.push({ mesh: plate, num: spec.num });
      buildings.push({ group: g, mat: heroWinMat, day: heroWinMat.map, night: heroWinMat.map, x: spec.x, side, num: spec.num, h });
      return g;
    }
    const g = new THREE.Group();
    const h = 3.0 + (spec.floors - 1) * 1.45;
    const w = 3.6, d = 3.4;
    const fac = makeFacade(spec);
    // Facade material starts as DAY; the director swaps to night.
    const mat = new THREE.MeshLambertMaterial({ map: fac.day });
    const body = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), [
      new THREE.MeshLambertMaterial({ color: spec.wall }), // +x
      new THREE.MeshLambertMaterial({ color: spec.wall }), // -x
      new THREE.MeshLambertMaterial({ color: spec.wall }), // +y top
      new THREE.MeshLambertMaterial({ color: spec.wall }), // -y
      side > 0 ? mat : new THREE.MeshLambertMaterial({ color: spec.wall }), // +z back or face
      side > 0 ? new THREE.MeshLambertMaterial({ color: spec.wall }) : mat, // -z face or back
    ]);
    body.position.y = h / 2;
    g.add(body);
    // roof cap + little parapet blocks
    const roof = box(w + 0.5, 0.34, d + 0.5, '#b0533f', { y: h + 0.17 });
    g.add(roof);
    if (rng() < 0.6) g.add(box(0.5, 0.5, 0.5, '#6f6f78', { x: (rng() - 0.5) * 2, y: h + 0.6, z: (rng() - 0.5) * 2 }));
    // chimney on some
    if (rng() < 0.4) g.add(box(0.42, 0.9, 0.42, spec.wall, { x: w / 2 - 0.6, y: h + 0.8, z: d / 2 - 0.7 }));
    g.position.set(spec.x, 0, side * 9.6);
    g.rotation.y = 0; // facades: right row faces -z (texture on -z face), left row +z
    town.add(g);
    // number plate above door (street side)
    const plate = new THREE.Mesh(
      new THREE.PlaneGeometry(0.92, 0.46),
      new THREE.MeshBasicMaterial({ map: makePlateTex(spec.num) })
    );
    plate.position.set(spec.x, 2.02, side * (9.6 - d / 2 - 0.012) * 1);
    plate.position.z = side * (9.6 - d / 2) - side * 0.012;
    plate.rotation.y = side > 0 ? Math.PI : 0;
    town.add(plate);
    plates.push({ mesh: plate, num: spec.num });
    buildings.push({ group: g, mat, day: fac.day, night: fac.night, x: spec.x, side, num: spec.num, doorY: 0, h });
    return g;
  };
  for (const s of rightRow) buildHouse(s, +1);
  for (const s of leftRow) buildHouse(s, -1);

  // ---- REAL working doors on the right row (slam scene + reveals) -----
  const doorSpec = [
    { x: 6, name: 'n143', color: '#6e5a3a' },
    { x: 10, name: 'n145', color: '#5a3d63' },
    { x: 14, name: 'finch', color: '#3d5266' },
    { x: 18, name: 'kid', color: '#7d5b33' },
  ];
  for (const d of doorSpec) {
    const pivot = new THREE.Group();
    // door plane: width 0.78, height 1.5, hinged on its -x edge
    const door = box(0.78, 1.5, 0.09, d.color, {});
    door.position.set(0.39, 0.75, 0);
    pivot.add(door);
    // knob
    const knob = new THREE.Mesh(new THREE.SphereGeometry(0.045, 10, 8), new THREE.MeshLambertMaterial({ color: '#e8d184' }));
    knob.position.set(0.66, 0.78, 0.07);
    pivot.add(knob);
    pivot.position.set(d.x - 0.39 - 0.06, 0, 9.6 - 3.4 / 2 - 0.02);
    // face -z (toward street): rotate so the door sits flush on the facade
    pivot.rotation.y = 0;
    town.add(pivot);
    heroDoors[d.name] = { pivot, open: 0 };
  }

  // ---- streetlights (aimable heads) -----------------------------------
  const lampXs = [-24, -16, -8, 0, 8, 16, 24];
  for (const lx of lampXs) {
    const g = new THREE.Group();
    g.position.set(lx, 0, -5.3); // left sidewalk edge
    const post = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.09, 5.2, 10), new THREE.MeshLambertMaterial({ color: '#3a4048' }));
    post.position.y = 2.6; g.add(post);
    const arm = box(1.5, 0.09, 0.09, '#3a4048', { x: 0.72, y: 5.15 });
    g.add(arm);
    const head = new THREE.Group();
    head.position.set(1.45, 5.05, 0);
    const headBox = box(0.42, 0.16, 0.3, '#3a4048', {});
    head.add(headBox);
    const lensMat = new THREE.MeshBasicMaterial({ color: '#3c3f45' }); // dark when off
    const lens = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.06, 0.34), lensMat);
    lens.position.y = -0.09;
    head.add(lens);
    const glowMat = new THREE.MeshBasicMaterial({ color: '#ffd98a', transparent: true, opacity: 0.0, depthWrite: false });
    const glow = new THREE.Mesh(new THREE.SphereGeometry(0.20, 12, 10), glowMat);
    glow.position.y = -0.14;
    head.add(glow);
    head.rotation.z = 0.32; // aim slightly down toward road
    g.add(head);
    town.add(g);
    lamps.push({ group: g, head, lensMat, glowMat, baseAim: 0.32, x: lx });
  }

  // ---- trees ----------------------------------------------------------
  const treeXs = [[-19, 5.4], [-11, 5.4], [-3, 5.4], [4, 5.4], [12, 5.4], [20, 5.4], [27, 5.4], [-19, -5.4], [-5, -5.4], [9, -5.4], [22, -5.4]];
  for (const [tx, tz] of treeXs) {
    const g = new THREE.Group();
    g.position.set(tx, 0, tz);
    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.18, 1.1, 8), new THREE.MeshLambertMaterial({ color: '#6d4a2f' }));
    trunk.position.y = 0.55; g.add(trunk);
    const leaf = new THREE.MeshLambertMaterial({ color: '#3f7d3a' });
    const c1 = new THREE.Mesh(new THREE.BoxGeometry(1.5, 1.0, 1.5), leaf); c1.position.y = 1.6; g.add(c1);
    const c2 = new THREE.Mesh(new THREE.BoxGeometry(1.05, 0.8, 1.05), leaf); c2.position.y = 2.45; g.add(c2);
    const c3 = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.55, 0.6), leaf); c3.position.y = 3.1; g.add(c3);
    town.add(g);
    trees.push(g);
  }

  // ---- parked blocky car ---------------------------------------------
  carGroup = new THREE.Group();
  carGroup.position.set(-13.5, 0, 3.6); carGroup.rotation.y = 0;
  const carBody = box(3.4, 0.85, 1.7, '#c8453a', { y: 0.75 });
  carGroup.add(carBody);
  const cabin = box(1.9, 0.75, 1.55, '#a83830', { y: 1.5, x: -0.15 });
  carGroup.add(cabin);
  const windGlass = box(1.7, 0.55, 1.58, '#9fc4d8', { y: 1.5, x: -0.15 });
  carGroup.add(windGlass);
  for (const [wx, wz] of [[-1.15, 0.88], [1.15, 0.88], [-1.15, -0.88], [1.15, -0.88]]) {
    const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.36, 0.36, 0.26, 12), new THREE.MeshLambertMaterial({ color: '#23262c' }));
    wheel.rotation.x = Math.PI / 2;
    wheel.position.set(wx, 0.36, wz);
    carGroup.add(wheel);
  }
  town.add(carGroup);

  // ---- clouds (day) ----------------------------------------------------
  const cloudMat = new THREE.MeshLambertMaterial({ color: '#ffffff', transparent: true, opacity: 0.92 });
  for (const [cx, cy, cz, s] of [[-14, 22, -18, 1.6], [6, 24, -26, 2.1], [22, 21, -14, 1.3], [-26, 23, -10, 1.5]]) {
    const cg = new THREE.Group();
    for (const [ox, oy, oz, bs] of [[0, 0, 0, 2.4], [1.6, -0.3, 0.3, 1.7], [-1.7, -0.25, -0.2, 1.5], [0.5, 0.55, 0.4, 1.4]]) {
      const b = new THREE.Mesh(new THREE.BoxGeometry(bs * s, bs * s * 0.55, bs * s * 0.8), cloudMat);
      b.position.set(ox * s, oy * s, oz * s);
      cg.add(b);
    }
    cg.position.set(cx, cy, cz);
    town.add(cg);
    clouds.push(cg);
  }

  // ---- stars (night) ---------------------------------------------------
  {
    const n = 260;
    const pos = new Float32Array(n * 3);
    const rr = mulberry32(99);
    for (let i = 0; i < n; i++) {
      // dome above and around
      const a = rr() * Math.PI * 2, r = 60 + rr() * 40, yy = 18 + rr() * 55;
      pos[i * 3] = Math.cos(a) * r;
      pos[i * 3 + 1] = yy;
      pos[i * 3 + 2] = Math.sin(a) * r;
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    stars = new THREE.Points(geo, new THREE.PointsMaterial({
      color: '#dfe8ff', size: 0.5, transparent: true, opacity: 0, sizeAttenuation: true,
    }));
    town.add(stars);
  }

  return { buildings, heroDoors, plates, lamps, trees, clouds, stars, carGroup, heroWinMat };
}
