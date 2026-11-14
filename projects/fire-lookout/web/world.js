// ============================================================================
// WORLD.JS — "The Fire Lookout" — stylized flat-shaded 3D world (Zack-style)
// Exterior: pine ridge, gravel road, wooden lookout tower, pickup truck, moon.
// Interior: lookout cab (desk, radio, lantern, notebook, clock, phone, door,
//           stair hatch), office flashback vignette, macro texture stages.
// All geometry is code; generated images are used as backdrop/texture assets.
// ============================================================================
import * as THREE from 'three';

const cv = (w, h) => {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  return [c, c.getContext('2d')];
};
const tex = (c) => {
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4;
  return t;
};
export const box = (w, h, d, hex, opts = {}) => {
  const m = new THREE.Mesh(
    new THREE.BoxGeometry(w, h, d),
    new THREE.MeshLambertMaterial({ color: hex, emissive: opts.emissive || '#000000' })
  );
  if (opts.x !== undefined) m.position.x = opts.x;
  if (opts.y !== undefined) m.position.y = opts.y;
  if (opts.z !== undefined) m.position.z = opts.z;
  if (opts.ry) m.rotation.y = opts.ry;
  return m;
};
const cyl = (rT, rB, h, hex, seg = 10) => new THREE.Mesh(
  new THREE.CylinderGeometry(rT, rB, h, seg),
  new THREE.MeshLambertMaterial({ color: hex })
);
const plane = (w, h) => new THREE.PlaneGeometry(w, h);

// deterministic pseudo-random
let _seed = 1234567;
const rnd = () => { _seed = (_seed * 1103515245 + 12345) & 0x7fffffff; return _seed / 0x7fffffff; };

// ---------------------------------------------------------------- texture helpers
function makeCanvasTex(w, h, draw) {
  const [c, g] = cv(w, h);
  draw(g, w, h);
  return tex(c);
}

function makeClockTex(txt) {
  return makeCanvasTex(256, 128, (g, w, h) => {
    g.fillStyle = '#0a0d0a'; g.fillRect(0, 0, w, h);
    g.strokeStyle = '#2a2f2a'; g.lineWidth = 6; g.strokeRect(3, 3, w - 6, h - 6);
    g.fillStyle = '#39e07a';
    g.font = '700 64px "Courier New", monospace';
    g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(txt, w / 2, h / 2 + 4);
  });
}
function makeNameTagTex() {
  return makeCanvasTex(256, 128, (g, w, h) => {
    g.fillStyle = '#b8a888'; g.fillRect(0, 0, w, h);
    g.strokeStyle = '#6a5a3a'; g.lineWidth = 8; g.strokeRect(4, 4, w - 8, h - 8);
    g.fillStyle = '#3a3020';
    g.font = '700 44px Georgia, serif';
    g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText('NIGHT GUARD', w / 2, 42);
    g.font = '700 52px Georgia, serif';
    g.fillStyle = '#241c10';
    g.fillText('ROBERT', w / 2, 88);
  });
}
function makeCctvHudTex() {
  return makeCanvasTex(540, 960, (g, w, h) => {
    // scanlines
    g.fillStyle = 'rgba(0,0,0,0.22)';
    for (let y = 0; y < h; y += 4) g.fillRect(0, y, w, 2);
    // corner brackets
    g.strokeStyle = 'rgba(255,255,255,0.5)'; g.lineWidth = 3;
    const B = 46, L = 34;
    [[L, L, 1, 1], [w - L, L, -1, 1], [L, h - L, 1, -1], [w - L, h - L, -1, -1]].forEach(([x, y, sx, sy]) => {
      g.beginPath(); g.moveTo(x + sx * B, y); g.lineTo(x, y); g.lineTo(x, y + sy * B); g.stroke();
    });
    // REC dot + text
    g.fillStyle = '#ff2a2a';
    g.beginPath(); g.arc(66, 62, 11, 0, 7); g.fill();
    g.fillStyle = '#e8e8e8';
    g.font = '700 30px "Courier New", monospace';
    g.textAlign = 'left'; g.textBaseline = 'middle';
    g.fillText('REC  CAM 03', 88, 63);
    g.font = '700 26px "Courier New", monospace';
    g.fillText('LOOKOUT 04 — NORTH RIDGE', 34, 108);
    // big timestamp bottom
    g.font = '700 44px "Courier New", monospace';
    g.textAlign = 'right';
    g.fillText('11:47:12 PM', w - 34, h - 118);
    g.fillText('OCT 12', w - 34, h - 70);
  });
}
function makeGrainTex() {
  return makeCanvasTex(270, 480, (g, w, h) => {
    const img = g.createImageData(w, h);
    for (let i = 0; i < img.data.length; i += 4) {
      const v = 118 + Math.random() * 26;
      img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
      img.data[i + 3] = 255;
    }
    g.putImageData(img, 0, 0);
  });
}

