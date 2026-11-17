// Blocky character builder: rounded-cylinder head with a wrapped face decal, torso with printed shirt designs,
// sleeves/hands, pants/shorts/skirt, shoes, and a library of hats, hair and accessories.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { M, mesh, canvasTex, rng, pick, hash } from './util.js';
import { faceMaterial, faceParts, FW, FH } from './faces.js';

// ---------- shared geometry
const HEAD_R = .62, HEAD_H = 1.2;
function roundedCylinder(r, h, cr, seg = 40) {
  const pts = []; const hh = h / 2;
  pts.push(new THREE.Vector2(0, -hh));
  for (let i = 0; i <= 8; i++) { const a = -Math.PI / 2 + i / 8 * Math.PI / 2; pts.push(new THREE.Vector2(r - cr + Math.cos(a) * cr, -hh + cr + Math.sin(a) * cr)); }
  for (let i = 0; i <= 8; i++) { const a = i / 8 * Math.PI / 2; pts.push(new THREE.Vector2(r - cr + Math.cos(a) * cr, hh - cr + Math.sin(a) * cr)); }
  pts.push(new THREE.Vector2(0, hh));
  const g = new THREE.LatheGeometry(pts, seg); g.computeVertexNormals(); return g;
}
const GEO = {
  head: roundedCylinder(HEAD_R, HEAD_H, .27),
  face: new THREE.CylinderGeometry(HEAD_R + .006, HEAD_R + .006, .72, 32, 1, true, -0.9, 1.8),
  torso: new RoundedBoxGeometry(2, 2, 1, 3, .12),
  shirtDecal: new THREE.PlaneGeometry(1.92, 1.92),
  limb: new RoundedBoxGeometry(1, 2, 1, 3, .13),
  sleeveShort: new RoundedBoxGeometry(1.04, .8, 1.04, 2, .12),
  shoe: new RoundedBoxGeometry(1.04, .38, 1.18, 2, .13),
  hand: new RoundedBoxGeometry(1.02, .5, 1.02, 2, .14),
};

