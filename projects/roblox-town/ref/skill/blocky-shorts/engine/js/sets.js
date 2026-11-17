// Set library. Every set is built around the origin with "front" = +z (where the camera usually is).
// build(opts) returns { group, spots, interior, walkZone, crowd, setMood(mood) }.
// spots: { name: { pos:[x,y,z], yaw:deg, seat?:h, bed?:h } } — yaw 0 means facing +z (toward camera).
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { M, mesh, box, cyl, sph, tex, rng, canvasTex, textPlane, fitText, emissive } from './util.js';

// ---------- shared pieces
const skyTex = {
  day: canvasTex(256, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#2f7ff0'); gr.addColorStop(1, '#b8e0ff'); g.fillStyle = gr; g.fillRect(0, 0, w, h); g.fillStyle = 'rgba(255,255,255,.9)'; for (const [x, y, r] of [[60, 80, 26], [90, 74, 32], [120, 84, 24], [180, 150, 20], [205, 146, 26]]) { g.beginPath(); g.arc(x, y, r, 0, 7); g.fill(); } }),
  sunset: canvasTex(256, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#6a4bb0'); gr.addColorStop(.6, '#ff8a5c'); gr.addColorStop(1, '#ffd27a'); g.fillStyle = gr; g.fillRect(0, 0, w, h); }),
  night: canvasTex(256, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#050a1e'); gr.addColorStop(1, '#1b2a5c'); g.fillStyle = gr; g.fillRect(0, 0, w, h); const r = rng(3); g.fillStyle = '#fff'; for (let i = 0; i < 40; i++) g.fillRect(r() * w, r() * h * .8, 2, 2); g.fillStyle = '#f4f1d0'; g.beginPath(); g.arc(190, 60, 22, 0, 7); g.fill(); }),
};
function windowPane(w, h, parent, x, y, z, ry = 0) {
  const g = new THREE.Group(); g.position.set(x, y, z); g.rotation.y = ry; parent.add(g);
  const mat = new THREE.MeshStandardMaterial({ map: skyTex.day, emissive: '#ffffff', emissiveMap: skyTex.day, emissiveIntensity: .9 });
  const p = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat); g.add(p);
  const fm = M('#f4f4f4');
  box(w + .3, .18, .2, fm, 0, h / 2, .05, g); box(w + .3, .18, .2, fm, 0, -h / 2, .05, g); box(.18, h, .2, fm, -w / 2, 0, .05, g); box(.18, h, .2, fm, w / 2, 0, .05, g); box(.1, h, .12, fm, 0, 0, .05, g); box(w, .1, .12, fm, 0, 0, .05, g);
  box(w + .6, .14, .5, fm, 0, -h / 2 - .1, .2, g);
  g.traverse(m => { if (m.isMesh) m.castShadow = false; });
  return (mood) => { mat.map = mat.emissiveMap = skyTex[mood] || skyTex.day; mat.emissiveIntensity = mood === 'night' ? .7 : 1.0; mat.needsUpdate = true; };
}
function lampPost(parent, x, z, lights) {
  const g = new THREE.Group(); g.position.set(x, 0, z); parent.add(g);
  cyl(.09, .14, 4.6, M('#2b2d31', { metalness: .5, roughness: .4 }), 0, 2.3, 0, g, 10);
  const bm = new THREE.MeshStandardMaterial({ color: '#fff5d6', emissive: '#ffd27a', emissiveIntensity: .3 });
  for (const s of [-1, 1]) { box(1.0, .08, .08, M('#2b2d31'), s * .45, 4.5, 0, g); const b = sph(.26, bm, s * .9, 4.35, 0, g, 14); b.castShadow = false; }
  const L = new THREE.PointLight('#ffcf80', 0, 16, 1.6); L.position.set(0, 4.2, 0); g.add(L);
  lights.push({ L, bm });
}
function lampsMood(lights, mood) { for (const { L, bm } of lights) { L.intensity = mood === 'night' ? 30 : mood === 'sunset' ? 6 : 0; bm.emissiveIntensity = mood === 'night' ? 2.2 : mood === 'sunset' ? 1 : .3; } }
function pine(parent, x, z, s = 1) { const g = new THREE.Group(); g.position.set(x, 0, z); g.scale.setScalar(s); parent.add(g); cyl(.25, .35, 1.6, M('#6b4425'), 0, .8, 0, g, 8); for (let i = 0; i < 3; i++) { const c = mesh(new THREE.ConeGeometry(2.1 - i * .5, 2.4, 8), M('#2f7a3d', { flatShading: true })); c.position.y = 2.2 + i * 1.3; g.add(c); } return g; }
function palm(parent, x, z, s = 1, rot = 0) {
  const g = new THREE.Group(); g.position.set(x, 0, z); g.scale.setScalar(s); g.rotation.y = rot; parent.add(g);
  let y = 0, xo = 0; for (let i = 0; i < 6; i++) { const seg = cyl(.22, .28, 1.05, M('#8a6a45', { flatShading: true }), xo, y + .5, 0, g, 8); seg.rotation.z = -.06 * i; y += 1; xo += .07 * i; }
  for (let i = 0; i < 7; i++) { const lf = new THREE.Group(); lf.position.set(xo, y, 0); lf.rotation.y = i / 7 * Math.PI * 2; const a = box(.7, .06, 2.6, M('#3f9e3a', { flatShading: true }), 0, 0, 1.2, lf); a.rotation.x = .45; const b = box(.5, .05, 1.2, M('#368f33', { flatShading: true }), 0, -.75, 2.8, lf); b.rotation.x = .95; g.add(lf); }
  return g;
}
function roundTree(parent, x, z, s = 1, color = '#3f9e3a') { const g = new THREE.Group(); g.position.set(x, 0, z); g.scale.setScalar(s); parent.add(g); cyl(.3, .4, 2.4, M('#6b4425'), 0, 1.2, 0, g, 8); const r = rng(Math.round(x * 13 + z * 7)); for (let i = 0; i < 4; i++) sph(1.3 + r() * .5, M(color, { flatShading: true }), (r() - .5) * 1.6, 3.4 + r() * 1.2, (r() - .5) * 1.6, g, 8); return g; }
function bench(parent, x, z, yaw) { const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = yaw; parent.add(g); const wm = M('#ffffff', { map: tex('wood') }); box(2.8, .22, .9, wm, 0, .9, 0, g); box(2.8, .7, .16, wm, 0, 1.45, -.4, g); for (const s of [-1.2, 1.2]) box(.18, .9, .8, M('#3a3c40'), s, .45, 0, g); return g; }
function ground(parent, size, mat, y = 0) { const p = mesh(new THREE.PlaneGeometry(size, size), mat, false, true); p.rotation.x = -Math.PI / 2; p.position.y = y; parent.add(p); return p; }
function hills(parent, seed = 13) { const r = rng(seed); for (let i = 0; i < 9; i++) { const a = -Math.PI * .1 - r() * Math.PI * 1.2 + (i % 2) * Math.PI, d = 140 + r() * 80; const h = mesh(new THREE.SphereGeometry(1, 16, 10), M('#5d9a4a', { flatShading: true, roughness: 1 }), false, false); h.scale.set(40 + r() * 40, 12 + r() * 16, 40 + r() * 30); h.position.set(Math.cos(a) * d, -2, Math.sin(a) * d); parent.add(h); } }
function room(g, { w = 18, d = 14, h = 7, wall = '#ece0b0', low = '#2f6ed8', floor = 'planks', floorRep = 4, ceiling = true }) {
  const fl = mesh(new THREE.PlaneGeometry(w, d), M('#ffffff', { map: tex(floor, floorRep), roughness: .7 }), false, true); fl.rotation.x = -Math.PI / 2; g.add(fl);
  const up = M(wall, { roughness: .9 }), lo = M(low, { roughness: .8 });
  const wallAt = (W, x, z, ry) => { const u = mesh(new THREE.PlaneGeometry(W, h - 2), up, false, true); u.position.set(x, 2 + (h - 2) / 2, z); u.rotation.y = ry; g.add(u); const l = mesh(new THREE.PlaneGeometry(W, 2), lo, false, true); l.position.set(x, 1, z); l.rotation.y = ry; g.add(l); };
  wallAt(w, 0, -d / 2, 0); wallAt(d, -w / 2, 0, Math.PI / 2); wallAt(d, w / 2, 0, -Math.PI / 2);
  if (ceiling) { const c = mesh(new THREE.PlaneGeometry(w, d), M('#f0efe8'), false, false); c.rotation.x = Math.PI / 2; c.position.y = h; g.add(c); }
  return { up, lo };
}
function ceilingPanels(g, positions, y = 6.95) { const pm = new THREE.MeshStandardMaterial({ color: '#ffffff', emissive: '#ffffff', emissiveIntensity: 1.4 }); for (const [x, z] of positions) { const p = new THREE.Mesh(new THREE.BoxGeometry(2.6, .08, .6), pm); p.position.set(x, y, z); g.add(p); } return pm; }
function interiorLights(g, spots) { const ls = spots.map(([x, y, z]) => { const L = new THREE.PointLight('#fff4e0', 40, 40, 1.4); L.position.set(x, y, z); g.add(L); return L; }); return ls; }
function poster(g, x, y, z, ry, w, h, draw) { const p = textPlane(w, h, draw); p.position.set(x, y, z); p.rotation.y = ry; g.add(p); return p; }
function plant(g, x, z, s = 1) { const p = new THREE.Group(); p.position.set(x, 0, z); p.scale.setScalar(s); g.add(p); cyl(.5, .4, .9, M('#c0603a'), 0, .45, 0, p, 14); for (let i = 0; i < 6; i++) { const l = box(.3, 1.6, .08, M('#3f9e3a'), 0, 1.4, 0, p); l.rotation.set(Math.cos(i) * .5, i, Math.sin(i) * .5); } }
function desk(g, x, z, yaw = 0, { chair = true } = {}) { const d = new THREE.Group(); d.position.set(x, 0, z); d.rotation.y = yaw; g.add(d); const wm = M('#ffffff', { map: tex('wood') }), mm = M('#3a3d44', { metalness: .6, roughness: .35 }); box(2.4, .16, 1.4, wm, 0, 2.62, 1.45, d); for (const sx of [-1, 1]) box(.12, 2.6, .12, mm, sx * 1.05, 1.3, 1.45, d); if (chair) { box(1.8, .16, 1.5, wm, 0, 1.3, 0, d); box(1.8, 1.6, .14, wm, 0, 2.3, -.75, d); for (const sx of [-.8, .8]) for (const sz of [-.65, .65]) box(.1, 1.3, .1, mm, sx, .65, sz, d); } return d; }
function car(g, x, z, yaw, color) { const c = new THREE.Group(); c.position.set(x, 0, z); c.rotation.y = yaw; g.add(c); const bm = M(color, { roughness: .3, metalness: .2 }); const body = mesh(new RoundedBoxGeometry(5, 1.3, 2.4, 3, .3), bm); body.position.y = 1.15; c.add(body); const top = mesh(new RoundedBoxGeometry(2.8, 1.0, 2.2, 3, .3), M('#9fd0ff', { roughness: .1, metalness: .3 })); top.position.set(-.3, 2.2, 0); c.add(top); for (const sx of [-1.6, 1.6]) for (const sz of [-1.15, 1.15]) { const w = cyl(.55, .55, .4, M('#1c1c1c'), sx, .55, sz, c, 16); w.rotation.x = Math.PI / 2; } return c; }
function house(g, x, z, color, roof, seed) { const h = new THREE.Group(); h.position.set(x, 0, z); g.add(h); const r = rng(seed); const W = 7 + r() * 2, H = 5 + r() * 2; box(W, H, 6, M(color), 0, H / 2, 0, h); const rf = mesh(new THREE.ConeGeometry(W * .78, 3, 4), M(roof, { flatShading: true })); rf.position.y = H + 1.5; rf.rotation.y = Math.PI / 4; rf.scale.z = .85; h.add(rf); box(1.4, 2.6, .1, M('#6b3a1e'), -W / 4, 1.3, 3.02, h); const wins = []; for (const wx of [W / 6, W / 3 + .3]) { const wm = new THREE.MeshStandardMaterial({ color: '#bfe2ff', emissive: '#ffd27a', emissiveIntensity: 0 }); const wp = new THREE.Mesh(new THREE.PlaneGeometry(1.3, 1.3), wm); wp.position.set(wx, H * .62, 3.02); h.add(wp); wins.push(wm); } return wins; }

// ---------- SETS
export const SETS = {
  plaza(opts = {}) {
    const g = new THREE.Group(); const lights = [];
    const ocean = mesh(new THREE.PlaneGeometry(3000, 3000), M('#2a74d8', { roughness: .15, metalness: .1 }), false, false); ocean.rotation.x = -Math.PI / 2; ocean.position.y = -1.2; g.add(ocean);
    const gr = mesh(new THREE.CircleGeometry(55, 64), M('#ffffff', { map: tex('asphalt', 14), roughness: .9 }), false, true); gr.rotation.x = -Math.PI / 2; g.add(gr);
    const sk = mesh(new THREE.CylinderGeometry(55, 60, 1.2, 64, 1, true), M('#6b8f4a', { roughness: 1 }), false, false); sk.position.y = -.6; g.add(sk);
    const ring = mesh(new THREE.RingGeometry(4.6, 6.6, 64), M('#ffffff', { map: tex('grass', 8), roughness: 1 }), false, true); ring.rotation.x = -Math.PI / 2; ring.position.y = .03; g.add(ring);
    const curb = mesh(new THREE.TorusGeometry(6.7, .18, 8, 64), M('#c9ccd2'), false, true); curb.rotation.x = Math.PI / 2; curb.position.y = .1; g.add(curb);
    { const r = rng(8); for (let i = 0; i < 14; i++) { const a = r() * Math.PI * 2, d = 22 + r() * 26; const p = mesh(new THREE.CircleGeometry(4 + r() * 6, 24), M('#ffffff', { map: tex('grass', 8), roughness: 1 }), false, true); p.rotation.x = -Math.PI / 2; p.position.set(Math.cos(a) * d, .02, Math.sin(a) * d); g.add(p); } }
    // fountain
    const f = new THREE.Group(); g.add(f); const st = M('#ffffff', { map: tex('stone', 3), roughness: .85 });
    cyl(4.3, 4.5, 1.1, st, 0, 0, 0, f, 48);
    const waterM = new THREE.MeshStandardMaterial({ color: '#3d8fe0', roughness: .08, metalness: .2, emissive: '#1b5fff', emissiveIntensity: 0 });
    cyl(3.95, 3.95, .1, waterM, 0, 1.0, 0, f, 48).castShadow = false;
    cyl(1.4, 1.8, 1.8, st, 0, 1.9, 0, f, 32); cyl(2.3, 1.3, .5, st, 0, 3.0, 0, f, 32); cyl(.35, .5, 1.3, st, 0, 3.9, 0, f, 16); cyl(1.0, .45, .35, st, 0, 4.6, 0, f, 24);
    const dropTex = canvasTex(64, 64, (c) => { const q = c.createRadialGradient(32, 32, 0, 32, 32, 32); q.addColorStop(0, 'rgba(255,255,255,1)'); q.addColorStop(.4, 'rgba(255,255,255,.8)'); q.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = q; c.fillRect(0, 0, 64, 64); });
    const JETS = []; for (let i = 0; i < 10; i++) JETS.push({ a: i / 10 * Math.PI * 2, y0: 4.85, r0: .2, R: 3.4, h: 2.6, y1: 1.05, sp: .9 }); for (let i = 0; i < 14; i++) JETS.push({ a: i / 14 * Math.PI * 2 + .2, y0: 3.3, r0: 2.2, R: 3.7, h: 1.0, y1: 1.05, sp: 1.2 });
    const PER = 46; const dg = new THREE.BufferGeometry(); dg.setAttribute('position', new THREE.Float32BufferAttribute(new Float32Array(JETS.length * PER * 3), 3));
    const dm = new THREE.PointsMaterial({ color: '#d6ecff', size: .22, map: dropTex, transparent: true, depthWrite: false, opacity: .85 });
    f.add(new THREE.Points(dg, dm));
    const update = (t) => { const p = dg.attributes.position.array; let k = 0; const r = rng(99); for (const j of JETS) for (let i = 0; i < PER; i++) { const s = ((i / PER + t * j.sp * .55 + r() * .02) % 1); const d = j.r0 + (j.R - j.r0) * s + (r() - .5) * .15, a = j.a + (r() - .5) * .05; p[k++] = Math.cos(a) * d; p[k++] = j.y0 + (j.y1 - j.y0) * s + 4 * j.h * s * (1 - s); p[k++] = Math.sin(a) * d; } dg.attributes.position.needsUpdate = true; };
    for (const a of [-Math.PI / 6, -Math.PI / 2, -5 * Math.PI / 6, Math.PI * 5 / 6, Math.PI / 6 + .05]) lampPost(g, Math.cos(a) * 10.5, Math.sin(a) * 10.5, lights);
    for (const a of [0, -Math.PI / 3, -2 * Math.PI / 3, Math.PI, 2.35]) bench(g, Math.cos(a) * 9, Math.sin(a) * 9, -a + Math.PI / 2);
    { const r = rng(42); for (let i = 0; i < 26; i++) { const a = r() * Math.PI * 2, d = 15 + r() * 30; const x = Math.cos(a) * d, z = Math.sin(a) * d; if (Math.abs(x) < 9 && z > 6 && z < 34) continue; (r() < .55 ? pine : palm)(g, x, z, .9 + r() * .6, r() * 6); } }
    hills(g);
    if (opts.stage) { box(9, .6, 4, M('#ffffff', { map: tex('stone', 3) }), 0, .3, 7.0, g); }
    const lectern = opts.stage ? (() => { const l = new THREE.Group(); l.position.set(0, .6, 8.45); g.add(l); const wm = M('#ffffff', { map: tex('wood') }); box(2.6, 2.8, 1.1, wm, 0, 1.4, 0, l); const tp = box(2.9, .18, 1.5, wm, 0, 2.9, -.1, l); tp.rotation.x = -.18; box(3.0, .25, 1.5, wm, 0, .12, 0, l); const mic = cyl(.04, .04, .9, M('#222'), .5, 3.3, -.3, l, 8); mic.rotation.x = -.5; sph(.13, M('#999', { metalness: .8, roughness: .3 }), .5, 3.72, -.52, l, 12); const seal = textPlane(1.1, 1.1, (c, w, h) => { c.fillStyle = '#f2c230'; c.beginPath(); c.arc(w / 2, h / 2, w / 2 - 2, 0, 7); c.fill(); c.fillStyle = '#b8860b'; c.beginPath(); c.arc(w / 2, h / 2, w * .38, 0, 7); c.fill(); fitText(c, ['★'], w, h, { color: '#fff3c0', maxSize: 150 }); }); seal.position.set(0, 1.8, .56); l.add(seal); return l; })() : null;
    void lectern;
    return {
      group: g, interior: false, update,
      spots: { center: { pos: [0, 0, 8] }, front: { pos: [-2, 0, 9] }, left: { pos: [-6, 0, 9], yaw: 20 }, right: { pos: [6, 0, 9], yaw: -20 }, fountain: { pos: [0, 0, 5.4] }, bench: { pos: [9, 0, 0], yaw: -90, seat: .98 }, podium: { pos: [0, .6, 7.2] }, far: { pos: [0, 0, -9], yaw: 180 } },
      walkZone: { x: [-16, 16], z: [-12, 4] }, crowd: { center: [0, 0, 16], yaw: 180 },
      setMood(m) { lampsMood(lights, m); waterM.emissiveIntensity = m === 'night' ? .9 : 0; dm.color.set(m === 'night' ? '#4d8dff' : '#d9eeff'); ocean.material.color.set(m === 'night' ? '#081a44' : '#2a74d8'); },
    };
  },

  street(opts = {}) {
    const g = new THREE.Group(); const lights = [];
    ground(g, 300, M('#ffffff', { map: tex('grass', 40), roughness: 1 }), -.02);
    box(300, .05, 9, M('#ffffff', { map: tex('asphalt', 30), roughness: .9 }), 0, 0, 0, g).castShadow = false;
    for (let x = -60; x < 60; x += 6) box(3, .02, .3, M('#f5f5f5'), x, .04, 0, g).castShadow = false;
    for (const z of [6.2, -6.2]) { box(300, .3, 3.4, M('#ffffff', { map: tex('concrete', 30) }), 0, .15, z, g).castShadow = false; box(300, .32, .3, M('#c9ccd2'), 0, .16, z - Math.sign(z) * 1.7, g); }
    for (let i = 0; i < 6; i++) box(.9, .03, 6, M('#f5f5f5'), 10 + i * 1.6, .04, 0, g).castShadow = false; // crosswalk
    const winMats = []; const cols = ['#f2d0a4', '#a8d5e2', '#f7a8a8', '#c7e9b0', '#f5e6a8', '#d6c1f0']; const roofs = ['#8a3a2a', '#3a4a6a', '#5a3a2a'];
    for (let i = 0; i < 8; i++) winMats.push(...house(g, -36 + i * 10, -13, cols[i % cols.length], roofs[i % 3], i + 3));
    for (let i = -3; i <= 3; i++) lampPost(g, i * 14 + 4, -4.8, lights);
    car(g, -14, 2.4, Math.PI / 2 * 0 + 0, '#e8352e'); car(g, 24, -2.4, Math.PI, '#2b7bf0');
    for (let i = 0; i < 8; i++) roundTree(g, -40 + i * 11 + 5, -19, 1.2);
    hills(g, 21);
    const tl = new THREE.Group(); tl.position.set(8.3, 0, 4.8); g.add(tl); cyl(.12, .12, 5, M('#2b2d31'), 0, 2.5, 0, tl, 8); box(.7, 1.9, .6, M('#222'), 0, 5.2, 0, tl); const tls = ['#ff3b30', '#ffcc00', '#34c759'].map((c, i) => { const m = emissive(c, i === 2 ? 2 : .15); sph(.22, m, 0, 5.8 - i * .6, .32, tl, 12); return m; }); void tls;
    return {
      group: g, interior: false, spots: { sidewalk: { pos: [0, .3, 6.2] }, center: { pos: [0, 0, 1.5] }, road: { pos: [0, 0, 0] }, left: { pos: [-6, .3, 6.2], yaw: 90 }, right: { pos: [6, .3, 6.2], yaw: -90 }, door: { pos: [-6.5, .3, -6.0] }, crosswalk: { pos: [13, 0, 0], yaw: -90 } },
      walkZone: { x: [-20, 20], z: [-7, -5] }, crowd: { center: [0, .3, 6.5], yaw: 0 },
      setMood(m) { lampsMood(lights, m); for (const w of winMats) w.emissiveIntensity = m === 'night' ? 1.4 : 0; },
    };
  },

  living_room(opts = {}) {
    const g = new THREE.Group(); room(g, { w: 18, d: 14, wall: opts.wall || '#e9d8b4', low: opts.trim || '#8a5a3a' });
    const sw = windowPane(4, 2.8, g, -2, 4.4, -6.95);
    const rug = mesh(new THREE.CylinderGeometry(3.6, 3.6, .04, 40), M('#c0392b', { roughness: 1 }), false, true); rug.position.set(0, .03, 0); rug.scale.z = .7; g.add(rug);
    // sofa on the left, facing +x
    const so = new THREE.Group(); so.position.set(-5.4, 0, -.5); so.rotation.y = Math.PI / 2; g.add(so); const sm = M(opts.sofa || '#4a6fa5', { roughness: .9 });
    so.add(mesh(new RoundedBoxGeometry(6, 1.1, 2.4, 3, .3), sm)); so.children[0].position.y = .9; const bk = mesh(new RoundedBoxGeometry(6, 1.8, .8, 3, .3), sm); bk.position.set(0, 1.9, -1.0); so.add(bk); for (const s of [-1, 1]) { const a = mesh(new RoundedBoxGeometry(.8, 1.6, 2.4, 3, .3), sm); a.position.set(s * 3.1, 1.2, 0); so.add(a); }
    for (const s of [-1.2, 1.2]) { const c = mesh(new RoundedBoxGeometry(1.2, 1.0, .4, 2, .15), M('#f2c230', { roughness: 1 })); c.position.set(s, 1.9, -.5); c.rotation.x = -.2; so.add(c); }
    // TV on the right wall, facing -x
    const tv = new THREE.Group(); tv.position.set(7.6, 0, -.5); tv.rotation.y = -Math.PI / 2; g.add(tv); box(4.5, 1.4, 1.4, M('#5a3a24'), 0, .7, 0, tv); box(4.6, 2.7, .2, M('#111'), 0, 3.0, 0, tv);
    const scr = new THREE.MeshStandardMaterial({ color: '#203a7a', emissive: '#3a6fd8', emissiveIntensity: .6 }); const sp = new THREE.Mesh(new THREE.PlaneGeometry(4.3, 2.4), scr); sp.position.set(0, 3.0, .11); tv.add(sp);
    box(3.2, .2, 1.8, M('#ffffff', { map: tex('wood') }), -1, 1.3, -.5, g); for (const [x, z] of [[-2.4, -1.2], [.4, -1.2], [-2.4, .2], [.4, .2]]) box(.15, 1.3, .15, M('#5a3a24'), x, .65, z, g);
    const fl = new THREE.Group(); fl.position.set(-7, 0, -5.4); g.add(fl); cyl(.08, .08, 4.6, M('#333'), 0, 2.3, 0, fl, 8); const lampM = emissive('#ffe2a8', .4); const sh = cyl(.5, .8, .9, lampM, 0, 4.7, 0, fl, 20); sh.castShadow = false;
    plant(g, 6.8, -5.5, 1.2); plant(g, -7.3, 5, 1);
    poster(g, 4, 4.6, -6.95, 0, 2.2, 1.6, (c, w, h) => { c.fillStyle = '#f4f1e8'; c.fillRect(0, 0, w, h); c.fillStyle = '#4f9a35'; c.fillRect(20, h * .55, w - 40, h * .35); c.fillStyle = '#ffd24a'; c.beginPath(); c.arc(w * .7, h * .35, 26, 0, 7); c.fill(); c.strokeStyle = '#5a3a24'; c.lineWidth = 16; c.strokeRect(0, 0, w, h); });
    const shelf = new THREE.Group(); shelf.position.set(-7.6, 0, 2.2); g.add(shelf); box(.8, 4.4, 3, M('#7a4a2a'), 0, 2.2, 0, shelf); const r = rng(5); for (let y = 0; y < 3; y++) for (let i = 0; i < 6; i++) box(.6, .9, .25, M(['#e8352e', '#2b7bf0', '#f4c542', '#3cba54'][(i + y) % 4]), .1, .9 + y * 1.3, -1.2 + i * .45 + r() * .1, shelf);
    const lights = interiorLights(g, [[0, 6.2, 0]]);
    return {
      group: g, interior: true, spots: { sofa: { pos: [-5.2, 0, -.5], yaw: 90, seat: 1.45 }, sofa2: { pos: [-5.2, 0, 1.3], yaw: 90, seat: 1.45 }, center: { pos: [1.5, 0, 1.5] }, tv: { pos: [5.5, 0, 1.5], yaw: -90 }, window: { pos: [-2, 0, -4.5], yaw: 180 }, door: { pos: [6, 0, 4] } },
      walkZone: null, crowd: null,
      setMood(m) { sw(m); for (const L of lights) L.intensity = m === 'night' ? 0 : 40; lampM.emissiveIntensity = m === 'night' ? 1.6 : .4; scr.emissiveIntensity = m === 'night' ? 1.4 : .6; },
      nightLight: { pos: [5, 4, 0], color: '#6b8cff', intensity: 18 },
    };
  },

  bedroom(opts = {}) {
    const g = new THREE.Group(); room(g, { w: 16, d: 14, wall: opts.wall || '#bcd7f2', low: opts.trim || '#f4f4f4', floor: 'planks' });
    const sw = windowPane(3.6, 2.8, g, 4, 4.4, -6.95);
    // bed: head at -z, against back wall
    const bed = new THREE.Group(); bed.position.set(-2.5, 0, -3.2); g.add(bed); const wm = M('#ffffff', { map: tex('wood') });
    box(3.6, 1.2, 6.6, wm, 0, .6, 0, bed); box(3.7, 2.8, .4, wm, 0, 1.4, -3.3, bed); box(3.4, .5, 6.2, M('#ffffff'), 0, 1.45, 0, bed); const blanket = mesh(new RoundedBoxGeometry(3.6, .3, 4.0, 2, .12), M(opts.blanket || '#3a5fd8', { roughness: 1 })); blanket.position.set(0, 1.78, 1.0); bed.add(blanket);
    const pil = mesh(new RoundedBoxGeometry(2.4, .45, 1.1, 2, .2), M('#ffffff', { roughness: 1 })); pil.position.set(0, 1.9, -2.5); bed.add(pil);
    const ns = new THREE.Group(); ns.position.set(.6, 0, -5.6); g.add(ns); box(1.4, 1.6, 1.2, wm, 0, .8, 0, ns); const clk = new THREE.Group(); clk.position.set(0, 1.9, .1); ns.add(clk); box(.8, .55, .4, M('#e8352e', { roughness: .3 }), 0, 0, 0, clk); const disp = textPlane(.6, .3, (c, w, h) => { c.fillStyle = '#111'; c.fillRect(0, 0, w, h); fitText(c, ['7:00'], w, h, { color: '#ff4d4d', maxSize: 90 }); }, { emissiveI: 1.2 }); disp.position.z = .21; clk.add(disp);
    const wardrobe = new THREE.Group(); wardrobe.position.set(6.6, 0, -2); g.add(wardrobe); box(1.6, 5.5, 3.6, M('#8a5a3a'), 0, 2.75, 0, wardrobe);
    const rug = mesh(new THREE.CylinderGeometry(2.4, 2.4, .04, 32), M('#f2c230', { roughness: 1 }), false, true); rug.position.set(2, .03, 1.5); g.add(rug);
    poster(g, -7.95, 4.4, -1, Math.PI / 2, 2, 2.6, (c, w, h) => { c.fillStyle = '#222'; c.fillRect(0, 0, w, h); c.fillStyle = '#ffdc1f'; c.beginPath(); for (let i = 0; i < 10; i++) { const r = i % 2 ? 22 : 54, a = -Math.PI / 2 + i * Math.PI / 5; c.lineTo(w / 2 + Math.cos(a) * r, h * .45 + Math.sin(a) * r); } c.fill(); });
    const lights = interiorLights(g, [[0, 6.2, 0]]);
    return {
      group: g, interior: true, spots: { bed: { pos: [-2.5, 0, -3.0], yaw: 0, bed: 1.62 }, bedside: { pos: [-.2, 0, -.5], yaw: -60 }, center: { pos: [1.5, 0, 1.5] }, window: { pos: [4, 0, -4.5], yaw: 180 }, door: { pos: [5, 0, 4.5] } },
      setMood(m) { sw(m); for (const L of lights) L.intensity = m === 'night' ? 0 : 40; },
      nightLight: { pos: [4, 4.4, -4], color: '#6b8cff', intensity: 22 },
    };
  },

  classroom(opts = {}) {
    const g = new THREE.Group(); room(g, { w: 18, d: 20, wall: '#ece0b0', low: '#2f6ed8' });
    const winFns = [-4.5, .5, 5.5].map(z => windowPane(3.2, 2.6, g, -8.95, 4.1, z, Math.PI / 2));
    const board = textPlane(9, 3.4, (c, w, h) => { c.fillStyle = '#1f3a2a'; c.fillRect(0, 0, w, h); c.strokeStyle = '#8a5a3a'; c.lineWidth = 24; c.strokeRect(0, 0, w, h); fitText(c, String(opts.board || 'MATH\n7 × 8 = ?').split('\n'), w, h, { color: '#f4f4ea', maxSize: 120, font: "'BS Black'" }); }, { px: 400 });
    board.position.set(0, 4.3, 9.9); board.rotation.y = Math.PI; g.add(board);
    const fw = mesh(new THREE.PlaneGeometry(18, 7), M('#ece0b0', { roughness: .9 }), false, true); fw.position.set(0, 3.5, 10); fw.rotation.y = Math.PI; g.add(fw);
    const bb = textPlane(9, 2.8, (c, w, h) => { c.fillStyle = '#c99556'; c.fillRect(0, 0, w, h); c.strokeStyle = '#6b4a24'; c.lineWidth = 14; c.strokeRect(0, 0, w, h); const r = rng(4); const cs = ['#ffd84d', '#ff7a7a', '#7ad0ff', '#9be37a', '#ffffff', '#ffb35c']; for (let i = 0; i < 22; i++) { c.save(); c.translate(30 + r() * (w - 90), 25 + r() * (h - 90)); c.rotate((r() - .5) * .2); c.fillStyle = cs[i % cs.length]; c.fillRect(0, 0, 60 + r() * 40, 45 + r() * 30); c.restore(); } }, { px: 280 });
    bb.position.set(0, 4.6, -9.95); g.add(bb);
    const desks = [[-4.2, 0], [0, 0], [4.2, 0], [-4.2, -4.6], [0, -4.6], [4.2, -4.6]]; desks.forEach(([x, z]) => desk(g, x, z, 0));
    const tdesk = new THREE.Group(); tdesk.position.set(3.5, 0, 7.4); g.add(tdesk); box(3.4, .2, 1.6, M('#ffffff', { map: tex('wood') }), 0, 2.6, 0, tdesk); box(3.2, 2.5, 1.4, M('#7a4a2a'), 0, 1.25, 0, tdesk);
    const pm = ceilingPanels(g, [[-3, -4], [3, -4], [-3, 1], [3, 1], [-3, 6], [3, 6]]);
    const lights = interiorLights(g, [[0, 6.2, 1]]);
    const spots = { teacher: { pos: [0, 0, 7.2], yaw: 180 }, board: { pos: [-2.5, 0, 8.6], yaw: 180 }, center: { pos: [0, 0, 3.2] } };
    desks.forEach(([x, z], i) => spots['desk' + (i + 1)] = { pos: [x, 0, z], yaw: 0, seat: 1.38 });
    return {
      group: g, interior: true, spots, crowd: null,
      setMood(m) { winFns.forEach(f => f(m)); for (const L of lights) L.intensity = m === 'night' ? 0 : 40; pm.emissiveIntensity = m === 'night' ? 0 : 1.4; },
      nightLight: { pos: [-6, 5, 2], color: '#5a7dff', intensity: 30 },
    };
  },

  office(opts = {}) {
    const g = new THREE.Group(); room(g, { w: 20, d: 16, wall: '#dfe4ea', low: '#9aa5b1', floor: 'carpet', floorRep: 6 });
    // window wall with city
    const city = canvasTex(512, 200, (c, w, h) => { c.fillStyle = '#9fd0ff'; c.fillRect(0, 0, w, h); const r = rng(9); for (let i = 0; i < 26; i++) { const bw = 14 + r() * 30, bh = 40 + r() * 140, x = r() * w; c.fillStyle = `hsl(215,${15 + r() * 15}%,${45 + r() * 25}%)`; c.fillRect(x, h - bh, bw, bh); c.fillStyle = 'rgba(255,255,255,.5)'; for (let y = h - bh + 6; y < h - 6; y += 12) for (let xx = x + 4; xx < x + bw - 4; xx += 8) c.fillRect(xx, y, 4, 6); } });
    const cityN = canvasTex(512, 200, (c, w, h) => { c.fillStyle = '#081230'; c.fillRect(0, 0, w, h); const r = rng(9); for (let i = 0; i < 26; i++) { const bw = 14 + r() * 30, bh = 40 + r() * 140, x = r() * w; c.fillStyle = '#121a33'; c.fillRect(x, h - bh, bw, bh); c.fillStyle = 'rgba(255,214,120,.9)'; for (let y = h - bh + 6; y < h - 6; y += 12) for (let xx = x + 4; xx < x + bw - 4; xx += 8) if (r() < .5) c.fillRect(xx, y, 4, 6); } });
    const cm = new THREE.MeshStandardMaterial({ map: city, emissive: '#ffffff', emissiveMap: city, emissiveIntensity: .9 }); const cw = new THREE.Mesh(new THREE.PlaneGeometry(14, 4.4), cm); cw.position.set(0, 4.1, -7.95); g.add(cw);
    for (let x = -7; x <= 7; x += 3.5) box(.2, 4.6, .2, M('#d0d4da'), x, 4.1, -7.85, g);
    const screens = []; const pos = [[-4.5, -2], [0, -2], [4.5, -2], [-4.5, 2.5], [0, 2.5], [4.5, 2.5]];
    for (const [x, z] of pos) { const d = new THREE.Group(); d.position.set(x, 0, z); g.add(d); box(3.2, .16, 1.8, M('#f2f2f2'), 0, 2.6, -1.0, d); for (const s of [-1, 1]) box(.12, 2.6, 1.6, M('#bfc5cc'), s * 1.5, 1.3, -1.0, d); box(1.8, 1.1, .1, M('#222'), 0, 3.4, -1.6, d); const sm = new THREE.MeshStandardMaterial({ color: '#2b7bf0', emissive: '#4a8cff', emissiveIntensity: .8 }); const s = new THREE.Mesh(new THREE.PlaneGeometry(1.65, .95), sm); s.position.set(0, 3.4, -1.54); d.add(s); screens.push(sm); box(1, .05, .4, M('#333'), 0, 2.7, -.6, d); const ch = new THREE.Group(); d.add(ch); cyl(.9, .9, .25, M('#222'), 0, 1.3, .3, ch, 16); box(1.5, 1.6, .2, M('#222'), 0, 2.3, 1.0, ch); cyl(.08, .08, 1.2, M('#666'), 0, .6, .3, ch, 8); }
    const wc = new THREE.Group(); wc.position.set(8.5, 0, -6); g.add(wc); box(1.2, 2.8, 1.2, M('#e6e9ee'), 0, 1.4, 0, wc); cyl(.5, .5, 1.4, M('#7fc4ff', { transparent: true, opacity: .7, roughness: .1 }), 0, 3.5, 0, wc, 16);
    plant(g, -9, -7, 1.3); plant(g, 9, 6, 1.2);
    const pm = ceilingPanels(g, [[-5, -3], [0, -3], [5, -3], [-5, 3], [0, 3], [5, 3]]);
    const lights = interiorLights(g, [[0, 6.2, 0]]);
    const spots = { center: { pos: [0, 0, 5.5] }, cooler: { pos: [7, 0, -5], yaw: 90 }, window: { pos: [0, 0, -6.2], yaw: 180 } };
    pos.forEach(([x, z], i) => spots['desk' + (i + 1)] = { pos: [x, 0, z + .3], yaw: 180, seat: 1.43 });
    return { group: g, interior: true, spots, setMood(m) { cm.map = cm.emissiveMap = m === 'night' ? cityN : city; cm.needsUpdate = true; for (const L of lights) L.intensity = m === 'night' ? 0 : 40; pm.emissiveIntensity = m === 'night' ? 0 : 1.4; for (const s of screens) s.emissiveIntensity = m === 'night' ? 1.6 : .8; }, nightLight: { pos: [0, 4, 3], color: '#5a7dff', intensity: 22 } };
  },

  farm(opts = {}) {
    const g = new THREE.Group(); const lights = [];
    ground(g, 400, M('#ffffff', { map: tex('grass', 50), roughness: 1 }));
    const path = mesh(new THREE.PlaneGeometry(5, 40), M('#ffffff', { map: tex('dirt', 6), roughness: 1 }), false, true); path.rotation.x = -Math.PI / 2; path.position.set(0, .02, 0); g.add(path);
    const barn = new THREE.Group(); barn.position.set(0, 0, -16); g.add(barn); const red = M('#c0392b', { roughness: .8 });
    box(14, 8, 10, red, 0, 4, 0, barn); for (const s of [-1, 1]) { const rf = box(14.6, .35, 6.6, M('#5a5f66'), 0, 9.9, s * 2.6, barn); rf.rotation.x = s * .62; } const gable = mesh(new THREE.CylinderGeometry(5.9, 5.9, 13.9, 3, 1), red); gable.rotation.set(-Math.PI / 2, 0, Math.PI / 2); gable.position.y = 8 + 5.9 * .5; gable.scale.set(.62, 1, 1); barn.add(gable);
    const door = box(5, 6, .2, M('#8a2a1e'), 0, 3, 5.05, barn); void door; for (const s of [-1, 1]) { const x1 = box(.3, 6.6, .25, M('#ffffff'), s * 1.25, 3, 5.15, barn); x1.rotation.z = s * .7; } box(5.4, .3, .3, M('#ffffff'), 0, 6.1, 5.15, barn); box(2, 1.6, .2, M('#ffffff'), 0, 9.2, 5.05, barn);
    for (let i = -6; i <= 6; i++) { if (Math.abs(i) < 1) continue; cyl(.15, .15, 2.2, M('#8a6a45'), i * 2.4, 1.1, 2, g, 8); }
    for (const y of [1.0, 1.8]) for (const s of [-1, 1]) box(13, .18, .12, M('#a07a50'), s * 8.6, y, 2, g);
    for (const [x, z] of [[-7, -6], [-9, -4], [8, -7]]) { const h = cyl(1.1, 1.1, 1.8, M('#e3c25a', { roughness: 1 }), x, .9, z, g, 16); h.rotation.z = Math.PI / 2; }
    for (let i = 0; i < 10; i++) roundTree(g, -40 + i * 9, -34 - (i % 2) * 6, 1.4, i % 3 ? '#3f9e3a' : '#4fae45');
    hills(g, 31);
    const pole = new THREE.Group(); pole.position.set(4.5, 0, 2); g.add(pole); cyl(.18, .2, 2.6, M('#8a6a45'), 0, 1.3, 0, pole, 8);
    return { group: g, interior: false, spots: { barn: { pos: [0, 0, -9] }, field: { pos: [-3, 0, 5] }, center: { pos: [0, 0, 6] }, post: { pos: [4.5, 2.6, 2] }, fence: { pos: [7, 0, 3.4] } }, walkZone: { x: [-14, 14], z: [-8, -2] }, crowd: { center: [0, 0, 9], yaw: 180 }, setMood(m) { lampsMood(lights, m); } };
  },

  clinic(opts = {}) {
    const g = new THREE.Group(); room(g, { w: 16, d: 14, wall: '#e8f4f2', low: '#5ec2b7', floor: 'tiles', floorRep: 5 });
    const sw = windowPane(3, 2.4, g, 5, 4.4, -6.95);
    // dentist chair facing +x (patient reclines, head toward -x)
    const ch = new THREE.Group(); ch.position.set(-1, 0, -1.5); g.add(ch); const cm = M('#2f8fd8', { roughness: .4 });
    cyl(.7, .9, 1.0, M('#dfe4ea'), 0, .5, 0, ch, 16); const seat = mesh(new RoundedBoxGeometry(2.6, .5, 2.2, 2, .2), cm); seat.position.set(.4, 1.3, 0); ch.add(seat); const back = mesh(new RoundedBoxGeometry(.5, 3.2, 2.2, 2, .2), cm); back.position.set(-1.4, 2.6, 0); back.rotation.z = -.55; ch.add(back); const leg = mesh(new RoundedBoxGeometry(2.4, .4, 2.0, 2, .18), cm); leg.position.set(2.5, 1.05, 0); leg.rotation.z = -.25; ch.add(leg);
    const arm = new THREE.Group(); arm.position.set(-2.5, 0, -3); g.add(arm); cyl(.12, .12, 6, M('#bfc5cc'), 0, 3, 0, arm, 8); const lampHead = new THREE.Group(); lampHead.position.set(1.2, 6, 1.6); arm.add(lampHead); const lh = mesh(new THREE.CylinderGeometry(.7, .4, .4, 20), M('#dfe4ea')); lampHead.add(lh); const lamp = emissive('#fffbe8', 1.8); const lg = mesh(new THREE.CircleGeometry(.6, 20), lamp); lg.rotation.x = Math.PI / 2; lg.position.y = -.21; lampHead.add(lg); box(1.4, .1, .1, M('#bfc5cc'), .6, 6, .8, arm).rotation.y = -.9;
    const cab = new THREE.Group(); cab.position.set(0, 0, -6.2); g.add(cab); box(8, 2.6, 1.4, M('#ffffff'), 0, 1.3, 0, cab); box(8.2, .2, 1.6, M('#bfc5cc'), 0, 2.7, 0, cab); for (let i = 0; i < 4; i++) box(1.6, .1, .05, M('#888'), -3 + i * 2, 2, .72, cab);
    poster(g, -7.95, 4.4, 0, Math.PI / 2, 2.4, 3, (c, w, h) => { c.fillStyle = '#ffffff'; c.fillRect(0, 0, w, h); c.fillStyle = '#5ec2b7'; c.fillRect(0, 0, w, 50); c.fillStyle = '#fff'; c.beginPath(); const x = w / 2, y = h * .55; c.moveTo(x - 50, y - 60); c.quadraticCurveTo(x, y - 90, x + 50, y - 60); c.lineTo(x + 40, y + 60); c.lineTo(x + 15, y + 60); c.lineTo(x, y + 10); c.lineTo(x - 15, y + 60); c.lineTo(x - 40, y + 60); c.closePath(); c.fill(); c.strokeStyle = '#5ec2b7'; c.lineWidth = 8; c.stroke(); });
    plant(g, 7, 5.5, 1.1);
    const lights = interiorLights(g, [[0, 6.2, 0]]);
    return { group: g, interior: true, spots: { chair: { pos: [-.6, 0, -1.5], yaw: 90, seat: 1.55, recline: .45 }, doctor: { pos: [-.6, 0, -4.0], yaw: 0 }, center: { pos: [2, 0, 2] }, door: { pos: [6, 0, 4.5] } }, setMood(m) { sw(m); for (const L of lights) L.intensity = m === 'night' ? 0 : 40; lamp.emissiveIntensity = m === 'night' ? .4 : 1.8; }, nightLight: { pos: [5, 4, -3], color: '#6b8cff', intensity: 20 } };
  },

  studio(opts = {}) {
    const g = new THREE.Group(); const c1 = opts.color || '#3a7bd5';
    const cyc = mesh(new THREE.CylinderGeometry(30, 30, 30, 48, 1, true, Math.PI * .5, Math.PI), M(c1, { side: THREE.BackSide, roughness: 1 }), false, true); cyc.position.set(0, 15, 0); g.add(cyc);
    ground(g, 80, M(c1, { roughness: 1 }));
    return { group: g, interior: false, spots: { center: { pos: [0, 0, 4] }, left: { pos: [-3, 0, 4], yaw: 20 }, right: { pos: [3, 0, 4], yaw: -20 } }, crowd: { center: [0, 0, 14], yaw: 180 }, setMood() { }, noSky: true };
  },
};
export const SET_NAMES = Object.keys(SETS);