export function buildWorld(scene, loader) {
  const W = {};
  const lam = (hex, o = {}) => new THREE.MeshLambertMaterial({ color: hex, emissive: o.em || '#000000', transparent: !!o.tr, opacity: o.op ?? 1 });

  // ========================================================== EXTERIOR
  const ext = new THREE.Group();
  scene.add(ext);
  W.ext = ext;

  // ground
  const ground = new THREE.Mesh(plane(220, 220), lam('#22301e'));
  ground.rotation.x = -Math.PI / 2;
  ext.add(ground);

  // gravel road (along X)
  const road = new THREE.Mesh(plane(90, 3.4), lam('#4a4438'));
  road.rotation.x = -Math.PI / 2;
  road.position.set(-6, 0.015, -13);
  ext.add(road);

  // pine forest
  const pineGeoTrunk = new THREE.CylinderGeometry(0.09, 0.13, 0.9, 6);
  const pineTrunkMat = lam('#3a2c20');
  const pineMatA = lam('#1d3a24');
  const pineMatB = lam('#24422a');
  const pines = new THREE.Group();
  for (let i = 0; i < 130; i++) {
    const ang = rnd() * Math.PI * 2;
    const rad = 10 + rnd() * 55;
    const x = Math.cos(ang) * rad - 4;
    const z = Math.sin(ang) * rad - 4;
    if (Math.abs(z + 13) < 3.2 && x > -30 && x < 20) continue; // keep road clear
    if (z > 3.5 && z < 15 && x > -7 && x < 9) continue; // keep figure-viewing corridor clear (south approach)
    const s = 0.8 + rnd() * 1.5;
    const t = new THREE.Group();
    const trunk = new THREE.Mesh(pineGeoTrunk, pineTrunkMat);
    trunk.position.y = 0.45 * s;
    t.add(trunk);
    const c1 = new THREE.Mesh(new THREE.ConeGeometry(1.05 * s, 1.7 * s, 7), rnd() > 0.5 ? pineMatA : pineMatB);
    c1.position.y = (0.9 + 0.75) * s;
    const c2 = new THREE.Mesh(new THREE.ConeGeometry(0.78 * s, 1.4 * s, 7), c1.material);
    c2.position.y = (0.9 + 1.55) * s;
    const c3 = new THREE.Mesh(new THREE.ConeGeometry(0.5 * s, 1.0 * s, 7), c1.material);
    c3.position.y = (0.9 + 2.25) * s;
    t.add(c1, c2, c3);
    t.position.set(x, 0, z);
    pines.add(t);
  }
  ext.add(pines);

  // ---- lookout tower ----
  const tower = new THREE.Group();
  const LEG_H = 7.2;
  const legMat = lam('#5c4630');
  const braceMat = lam('#4e3b28');
  const legPositions = [[-2.1, -1.7], [2.1, -1.7], [-2.1, 1.7], [2.1, 1.7]];
  legPositions.forEach(([lx, lz]) => {
    const leg = box(0.34, LEG_H, 0.34, '#5c4630');
    leg.position.set(lx * 0.82, LEG_H / 2, lz * 0.82);
    leg.rotation.z = -lx * 0.035;
    leg.rotation.x = lz * 0.028;
    tower.add(leg);
  });
  // cross braces (two levels)
  for (const lvl of [2.2, 4.6]) {
    const b1 = box(3.4, 0.16, 0.16, '#4e3b28', { y: lvl, z: -1.42 });
    const b2 = box(3.4, 0.16, 0.16, '#4e3b28', { y: lvl, z: 1.42 });
    const b3 = box(0.16, 0.16, 2.9, '#4e3b28', { y: lvl, x: -1.78 });
    const b4 = box(0.16, 0.16, 2.9, '#4e3b28', { y: lvl, x: 1.78 });
    tower.add(b1, b2, b3, b4);
    // diagonals
    const d1 = box(3.6, 0.12, 0.12, '#463522', { y: lvl + 1.1, z: -1.42, ry: 0.72 });
    const d2 = box(3.6, 0.12, 0.12, '#463522', { y: lvl + 1.1, z: 1.42, ry: -0.72 });
    tower.add(d1, d2);
  }
  // cab platform + cab
  const cabBase = box(5.4, 0.3, 4.4, '#634c34', { y: LEG_H + 0.15 });
  tower.add(cabBase);
  // catwalk + railing
  const catwalk = box(6.2, 0.12, 5.2, '#54402a', { y: LEG_H + 0.36 });
  tower.add(catwalk);
  for (const [rx, rz, rw, rd] of [[0, 2.6, 6.2, 0.08], [0, -2.6, 6.2, 0.08], [3.1, 0, 0.08, 5.2], [-3.1, 0, 0.08, 5.2]]) {
    tower.add(box(rw, 0.7, rd, '#54402a', { x: rx, y: LEG_H + 0.85, z: rz }));
  }
  // roof
  const roof = new THREE.Mesh(new THREE.ConeGeometry(4.4, 1.7, 4), lam('#3c2e1e'));
  roof.position.y = LEG_H + 3.6;
  roof.rotation.y = Math.PI / 4;
  tower.add(roof);
  const roofStem = cyl(0.09, 0.09, 1.2, '#2e2216', 6);
  roofStem.position.y = LEG_H + 4.4;
  tower.add(roofStem);
  // lightning rod
  const rod = cyl(0.02, 0.02, 1.4, '#9aa2aa', 4);
  rod.position.y = LEG_H + 5.1;
  tower.add(rod);
  // stairs zigzag on the -x side
  const stairs = new THREE.Group();
  let sy = 0;
  let sdir = 1;
  let sz = 0;
  for (let i = 0; i < 22; i++) {
    const step = box(1.0, 0.1, 0.34, '#5c4630');
    step.position.set(-2.55 - Math.floor(i / 11) * 1.1, sy + 0.05, sz);
    stairs.add(step);
    sy += 0.3;
    sz += sdir * 0.34;
    if ((i + 1) % 11 === 0) { sdir *= -1; sz -= sdir * 0.17; }
  }
  tower.add(stairs);
  ext.add(tower);
  W.tower = tower;

  // pickup truck
  const truck = new THREE.Group();
  const tBody = box(2.6, 0.62, 1.25, '#7a4a28', { y: 0.62 });
  const tCab = box(1.15, 0.58, 1.15, '#8a5630', { x: 0.35, y: 1.2 });
  const tGlass = box(1.0, 0.34, 1.2, '#9db6c4', { x: 0.35, y: 1.28 });
  const tBed = box(1.15, 0.3, 1.2, '#6a3e22', { x: -0.75, y: 0.98 });
  truck.add(tBody, tCab, tGlass, tBed);
  const wGeo = new THREE.CylinderGeometry(0.3, 0.3, 0.22, 10);
  const wMat = lam('#181a1c');
  [[-0.85, 0.66], [0.85, 0.66], [-0.85, -0.66], [0.85, -0.66]].forEach(([wx, wz]) => {
    const w = new THREE.Mesh(wGeo, wMat);
    w.rotation.x = Math.PI / 2;
    w.position.set(wx, 0.3, wz);
    truck.add(w);
  });
  truck.position.set(-30, 0, -13);
  truck.rotation.y = Math.PI / 2;
  ext.add(truck);
  W.truck = truck;

  // dusk backdrop (generated image asset) — far plane
  const bdTex = loader.load('img/img02_forest_dusk.png');
  const backdrop = new THREE.Mesh(plane(150, 90), new THREE.MeshBasicMaterial({ map: bdTex, transparent: true, opacity: 0.0, depthWrite: false }));
  backdrop.position.set(-10, 24, -70);
  ext.add(backdrop);
  W.backdrop = backdrop;

  // moon + stars
  const moon = new THREE.Mesh(new THREE.CircleGeometry(2.6, 24), new THREE.MeshBasicMaterial({ color: '#dfe6ee', transparent: true, opacity: 0 }));
  moon.position.set(-34, 42, -62);
  ext.add(moon);
  W.moon = moon;
  const stars = new THREE.Group();
  for (let i = 0; i < 240; i++) {
    const st = new THREE.Mesh(new THREE.CircleGeometry(0.09 + rnd() * 0.1, 5), new THREE.MeshBasicMaterial({ color: '#cfd8e4', transparent: true, opacity: 0 }));
    const a = rnd() * Math.PI * 2;
    const r = 30 + rnd() * 60;
    st.position.set(Math.cos(a) * r, 14 + rnd() * 55, Math.sin(a) * r - 30);
    st.lookAt(0, 10, 0);
    stars.add(st);
  }
  ext.add(stars);
  W.stars = stars;

  // mist quads near ground for night shots
  const mists = [];
  for (let i = 0; i < 6; i++) {
    const mq = new THREE.Mesh(plane(16, 4), new THREE.MeshBasicMaterial({ color: '#9fb2c8', transparent: true, opacity: 0, depthWrite: false }));
    mq.position.set((rnd() - 0.5) * 30, 1.2 + rnd() * 2, (rnd() - 0.5) * 26 - 6);
    ext.add(mq);
    mists.push(mq);
  }
  W.mists = mists;

  // flashlight beam cone (from cab window downward)
  const beam = new THREE.Mesh(
    new THREE.ConeGeometry(1.5, 12, 12, 1, true),
    new THREE.MeshBasicMaterial({ color: '#ffe9b0', transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide })
  );
  beam.position.set(0, LEG_H - 4.5, 2.6);
  beam.rotation.x = Math.PI - 0.34;
  ext.add(beam);
  W.beam = beam;

  // ground light pool (where beam lands)
  const beamPool = new THREE.Mesh(new THREE.CircleGeometry(2.2, 20), new THREE.MeshBasicMaterial({ color: '#ffe9b0', transparent: true, opacity: 0, depthWrite: false }));
  beamPool.rotation.x = -Math.PI / 2;
  beamPool.position.set(0, 0.03, 5.2);
  ext.add(beamPool);
  W.beamPool = beamPool;

  // ========================================================== INTERIOR (cab)
  // cab interior sits inside the tower cab box (y = LEG_H+0.3 floor)
  const FLOOR = LEG_H + 0.3;
  const inte = new THREE.Group();
  inte.position.y = FLOOR;
  scene.add(inte);
  W.inte = inte;
  W.FLOOR = FLOOR;

  const floor = new THREE.Mesh(plane(5.0, 4.2), lam('#6b5236'));
  floor.rotation.x = -Math.PI / 2;
  inte.add(floor);
  // plank lines
  for (let i = 0; i < 7; i++) {
    const ln = box(5.0, 0.012, 0.03, '#57431f', { z: -1.8 + i * 0.6, y: 0.008 });
    inte.add(ln);
  }
  // back wall (door wall)
  const backWall = box(5.0, 2.6, 0.14, '#71563a', { y: 1.3, z: -2.06 });
  inte.add(backWall);
  // side walls
  inte.add(box(0.14, 2.6, 4.2, '#6b5234', { x: -2.46, y: 1.3 }));
  inte.add(box(0.14, 2.6, 4.2, '#6b5234', { x: 2.46, y: 1.3 }));
  // ceiling
  inte.add(box(5.0, 0.12, 4.2, '#5c4630', { y: 2.62 }));
  // front window wall: sill + mullions + glass
  inte.add(box(5.0, 0.7, 0.14, '#71563a', { y: 0.35, z: 2.06 }));
  inte.add(box(5.0, 0.42, 0.14, '#71563a', { y: 2.4, z: 2.06 }));
  const glassMat = new THREE.MeshLambertMaterial({ color: '#a8c4d8', transparent: true, opacity: 0.16, emissive: '#000000' });
  W.glassMat = glassMat;
  for (const gx of [-1.6, 0, 1.6]) {
    const gl = new THREE.Mesh(plane(1.5, 1.35), glassMat);
    gl.position.set(gx, 1.42, 2.06);
    inte.add(gl);
  }
  for (const gx of [-0.85, 0.85]) inte.add(box(0.1, 1.35, 0.16, '#71563a', { x: gx, y: 1.42, z: 2.06 }));

  // ---- desk (front-left, facing window) ----
  const desk = new THREE.Group();
  desk.position.set(-1.25, 0, 1.15);
  const dTop = box(1.9, 0.09, 0.85, '#7a5f3e', { y: 0.76 });
  desk.add(dTop);
  [[-0.85, -0.32], [0.85, -0.32], [-0.85, 0.32], [0.85, 0.32]].forEach(([lx, lz]) => {
    desk.add(box(0.09, 0.76, 0.09, '#5c4630', { x: lx, y: 0.38, z: lz }));
  });
  inte.add(desk);
  // chair
  const chair = new THREE.Group();
  chair.position.set(-1.25, 0, 0.35);
  chair.add(box(0.62, 0.07, 0.62, '#6b5236', { y: 0.45 }));
  chair.add(box(0.62, 0.75, 0.07, '#6b5236', { y: 0.82, z: -0.28 }));
  [[-0.26, -0.26], [0.26, -0.26], [-0.26, 0.26], [0.26, 0.26]].forEach(([lx, lz]) => {
    chair.add(box(0.06, 0.45, 0.06, '#5c4630', { x: lx, y: 0.225, z: lz }));
  });
  chair.rotation.y = 0.3;
  inte.add(chair);
  W.chair = chair;

  // ---- radio ----
  const radio = new THREE.Group();
  radio.position.set(-0.55, 0.81, 1.3); // on desk
  radio.add(box(0.52, 0.3, 0.26, '#3c3630'));
  const dialMat = new THREE.MeshLambertMaterial({ color: '#ffb44a', emissive: '#ff9a20' });
  const dial = new THREE.Mesh(new THREE.CircleGeometry(0.085, 14), dialMat);
  dial.position.set(0.1, 0.02, 0.135);
  radio.add(dial);
  const dial2 = new THREE.Mesh(new THREE.CircleGeometry(0.055, 12), dialMat);
  dial2.position.set(-0.12, 0.02, 0.135);
  radio.add(dial2);
  // frequency ticks
  const ticks = box(0.4, 0.03, 0.01, '#d8cfb8', { y: 0.1, z: 0.132 });
  radio.add(ticks);
  // knobs
  [[-0.19, -0.08], [-0.19, 0.08]].forEach(([kx, ky]) => {
    const k = cyl(0.028, 0.028, 0.03, '#1c1a16', 8);
    k.rotation.x = Math.PI / 2;
    k.position.set(kx, ky, 0.135);
    radio.add(k);
  });
  // antenna
  const ant = cyl(0.008, 0.008, 0.6, '#9aa2aa', 4);
  ant.position.set(0.2, 0.44, 0);
  ant.rotation.z = -0.3;
  radio.add(ant);
  inte.add(radio);
  W.radio = radio;
  W.radioDialMat = dialMat;

  // ---- lantern ----
  const lantern = new THREE.Group();
  lantern.position.set(-1.7, 0.83, 1.05);
  lantern.add(box(0.16, 0.22, 0.16, '#3c3630'));
  const lampGlass = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.14, 0.12), new THREE.MeshLambertMaterial({ color: '#ffd98a', emissive: '#ffb35a' }));
  lampGlass.position.y = 0.0;
  lantern.add(lampGlass);
  lantern.add(box(0.18, 0.03, 0.18, '#2c2822', { y: 0.13 }));
  const lanternLight = new THREE.PointLight(0xffd9a8, 0, 12, 1.15);
  lanternLight.position.set(-1.7, 1.35, 1.05);
  inte.add(lanternLight);
  inte.add(lantern);
  W.lanternLight = lanternLight;
  W.lampGlassMat = lampGlass.material;

  // ---- notebook (opens) ----
  const notebook = new THREE.Group();
  notebook.position.set(0.35, 0.83, 1.0);
  notebook.rotation.y = -0.35;
  const nbCover = box(0.38, 0.022, 0.27, '#5a3a22');
  notebook.add(nbCover);
  const nbPagesTex = loader.load('img/tex_notebook.png');
  const nbPageMat = new THREE.MeshLambertMaterial({ map: nbPagesTex });
  const nbPage = new THREE.Mesh(plane(0.36, 0.25), nbPageMat);
  nbPage.rotation.x = -Math.PI / 2;
  nbPage.position.set(0, 0.014, 0);
  nbPage.visible = false;
  notebook.add(nbPage);
  inte.add(notebook);
  W.notebook = notebook;
  W.nbCover = nbCover;
  W.nbPage = nbPage;

  // ---- keys + tag on desk ----
  const keys = new THREE.Group();
  keys.position.set(-1.1, 0.81, 0.85);
  const key1 = box(0.11, 0.015, 0.045, '#c8b060');
  const key2 = box(0.09, 0.015, 0.045, '#c8b060', { x: 0.06, z: 0.03, ry: 0.5 });
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.035, 0.008, 6, 12), lam('#a89050'));
  ring.rotation.x = Math.PI / 2;
  keys.add(key1, key2, ring);
  inte.add(keys);
  W.keys = keys;
  // name tag
  const tag = new THREE.Mesh(plane(0.26, 0.13), new THREE.MeshLambertMaterial({ map: makeNameTagTex() }));
  tag.rotation.x = -Math.PI / 2;
  tag.position.set(0.9, 0.815, 0.9);
  tag.rotation.z = 0.2;
  inte.add(tag);
  W.nameTag = tag;

  // ---- wall clock ----
  const clock = new THREE.Mesh(plane(0.5, 0.25), new THREE.MeshBasicMaterial({ map: makeClockTex('11:47') }));
  clock.position.set(1.35, 1.9, -1.98);
  inte.add(clock);
  W.clock = clock;

  // ---- phone on desk ----
  const phone = new THREE.Group();
  phone.position.set(1.35, 0.815, 1.25);
  phone.add(box(0.2, 0.016, 0.1, '#181a1e'));
  const screenTexes = {
    msg: loader.load('img/tex_phone_msg.png'),
    photo: loader.load('img/tex_phone_photo.png'),
    noservice: loader.load('img/tex_phone_noservice.png'),
  };
  const screenMat = new THREE.MeshBasicMaterial({ map: screenTexes.msg });
  const screen = new THREE.Mesh(plane(0.185, 0.33), screenMat);
  screen.rotation.x = -Math.PI / 2 - 0.0;
  screen.rotation.z = Math.PI / 2;
  screen.position.y = 0.012;
  screen.visible = false;
  phone.add(screen);
  inte.add(phone);
  W.phone = phone;
  W.phoneScreen = screen;
  W.screenTexes = screenTexes;
  W.screenMat = screenMat;

  // ---- back door ----
  const doorPivot = new THREE.Group();
  doorPivot.position.set(-2.44, 0, -0.6);
  const doorMesh = box(0.09, 2.1, 0.86, '#5c4630', { x: 0.045, y: 1.05 });
  doorPivot.add(doorMesh);
  const knob = cyl(0.035, 0.035, 0.05, '#c8b060', 8);
  knob.rotation.z = Math.PI / 2;
  knob.position.set(0.09, 1.02, 0.32);
  doorPivot.add(knob);
  inte.add(doorPivot);
  W.doorPivot = doorPivot;

  // ---- stair hatch + descending steps (danger from below) ----
  const hatch = new THREE.Group();
  hatch.position.set(1.9, 0, 0.9);
  const hatchFrame = box(0.95, 0.1, 0.95, '#4e3b28', { y: 0.05 });
  hatch.add(hatchFrame);
  const darkBelow = new THREE.Mesh(plane(0.85, 0.85), new THREE.MeshBasicMaterial({ color: '#050608' }));
  darkBelow.rotation.x = -Math.PI / 2;
  darkBelow.position.y = -0.02;
  hatch.add(darkBelow);
  // descending steps (below floor, going -y)
  const belowSteps = new THREE.Group();
  for (let i = 0; i < 7; i++) {
    belowSteps.add(box(0.8, 0.07, 0.26, '#5c4630', { x: 1.9, y: -0.18 - i * 0.3, z: 0.55 + i * 0.26 }));
  }
  inte.add(belowSteps);
  W.belowSteps = belowSteps;
  const belowGlow = new THREE.PointLight(0xff3020, 0, 9, 1.2);
  belowGlow.position.set(1.9, -1.4, 1.4);
  inte.add(belowGlow);
  W.belowGlow = belowGlow;
  inte.add(hatch);
  W.hatch = hatch;

  // ---- office flashback vignette (far away) ----
  const office = new THREE.Group();
  office.position.set(40, 0, 40);
  scene.add(office);
  office.add(box(6, 4, 0.3, '#a89878', { y: 2, z: -0.2 })); // wall
  office.add(box(6, 0.2, 3, '#6b5a40', { y: 0.1 })); // floor patch
  // coat hanger hook
  const hook = cyl(0.03, 0.03, 0.34, '#8a8070', 6);
  hook.position.set(0, 2.6, 0.02);
  office.add(hook);
  // orange jacket on hanger
  const jacket = new THREE.Group();
  jacket.position.set(0, 2.28, 0.12);
  jacket.add(box(0.7, 0.85, 0.22, '#c05a20', { y: -0.42 }));
  jacket.add(box(0.16, 0.34, 0.2, '#c05a20', { x: -0.42, y: -0.25, ry: 0.3 }));
  jacket.add(box(0.16, 0.34, 0.2, '#c05a20', { x: 0.42, y: -0.25, ry: -0.3 }));
  jacket.add(box(0.5, 0.14, 0.24, '#a84a18', { y: -0.05 })); // collar
  office.add(jacket);
  W.office = office;
  W.jacket = jacket;
  // green outline shell on jacket (reveal annotation)
  const jOutline = new THREE.Mesh(new THREE.BoxGeometry(0.95, 1.1, 0.4), new THREE.MeshBasicMaterial({ color: '#2aff7a', transparent: true, opacity: 0, side: THREE.BackSide }));
  jOutline.position.copy(jacket.position);
  jOutline.position.y -= 0.42;
  office.add(jOutline);
  W.jacketOutline = jOutline;

  // ========================================================== MACRO STAGES
  // dark stage area at x=40; slots along z. Camera visits for macro shots.
  const macro = new THREE.Group();
  macro.position.set(40, 2, 0);
  scene.add(macro);
  W.macro = macro;
  const mkStage = (z, w, h, texOrColor, basic = true) => {
    const grp = new THREE.Group();
    grp.position.z = z;
    const mat = basic
      ? new THREE.MeshBasicMaterial(texOrColor instanceof THREE.Texture ? { map: texOrColor } : { color: texOrColor })
      : new THREE.MeshLambertMaterial(texOrColor instanceof THREE.Texture ? { map: texOrColor } : { color: texOrColor });
    const pl = new THREE.Mesh(plane(w, h), mat);
    grp.add(pl);
    // dim backing wall for parallax
    const back = new THREE.Mesh(plane(w * 1.6, h * 1.6), new THREE.MeshBasicMaterial({ color: '#07080c' }));
    back.position.z = -1.4;
    grp.add(back);
    grp.visible = false;
    macro.add(grp);
    return grp;
  };
  W.stageCctv = mkStage(0, 9.6, 17.1, loader.load('img/img01_cctv.png'));       // slot 0