// ---------- shirt designs (front decal)
const shirtCache = {};
function shirtMaterial(design, main, accent) {
  const key = design + main + accent; if (shirtCache[key]) return shirtCache[key];
  const [kind, arg] = String(design).split(':');
  const t = canvasTex(256, 256, (g, w, h) => {
    g.clearRect(0, 0, w, h); g.lineCap = 'round';
    const A = accent || '#ffffff';
    switch (kind) {
      case 'stripe': g.fillStyle = A; g.fillRect(0, 96, w, 44); break;
      case 'stripes': g.fillStyle = A; for (let y = 20; y < h; y += 56) g.fillRect(0, y, w, 24); break;
      case 'number': g.fillStyle = A; g.font = "900 150px 'BS Black'"; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(arg || '7', w / 2, h / 2 + 8); break;
      case 'letter': g.fillStyle = A; g.beginPath(); g.arc(w / 2, h / 2 - 10, 62, 0, 7); g.fill(); g.fillStyle = main; g.font = "900 84px 'BS Black'"; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText((arg || 'A').slice(0, 2), w / 2, h / 2 - 4); break;
      case 'star': g.fillStyle = A; g.beginPath(); for (let i = 0; i < 10; i++) { const r = i % 2 ? 30 : 70, a = -Math.PI / 2 + i * Math.PI / 5; g.lineTo(w / 2 + Math.cos(a) * r, h / 2 - 6 + Math.sin(a) * r); } g.fill(); break;
      case 'heart': g.fillStyle = A; const x = w / 2, y = h / 2; g.beginPath(); g.moveTo(x, y + 60); g.bezierCurveTo(x - 110, y - 10, x - 50, y - 90, x, y - 30); g.bezierCurveTo(x + 50, y - 90, x + 110, y - 10, x, y + 60); g.fill(); break;
      case 'suit': g.fillStyle = '#ffffff'; g.beginPath(); g.moveTo(w / 2 - 54, 0); g.lineTo(w / 2, 150); g.lineTo(w / 2 + 54, 0); g.fill(); g.fillStyle = A; g.beginPath(); g.moveTo(w / 2 - 14, 14); g.lineTo(w / 2 + 14, 14); g.lineTo(w / 2 + 20, 120); g.lineTo(w / 2, 150); g.lineTo(w / 2 - 20, 120); g.fill(); g.strokeStyle = 'rgba(0,0,0,.35)'; g.lineWidth = 6; g.beginPath(); g.moveTo(w / 2 - 54, 0); g.lineTo(w / 2 - 6, 150); g.moveTo(w / 2 + 54, 0); g.lineTo(w / 2 + 6, 150); g.stroke(); g.fillStyle = 'rgba(0,0,0,.4)'; for (const yy of [180, 220]) { g.beginPath(); g.arc(w / 2, yy, 7, 0, 7); g.fill(); } break;
      case 'hoodie': g.fillStyle = 'rgba(0,0,0,.18)'; g.beginPath(); g.roundRect(56, 150, 144, 80, 20); g.fill(); g.strokeStyle = A; g.lineWidth = 8; g.beginPath(); g.moveTo(104, 0); g.lineTo(98, 80); g.moveTo(152, 0); g.lineTo(158, 80); g.stroke(); break;
      case 'overalls': g.fillStyle = A; g.fillRect(56, 110, 144, 146); g.fillRect(56, 0, 26, 120); g.fillRect(174, 0, 26, 120); g.fillStyle = '#f4d35e'; for (const xx of [69, 187]) { g.beginPath(); g.arc(xx, 116, 9, 0, 7); g.fill(); } break;
      case 'coat': g.fillStyle = 'rgba(0,0,0,.12)'; g.fillRect(124, 0, 8, h); g.fillStyle = '#9fb3c8'; g.beginPath(); g.moveTo(w / 2 - 50, 0); g.lineTo(w / 2, 90); g.lineTo(w / 2 + 50, 0); g.fill(); g.fillStyle = 'rgba(0,0,0,.35)'; for (const yy of [120, 165, 210]) { g.beginPath(); g.arc(w / 2 + 18, yy, 7, 0, 7); g.fill(); } g.fillStyle = A; g.fillRect(150, 130, 50, 8); break;
      case 'police': g.fillStyle = '#f2c230'; g.beginPath(); for (let i = 0; i < 12; i++) { const r = i % 2 ? 16 : 30, a = -Math.PI / 2 + i * Math.PI / 6; g.lineTo(170 + Math.cos(a) * r, 80 + Math.sin(a) * r); } g.fill(); g.fillStyle = 'rgba(0,0,0,.3)'; g.fillRect(124, 0, 8, h); break;
      case 'chef': g.fillStyle = 'rgba(0,0,0,.35)'; for (const yy of [60, 120, 180]) for (const xx of [96, 160]) { g.beginPath(); g.arc(xx, yy, 8, 0, 7); g.fill(); } break;
      case 'tank': g.fillStyle = 'rgba(0,0,0,0)'; break;
      case 'tie': g.fillStyle = A; g.beginPath(); g.moveTo(w / 2 - 14, 0); g.lineTo(w / 2 + 14, 0); g.lineTo(w / 2 + 22, 150); g.lineTo(w / 2, 180); g.lineTo(w / 2 - 22, 150); g.fill(); break;
      case 'skull': g.fillStyle = A; g.beginPath(); g.arc(w / 2, 110, 56, 0, 7); g.fill(); g.fillRect(w / 2 - 34, 140, 68, 50); g.fillStyle = main; for (const s of [-1, 1]) { g.beginPath(); g.arc(w / 2 + s * 24, 110, 15, 0, 7); g.fill(); } break;
      default: break;
    }
  });
  shirtCache[key] = new THREE.MeshStandardMaterial({ map: t, transparent: true, alphaTest: .05, roughness: .6, polygonOffset: true, polygonOffsetFactor: -2, depthWrite: false });
  return shirtCache[key];
}

// ---------- presets
export const PRESETS = {
  kid: { skin: '#f5cd30', shirt: '#1fbf6a', shirtDesign: 'stripe', accent: '#ffffff', pants: '#2b4fb8', sleeves: 'long', hat: 'cap', hatColor: '#e8352e' },
  girl: { skin: '#f1c9a5', shirt: '#ff5fa2', shirtDesign: 'heart', accent: '#ffffff', pants: '#6fa8ff', sleeves: 'short', hair: 'pony', hairColor: '#5a3a1e', extras: ['blush'] },
  boy: { skin: '#c58c5c', shirt: '#2b7bf0', shirtDesign: 'number:7', accent: '#ffffff', pants: '#1f1f24', sleeves: 'short', hair: 'short', hairColor: '#1b120c' },
  dad: { skin: '#e9b98f', shirt: '#4a7fbf', shirtDesign: 'plain', pants: '#5b4a3a', sleeves: 'long', hair: 'short', hairColor: '#3b2716', beard: '#3b2716' },
  mom: { skin: '#f1c9a5', shirt: '#9b59d0', shirtDesign: 'plain', pants: '#2a2a35', sleeves: 'long', hair: 'bob', hairColor: '#6b3a1e' },
  grandma: { skin: '#f1c9a5', shirt: '#c97fb5', shirtDesign: 'plain', pants: '#7d5a8a', bottom: 'skirt', hair: 'bun', hairColor: '#d9d9d9', extras: ['glasses'] },
  grandpa: { skin: '#e9b98f', shirt: '#8a7a5a', shirtDesign: 'plain', pants: '#4a4a52', hair: 'bald', hairColor: '#dddddd', extras: ['glasses', 'stache'] },
  teacher: { skin: '#e2b48a', shirt: '#f4f4f4', shirtDesign: 'tie', accent: '#1f2b5a', pants: '#2c2c34', sleeves: 'long', hair: 'short', hairColor: '#2e1e12', beard: '#3b2716', extras: ['glasses'], bowtie: '#151515', suspenders: '#4a3a2a' },
  mayor: { skin: '#f5cd30', shirt: '#e2ad1e', shirtDesign: 'suit', accent: '#7a1414', pants: '#1d1d22', sleeves: 'long', hat: 'top', hatColor: '#141418', extras: ['stache'], shoes: '#111111' },
  boss: { skin: '#e9b98f', shirt: '#2a2d36', shirtDesign: 'suit', accent: '#c0392b', pants: '#2a2d36', sleeves: 'long', hair: 'short', hairColor: '#222', shoes: '#111111' },
  worker: { skin: '#c58c5c', shirt: '#f28c1c', shirtDesign: 'overalls', accent: '#2b4fb8', pants: '#2b4fb8', sleeves: 'none', hat: 'hard', hatColor: '#f4c20d' },
  chef: { skin: '#f1c9a5', shirt: '#ffffff', shirtDesign: 'chef', pants: '#2c2c34', sleeves: 'long', hat: 'chef', hatColor: '#ffffff', extras: ['stache'] },
  doctor: { skin: '#e9b98f', shirt: '#ffffff', shirtDesign: 'coat', accent: '#2a6fd6', pants: '#3a4a6a', sleeves: 'long', hair: 'short', hairColor: '#3b2716', extras: ['glasses'] },
  dentist: { skin: '#f1c9a5', shirt: '#5ec2b7', shirtDesign: 'plain', pants: '#5ec2b7', sleeves: 'short', hair: 'pony', hairColor: '#2e1e12', mask: true },
  cop: { skin: '#8a5a36', shirt: '#24407a', shirtDesign: 'police', pants: '#1c2c52', sleeves: 'long', hat: 'police', hatColor: '#1c2c52', extras: ['shades'] },
  farmer: { skin: '#e9b98f', shirt: '#c0392b', shirtDesign: 'overalls', accent: '#3a5fa8', pants: '#3a5fa8', sleeves: 'long', hat: 'cowboy', hatColor: '#c8a04a', beard: '#8a5a2b' },
  gamer: { skin: '#f5cd30', shirt: '#222428', shirtDesign: 'hoodie', accent: '#ffffff', pants: '#3a3d44', sleeves: 'long', hat: 'beanie', hatColor: '#8e44d6', headphones: '#e8352e' },
  noob: { skin: '#f5cd30', shirt: '#2a7bd8', shirtDesign: 'plain', pants: '#3cba54', sleeves: 'none', hair: 'bald' },
  king: { skin: '#f5cd30', shirt: '#8e1c2a', shirtDesign: 'plain', pants: '#3a1a40', sleeves: 'long', hat: 'crown', hatColor: '#f2c230', cape: '#b3132e', beard: '#d9d9d9' },
  robot: { skin: '#b9c2cc', shirt: '#8a96a3', shirtDesign: 'letter:R', accent: '#3fd0ff', pants: '#6b7682', sleeves: 'long', hair: 'bald', antenna: true, extras: [] },
  villain: { skin: '#a8b0a0', shirt: '#151518', shirtDesign: 'skull', accent: '#b3132e', pants: '#151518', sleeves: 'long', hair: 'spiky', hairColor: '#151518', cape: '#151518', extras: [] },
};
export const SKINS = ['#f5cd30', '#e9b98f', '#c58c5c', '#8a5a36', '#f1c9a5', '#5e3b24'];
export const SHIRTS = ['#e8352e', '#2b7bf0', '#f28c1c', '#8e44d6', '#ff5fa2', '#16a3a3', '#f2f2f2', '#222428', '#f4c542', '#3cba54', '#1fbf6a', '#c0392b'];
export const PANTS = ['#2b4fb8', '#1f1f24', '#4a7f2a', '#6b4a2b', '#2a6fd6', '#7d7f86', '#3a3d44'];