W.stageCctv.children[0].material.color.setRGB(1.45, 1.45, 1.45);
  W.stageNotebook = mkStage(6, 7.2, 3.9, loader.load('img/tex_notebook.png'));  // slot 1
  W.stageWarning = mkStage(12, 7.2, 3.9, loader.load('img/tex_warning.png'));   // slot 2
  W.stagePhoneMsg = mkStage(18, 3.6, 6.4, screenTexes.msg);                     // slot 3
  W.stagePhonePhoto = mkStage(24, 3.6, 6.4, screenTexes.photo);                 // slot 4
  W.stagePhoneNoSvc = mkStage(30, 3.6, 6.4, screenTexes.noservice);             // slot 5
  // CCTV scanline HUD overlay (separate, in front of cctv stage)
  const cctvHud = new THREE.Mesh(plane(9.6, 17.1), new THREE.MeshBasicMaterial({ map: makeCctvHudTex(), transparent: true, opacity: 0 }));
  cctvHud.position.z = 0.3;
  W.stageCctv.add(cctvHud);
  W.cctvHud = cctvHud;
  // grain overlay for cctv
  const grain = new THREE.Mesh(plane(9.6, 17.1), new THREE.MeshBasicMaterial({ map: makeGrainTex(), transparent: true, opacity: 0, depthWrite: false }));
  grain.position.z = 0.32;
  W.stageCctv.add(grain);
  W.cctvGrain = grain;
  // red pulse frame for warning stage
  const redFrame = new THREE.Mesh(plane(7.6, 4.2), new THREE.MeshBasicMaterial({ color: '#ff2015', transparent: true, opacity: 0, depthWrite: false }));
  redFrame.position.z = 0.15;
  W.stageWarning.add(redFrame);
  W.warnRedFrame = redFrame;

  // ========================================================== LIGHTS (globals)
  const sun = new THREE.DirectionalLight(0xffd9a0, 0);
  sun.position.set(-18, 22, -14);
  scene.add(sun);
  W.sun = sun;
  const moonLight = new THREE.DirectionalLight(0x8fa3e8, 0);
  moonLight.position.set(-20, 30, -18);
  scene.add(moonLight);
  W.moonLight = moonLight;
  const amb = new THREE.AmbientLight(0x404860, 0.3);
  scene.add(amb);
  W.amb = amb;
  const hemi = new THREE.HemisphereLight(0x8fa8c8, 0x4a3c2c, 0.7);
  scene.add(hemi);
  W.hemi = hemi;
  // beam landing light (lights the figure when flashlight is on)
  const figLight = new THREE.PointLight(0xffe9b0, 0, 14, 1.15);
  figLight.position.set(0.3, 3.0, 5.2);
  scene.add(figLight);
  W.figLight = figLight;
  // red danger light under the tower (knocks beat)
  const underRed = new THREE.PointLight(0xff2818, 0, 12, 1.2);
  underRed.position.set(0, 1.4, 3.0);
  scene.add(underRed);
  W.underRed = underRed;
  // office flashback light
  const officeLight = new THREE.PointLight(0xffe2c0, 0, 10, 1.15);
  officeLight.position.set(40, 3.4, 41.6);
  scene.add(officeLight);
  W.officeLight = officeLight;
  const cabGlow = new THREE.PointLight(0xffd9b8, 0, 16, 1.1); // interior fill
  cabGlow.position.set(0, FLOOR + 1.7, 0);
  scene.add(cabGlow);
  W.cabGlow = cabGlow;

  // ========================================================== VIGNETTE (screen-space)
  const vig = new THREE.Mesh(plane(5.6, 10.0), new THREE.MeshBasicMaterial({ map: makeVignetteTex(), transparent: true, opacity: 0.9, depthTest: false }));
  vig.renderOrder = 998;
  W.vig = vig;

  return W;
}

function makeVignetteTex() {
  return makeCanvasTex(360, 640, (g, w, h) => {
    const grd = g.createRadialGradient(w / 2, h / 2, h * 0.34, w / 2, h / 2, h * 0.62);
    grd.addColorStop(0, 'rgba(0,0,0,0)');
    grd.addColorStop(1, 'rgba(0,0,0,0.5)');
    g.fillStyle = grd;
    g.fillRect(0, 0, w, h);
  });
}