export function randomSpec(seed) {
  const r = rng(seed); const hk = r();
  const o = { skin: pick(r, SKINS), shirt: pick(r, SHIRTS), pants: pick(r, PANTS), sleeves: pick(r, ['long', 'short', 'none']), shirtDesign: pick(r, ['plain', 'plain', 'stripe', 'hoodie', 'number:' + (1 + (r() * 9 | 0)), 'star', 'stripes']), accent: '#ffffff' };
  if (hk < .2) Object.assign(o, { hat: 'hard', hatColor: '#f4c20d' });
  else if (hk < .36) Object.assign(o, { hat: pick(r, ['cap', 'cap_back', 'beanie']), hatColor: pick(r, SHIRTS) });
  else if (hk < .56) Object.assign(o, { hair: pick(r, ['pony', 'bob', 'long', 'buns']), hairColor: pick(r, ['#5a3a1e', '#1b120c', '#c8a04a', '#8a2a1a']) });
  else if (hk < .82) Object.assign(o, { hair: pick(r, ['short', 'spiky', 'afro']), hairColor: pick(r, ['#1b120c', '#3b2716', '#5a3a1e']) });
  if (r() < .12) o.extras = ['glasses'];
  return o;
}

// ---------- builder
export function makeCharacter(specIn = {}, name = 'npc') {
  const spec = { ...(PRESETS[specIn.preset] || {}), ...specIn };
  const o = { skin: '#f5cd30', shirt: '#2b7bf0', pants: '#2b4fb8', shoes: '#f2f2f2', sleeves: 'long', shirtDesign: 'plain', accent: '#ffffff', expr: 'smile', ...spec };
  const c = { name, spec: o, extras: [...(o.extras || [])] };
  const root = c.root = new THREE.Group(); root.name = name;
  const body = c.body = new THREE.Group(); root.add(body);            // body: whole-body rotations (fall/lie/spin)
  const hips = c.hips = new THREE.Group(); hips.position.y = 2; body.add(hips);
  const upper = c.upper = new THREE.Group(); hips.add(upper);
  const shirtM = M(o.shirt), skinM = new THREE.MeshStandardMaterial({ color: o.skin, roughness: .5 });
  c.skinMat = skinM;
  const torso = mesh(GEO.torso, shirtM); torso.position.y = 1; upper.add(torso);
  if (o.shirtDesign && o.shirtDesign !== 'plain') { const d = new THREE.Mesh(GEO.shirtDecal, shirtMaterial(o.shirtDesign, o.shirt, o.accent)); d.position.set(0, 1, .505); upper.add(d); }
  if (o.bowtie) for (const s of [-1, 1]) { const b = mesh(new THREE.BoxGeometry(.32, .26, .1), M(o.bowtie)); b.position.set(s * .19, 1.86, .54); b.rotation.z = s * .35; upper.add(b); }
  if (o.suspenders) for (const s of [-.55, .55]) { const b = mesh(new THREE.BoxGeometry(.18, 2.02, 1.03), M(o.suspenders)); b.position.set(s, 1, 0); upper.add(b); }
  if (o.backpack) { const b = mesh(new RoundedBoxGeometry(1.5, 1.5, .6, 2, .15), M(o.backpack)); b.position.set(0, 1.1, -.75); upper.add(b); }
  if (o.cape) { const cp = mesh(new THREE.BoxGeometry(2.1, 3.2, .08), M(o.cape, { side: THREE.DoubleSide })); cp.position.set(0, .45, -.56); cp.rotation.x = .08; upper.add(cp); c.cape = cp; }
  const neck = c.neck = new THREE.Group(); neck.position.y = 2.02; upper.add(neck);
  const head = mesh(GEO.head, skinM); head.position.y = .6; neck.add(head); c.head = head;
  c.face = new THREE.Mesh(GEO.face, faceMaterial(faceParts(o.expr, c.extras))); c.face.position.y = .6; neck.add(c.face);
  if (o.beard) { const b = mesh(new RoundedBoxGeometry(1.18, .5, .5, 2, .2), M(o.beard)); b.position.set(0, .18, .42); neck.add(b); }
  if (o.mask) { const mk = mesh(new THREE.CylinderGeometry(HEAD_R + .02, HEAD_R + .02, .34, 24, 1, true, -1.0, 2.0), M('#cfe9f2', { side: THREE.DoubleSide })); mk.position.y = .36; neck.add(mk); }
  if (o.antenna) { const a = mesh(new THREE.CylinderGeometry(.04, .04, .6, 8), M('#555')); a.position.y = 1.5; neck.add(a); const b = mesh(new THREE.SphereGeometry(.12, 12, 8), new THREE.MeshStandardMaterial({ color: '#ff4040', emissive: '#ff2020', emissiveIntensity: 1.5 })); b.position.y = 1.82; neck.add(b); }
  if (o.headphones) { const hm = M(o.headphones); const band = mesh(new THREE.TorusGeometry(.7, .07, 8, 24, Math.PI), hm); band.position.y = .72; neck.add(band); for (const s of [-1, 1]) { const cup = mesh(new THREE.CylinderGeometry(.24, .24, .2, 16), hm); cup.rotation.z = Math.PI / 2; cup.position.set(s * .7, .62, 0); neck.add(cup); } }
  addHeadwear(neck, o);
  // arms (pivot at shoulder)
  const sleeveM = o.sleeves === 'none' ? skinM : shirtM;
  const mkArm = (sx) => {
    const p = new THREE.Group(); p.position.set(sx * 1.5, 1.85, 0); p.rotation.order = 'YXZ'; upper.add(p);
    const a = mesh(GEO.limb, o.sleeves === 'long' ? shirtM : skinM); a.position.y = -.85; p.add(a);
    if (o.sleeves === 'short') { const s = mesh(GEO.sleeveShort, shirtM); s.position.y = -.25; p.add(s); }
    if (o.sleeves === 'long') { const h = mesh(GEO.hand, skinM); h.position.y = -1.62; p.add(h); }
    const hand = new THREE.Group(); hand.position.set(0, -1.9, 0); p.add(hand); p.userData.hand = hand;
    return p;
  };
  c.armL = mkArm(1); c.armR = mkArm(-1);
  void sleeveM;
  const pantsM = M(o.pants);
  const mkLeg = (sx) => {
    const p = new THREE.Group(); p.position.set(sx * .5, 0, 0); hips.add(p);
    if (o.bottom === 'shorts') { const l = mesh(GEO.limb, skinM); l.position.y = -1; p.add(l); const s = mesh(new RoundedBoxGeometry(1.03, .9, 1.03, 2, .12), pantsM); s.position.y = -.42; p.add(s); }
    else { const l = mesh(GEO.limb, pantsM); l.position.y = -1; p.add(l); }
    const s = mesh(GEO.shoe, M(o.shoes)); s.position.set(0, -1.82, .07); p.add(s);
    return p;
  };
  c.legL = mkLeg(1); c.legR = mkLeg(-1);
  if (o.bottom === 'skirt') { const sk = mesh(new THREE.CylinderGeometry(1.05, 1.45, 1.2, 24), pantsM); sk.position.y = -.5; hips.add(sk); }
  root.traverse(m => { if (m.isMesh && m !== c.face) { m.castShadow = true; } });
  c.held = {};
  return c;
}

function addHeadwear(neck, o) {
  const top = 1.2; const hc = o.hatColor || '#333';
  const H = (geo, mat, y, x = 0, z = 0) => { const m = mesh(geo, mat); m.position.set(x, y, z); neck.add(m); return m; };
  switch (o.hat) {
    case 'cap': case 'cap_back': { H(new THREE.SphereGeometry(.68, 22, 12, 0, Math.PI * 2, 0, Math.PI / 2), M(hc), top - .06).scale.y = .78; const br = H(new THREE.BoxGeometry(1.0, .07, .78), M(o.brimColor || hc), top - .03, 0, o.hat === 'cap' ? .82 : -.82); void br; break; }
    case 'beanie': { H(new THREE.SphereGeometry(.69, 22, 14, 0, Math.PI * 2, 0, Math.PI / 2), M(hc, { roughness: .9 }), top - .12).scale.y = .95; H(new THREE.CylinderGeometry(.7, .7, .26, 24), M(hc, { roughness: .9 }), top - .06); H(new THREE.SphereGeometry(.16, 12, 8), M('#ffffff', { roughness: 1 }), top + .56); break; }
    case 'top': { H(new THREE.CylinderGeometry(.56, .56, 1.25, 28), M(hc, { roughness: .35 }), top + .58); H(new THREE.CylinderGeometry(.96, .96, .08, 28), M(hc, { roughness: .35 }), top - .03); H(new THREE.CylinderGeometry(.575, .575, .24, 28), M(o.bandColor || '#d4a017', { metalness: .6, roughness: .3 }), top + .14); break; }
    case 'fedora': { H(new THREE.CylinderGeometry(.55, .63, .6, 24), M(hc, { roughness: .6 }), top + .27); const b = H(new THREE.CylinderGeometry(1.06, 1.06, .07, 28), M(hc, { roughness: .6 }), top); b.rotation.x = .08; H(new THREE.CylinderGeometry(.635, .635, .14, 24), M('#111'), top + .05); break; }
    case 'hard': { H(new THREE.SphereGeometry(.73, 22, 12, 0, Math.PI * 2, 0, Math.PI / 2), M(hc, { roughness: .3 }), top - .07).scale.y = .82; H(new THREE.CylinderGeometry(.9, .9, .07, 26), M(hc, { roughness: .3 }), top - .05); H(new THREE.BoxGeometry(.18, .12, 1.44), M('#41a7ff'), top + .5); break; }
    case 'crown': { const g = new THREE.CylinderGeometry(.62, .62, .5, 10, 1, true); H(g, M(hc, { metalness: .8, roughness: .25, side: THREE.DoubleSide }), top + .2); for (let i = 0; i < 5; i++) { const a = i / 5 * Math.PI * 2; const s = H(new THREE.ConeGeometry(.14, .34, 4), M(hc, { metalness: .8, roughness: .25 }), top + .58, Math.sin(a) * .58, Math.cos(a) * .58); void s; } H(new THREE.SphereGeometry(.11, 10, 8), M('#e8352e', { roughness: .2 }), top + .2, 0, .63); break; }
    case 'chef': { H(new THREE.CylinderGeometry(.66, .6, .7, 24), M('#ffffff'), top + .3); H(new THREE.SphereGeometry(.82, 20, 12), M('#ffffff'), top + .82).scale.y = .6; break; }
    case 'police': { H(new THREE.CylinderGeometry(.74, .64, .42, 24), M(hc), top + .16); const v = H(new THREE.BoxGeometry(1.0, .06, .5), M('#111'), top - .02, 0, .7); v.rotation.x = .2; H(new THREE.CylinderGeometry(.12, .12, .04, 12), M('#f2c230', { metalness: .7 }), top + .2, 0, .66).rotation.x = Math.PI / 2; break; }
    case 'cowboy': { H(new THREE.CylinderGeometry(.5, .62, .6, 22), M(hc), top + .27); const b = H(new THREE.TorusGeometry(.95, .14, 8, 28), M(hc), top); b.rotation.x = Math.PI / 2; b.scale.set(1, 1.2, .5); H(new THREE.CylinderGeometry(.96, .96, .05, 28), M(hc), top - .02); break; }
    case 'party': { const cone = H(new THREE.ConeGeometry(.45, 1.1, 20), M(hc), top + .5); cone.rotation.z = .15; H(new THREE.SphereGeometry(.12, 10, 8), M('#ffffff'), top + 1.06, -.08); break; }
    case 'bunny': { for (const s of [-1, 1]) { const e = H(new RoundedBoxGeometry(.28, 1.0, .14, 2, .07), M(hc || '#fff'), top + .55, s * .3); e.rotation.z = -s * .15; } break; }
  }
  if (o.hat) return;
  const hm = M(o.hairColor || '#2a1a0e', { roughness: .7 });
  switch (o.hair) {
    case 'short': H(new RoundedBoxGeometry(1.36, .36, 1.36, 2, .16), hm, top - .02); H(new RoundedBoxGeometry(1.36, .7, .3, 2, .1), hm, .82, 0, -.55); break;
    case 'spiky': H(new RoundedBoxGeometry(1.34, .3, 1.34, 2, .12), hm, top - .04); for (let i = 0; i < 7; i++) { const sp = H(new THREE.ConeGeometry(.22, .6, 5), hm, top + .3, (i % 4 - 1.5) * .3, (i < 4 ? .2 : -.25)); sp.rotation.x = -.3; } break;
    case 'bob': H(new RoundedBoxGeometry(1.42, .5, 1.42, 2, .2), hm, top - .02); H(new RoundedBoxGeometry(1.44, 1.05, .34, 2, .12), hm, .62, 0, -.58); for (const s of [-1, 1]) H(new RoundedBoxGeometry(.24, 1.0, 1.2, 2, .1), hm, .65, s * .68, -.05); break;
    case 'pony': H(new RoundedBoxGeometry(1.38, .5, 1.38, 2, .2), hm, top); H(new RoundedBoxGeometry(1.38, 1.2, .34, 2, .12), hm, .66, 0, -.56); { const p = H(new THREE.CylinderGeometry(.24, .1, 1.7, 10), hm, .3, 0, -.88); p.rotation.x = .25; } break;
    case 'long': H(new RoundedBoxGeometry(1.42, .5, 1.42, 2, .2), hm, top); H(new RoundedBoxGeometry(1.5, 2.3, .4, 2, .14), hm, .1, 0, -.56); for (const s of [-1, 1]) H(new RoundedBoxGeometry(.26, 1.7, .9, 2, .1), hm, .25, s * .7, -.2); break;
    case 'buns': H(new RoundedBoxGeometry(1.38, .45, 1.38, 2, .2), hm, top); for (const s of [-1, 1]) H(new THREE.SphereGeometry(.34, 14, 10), hm, top + .3, s * .55, -.1); break;
    case 'bun': H(new RoundedBoxGeometry(1.38, .45, 1.38, 2, .2), hm, top); H(new THREE.SphereGeometry(.42, 14, 10), hm, top + .38, 0, -.2); break;
    case 'afro': H(new THREE.SphereGeometry(.95, 18, 14), M(o.hairColor || '#1b120c', { roughness: 1 }), top + .05).scale.set(1, .85, 1); break;
    case 'mohawk': for (let i = 0; i < 5; i++) H(new THREE.BoxGeometry(.18, .5, .3), hm, top + .2, 0, .5 - i * .26); break;
    case 'bald': default: break;
  }
}

// set the face for this frame (expression + blink/talk), and head tint
export function applyFace(c, expr, { blink = false, mouthOpen = false } = {}) {
  const parts = faceParts(expr, c.extras, { blink, mouthOpen });
  const mat = faceMaterial(parts); if (c.face.material !== mat) c.face.material = mat;
}
export function setTint(c, color, amt) {
  c.skinMat.color.set(c.spec.skin); if (color && amt > 0) c.skinMat.color.lerp(new THREE.Color(color), amt);
}
export const _faceSize = { FW, FH };
void hash;
