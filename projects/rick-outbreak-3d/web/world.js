// V3 Unified Inked 3D World — RICK CLIPS STUDIO POLISH EDITION:
// 1. Convenience Store + Full-Height Top-Drum Hermetic Security Shutters ("sheleter bnd bilkul" -> y=0.00m!)
//    + READABLE LABELED PRODUCTS everywhere: TOMATO SOUP / BAKED BEANS / CHUNKY TUNA cans,
//      CHOCOLATE bar, PURE WATER bottles, FIRST AID KIT, POTATO CHIPS / COOKIES / CEREAL / NOODLES
//      shelf rows + yellow SALE price strips + stocked labeled cooler (COLA/ENERGY/SODA/MILK)
//    + detailed POS register (screen/scanner/receipt/card reader), impulse candy box, back-counter
//      cabinet, coffee brewer, twin-bowl slushie machine, CCTV monitor, 4:17 wall clock,
//      OPEN 24 HRS neon, promo posters, WELCOME mat, hanging 2 FOR $3 promo.
// 2. Outside City Street + SLEEK 3D Cars + Swerve/Abandoned + Broken Sunrise Shopfronts
//    + labeled across-street storefronts (PHARMACY / DINER / BANK / PIZZA / LAUNDRY / HARDWARE)
//    + striped awnings, bank columns, fire hydrant, trash bin.
// 3. Back Storage Corridor + Steel/Wood Alley Door with Peep Window at y=1.55m (eye-level mimic!)
// 4. Exterior Narrow Brick Delivery Alley + Transit Station Entrance with Open Maintenance Door
//    + hazard-trimmed door frame, caged emergency lamp, fire-escape ladder, labeled dumpster/crates.
// 5. Underground Transit Station Stairwell + Platform 3 + Emergency Radio (detailed faceplate)
//    + yellow step nosings, hazard bulkhead + warm emergency light at self-closing door,
//    MIND THE GAP / DANGER / WAY OUT signage.
import * as THREE from './lib/three.module.js';
import * as P from './paint.js';

export const INK = '#351f22';
const INK_COLOR = new THREE.Color(INK);

const gradData = new Uint8Array([
  132, 132, 144, 255,
  188, 188, 198, 255,
  232, 232, 238, 255,
  255, 255, 255, 255,
]);
export const TOON_GRAD = new THREE.DataTexture(gradData, 4, 1, THREE.RGBAFormat);
TOON_GRAD.minFilter = TOON_GRAD.magFilter = THREE.NearestFilter;
TOON_GRAD.needsUpdate = true;

const matCache = new Map();
export function toon(color, map = null, extra = {}) {
  const key = map ? null : color + JSON.stringify(extra);
  if (key && matCache.has(key)) return matCache.get(key);
  const m = new THREE.MeshToonMaterial({ color, gradientMap: TOON_GRAD, map, ...extra });
  if (key) matCache.set(key, m);
  return m;
}

const edgeMat = new THREE.LineBasicMaterial({ color: INK });
const hullCache = new Map();
function getHullMat(thick) {
  const k = thick.toFixed(4);
  if (!hullCache.has(k)) {
    hullCache.set(k, new THREE.ShaderMaterial({
      uniforms: { thick: { value: thick }, col: { value: INK_COLOR } },
      vertexShader: `uniform float thick; void main(){ vec3 p = position + normal * thick; gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0); }`,
      fragmentShader: `uniform vec3 col; void main(){ gl_FragColor = vec4(col, 1.0); }`,
      side: THREE.BackSide,
    }));
  }
  return hullCache.get(k);
}

export function ink(mesh, thick = 0.022, edges = true, angle = 26) {
  if (thick > 0) {
    const h = new THREE.Mesh(mesh.geometry, getHullMat(thick));
    mesh.add(h);
  }
  if (edges) {
    mesh.add(new THREE.LineSegments(new THREE.EdgesGeometry(mesh.geometry, angle), edgeMat));
  }
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

export function ibox(w, h, d, color, { map = null, x = 0, y = 0, z = 0, rx = 0, ry = 0, rz = 0, thick = 0.02, edges = true, cast = true } = {}) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), map ? toon('#ffffff', map) : toon(color));
  m.position.set(x, y, z);
  m.rotation.set(rx, ry, rz);
  ink(m, thick, edges);
  m.castShadow = cast;
  return m;
}

export function icyl(rt, rb, h, color, { map = null, x = 0, y = 0, z = 0, rx = 0, ry = 0, rz = 0, seg = 14, thick = 0.016, edges = true } = {}) {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, seg), toon(map ? '#ffffff' : color, map));
  m.position.set(x, y, z);
  m.rotation.set(rx, ry, rz);
  return ink(m, thick, edges, 42);
}

function cv(w, h) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  return [c, c.getContext('2d')];
}

function makeCheckeredFloorTex() {
  const [c, g] = cv(512, 512);
  const r = P.rng(12);
  const n = 4, s = 512 / n;
  for (let y = 0; y < n; y++) {
    for (let x = 0; x < n; x++) {
      g.fillStyle = (x + y) % 2 === 0 ? '#ebe3cf' : '#cad8d2';
      g.fillRect(x * s, y * s, s, s);
      g.strokeStyle = 'rgba(53,31,34,0.28)';
      g.lineWidth = 3;
      g.strokeRect(x * s + 1.5, y * s + 1.5, s - 3, s - 3);
      for (let k = 0; k < 5; k++) {
        g.fillStyle = 'rgba(70,60,50,0.09)';
        g.beginPath();
        g.ellipse(x * s + r() * s, y * s + r() * s, 4 + r() * 10, 2 + r() * 6, r() * 3, 0, 7);
        g.fill();
      }
    }
  }
  return P.tex(c, 5.5, 7.5);
}

function makeWallTileTex(base = '#6f8782', seam = '#425652', rx = 4, ry = 2) {
  const [c, g] = cv(256, 256);
  const r = P.rng(33);
  g.fillStyle = base; g.fillRect(0, 0, 256, 256);
  const bw = 64, bh = 32;
  for (let row = 0; row < 8; row++) {
    for (let col = -1; col < 5; col++) {
      const x = col * bw + (row % 2) * 32, y = row * bh;
      g.fillStyle = r() > 0.5 ? base : '#637a75';
      g.fillRect(x + 2, y + 2, bw - 4, bh - 4);
      g.strokeStyle = seam; g.lineWidth = 2;
      g.strokeRect(x + 1, y + 1, bw - 2, bh - 2);
    }
  }
  return P.tex(c, rx, ry);
}

function makeBrickTex(rx = 5, ry = 3) {
  const [c, g] = cv(256, 256);
  const r = P.rng(58);
  g.fillStyle = '#3b2b28'; g.fillRect(0, 0, 256, 256);
  const bw = 64, bh = 32;
  for (let row = 0; row < 8; row++) {
    for (let col = -1; col < 5; col++) {
      const x = col * bw + (row % 2) * 32, y = row * bh;
      g.fillStyle = r() > 0.45 ? '#6e3d34' : '#5c322b';
      g.fillRect(x + 2, y + 2, bw - 4, bh - 4);
    }
  }
  return P.tex(c, rx, ry);
}

function makeConcreteTex(rx = 3, ry = 4) {
  const [c, g] = cv(512, 512);
  const r = P.rng(44);
  g.fillStyle = '#73787e'; g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 180; i++) {
    g.fillStyle = r() > 0.5 ? 'rgba(38,42,46,0.20)' : 'rgba(185,192,198,0.12)';
    g.beginPath();
    g.ellipse(r() * 512, r() * 512, 6 + r() * 28, 4 + r() * 18, r() * 3, 0, 7);
    g.fill();
  }
  g.strokeStyle = 'rgba(36,38,42,0.38)'; g.lineWidth = 3;
  g.strokeRect(4, 4, 504, 504);
  return P.tex(c, rx, ry);
}

function makeShutterTex() {
  const [c, g] = cv(256, 512);
  g.fillStyle = '#788490'; g.fillRect(0, 0, 256, 512);
  for (let y = 0; y < 512; y += 20) {
    g.fillStyle = '#9aa8b6'; g.fillRect(0, y + 2, 256, 7);
    g.fillStyle = '#4e5862'; g.fillRect(0, y + 13, 256, 5);
    g.fillStyle = '#2b1e22'; g.fillRect(0, y + 18, 256, 2);
  }
  return P.tex(c, 2, 3);
}

function makeAsphaltTex(rx = 8, ry = 8) {
  // V6: hi-fidelity street asphalt — fine aggregate speckle, tar repair seams, oil weathering.
  const [c, g] = cv(1024, 1024);
  const r = P.rng(71);
  g.fillStyle = '#343942'; g.fillRect(0, 0, 1024, 1024);
  for (let i = 0; i < 2800; i++) {
    const v = r();
    g.fillStyle = v > 0.62 ? `rgba(232,236,244,${0.028 + 0.05 * r()})`
      : v > 0.30 ? `rgba(98,106,120,${0.05 + 0.09 * r()})`
      : `rgba(12,14,18,${0.06 + 0.11 * r()})`;
    const s2 = 1.5 + r() * 4.5;
    g.fillRect(r() * 1024, r() * 1024, s2, s2);
  }
  g.lineCap = 'round';
  for (let k = 0; k < 5; k++) { // meandering tar repair seams
    g.strokeStyle = `rgba(10,12,16,${0.32 + 0.22 * r()})`;
    g.lineWidth = 5 + r() * 8;
    g.beginPath();
    let x = r() * 1024, y = r() * 1024;
    g.moveTo(x, y);
    for (let s2 = 0; s2 < 7; s2++) { x += (r() - 0.5) * 270; y += (r() - 0.5) * 270; g.lineTo(x, y); }
    g.stroke();
  }
  for (let k = 0; k < 10; k++) { // oil / weather patches
    const px = r() * 1024, py = r() * 1024, pr = 40 + r() * 100;
    const rg = g.createRadialGradient(px, py, 4, px, py, pr);
    rg.addColorStop(0, `rgba(${r() > 0.5 ? '56,62,72' : '20,23,28'},${0.15 + 0.13 * r()})`);
    rg.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = rg; g.beginPath(); g.arc(px, py, pr, 0, 7); g.fill();
  }
  return P.tex(c, rx, ry);
}

function makePaverTex() {
  // V6: concrete sidewalk pavers — joint grid, per-slab tint variance, grime.
  const [c, g] = cv(512, 512);
  const r = P.rng(97);
  for (let j = 0; j < 8; j++) {
    for (let i = 0; i < 8; i++) {
      const v = 0.92 + 0.14 * r();
      g.fillStyle = `rgb(${Math.round(156 * v)},${Math.round(151 * v)},${Math.round(140 * v)})`;
      g.fillRect(i * 64 + 2, j * 64 + 2, 60, 60);
    }
  }
  for (let i = 0; i < 300; i++) {
    g.fillStyle = r() > 0.5 ? 'rgba(78,74,64,0.11)' : 'rgba(242,240,232,0.08)';
    g.fillRect(r() * 512, r() * 512, 2 + r() * 5, 2 + r() * 5);
  }
  for (let k = 0; k < 7; k++) {
    const px = r() * 512, py = r() * 512, pr = 26 + r() * 64;
    const rg = g.createRadialGradient(px, py, 2, px, py, pr);
    rg.addColorStop(0, 'rgba(66,62,54,0.20)'); rg.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = rg; g.beginPath(); g.arc(px, py, pr, 0, 7); g.fill();
  }
  return P.tex(c, 24, 1);
}

function makeGlowTex() {
  // V6: soft radial lamp-pool glow decal.
  const [c, g] = cv(256, 256);
  const rg = g.createRadialGradient(128, 128, 6, 128, 128, 126);
  rg.addColorStop(0, 'rgba(255,255,255,0.95)');
  rg.addColorStop(0.45, 'rgba(255,255,255,0.38)');
  rg.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = rg; g.fillRect(0, 0, 256, 256);
  return new THREE.CanvasTexture(c);
}

// =========================== RICK CLIPS LABEL PRINTERS ===========================

/** Crisp readable wrapped label for cylinders (cans/bottles): name drawn TWICE so it always faces camera. */
function makeWrapLabelTex(name, { bg = '#c8382e', band = '#8f1f18', fg = '#fdf6e8', sub = '' } = {}) {
  const [c, g] = cv(512, 256);
  g.fillStyle = bg; g.fillRect(0, 0, 512, 256);
  g.fillStyle = band; g.fillRect(0, 26, 512, 20); g.fillRect(0, 210, 512, 20);
  g.fillStyle = '#c9ced4'; g.fillRect(0, 0, 512, 22); g.fillRect(0, 234, 512, 22); // metal rims
  g.strokeStyle = 'rgba(40,26,24,0.65)'; g.lineWidth = 6; g.strokeRect(3, 3, 506, 250);
  const words = name.split(' ');
  for (const cx of [128, 384]) {
    g.save();
    g.translate(cx, 0);
    g.fillStyle = fg; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.strokeStyle = 'rgba(40,22,20,0.55)'; g.lineWidth = 7;
    if (words.length >= 2) {
      g.font = '900 52px Arial, sans-serif';
      for (const [i, w] of [words[0], words.slice(1).join(' ')].entries()) {
        g.strokeText(w, 0, 96 + i * 62);
        g.fillText(w, 0, 96 + i * 62);
      }
    } else {
      g.font = '900 58px Arial, sans-serif';
      g.strokeText(name, 0, 118);
      g.fillText(name, 0, 118);
    }
    if (sub) {
      g.font = 'bold 24px Arial, sans-serif'; g.fillStyle = '#ffe9a8';
      g.fillText(sub, 0, 188);
    }
    g.restore();
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/** Shelf product box front (256x256): bold name + brand band + baked ink border. */
function makeShelfBoxTex(name, { bg = '#c8453a', band = '#7e211a', fg = '#fff7e8', tag = 'NET 400g' } = {}) {
  const [c, g] = cv(256, 256);
  g.fillStyle = bg; g.fillRect(0, 0, 256, 256);
  g.fillStyle = band; g.fillRect(0, 0, 256, 54); g.fillRect(0, 202, 256, 54);
  g.strokeStyle = '#33201f'; g.lineWidth = 10; g.strokeRect(5, 5, 246, 246);
  g.fillStyle = fg; g.textAlign = 'center'; g.textBaseline = 'middle';
  const words = name.split(' ');
  if (words.length >= 2) {
    g.font = '900 46px Arial, sans-serif';
    g.fillText(words[0], 128, 108);
    g.fillText(words.slice(1).join(' '), 128, 162);
  } else {
    g.font = '900 54px Arial, sans-serif';
    g.fillText(name, 128, 132);
  }
  g.font = 'bold 22px Arial, sans-serif'; g.fillStyle = '#ffe9a8';
  g.fillText(tag, 128, 34);
  g.font = 'bold 20px Arial, sans-serif'; g.fillStyle = fg;
  g.fillText('CORNER MART', 128, 230);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/** Bottle wrap label: colored drink body + white center band with bold name. */
function makeBottleTex(name, { bg = '#b8231e', fg = '#20262e' } = {}) {
  const [c, g] = cv(256, 256);
  g.fillStyle = bg; g.fillRect(0, 0, 256, 256);
  g.fillStyle = '#f5f1e6'; g.fillRect(0, 86, 256, 84);
  g.strokeStyle = 'rgba(40,26,24,0.6)'; g.lineWidth = 6; g.strokeRect(3, 3, 250, 250);
  for (const cx of [64, 192]) {
    g.fillStyle = fg; g.textAlign = 'center'; g.textBaseline = 'middle';
    const words = name.split(' ');
    if (words.length >= 2) {
      g.font = '900 30px Arial, sans-serif';
      g.fillText(words[0], cx, 112);
      g.fillText(words[1], cx, 144);
    } else {
      g.font = '900 34px Arial, sans-serif';
      g.fillText(name, cx, 128);
    }
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/** CHOCOLATE bar top wrapper (the hero readable product!). */
function makeChocoTex() {
  const [c, g] = cv(512, 256);
  g.fillStyle = '#5c3a22'; g.fillRect(0, 0, 512, 256);
  g.fillStyle = '#6e4a2c'; g.fillRect(0, 0, 512, 26); g.fillRect(0, 230, 512, 26);
  g.strokeStyle = '#e8b64a'; g.lineWidth = 10; g.strokeRect(10, 10, 492, 236);
  g.strokeStyle = '#3a2312'; g.lineWidth = 5; g.strokeRect(24, 24, 464, 208);
  for (let i = 0; i < 6; i++) { // foil ridge lines
    g.strokeStyle = 'rgba(255,226,150,0.28)'; g.lineWidth = 4;
    g.beginPath(); g.moveTo(30 + i * 78, 30); g.lineTo(30 + i * 78, 226); g.stroke();
  }
  g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillStyle = '#f7df9a'; g.font = '900 88px Arial, sans-serif';
  g.strokeStyle = '#2c1a0c'; g.lineWidth = 10;
  g.strokeText('CHOCOLATE', 256, 106);
  g.fillText('CHOCOLATE', 256, 106);
  g.fillStyle = '#f2e3bd'; g.font = 'bold 30px Arial, sans-serif';
  g.fillText('MILK CHOCOLATE · CRISPY', 256, 176);
  g.font = 'bold 24px Arial, sans-serif'; g.fillStyle = '#e8b64a';
  g.fillText('RICH COCOA  40g', 256, 210);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/** FIRST AID KIT face. */
function makeFakTex() {
  const [c, g] = cv(256, 256);
  g.fillStyle = '#f7f5ef'; g.fillRect(0, 0, 256, 256);
  g.strokeStyle = '#351f22'; g.lineWidth = 10; g.strokeRect(6, 6, 244, 244);
  g.fillStyle = '#d92822'; g.fillRect(96, 60, 64, 20); g.fillRect(118, 38, 20, 64);
  g.fillStyle = '#20262e'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.font = '900 42px Arial, sans-serif';
  g.fillText('FIRST AID', 128, 158);
  g.font = '900 54px Arial, sans-serif';
  g.fillText('KIT', 128, 210);
  g.font = 'bold 18px Arial, sans-serif'; g.fillStyle = '#7a4a44';
  g.fillText('STERILE · 12 PIECES', 128, 30);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/** Yellow shelf-edge SALE price strip (repeats along the rail). */
function makePriceStripTex() {
  const [c, g] = cv(1024, 64);
  g.fillStyle = '#f2c832'; g.fillRect(0, 0, 1024, 64);
  g.fillStyle = '#231a10'; g.fillRect(0, 0, 1024, 8); g.fillRect(0, 56, 1024, 8);
  g.fillStyle = '#231a10'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.font = '900 34px Arial, sans-serif';
  for (const x of [128, 384, 640, 896]) {
    g.fillText('SALE  $1.29', x, 34);
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = THREE.RepeatWrapping;
  t.repeat.set(2, 1);
  return t;
}

/** Yellow/black diagonal hazard stripes. */
function makeHazardTex() {
  const [c, g] = cv(256, 128);
  g.fillStyle = '#e6b83c'; g.fillRect(0, 0, 256, 128);
  g.fillStyle = '#221f1c';
  for (let i = -4; i < 10; i++) {
    g.beginPath();
    g.moveTo(i * 40, 128); g.lineTo(i * 40 + 40, 128);
    g.lineTo(i * 40 + 40 + 64, 0); g.lineTo(i * 40 + 64, 0);
    g.closePath(); g.fill();
  }
  g.strokeStyle = '#33201f'; g.lineWidth = 8; g.strokeRect(2, 2, 252, 124);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/** Striped shop awning. */
function makeAwningTex(colA = '#c8453a', colB = '#f2ead8') {
  const [c, g] = cv(256, 64);
  for (let i = 0; i < 8; i++) {
    g.fillStyle = i % 2 === 0 ? colA : colB;
    g.fillRect(i * 32, 0, 32, 64);
  }
  g.fillStyle = 'rgba(40,26,24,0.35)'; g.fillRect(0, 52, 256, 12);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = THREE.RepeatWrapping;
  return t;
}

/** POS register touchscreen (green LCD). */
function makePosScreenTex() {
  const [c, g] = cv(256, 192);
  g.fillStyle = '#0d2415'; g.fillRect(0, 0, 256, 192);
  g.fillStyle = '#7dffa8'; g.font = 'bold 26px monospace'; g.textAlign = 'left';
  g.fillText('CORNER MART', 14, 34);
  g.fillStyle = '#d8ffe4'; g.font = 'bold 34px monospace';
  g.fillText('TOTAL  6.40', 14, 92);
  g.fillStyle = '#7dffa8'; g.font = 'bold 22px monospace';
  g.fillText('CASH / CARD', 14, 136);
  g.fillText('09-11  16:17', 14, 170);
  g.strokeStyle = '#356644'; g.lineWidth = 4; g.strokeRect(4, 4, 248, 184);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/** CCTV security monitor (2 grainy cams + timestamp). */
function makeCctvTex() {
  const [c, g] = cv(256, 160);
  g.fillStyle = '#10151c'; g.fillRect(0, 0, 256, 160);
  for (const [vx, label] of [[8, 'CAM 01 AISLE'], [132, 'CAM 02 STORAGE']]) {
    g.fillStyle = '#1c2a33'; g.fillRect(vx, 8, 116, 88);
    g.fillStyle = '#2c3d49'; g.fillRect(vx + 8, 16, 44, 60); // shelf blob
    g.fillStyle = '#42576a'; g.fillRect(vx + 14, 24, 32, 8); g.fillRect(vx + 14, 40, 32, 8); g.fillRect(vx + 14, 56, 32, 8);
    g.fillStyle = '#9fb6c8'; g.fillRect(vx + 62, 20, 42, 54); // doorway glow
    g.fillStyle = '#cfe4f2'; g.font = 'bold 12px monospace'; g.textAlign = 'left';
    g.fillText(label, vx + 4, 112);
    g.fillStyle = '#ffd24c'; g.font = 'bold 13px monospace';
    g.fillText('REC 04:17PM', vx + 4, 130);
  }
  g.strokeStyle = '#39434e'; g.lineWidth = 5; g.strokeRect(3, 3, 250, 154);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/** Wall clock frozen at 4:17 (story time!). */
function makeClockTex() {
  const [c, g] = cv(256, 256);
  g.fillStyle = '#f6f2e8'; g.beginPath(); g.arc(128, 128, 124, 0, 7); g.fill();
  g.strokeStyle = '#351f22'; g.lineWidth = 10; g.beginPath(); g.arc(128, 128, 118, 0, 7); g.stroke();
  for (let i = 0; i < 12; i++) {
    const a = (i / 12) * Math.PI * 2;
    g.strokeStyle = '#351f22'; g.lineWidth = i % 3 === 0 ? 9 : 5;
    g.beginPath();
    g.moveTo(128 + Math.sin(a) * 96, 128 - Math.cos(a) * 96);
    g.lineTo(128 + Math.sin(a) * 108, 128 - Math.cos(a) * 108);
    g.stroke();
  }
  const hourA = ((4 + 17 / 60) / 12) * Math.PI * 2;
  const minA = (17 / 60) * Math.PI * 2;
  g.strokeStyle = '#20262e'; g.lineWidth = 12; g.lineCap = 'round';
  g.beginPath(); g.moveTo(128, 128); g.lineTo(128 + Math.sin(hourA) * 56, 128 - Math.cos(hourA) * 56); g.stroke();
  g.lineWidth = 8;
  g.beginPath(); g.moveTo(128, 128); g.lineTo(128 + Math.sin(minA) * 88, 128 - Math.cos(minA) * 88); g.stroke();
  g.strokeStyle = '#c8382e'; g.lineWidth = 4;
  g.beginPath(); g.moveTo(128, 128); g.lineTo(128 + Math.sin(minA + 2.1) * 92, 128 - Math.cos(minA + 2.1) * 92); g.stroke();
  g.fillStyle = '#351f22'; g.beginPath(); g.arc(128, 128, 10, 0, 7); g.fill();
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/** Glowing OPEN 24 HRS neon (transparent canvas). */
function makeNeonTex() {
  const [c, g] = cv(512, 160);
  g.clearRect(0, 0, 512, 160);
  g.textAlign = 'center'; g.textBaseline = 'middle';
  g.strokeStyle = 'rgba(64,239,255,0.35)'; g.lineWidth = 26; g.lineJoin = 'round';
  g.font = '900 92px Arial, sans-serif';
  g.strokeText('OPEN', 256, 58);
  g.font = '900 54px Arial, sans-serif';
  g.strokeText('24 HRS', 256, 124);
  g.shadowColor = '#53f2ff'; g.shadowBlur = 26;
  g.fillStyle = '#d9fbff';
  g.font = '900 92px Arial, sans-serif';
  g.fillText('OPEN', 256, 58);
  g.font = '900 54px Arial, sans-serif';
  g.fillText('24 HRS', 256, 124);
  g.shadowBlur = 0;
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/** Wall promo poster. */
function makePosterTex(title, sub, { bg = '#f2ead8', accent = '#c8382e', art = 'cup' } = {}) {
  const [c, g] = cv(256, 384);
  g.fillStyle = bg; g.fillRect(0, 0, 256, 384);
  g.fillStyle = accent; g.fillRect(0, 0, 256, 60);
  g.strokeStyle = '#351f22'; g.lineWidth = 10; g.strokeRect(6, 6, 244, 372);
  g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillStyle = '#fff6e4'; g.font = '900 40px Arial, sans-serif';
  g.fillText(title.split(' ')[0], 128, 32);
  if (art === 'cup') {
    g.fillStyle = '#e8e2d4'; g.fillRect(88, 120, 80, 78);
    g.fillStyle = '#6e4a2c'; g.fillRect(96, 130, 64, 16);
    g.strokeStyle = '#e8e2d4'; g.lineWidth = 10;
    g.beginPath(); g.arc(170, 158, 20, -1.2, 1.2); g.stroke();
    g.strokeStyle = '#c8b9a4'; g.lineWidth = 6;
    g.beginPath(); g.moveTo(110, 100); g.quadraticCurveTo(128, 88, 146, 100); g.stroke();
  } else if (art === 'slush') {
    g.fillStyle = '#d94136'; g.beginPath(); g.moveTo(84, 210); g.lineTo(118, 118); g.lineTo(138, 118); g.lineTo(172, 210); g.closePath(); g.fill();
    g.fillStyle = '#2f6db3'; g.beginPath(); g.moveTo(108, 118); g.lineTo(148, 118); g.lineTo(138, 96); g.lineTo(118, 96); g.closePath(); g.fill();
  } else {
    g.fillStyle = '#e6b83c'; g.font = '900 110px Arial, sans-serif';
    g.fillText('%', 128, 165);
  }
  g.fillStyle = '#20262e'; g.font = '900 44px Arial, sans-serif';
  const words = sub.split(' ');
  if (words.length > 2) {
    g.fillText(words.slice(0, 2).join(' '), 128, 268);
    g.fillText(words.slice(2).join(' '), 128, 318);
  } else {
    g.fillText(sub, 128, 292);
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/** WELCOME door mat. */
function makeMatTex() {
  const [c, g] = cv(512, 256);
  g.fillStyle = '#7a2e28'; g.fillRect(0, 0, 512, 256);
  g.fillStyle = '#5c221e'; g.fillRect(0, 0, 512, 26); g.fillRect(0, 230, 512, 26); g.fillRect(0, 0, 26, 256); g.fillRect(486, 0, 26, 256);
  const r = P.rng(88);
  for (let i = 0; i < 500; i++) { // bristle noise
    g.fillStyle = r() > 0.5 ? 'rgba(255,220,200,0.05)' : 'rgba(30,10,8,0.08)';
    g.fillRect(r() * 512, r() * 256, 3, 3);
  }
  g.fillStyle = '#f2d9a8'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.font = '900 96px Georgia, serif';
  g.fillText('WELCOME', 256, 128);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/** Emergency field radio faceplate. */
function makeRadioFaceTex() {
  const [c, g] = cv(256, 128);
  g.fillStyle = '#232a26'; g.fillRect(0, 0, 256, 128);
  g.strokeStyle = '#101512'; g.lineWidth = 6; g.strokeRect(3, 3, 250, 122);
  g.fillStyle = '#181d1b'; g.fillRect(12, 12, 96, 104); // speaker grille
  for (let y = 20; y < 112; y += 9) { g.fillStyle = '#39423c'; g.fillRect(16, y, 88, 4); }
  g.fillStyle = '#c9d2c8'; g.textAlign = 'left'; g.textBaseline = 'middle';
  g.font = '900 22px Arial, sans-serif';
  g.fillText('EM-9 FIELD RADIO', 118, 26);
  g.fillStyle = '#0e1a10'; g.fillRect(118, 38, 60, 26);
  g.fillStyle = '#7dffa8'; g.font = 'bold 17px monospace';
  g.fillText('CH-9', 126, 52);
  g.fillStyle = '#c9d2c8'; g.font = 'bold 13px Arial, sans-serif';
  g.fillText('PWR', 190, 40); g.fillText('VOL', 190, 58);
  g.fillText('EMERGENCY BAND', 118, 82);
  g.fillStyle = '#e6b83c'; g.font = 'bold 14px Arial, sans-serif';
  g.fillText('USE ONLY IF ALIVE', 118, 104);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

export function makeSignBoard(title, sub = '', { w = 1.6, h = 0.48, bg = '#f4ead2', fg = '#351f22', accent = '#c83e32' } = {}) {
  const [c, g] = cv(512, 160);
  g.fillStyle = bg; g.fillRect(0, 0, 512, 160);
  g.fillStyle = accent; g.fillRect(0, 0, 512, 28);
  g.strokeStyle = fg; g.lineWidth = 8; g.strokeRect(6, 6, 500, 148);
  g.fillStyle = fg; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.font = '900 50px Arial, sans-serif';
  g.fillText(title, 256, sub ? 78 : 90);
  if (sub) {
    g.font = 'bold 27px Arial, sans-serif';
    g.fillStyle = '#5a463c';
    g.fillText(sub, 256, 128);
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  const plain = toon(bg);
  const face = toon('#ffffff', t);
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, 0.07), [plain, plain, plain, plain, face, face]);
  return ink(m, 0.015, true);
}

/** V6.5 REAL SMARTPHONE SCREENS (480x852, dynamic-island chrome, real app UIs). */
function makePhoneScreenTex(mode = 'alert1') {
  const [c, g] = cv(480, 852);
  const W = 480, H = 852;

  // ---- shared real-phone chrome: wallpaper, status bar, dynamic island, home bar ----
  const chrome = (wall, time, pct, lowBatt) => {
    g.fillStyle = wall; g.fillRect(0, 0, W, H);
    // status bar
    g.fillStyle = '#eef1f5'; g.font = 'bold 20px Arial'; g.textAlign = 'left';
    g.fillText(time, 34, 46);
    // signal bars
    for (let i = 0; i < 4; i++) g.fillRect(300 + i * 9, 40 - (7 + i * 4), 6, 7 + i * 4);
    g.font = 'bold 15px Arial'; g.fillText('LTE', 268, 46);
    // wifi arcs
    g.strokeStyle = '#eef1f5'; g.lineWidth = 3.4;
    for (let rr = 5; rr <= 15; rr += 5) { g.beginPath(); g.arc(356, 42, rr, Math.PI * 1.25, Math.PI * 1.75); g.stroke(); }
    g.fillStyle = '#eef1f5'; g.beginPath(); g.arc(356, 42, 3.2, 0, 7); g.fill();
    // battery
    g.strokeStyle = lowBatt ? '#ff4438' : '#eef1f5'; g.lineWidth = 3;
    g.strokeRect(392, 24, 46, 20);
    g.fillStyle = lowBatt ? '#ff4438' : '#eef1f5';
    g.fillRect(395, 27, Math.max(3, Math.round(40 * pct)), 14);
    g.fillRect(439, 29, 5, 10);
    g.font = 'bold 15px Arial'; g.textAlign = 'right'; g.fillText(`${Math.round(pct * 100)}%`, 384, 46);
    // dynamic island
    g.fillStyle = '#000000';
    g.beginPath(); g.roundRect(165, 12, 150, 32, 16); g.fill();
    g.fillStyle = '#10141c'; g.beginPath(); g.arc(288, 28, 6.5, 0, 7); g.fill();
    g.fillStyle = '#233043'; g.beginPath(); g.arc(288, 28, 2.6, 0, 7); g.fill();
    // home indicator
    g.fillStyle = 'rgba(238,241,245,0.85)';
    g.beginPath(); g.roundRect(180, 826, 120, 6, 3); g.fill();
  };

  if (mode === 'social0' || mode === 'social1') {
    // ================= FACEBOOK-STYLE SOCIAL FEED (bright normal life, pre-alert) =================
    const wall = '#e9edf3';
    g.fillStyle = wall; g.fillRect(0, 0, W, H);
    // fb header
    g.fillStyle = '#ffffff'; g.fillRect(0, 52, W, 76);
    g.fillStyle = '#1877f2'; g.font = '900 31px Arial'; g.textAlign = 'left';
    g.fillText('facebook', 30, 104);
    // search + messenger circles
    g.fillStyle = '#e4e6eb'; g.beginPath(); g.arc(366, 90, 25, 0, 7); g.fill();
    g.fillStyle = '#65676b'; g.font = '900 20px Arial'; g.textAlign = 'center'; g.fillText('Q', 366, 100);
    g.fillStyle = '#e4e6eb'; g.beginPath(); g.arc(428, 90, 25, 0, 7); g.fill();
    g.strokeStyle = '#0084ff'; g.lineWidth = 3;
    g.beginPath(); g.moveTo(418, 84); g.lineTo(438, 84); g.moveTo(418, 94); g.lineTo(432, 94); g.stroke(); // messenger bolt
    if (mode === 'social1') {
      g.fillStyle = '#e41e3f'; g.beginPath(); g.arc(448, 70, 14, 0, 7); g.fill();
      g.fillStyle = '#fff'; g.font = 'bold 14px Arial'; g.fillText('9', 448, 76);
    }
    // ===== post 1: city news page =====
    g.fillStyle = '#ffffff'; g.fillRect(0, 128, W, 300);
    g.fillStyle = '#c8102e'; g.beginPath(); g.roundRect(30, 152, 56, 56, 12); g.fill();
    g.fillStyle = '#fff'; g.font = '900 20px Arial'; g.textAlign = 'center'; g.fillText('OCN', 58, 188);
    g.textAlign = 'left'; g.fillStyle = '#050505'; g.font = 'bold 20px Arial';
    g.fillText('Outbreak City News', 102, 172);
    g.fillStyle = '#0084ff'; g.beginPath(); g.arc(340, 164, 9, 0, 7); g.fill();
    g.fillStyle = '#fff'; g.font = 'bold 13px Arial'; g.fillText('✓', 336, 169);
    g.fillStyle = '#65676b'; g.font = 'normal 16px Arial'; g.fillText('Sponsored · 4m', 102, 198);
    g.fillStyle = '#050505'; g.font = 'normal 19px Arial';
    g.fillText('BREAKING: Hospitals report a fast-spreading', 30, 246);
    g.fillText('illness. Officials urge everyone to stay', 30, 278);
    g.fillText('indoors until further notice.', 30, 310);
    // link preview with LIVE tag
    g.fillStyle = '#1c1e21'; g.fillRect(30, 330, 420, 56);
    g.fillStyle = '#c8102e'; g.beginPath(); g.roundRect(40, 344, 58, 26, 5); g.fill();
    g.fillStyle = '#fff'; g.font = '900 13px Arial'; g.textAlign = 'center'; g.fillText('LIVE', 69, 363);
    g.fillStyle = '#d8dbe1'; g.textAlign = 'left'; g.font = 'bold 16px Arial';
    g.fillText('LIVE: Emergency briefing — city lockdown', 110, 366);
    // reactions row (drawn icons — no emoji)
    g.fillStyle = '#1877f2'; g.beginPath(); g.arc(48, 412, 12, 0, 7); g.fill();
    g.fillStyle = '#e41e3f'; g.beginPath(); g.arc(63, 412, 12, 0, 7); g.fill();
    g.fillStyle = '#65676b'; g.font = 'normal 16px Arial';
    g.fillText('15.2K', 84, 419);
    g.textAlign = 'right'; g.fillText('612 comments · 4.1K shares', 450, 419);
    // ===== post 2 (partial): community panic =====
    g.fillStyle = '#ffffff'; g.fillRect(0, 442, W, 210);
    g.fillStyle = '#7a5af8'; g.beginPath(); g.roundRect(30, 466, 56, 56, 28); g.fill();
    g.fillStyle = '#fff'; g.font = '900 19px Arial'; g.textAlign = 'center'; g.fillText('CA', 58, 502);
    g.textAlign = 'left'; g.fillStyle = '#050505'; g.font = 'bold 20px Arial';
    g.fillText('Community Alert Group', 102, 486);
    g.fillStyle = '#65676b'; g.font = 'normal 16px Arial'; g.fillText('1m · Public', 102, 512);
    g.fillStyle = '#050505'; g.font = 'normal 19px Arial';
    g.fillText('They are NOT sick. They are not people', 30, 558);
    g.fillText('anymore. Lock your doors. Do not open', 30, 590);
    g.fillText('for ANYONE.', 30, 622);
    // ===== notification banner (social1 only) — the moment the world changes =====
    if (mode === 'social1') {
      g.save();
      g.shadowColor = 'rgba(10,12,18,0.55)'; g.shadowBlur = 34; g.shadowOffsetY = 14;
      g.fillStyle = '#ffffff'; g.beginPath(); g.roundRect(20, 66, 440, 118, 26); g.fill();
      g.restore();
      g.strokeStyle = 'rgba(20,24,34,0.18)'; g.lineWidth = 2;
      g.beginPath(); g.roundRect(21, 67, 438, 116, 25); g.stroke();
      g.fillStyle = '#c8102e'; g.beginPath(); g.roundRect(40, 84, 64, 64, 16); g.fill();
      g.fillStyle = '#fff'; g.font = '900 31px Arial'; g.textAlign = 'center'; g.fillText('!', 72, 130);
      g.textAlign = 'left'; g.fillStyle = '#050505'; g.font = '900 19px Arial';
      g.fillText('EMERGENCY ALERTS', 120, 108);
      g.fillStyle = '#3a3d42'; g.font = 'normal 16px Arial';
      g.fillText('Severe threat in this area. Tap', 120, 138);
      g.fillStyle = '#3a3d42'; g.fillText('to read the full alert', 120, 164);
      g.fillStyle = '#8a8d91'; g.font = 'normal 13px Arial'; g.textAlign = 'right'; g.fillText('now', 444, 108);
    }
  } else if (mode === 'alert1') {
    // ================= iOS GOVERNMENT EMERGENCY ALERT (4:17 PM) =================
    chrome('#12233c', '4:17', 0.78, false);
    // dim wallpaper stripes for depth
    g.fillStyle = 'rgba(255,255,255,0.028)';
    for (let y = 60; y < 852; y += 44) g.fillRect(0, y, W, 16);
    // alert card
    g.save();
    g.shadowColor = 'rgba(0,0,0,0.5)'; g.shadowBlur = 30; g.shadowOffsetY = 12;
    g.fillStyle = '#f7f5f0'; g.beginPath(); g.roundRect(28, 210, 424, 400, 30); g.fill();
    g.restore();
    g.textAlign = 'center';
    g.fillStyle = '#b25000'; g.font = '900 27px Arial';
    g.fillText('EMERGENCY ALERT', 240, 276);
    g.fillStyle = '#8d939c'; g.font = 'bold 17px Arial';
    g.fillText('CIVIL DANGER WARNING', 240, 312);
    g.strokeStyle = '#d9d4c8'; g.lineWidth = 2; g.beginPath(); g.moveTo(60, 338); g.lineTo(420, 338); g.stroke();
    g.fillStyle = '#15181d'; g.font = '900 34px Arial';
    g.fillText('STAY INDOORS', 240, 398);
    g.fillStyle = '#33383f'; g.font = 'bold 20px Arial';
    for (const [i, ln] of [
      'Avoid confused or violent', 'individuals.', '',
      'Do not approach emergency', 'responders unless instructed.',
    ].entries()) g.fillText(ln, 240, 452 + i * 42);
    // realistic Dismiss button
    g.fillStyle = '#e8e4da'; g.beginPath(); g.roundRect(150, 528, 180, 56, 28); g.fill();
    g.fillStyle = '#007aff'; g.font = '900 20px Arial'; g.fillText('Dismiss', 240, 564);
  } else if (mode === 'alert2') {
    // ================= 2:14 AM CRITICAL UPDATE + missed-message stack =================
    chrome('#0a0507', '2:14', 0.17, true);
    g.save();
    g.shadowColor = 'rgba(0,0,0,0.6)'; g.shadowBlur = 30; g.shadowOffsetY = 12;
    g.fillStyle = '#b8171e'; g.beginPath(); g.roundRect(28, 140, 424, 210, 28); g.fill();
    g.restore();
    g.textAlign = 'center'; g.fillStyle = '#ffffff';
    g.font = '900 28px Arial'; g.fillText('CRITICAL UPDATE', 240, 206);
    g.font = 'bold 18px Arial'; g.fillStyle = '#ffd9d4'; g.fillText('NEW EMERGENCY MESSAGE', 240, 244);
    g.strokeStyle = 'rgba(255,255,255,0.35)'; g.lineWidth = 2; g.beginPath(); g.moveTo(60, 268); g.lineTo(420, 268); g.stroke();
    g.fillStyle = '#ffffff'; g.font = '900 23px Arial';
    g.fillText('Do not respond to voices outside.', 240, 310);
    // missed messages stack (the dread of an unread world)
    for (const [yy, icon, iconCol, name, body, when] of [
      [372, 'M', '#34c759', 'Mom', 'please answer your phone', '2:02 AM'],
      [500, 'f', '#1877f2', 'facebook', '1,204 new alerts near you', '1:58 AM'],
    ]) {
      g.save();
      g.shadowColor = 'rgba(0,0,0,0.5)'; g.shadowBlur = 18; g.shadowOffsetY = 8;
      g.fillStyle = '#1c1f26'; g.beginPath(); g.roundRect(28, yy, 424, 108, 24); g.fill();
      g.restore();
      g.fillStyle = iconCol; g.beginPath(); g.roundRect(48, yy + 24, 56, 56, 14); g.fill();
      g.fillStyle = '#fff'; g.font = '900 20px Arial'; g.textAlign = 'center'; g.fillText(icon, 76, yy + 60);
      g.textAlign = 'left'; g.fillStyle = '#e8eaee'; g.font = 'bold 19px Arial';
      g.fillText(name, 122, yy + 42);
      g.fillStyle = '#9aa0a8'; g.font = 'normal 16px Arial';
      g.fillText(body, 122, yy + 74);
      g.textAlign = 'right'; g.fillStyle = '#6b7280'; g.font = 'normal 13px Arial';
      g.fillText(when, 432, yy + 40);
    }
    g.textAlign = 'center'; g.fillStyle = '#ff4f42'; g.font = '900 21px Arial';
    g.fillText('AFFECTED MAY IMITATE FAMILIAR SPEECH', 240, 664);
    g.fillStyle = '#ffd24c'; g.font = 'bold 19px Arial';
    g.fillText('KEEP ALL DOORS LOCKED', 240, 704);
  } else {
    // ================= SUNRISE OFFLINE MAP (4% battery) =================
    chrome('#0c1824', '6:12', 0.04, true);
    g.fillStyle = '#9ec0d8'; g.font = 'bold 17px Arial'; g.textAlign = 'left';
    g.fillText('OFFLINE MAP', 34, 96);
    g.fillStyle = '#132638'; g.beginPath(); g.roundRect(24, 120, 432, 470, 18); g.fill();
    g.save(); g.beginPath(); g.roundRect(24, 120, 432, 470, 18); g.clip();
    g.strokeStyle = '#294866'; g.lineWidth = 16;
    for (const gx of [130, 240, 350]) { g.beginPath(); g.moveTo(gx, 120); g.lineTo(gx, 590); g.stroke(); }
    for (const gy of [210, 340, 470]) { g.beginPath(); g.moveTo(24, gy); g.lineTo(456, gy); g.stroke(); }
    g.strokeStyle = '#ffd24c'; g.lineWidth = 9;
    g.beginPath(); g.moveTo(130, 470); g.lineTo(130, 210); g.lineTo(350, 210); g.stroke();
    g.fillStyle = '#3ad4ff'; g.beginPath(); g.arc(130, 470, 13, 0, 7); g.fill();
    g.fillStyle = '#ff4438'; g.beginPath(); g.arc(350, 210, 16, 0, 7); g.fill();
    g.strokeStyle = '#ff4438'; g.lineWidth = 4;
    g.beginPath(); g.arc(350, 210, 26 + 6 * Math.sin(Date.now() * 0.004), 0, 7); g.stroke();
    g.restore();
    g.textAlign = 'center'; g.fillStyle = '#ffffff'; g.font = '900 22px Arial';
    g.fillText('TRANSIT STATION', 240, 636);
    g.fillStyle = '#ffd24c'; g.font = 'bold 18px Arial';
    g.fillText('MAINTENANCE ENTRANCE', 240, 672);
    g.fillStyle = '#9ec0d8'; g.font = 'bold 16px Arial';
    g.fillText('2 STREETS AWAY · ALLEY ROUTE', 240, 708);
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

// =========================== SLEEK RICK CLIPS 3D CAR ===========================
function makeCar(color = '#3b73b5', kind = 'sedan', patrol = false) {
  const g = new THREE.Group();
  const glass = '#9fd0e8';
  const darkTrim = '#22262b';
  const chrome = '#c9ced4';

  // --- Realistic 5-spoke alloy wheel (tire + rim well + spokes + hub) ---
  const mkWheel = (wx, wz, r) => {
    const w = new THREE.Group();
    w.add(icyl(r, r, 0.26, '#191c1f', { x: wx, y: r, z: wz, rz: Math.PI / 2, thick: 0.014 }));
    w.add(icyl(r * 0.66, r * 0.66, 0.27, '#2b3036', { x: wx, y: r, z: wz, rz: Math.PI / 2, seg: 14, thick: 0.006, edges: false }));
    for (let i = 0; i < 5; i++) {
      const a = (i / 5) * Math.PI * 2 + 0.35;
      const sy = Math.sin(a), sz = Math.cos(a);
      for (const sx of [0.135, -0.135]) {
        w.add(ibox(0.035, r * 0.94, 0.075, '#b6bec7', { x: wx + sx, y: r + sy * r * 0.34, z: wz + sz * r * 0.34, rx: -a, thick: 0.004, edges: false }));
      }
    }
    w.add(icyl(0.075, 0.075, 0.32, '#8d959d', { x: wx, y: r, z: wz, rz: Math.PI / 2, seg: 10, edges: false }));
    return w;
  };

  if (kind === 'suv') {
    // ================= FULL-SIZE SUV (Land Cruiser / Everest class) =================
    const body = patrol ? '#e9ecf0' : color;
    g.add(ibox(1.92, 0.52, 4.55, body, { y: 0.72 }));                       // tall lower tub
    g.add(ibox(1.96, 0.22, 4.60, body, { y: 1.02 }));                       // shoulder line
    g.add(ibox(1.86, 0.12, 1.30, body, { y: 1.11, z: 1.55, rx: -0.02 }));   // flat tall hood
    g.add(ibox(1.72, 0.09, 2.35, patrol ? '#20304a' : body, { y: 1.50, z: -0.30 })); // long roof
    // upright greenhouse glass + pillars
    g.add(ibox(1.56, 0.50, 0.05, glass, { y: 1.22, z: 0.82, rx: 0.20, thick: 0.006, edges: false }));
    g.add(ibox(1.56, 0.50, 0.05, glass, { y: 1.22, z: -1.44, rx: -0.12, thick: 0.006, edges: false }));
    for (const sx of [-0.79, 0.79]) g.add(ibox(0.05, 0.48, 2.16, glass, { x: sx, y: 1.22, z: -0.30, thick: 0.005, edges: false }));
    for (const pz of [0.72, -0.05, -0.82, -1.50]) for (const sx of [-0.86, 0.86]) g.add(ibox(0.09, 0.52, 0.12, darkTrim, { x: sx, y: 1.22, z: pz, thick: 0.006, edges: false }));
    // roof rails on posts
    for (const rx2 of [-0.66, 0.66]) {
      g.add(ibox(0.07, 0.06, 2.20, '#3a4046', { x: rx2, y: 1.60, z: -0.30, thick: 0.008 }));
      for (const rz2 of [-1.20, -0.30, 0.60]) g.add(ibox(0.05, 0.09, 0.05, '#3a4046', { x: rx2, y: 1.55, z: rz2, thick: 0.006, edges: false }));
    }
    // front: chrome grille slats + emblem + skid plate + push bar (patrol)
    g.add(ibox(1.34, 0.30, 0.08, darkTrim, { y: 0.90, z: 2.31, thick: 0.010, edges: false }));
    for (let i = 0; i < 3; i++) g.add(ibox(1.24, 0.045, 0.09, chrome, { y: 0.83 + i * 0.085, z: 2.32, thick: 0.005, edges: false }));
    g.add(ibox(0.16, 0.16, 0.05, '#8ea4b8', { y: 0.98, z: 2.33, ry: Math.PI / 4, thick: 0.004, edges: false }));
    g.add(ibox(1.90, 0.16, 0.16, '#565d63', { y: 0.42, z: 2.32, thick: 0.008, edges: false }));
    g.add(ibox(1.10, 0.30, 0.06, '#a7adb3', { y: 0.36, z: 2.36, thick: 0.006, edges: false })); // skid plate
    if (patrol) {
      for (const bx of [-0.55, 0.55]) g.add(icyl(0.045, 0.045, 0.78, '#2c3238', { x: bx, y: 0.66, z: 2.44, thick: 0.006, edges: false }));
      g.add(ibox(1.24, 0.09, 0.09, '#2c3238', { y: 0.92, z: 2.44, thick: 0.006, edges: false }));
      g.add(ibox(1.24, 0.09, 0.09, '#2c3238', { y: 0.50, z: 2.44, thick: 0.006, edges: false }));
    }
    // headlights + fog lights
    for (const sx of [-0.64, 0.64]) {
      g.add(ibox(0.44, 0.15, 0.07, '#fff4c4', { x: sx, y: 1.06, z: 2.30, thick: 0.005, edges: false }));
      g.add(ibox(0.20, 0.11, 0.06, '#ffe9a8', { x: sx * 1.12, y: 0.52, z: 2.30, thick: 0.005, edges: false }));
      g.add(ibox(0.38, 0.16, 0.07, '#ff2d26', { x: sx, y: 1.06, z: -2.32, thick: 0.005, edges: false }));
    }
    g.add(ibox(0.90, 0.06, 0.06, '#ff3b30', { y: 1.06, z: -2.32, thick: 0.005, edges: false }));
    // rear mounted spare wheel (SUV signature)
    const spare = mkWheel(0, 0, 0.36);
    spare.position.set(0, 0.98, -2.42);
    g.add(spare);
    // patrol livery: navy hood stripe + door panel + reflective strip
    if (patrol) {
      g.add(ibox(1.94, 0.20, 1.32, '#20304a', { y: 1.03, z: 1.56, thick: 0.008, edges: false }));
      for (const sx of [-0.97, 0.97]) g.add(ibox(0.03, 0.34, 1.60, '#20304a', { x: sx, y: 0.72, z: 0.10, thick: 0.006, edges: false }));
      for (const sx of [-0.97, 0.97]) g.add(ibox(0.035, 0.07, 1.30, '#f7c948', { x: sx, y: 0.92, z: 0.10, thick: 0.004, edges: false }));
    }
    // wheels + flares
    for (const [wx, wz] of [[-0.95, -1.45], [0.95, -1.45], [-0.95, 1.45], [0.95, 1.45]]) {
      g.add(mkWheel(wx, wz, 0.42));
      g.add(ibox(0.10, 0.30, 1.06, darkTrim, { x: wx * 1.02, y: 0.62, z: wz, thick: 0.008, edges: false }));
    }
    g.add(ibox(0.42, 0.13, 0.03, '#ece8da', { y: 0.50, z: 2.34, thick: 0.004, edges: false }));
    g.add(ibox(0.42, 0.13, 0.03, '#ece8da', { y: 0.50, z: -2.36, thick: 0.004, edges: false }));
    // patrol light bar (strobe meshes exposed for main.js)
    if (patrol) {
      g.add(ibox(1.10, 0.09, 0.30, '#23282d', { y: 1.60, z: -0.30, thick: 0.008 }));
      const fl = [];
      const flR = new THREE.Mesh(new THREE.BoxGeometry(0.44, 0.14, 0.26), new THREE.MeshBasicMaterial({ color: '#ff2230' }));
      flR.position.set(-0.30, 1.70, -0.30); g.add(flR); fl.push(flR);
      const flB = new THREE.Mesh(new THREE.BoxGeometry(0.44, 0.14, 0.26), new THREE.MeshBasicMaterial({ color: '#2b6bff' }));
      flB.position.set(0.30, 1.70, -0.30); g.add(flB); fl.push(flB);
      g.userData.flashers = fl;
    }
    return g;
  }

  if (kind === 'sport') {
    // ================= SPORT COUPE (Civic Type-R / Mustang class) =================
    g.add(ibox(1.88, 0.30, 4.24, color, { y: 0.52 }));                       // low wide tub
    g.add(ibox(1.92, 0.17, 4.30, color, { y: 0.74 }));                       // taut shoulder
    g.add(ibox(1.82, 0.09, 1.42, color, { y: 0.87, z: 1.42, rx: -0.07 }));   // long raked hood
    g.add(ibox(0.46, 0.05, 1.05, darkTrim, { y: 0.905, z: 1.42, rx: -0.07, thick: 0.004, edges: false })); // hood vents
    g.add(ibox(1.78, 0.08, 0.80, color, { y: 0.86, z: -1.78, rx: 0.06 }));   // ducktail deck
    // set-back cabin, fastback glass, black roof
    g.add(ibox(1.50, 0.46, 0.05, glass, { y: 1.03, z: 0.52, rx: 0.50, thick: 0.006, edges: false }));
    g.add(ibox(1.50, 0.40, 0.05, glass, { y: 1.02, z: -1.18, rx: -0.52, thick: 0.006, edges: false }));
    g.add(ibox(1.54, 0.06, 1.55, '#17191c', { y: 1.235, z: -0.32 }));        // contrasting black roof
    for (const sx of [-0.75, 0.75]) g.add(ibox(0.05, 0.42, 1.55, glass, { x: sx, y: 1.03, z: -0.32, thick: 0.005, edges: false }));
    for (const pz of [0.42, -0.28, -1.05]) for (const sx of [-0.82, 0.82]) g.add(ibox(0.08, 0.46, 0.10, '#17191c', { x: sx, y: 1.03, z: pz, thick: 0.006, edges: false }));
    // REAR WING
    for (const fx of [-0.62, 0.62]) g.add(ibox(0.07, 0.20, 0.22, '#17191c', { x: fx, y: 1.00, z: -2.02, thick: 0.006 }));
    g.add(ibox(1.56, 0.05, 0.34, '#17191c', { y: 1.11, z: -2.04, thick: 0.008 }));
    // aggressive face: splitter + mesh grille + slim LED headlights
    g.add(ibox(1.94, 0.07, 0.34, '#17191c', { y: 0.34, z: 2.16, thick: 0.006 }));
    g.add(ibox(1.30, 0.24, 0.09, darkTrim, { y: 0.62, z: 2.15, thick: 0.010, edges: false }));
    g.add(ibox(0.98, 0.05, 0.10, '#c23b2e', { y: 0.66, z: 2.16, thick: 0.005, edges: false })); // red accent line
    for (const sx of [-0.66, 0.66]) g.add(ibox(0.46, 0.10, 0.07, '#eef6ff', { x: sx, y: 0.78, z: 2.14, thick: 0.005, edges: false }));
    for (const sx of [-0.66, 0.66]) g.add(ibox(0.42, 0.12, 0.06, '#ff2d26', { x: sx, y: 0.78, z: -2.14, thick: 0.005, edges: false }));
    g.add(ibox(0.98, 0.05, 0.05, '#ff3b30', { y: 0.78, z: -2.14, thick: 0.005, edges: false }));
    // side skirts + triple center exhaust
    for (const sx of [-0.96, 0.96]) g.add(ibox(0.06, 0.12, 2.30, '#17191c', { x: sx, y: 0.34, z: -0.10, thick: 0.006, edges: false }));
    for (const ex of [-0.17, 0.0, 0.17]) g.add(icyl(0.055, 0.055, 0.16, '#3a4046', { x: ex, y: 0.42, z: -2.16, rx: Math.PI / 2, seg: 10, edges: false }));
    // door seams + handles + mirrors
    for (const sx of [-0.95, 0.95]) {
      for (const dz of [0.62, -0.16]) g.add(ibox(0.02, 0.30, 0.015, darkTrim, { x: sx, y: 0.62, z: dz, thick: 0.003, edges: false }));
      g.add(ibox(0.15, 0.04, 0.05, '#17191c', { x: sx, y: 0.70, z: 0.30, thick: 0.003, edges: false }));
    }
    for (const mx of [-1.00, 1.00]) g.add(ibox(0.16, 0.08, 0.10, '#17191c', { x: mx, y: 0.92, z: 0.50, ry: mx < 0 ? 0.30 : -0.30, thick: 0.006, edges: false }));
    for (const [wx, wz] of [[-0.94, -1.36], [0.94, -1.36], [-0.94, 1.38], [0.94, 1.38]]) g.add(mkWheel(wx, wz, 0.36));
    g.add(ibox(0.40, 0.12, 0.02, '#ece8da', { y: 0.44, z: 2.18, thick: 0.004, edges: false }));
    g.add(ibox(0.40, 0.12, 0.02, '#ece8da', { y: 0.44, z: -2.18, thick: 0.004, edges: false }));
    return g;
  }

  // ================= SLEEK FAMILY SEDAN (Corolla / Camry class) =================
  g.add(ibox(1.86, 0.36, 4.28, color, { y: 0.60 }));                          // lower body
  g.add(ibox(1.90, 0.16, 4.34, color, { y: 0.84 }));                          // beltline shoulder
  g.add(ibox(1.80, 0.10, 1.24, color, { y: 0.95, z: 1.48, rx: -0.045 }));     // raked hood
  g.add(ibox(1.80, 0.09, 0.92, color, { y: 0.95, z: -1.72, rx: 0.04 }));      // short trunk deck
  g.add(ibox(1.92, 0.045, 4.20, chrome, { y: 0.945, thick: 0.004, edges: false })); // chrome window strip
  // greenhouse: raked A/C pillars, glass, roof
  g.add(ibox(1.52, 0.50, 0.05, glass, { y: 1.17, z: 0.74, rx: 0.44, thick: 0.006, edges: false }));
  g.add(ibox(1.52, 0.44, 0.05, glass, { y: 1.16, z: -1.06, rx: -0.40, thick: 0.006, edges: false }));
  g.add(ibox(1.62, 0.07, 2.04, color, { y: 1.40, z: -0.16 }));
  for (const sx of [-0.79, 0.79]) {
    g.add(ibox(0.05, 0.46, 0.95, glass, { x: sx, y: 1.17, z: 0.22, thick: 0.005, edges: false }));
    g.add(ibox(0.05, 0.46, 0.80, glass, { x: sx, y: 1.17, z: -0.60, thick: 0.005, edges: false }));
  }
  for (const [pz, rr] of [[0.68, 0.44], [-0.16, 0], [-0.98, -0.40]]) for (const sx of [-0.86, 0.86]) g.add(ibox(0.08, 0.50, 0.11, darkTrim, { x: sx, y: 1.17, z: pz, rx: rr, thick: 0.006, edges: false }));
  // front fascia: chrome wing grille + emblem + swept headlights + DRL + fogs
  g.add(ibox(1.34, 0.20, 0.08, darkTrim, { y: 0.72, z: 2.17, thick: 0.010, edges: false }));
  for (let i = 0; i < 2; i++) g.add(ibox(1.26, 0.04, 0.09, chrome, { y: 0.68 + i * 0.08, z: 2.18, thick: 0.005, edges: false }));
  g.add(icyl(0.09, 0.09, 0.05, '#8ea4b8', { y: 0.86, z: 2.19, rx: Math.PI / 2, seg: 6, edges: false }));
  for (const sx of [-0.62, 0.62]) {
    g.add(ibox(0.46, 0.12, 0.07, '#fff4c4', { x: sx, y: 0.86, z: 2.16, ry: sx < 0 ? 0.10 : -0.10, thick: 0.005, edges: false }));
    g.add(ibox(0.40, 0.045, 0.05, '#f3f8ff', { x: sx, y: 0.74, z: 2.17, thick: 0.004, edges: false }));
    g.add(ibox(0.18, 0.10, 0.05, '#ffe9a8', { x: sx * 1.25, y: 0.50, z: 2.13, thick: 0.004, edges: false }));
    g.add(ibox(0.42, 0.13, 0.06, '#ff2d26', { x: sx, y: 0.86, z: -2.17, thick: 0.005, edges: false }));
  }
  g.add(ibox(0.86, 0.05, 0.05, '#ff3b30', { y: 0.86, z: -2.17, thick: 0.004, edges: false }));
  // bumpers + plates + exhaust + shark-fin antenna
  g.add(ibox(1.88, 0.15, 0.15, '#3a4046', { y: 0.38, z: 2.19, thick: 0.008, edges: false }));
  g.add(ibox(1.88, 0.15, 0.15, '#3a4046', { y: 0.38, z: -2.19, thick: 0.008, edges: false }));
  g.add(ibox(0.40, 0.13, 0.02, '#ece8da', { y: 0.48, z: 2.21, thick: 0.004, edges: false }));
  g.add(ibox(0.40, 0.13, 0.02, '#ece8da', { y: 0.48, z: -2.21, thick: 0.004, edges: false }));
  g.add(icyl(0.045, 0.045, 0.14, '#3a4046', { x: -0.55, y: 0.40, z: -2.20, rx: Math.PI / 2, seg: 8, edges: false }));
  g.add(ibox(0.16, 0.09, 0.26, darkTrim, { y: 1.435, z: -0.98, rx: 0.25, thick: 0.005, edges: false }));
  // door seams, handles, mirrors
  for (const sx of [-0.94, 0.94]) {
    for (const dz of [0.58, -0.18]) g.add(ibox(0.02, 0.30, 0.015, darkTrim, { x: sx, y: 0.66, z: dz, thick: 0.003, edges: false }));
    for (const hz of [0.34, -0.42]) g.add(ibox(0.16, 0.045, 0.05, chrome, { x: sx, y: 0.80, z: hz, thick: 0.003, edges: false }));
  }
  for (const mx of [-0.99, 0.99]) g.add(ibox(0.15, 0.08, 0.10, darkTrim, { x: mx, y: 0.98, z: 0.62, ry: mx < 0 ? 0.28 : -0.28, thick: 0.006, edges: false }));
  for (const [wx, wz] of [[-0.93, -1.36], [0.93, -1.36], [-0.93, 1.38], [0.93, 1.38]]) g.add(mkWheel(wx, wz, 0.34));
  return g;
}

export function buildOutbreakWorld(scene) {
  const root = new THREE.Group();
  scene.add(root);

  const floorTex = makeCheckeredFloorTex();
  const subTileTex = makeWallTileTex('#667d78', '#3c4d49', 5, 2);
  const brickTex = makeBrickTex(5, 3);
  const creamWallTex = P.tex(P.plaster(12, 38), 3, 2);
  const concreteTex = makeConcreteTex(3, 4);
  const asphaltTex = makeAsphaltTex(7, 3.5);       // road: ~7.7m x 8m tiling
  const asphaltTexAlley = makeAsphaltTex(3, 10);   // V6: alley gets its own repeat scale
  const paverTex = makePaverTex();                 // V6: sidewalk slabs
  const shutterTex = makeShutterTex();
  const woodTex = P.tex(P.planks(5), 2, 3);
  const hazardTex = makeHazardTex();
  const priceStripTex = makePriceStripTex();

  // =========================================================================
  // 1. CONVENIENCE STORE MAIN FLOOR (`storeGroup`, x: -5.5..5.5, z: -7.5..7.5)
  // =========================================================================
  const storeGroup = new THREE.Group();
  root.add(storeGroup);

  const storeFloor = new THREE.Mesh(new THREE.PlaneGeometry(11.2, 15.2), toon('#ffffff', floorTex));
  storeFloor.rotation.x = -Math.PI / 2;
  storeFloor.receiveShadow = true;
  storeGroup.add(storeFloor);

  const ceiling = new THREE.Mesh(new THREE.PlaneGeometry(11.4, 15.4), toon('#dde3e8'));
  ceiling.rotation.x = Math.PI / 2;
  ceiling.position.y = 3.65;
  storeGroup.add(ceiling);

  const fluorStrips = [];
  for (const fx of [-2.8, 2.8]) {
    for (const fz of [-4.5, 0.0, 4.2]) {
      const housing = ibox(0.55, 0.10, 2.4, '#cfd6de', { x: fx, y: 3.59, z: fz, thick: 0.012, cast: false });
      const tubeMat = new THREE.MeshBasicMaterial({ color: '#fffdf2' });
      const tube = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.05, 2.25), tubeMat);
      tube.position.set(fx, 3.53, fz);
      storeGroup.add(housing, tube);
      fluorStrips.push(tubeMat);
    }
  }

  // Side walls + Wall Light Switch (for "Then, you switch off the lights" at 45.8s!)
  storeGroup.add(ibox(0.28, 3.7, 15.2, '#ffffff', { map: creamWallTex, x: -5.5, y: 1.85, z: 0, cast: false }));
  storeGroup.add(ibox(0.28, 3.7, 15.2, '#ffffff', { map: creamWallTex, x: 5.5, y: 1.85, z: 0, cast: false }));
  storeGroup.add(ibox(0.06, 1.1, 15.0, '#3e7a8c', { x: 5.34, y: 0.55, z: 0, thick: 0.008, cast: false }));
  // Wall light switch plate near front pillar (x = 1.35, y = 1.32, z = 7.28)
  storeGroup.add(ibox(0.16, 0.24, 0.05, '#eef2f5', { x: 1.35, y: 1.32, z: 7.28, thick: 0.008 }));
  storeGroup.add(ibox(0.05, 0.09, 0.06, '#d94136', { x: 1.35, y: 1.32, z: 7.26, thick: 0.005 }));

  // Back partition wall (z = -7.5) with doorway to Back Storage Corridor (x = 2.8)
  storeGroup.add(ibox(1.6, 3.7, 0.26, '#ffffff', { map: creamWallTex, x: -4.7, y: 1.85, z: -7.5 }));
  storeGroup.add(ibox(4.4, 3.7, 0.26, '#ffffff', { map: creamWallTex, x: -0.3, y: 1.85, z: -7.5 }));
  storeGroup.add(ibox(1.8, 3.7, 0.26, '#ffffff', { map: creamWallTex, x: 4.6, y: 1.85, z: -7.5 }));
  storeGroup.add(ibox(1.4, 1.1, 0.28, '#ffffff', { map: creamWallTex, x: -3.2, y: 3.15, z: -7.5 }));
  storeGroup.add(ibox(1.8, 1.1, 0.28, '#ffffff', { map: creamWallTex, x: 2.8, y: 3.15, z: -7.5 }));
  const storageSign = makeSignBoard('BACK ALLEY', 'DELIVERY EXIT', { w: 1.35, h: 0.34, accent: '#c83e32' });
  storageSign.position.set(2.8, 2.88, -7.32); storeGroup.add(storageSign);

  // WALL CLOCK frozen at 4:17 (right above the back counter, behind YOU in Shots 1-2!)
  const clockTex = makeClockTex();
  const clockFaceMat = toon('#ffffff', clockTex);
  const clock = new THREE.Mesh(new THREE.CylinderGeometry(0.30, 0.30, 0.06, 24), [toon('#8f2b26'), clockFaceMat, toon('#8f2b26')]);
  clock.rotation.x = Math.PI / 2;
  clock.position.set(1.30, 2.62, -7.30);
  storeGroup.add(ink(clock, 0.014, true));

  // Storefront Wall (z = 7.5)
  storeGroup.add(ibox(11.3, 0.72, 0.32, '#2d4659', { x: 0, y: 3.34, z: 7.5 }));
  storeGroup.add(ibox(4.1, 0.58, 0.30, '#3e5c73', { x: -3.45, y: 0.29, z: 7.5 }));
  storeGroup.add(ibox(4.1, 0.58, 0.30, '#3e5c73', { x: 3.45, y: 0.29, z: 7.5 }));
  for (const px of [-5.4, -1.35, 1.35, 5.4]) {
    storeGroup.add(ibox(0.26, 3.7, 0.34, '#2d4659', { x: px, y: 1.85, z: 7.5 }));
  }
  const extSign = makeSignBoard('CORNER MART', 'OPEN LATE', { w: 5.4, h: 0.82, bg: '#f7eed8', accent: '#d94136' });
  extSign.position.set(0, 3.95, 7.72); storeGroup.add(extSign);

  const glassMat = new THREE.MeshBasicMaterial({ color: '#a8dcf0', transparent: true, opacity: 0.18, depthWrite: false, side: THREE.DoubleSide });
  const winL = new THREE.Mesh(new THREE.PlaneGeometry(3.8, 2.4), glassMat); winL.position.set(-3.35, 1.78, 7.5);
  const winR = new THREE.Mesh(new THREE.PlaneGeometry(3.8, 2.4), glassMat); winR.position.set(3.35, 1.78, 7.5);
  storeGroup.add(winL, winR);

  // Glowing OPEN 24 HRS neon inside the right storefront window
  const neonMat = new THREE.MeshBasicMaterial({ map: makeNeonTex(), transparent: true, side: THREE.DoubleSide });
  const neonSign = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 0.47), neonMat);
  neonSign.rotation.y = Math.PI;
  neonSign.position.set(3.35, 2.62, 7.24);
  storeGroup.add(neonSign);

  // Double Entrance Glass Doors (x: -1.22..1.22)
  for (const sx of [-0.62, 0.62]) {
    storeGroup.add(ibox(1.18, 0.12, 0.10, '#cfd6dc', { x: sx, y: 2.90, z: 7.5, thick: 0.008, cast: false }));
    storeGroup.add(ibox(1.18, 0.18, 0.10, '#cfd6dc', { x: sx, y: 0.09, z: 7.5, thick: 0.008, cast: false }));
    const outerX = sx < 0 ? sx - 0.56 : sx + 0.56;
    const innerX = sx < 0 ? -0.025 : 0.025;
    storeGroup.add(ibox(0.08, 2.95, 0.10, '#cfd6dc', { x: outerX, y: 1.48, z: 7.5, thick: 0.008, cast: false }));
    storeGroup.add(ibox(0.035, 2.95, 0.08, '#cfd6dc', { x: innerX, y: 1.48, z: 7.5, thick: 0.006, cast: false }));
    const dg = new THREE.Mesh(new THREE.PlaneGeometry(1.08, 2.65), glassMat);
    dg.position.set(sx, 1.50, 7.5); storeGroup.add(dg);
    storeGroup.add(icyl(0.020, 0.020, 0.42, '#e6b84a', { x: sx * 0.16, y: 1.18, z: 7.42, thick: 0.006 }));
  }

  // WELCOME mat just inside the entrance
  const matMesh = new THREE.Mesh(new THREE.PlaneGeometry(1.7, 0.85), new THREE.MeshBasicMaterial({ map: makeMatTex() }));
  matMesh.rotation.x = -Math.PI / 2;
  matMesh.position.set(0, 0.015, 6.80);
  storeGroup.add(matMesh);

  // Heavy Metal Deadbolt across front entrance doors
  const deadboltGroup = new THREE.Group();
  deadboltGroup.position.set(0, 1.35, 7.38);
  deadboltGroup.add(ibox(0.56, 0.16, 0.08, '#4a525a', { x: 0, y: 0, z: 0, thick: 0.012 }));
  const deadboltBar = ibox(0.48, 0.07, 0.09, '#d94136', { x: -0.18, y: 0, z: -0.04, thick: 0.01 });
  deadboltGroup.add(deadboltBar);
  storeGroup.add(deadboltGroup);

  // =========================================================================
  // FULL-HEIGHT HERMETIC ROLL-DOWN METAL SECURITY SHUTTERS ("sheleter bnd bilkul")!
  // Unrolls from overhead steel drum housing at y=3.20m ALL THE WAY DOWN to y=0.00m (ZERO GAP)!
  // =========================================================================
  storeGroup.add(ibox(10.9, 0.24, 0.24, '#3d4650', { x: 0, y: 3.22, z: 7.31, thick: 0.012 }));

  const shutterWinPivot = new THREE.Group();
  shutterWinPivot.position.set(0, 3.20, 7.32);
  for (const wx of [-3.38, 3.38]) {
    shutterWinPivot.add(ibox(4.06, 3.12, 0.08, '#ffffff', { map: shutterTex, x: wx, y: -1.56, z: 0, thick: 0.014, cast: false }));
    shutterWinPivot.add(ibox(4.10, 0.10, 0.11, '#d9a438', { x: wx, y: -3.15, z: 0, thick: 0.010, cast: false }));
    shutterWinPivot.add(ibox(0.46, 0.06, 0.14, '#242a30', { x: wx, y: -3.08, z: -0.04, thick: 0.008, cast: false }));
  }
  storeGroup.add(shutterWinPivot);

  const shutterDoorPivot = new THREE.Group();
  shutterDoorPivot.position.set(0, 3.20, 7.30);
  shutterDoorPivot.add(ibox(2.74, 3.12, 0.08, '#ffffff', { map: shutterTex, x: 0, y: -1.56, z: 0, thick: 0.014, cast: false }));
  shutterDoorPivot.add(ibox(2.78, 0.10, 0.11, '#d9a438', { x: 0, y: -3.15, z: 0, thick: 0.010, cast: false }));
  storeGroup.add(shutterDoorPivot);

  // =========================================================================
  // FULLY LABELED AISLES (Rick Clips shelf rows with readable product names!)
  // =========================================================================
  const aisleConfigs = [
    { x: -3.2, title: 'AISLE 1', sub: 'SNACKS',   theme: 'snacks' },
    { x: -1.1, title: 'AISLE 2', sub: 'CANNED',   theme: 'canned' },
    { x: 1.0,  title: 'AISLE 3', sub: 'DRINKS',   theme: 'drinks' },
    { x: 3.1,  title: 'AISLE 4', sub: 'SUPPLIES', theme: 'supplies' },
  ];
  const SHELF_PRODUCTS = {
    snacks: [
      ['POTATO CHIPS', { bg: '#c8453a', band: '#7e211a', tag: 'NET 150g' }],
      ['COOKIES',      { bg: '#2f6db3', band: '#1c4676', tag: 'NET 300g' }],
      ['CEREAL',       { bg: '#e0a52e', band: '#a06d12', tag: 'NET 500g' }],
      ['NOODLES',      { bg: '#e07a20', band: '#9c4c0e', tag: 'NET 400g' }],
    ],
    canned: [
      ['TOMATO SOUP',  { bg: '#c8382e', band: '#7e1c16', tag: '400ml' }],
      ['BAKED BEANS',  { bg: '#e08a2e', band: '#9c5610', tag: '400g' }],
      ['CHUNKY TUNA',  { bg: '#2e6db8', band: '#1c4676', tag: '185g' }],
      ['CHILI BEANS',  { bg: '#8f2840', band: '#5c1428', tag: '400g' }],
    ],
    supplies: [
      ['FIRST AID',    { bg: '#f2ede2', band: '#d92822', tag: '12 PC' }],
      ['DETERGENT',    { bg: '#2fa8a0', band: '#1c6e68', tag: '1 L' }],
      ['BATTERIES',    { bg: '#e6b83c', band: '#231a10', tag: 'AA x8' }],
      ['LIGHT BULBS',  { bg: '#f2d9a8', band: '#b8862e', tag: '60W x2' }],
    ],
  };
  const SHELF_BOTTLES = {
    drinks: [
      ['COLA',       { bg: '#b8231e' }],
      ['SODA',       { bg: '#e07820' }],
      ['ENERGY',     { bg: '#3fae4a' }],
      ['PURE WATER', { bg: '#9fd0ea' }],
    ],
  };
  const shelfBoxGeo = new THREE.BoxGeometry(0.17, 0.28, 0.24);
  const shelfBottleGeo = new THREE.CylinderGeometry(0.062, 0.062, 0.32, 12);
  const dummy = new THREE.Object3D();
  const cTmp = new THREE.Color();
  const rng = P.rng(101);

  aisleConfigs.forEach((ac, idx) => {
    const g = new THREE.Group();
    g.position.set(ac.x, 0, -1.6);
    g.add(ibox(0.14, 2.15, 5.4, '#3e4f5e', { y: 1.08 }));
    for (let lv = 0; lv < 4; lv++) {
      g.add(ibox(0.82, 0.06, 5.4, '#dce2e6', { y: 0.25 + lv * 0.56, thick: 0.008 }));
      // yellow SALE price rail on both shelf front edges
      for (const side of [-1, 1]) {
        g.add(ibox(0.035, 0.055, 5.32, '#ffffff', { map: priceStripTex, x: side * 0.437, y: 0.30 + lv * 0.56, thick: 0, edges: false, cast: false }));
      }
    }
    const sgn = makeSignBoard(ac.title, ac.sub, { w: 1.35, h: 0.42, accent: idx === 3 ? '#d94136' : '#2f6db3' });
    sgn.position.set(0, 2.85, 2.2);
    g.add(sgn);

    // labeled product rows on both sides of every level (8 per row)!
    for (const side of [-1, 1]) {
      for (let lv = 0; lv < 4; lv++) {
        let mat, geo;
        if (ac.theme === 'drinks') {
          const [nm, op] = SHELF_BOTTLES.drinks[lv];
          mat = toon('#ffffff', makeBottleTex(nm, op));
          geo = shelfBottleGeo;
        } else {
          const [nm, op] = SHELF_PRODUCTS[ac.theme][lv];
          mat = toon('#ffffff', makeShelfBoxTex(nm, op));
          geo = shelfBoxGeo;
        }
        const im = new THREE.InstancedMesh(geo, mat, 8);
        for (let k = 0; k < 8; k++) {
          const z = -2.03 + k * 0.58 + (rng() - 0.5) * 0.03;
          const y = ac.theme === 'drinks' ? 0.44 + lv * 0.56 : 0.42 + lv * 0.56;
          dummy.position.set(side * 0.245, y, z);
          dummy.rotation.set(0, (rng() - 0.5) * 0.1, 0);
          dummy.updateMatrix();
          im.setMatrixAt(k, dummy.matrix);
          const jitter = 0.9 + rng() * 0.1;
          im.setColorAt(k, cTmp.setRGB(jitter, jitter, jitter));
        }
        im.instanceMatrix.needsUpdate = true;
        im.instanceColor.needsUpdate = true;
        g.add(im);
      }
    }
    storeGroup.add(g);
  });

  // Hanging 2 FOR $3 promo sign mid-store
  const promoTex = makePosterTex('2 FOR', '$3 SNACKS & DRINKS', { bg: '#f2ead8', accent: '#c8382e', art: 'tag' });
  const promoMesh = new THREE.Mesh(
    new THREE.PlaneGeometry(1.3, 0.95),
    new THREE.MeshBasicMaterial({ map: promoTex, side: THREE.DoubleSide })
  );
  promoMesh.position.set(-1.1, 3.18, 1.6);
  storeGroup.add(promoMesh);
  for (const sx of [-0.5, 0.5]) {
    storeGroup.add(ibox(0.02, 0.26, 0.02, '#5a5f66', { x: -1.1 + sx, y: 3.52, z: 1.6, thick: 0, edges: false, cast: false }));
  }

  // Wall promo posters (FRESH COFFEE / SLUSHIE / BIG SALE)
  const posterDefs = [
    [makePosterTex('FRESH', 'COFFEE $2', { art: 'cup' }),            -5.34, 2.30, 2.30,  Math.PI / 2],
    [makePosterTex('SLUSHIE', '2 FOR $3', { art: 'slush' }),         -5.34, 2.30, 4.80,  Math.PI / 2],
    [makePosterTex('BIG SALE', 'UP TO 50% OFF', { art: 'tag' }),      5.34, 2.35, 3.00, -Math.PI / 2],
  ];
  for (const [tex, px, py, pz, ry] of posterDefs) {
    const pm = new THREE.Mesh(new THREE.PlaneGeometry(0.72, 1.08), new THREE.MeshBasicMaterial({ map: tex }));
    pm.position.set(px, py, pz);
    pm.rotation.y = ry;
    storeGroup.add(pm);
  }

  // Left-wall Glass Refrigerators STOCKED with labeled drinks (COLA/SODA/MILK/ENERGY)!
  const fridgeLights = [];
  const fridgeStockDefs = [
    { fz: -4.0, rows: [['COLA', { bg: '#b8231e' }], ['SODA', { bg: '#e07820' }], ['MILK', { bg: '#e8e6df' }]] },
    { fz: -1.1, rows: [['ENERGY', { bg: '#3fae4a' }], ['COLA', { bg: '#b8231e' }], ['SODA', { bg: '#e07820' }]] },
  ];
  const fridgeBottleGeo = new THREE.CylinderGeometry(0.058, 0.058, 0.34, 12);
  for (const fd of fridgeStockDefs) {
    const fg = new THREE.Group();
    fg.position.set(-5.02, 0, fd.fz);
    fg.add(ibox(0.42, 2.55, 2.35, '#2d3742', { x: -0.16, y: 1.28 }));
    fg.add(ibox(0.46, 0.20, 2.38, '#3b4a59', { x: 0.08, y: 2.46 }));
    fg.add(ibox(0.46, 0.24, 2.38, '#3b4a59', { x: 0.08, y: 0.12 }));
    const glowMat = new THREE.MeshBasicMaterial({ color: '#c8f4ff' });
    const backGlow = new THREE.Mesh(new THREE.PlaneGeometry(2.18, 2.10), glowMat);
    backGlow.rotation.y = Math.PI / 2; backGlow.position.set(0.07, 1.28, 0);
    fg.add(backGlow);
    fridgeLights.push(glowMat);
    // glass shelves + 5 labeled bottles per row
    fd.rows.forEach(([nm, op], row) => {
      const sy = 0.55 + row * 0.60;
      fg.add(ibox(0.30, 0.025, 2.05, '#bfe0ea', { x: 0.10, y: sy - 0.175, thick: 0.004, edges: false }));
      const im = new THREE.InstancedMesh(fridgeBottleGeo, toon('#ffffff', makeBottleTex(nm, op)), 5);
      for (let k = 0; k < 5; k++) {
        dummy.position.set(0.10, sy, -0.88 + k * 0.44);
        dummy.rotation.set(0, 0, 0);
        dummy.updateMatrix();
        im.setMatrixAt(k, dummy.matrix);
      }
      im.instanceMatrix.needsUpdate = true;
      fg.add(im);
    });
    storeGroup.add(fg);
    const fhdr = makeSignBoard('COLD DRINKS', 'GRAB & GO', { w: 2.2, h: 0.32, bg: '#16222e', fg: '#ffffff', accent: '#2f6db3' });
    fhdr.rotation.y = Math.PI / 2;
    fhdr.position.set(-4.86, 2.72, fd.fz);
    storeGroup.add(fhdr);
  }

  // =========================================================================
  // CHECKOUT COUNTER ZONE: sleek POS register + scanner + labeled V3 rations!
  // (Everything sits LEFT or RIGHT of YOU's lane at x=3.10 so YOU reads waist-up!)
  // =========================================================================
  const counterGroup = new THREE.Group();
  counterGroup.position.set(3.1, 0, 4.1);
  counterGroup.add(ibox(2.4, 1.02, 0.95, '#8a5a3b', { map: woodTex, y: 0.51 }));
  counterGroup.add(ibox(2.5, 0.09, 1.05, '#e8dfd0', { y: 1.04, thick: 0.012 }));
  // Store landline desk phone with red blinking ring lamp
  counterGroup.add(ibox(0.26, 0.12, 0.22, '#242930', { x: -0.32, y: 1.14, z: 0.18, thick: 0.008 }));
  storeGroup.add(counterGroup);

  // --- Sleek POS register w/ touchscreen, receipt, scanner, card reader (LEFT of YOU) ---
  const posScreenMat = new THREE.MeshBasicMaterial({ map: makePosScreenTex() });
  const posG = new THREE.Group();
  posG.position.set(2.25, 1.09, 4.05);
  posG.add(ibox(0.46, 0.20, 0.34, '#33383f', { y: 0.10 }));
  const posScreenG = new THREE.Group();
  posScreenG.position.set(0, 0.22, -0.10);
  posScreenG.rotation.x = -0.40;
  posScreenG.add(ibox(0.42, 0.32, 0.035, '#22262c', { thick: 0.010 }));
  const posScr = new THREE.Mesh(new THREE.PlaneGeometry(0.36, 0.26), posScreenMat);
  posScr.position.z = 0.021;
  posScreenG.add(posScr);
  posG.add(posScreenG);
  posG.add(ibox(0.11, 0.05, 0.16, '#ece8da', { x: -0.06, y: 0.245, z: 0.10, rz: 0.18, thick: 0.004, edges: false })); // receipt
  posG.add(ibox(0.34, 0.015, 0.10, '#c9ced4', { x: 0.10, y: 0.205, z: 0.12, thick: 0.003, edges: false })); // keypad tray
  storeGroup.add(posG);
  // barcode scanner + card terminal on the front counter row
  storeGroup.add(ibox(0.15, 0.085, 0.17, '#2b3037', { x: 2.78, y: 1.145, z: 3.80, thick: 0.008 }));
  const scanLine = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.012, 0.012), new THREE.MeshBasicMaterial({ color: '#ff4438' }));
  scanLine.position.set(2.78, 1.19, 3.72);
  storeGroup.add(scanLine);
  storeGroup.add(ibox(0.12, 0.10, 0.14, '#3a4046', { x: 2.60, y: 1.16, z: 3.78, rx: -0.2, thick: 0.008 }));
  // impulse-buy candy box with mini chocolate bars
  const candyBox = new THREE.Group();
  candyBox.position.set(2.08, 1.09, 3.84);
  candyBox.add(ibox(0.30, 0.11, 0.22, '#c8382e', { y: 0.055, thick: 0.008 }));
  for (let i = 0; i < 6; i++) {
    candyBox.add(ibox(0.085, 0.028, 0.05, '#5c3a22', { x: -0.09 + (i % 3) * 0.09, y: 0.125 + Math.floor(i / 3) * 0.03, z: -0.05 + Math.floor(i / 3) * 0.07, ry: 0.2, thick: 0.003, edges: false }));
  }
  storeGroup.add(candyBox);

  // --- V3 EXACT RATIONS, all clearly LABELED (RIGHT of YOU, flashlight hero props!) ---
  // "Two bottles of water, a few cans, one chocolate bar, a first aid kit"
  const rationGroup = new THREE.Group();
  rationGroup.position.set(3.1, 1.09, 4.1);
  const capSilver = toon('#c9ced4');
  const mkLabeledCan = (name, op, rx, rz) => {
    const m = new THREE.Mesh(
      new THREE.CylinderGeometry(0.075, 0.075, 0.19, 16),
      [toon('#ffffff', makeWrapLabelTex(name, op)), capSilver, capSilver]
    );
    m.position.set(rx, 0.095, rz);
    return ink(m, 0.008, true, 42);
  };
  // Two bottles of PURE WATER
  for (const [bx, bz] of [[0.34, 0.20], [0.52, 0.08]]) {
    rationGroup.add(icyl(0.072, 0.072, 0.34, '#ffffff', { map: makeBottleTex('PURE WATER', { bg: '#bfe6f8', fg: '#1e5aa8' }), x: bx, y: 0.17, z: bz, seg: 14, thick: 0.008 }));
    rationGroup.add(icyl(0.034, 0.034, 0.05, '#1e5aa8', { x: bx, y: 0.365, z: bz, seg: 10, thick: 0.005 }));
  }
  // A few labeled cans: TOMATO SOUP / BAKED BEANS / CHUNKY TUNA
  rationGroup.add(mkLabeledCan('TOMATO SOUP', { bg: '#c8382e', band: '#7e1c16', sub: '400ml' }, 0.78, 0.20));
  rationGroup.add(mkLabeledCan('BAKED BEANS', { bg: '#e08a2e', band: '#9c5610', sub: '400g' }, 0.90, 0.05));
  rationGroup.add(mkLabeledCan('CHUNKY TUNA', { bg: '#2e6db8', band: '#1c4676', sub: '185g' }, 0.70, -0.12));
  // One CHOCOLATE bar (foil-wrapped, big readable label on top!)
  const chocoWrap = toon('#6b4326');
  const chocoTop = toon('#ffffff', makeChocoTex());
  const choco = new THREE.Mesh(
    new THREE.BoxGeometry(0.24, 0.05, 0.115),
    [chocoWrap, chocoWrap, chocoTop, chocoWrap, chocoWrap, chocoWrap]
  );
  choco.position.set(0.38, 0.026, -0.18);
  choco.rotation.y = 0.2;
  rationGroup.add(ink(choco, 0.006, true));
  // FIRST AID KIT (white box + bold red cross + label)
  const fakFace = toon('#ffffff', makeFakTex());
  const fak = new THREE.Group();
  fak.position.set(0.96, 0, -0.16);
  const fakBox = new THREE.Mesh(
    new THREE.BoxGeometry(0.36, 0.24, 0.26),
    [toon('#f7f5f0'), toon('#f7f5f0'), toon('#f7f5f0'), toon('#f7f5f0'), toon('#f7f5f0'), fakFace]
  );
  fakBox.position.y = 0.12;
  fak.add(ink(fakBox, 0.010, true));
  fak.add(ibox(0.14, 0.045, 0.27, '#d92822', { y: 0.255, thick: 0.004, edges: false }));
  storeGroup.add(rationGroup);
  rationGroup.add(fak);

  // Survival Backpack on counter (for packing supplies at 169.7s!)
  const counterBackpack = new THREE.Group();
  counterBackpack.position.set(2.45, 1.28, 4.10);
  counterBackpack.add(ibox(0.38, 0.44, 0.24, '#2d3530', { thick: 0.012 }));
  counterBackpack.add(ibox(0.30, 0.22, 0.08, '#3f4a43', { y: -0.06, z: 0.14, thick: 0.008 }));
  storeGroup.add(counterBackpack);

  // --- BACK COUNTER: cabinet + COFFEE brewer + twin-bowl SLUSHIE + CCTV monitor ---
  const backCounter = new THREE.Group();
  backCounter.position.set(-0.55, 0, -7.10);
  backCounter.add(ibox(3.3, 0.92, 0.5, '#8a5a3b', { map: woodTex, y: 0.46 }));
  backCounter.add(ibox(3.4, 0.06, 0.56, '#e8dfd0', { y: 0.95, thick: 0.008 }));
  storeGroup.add(backCounter);
  // Coffee brewer with two glass pots
  const coffee = new THREE.Group();
  coffee.position.set(-1.55, 0.98, -7.08);
  coffee.add(ibox(0.34, 0.42, 0.28, '#3a2e28', { y: 0.21, thick: 0.010 }));
  coffee.add(ibox(0.30, 0.10, 0.20, '#221a16', { y: 0.46, thick: 0.006 }));
  for (const px of [-0.08, 0.08]) {
    coffee.add(icyl(0.052, 0.052, 0.13, '#c8dbe4', { x: px, y: 0.065, z: 0.16, seg: 10, thick: 0.004 }));
    coffee.add(icyl(0.045, 0.045, 0.07, '#5c3a22', { x: px, y: 0.05, z: 0.16, seg: 10, thick: 0.003, edges: false }));
  }
  const coffeeLbl = makeSignBoard('COFFEE', 'FRESH $2', { w: 0.44, h: 0.15, bg: '#3a2e28', fg: '#f2e3bd', accent: '#e0a52e' });
  coffeeLbl.position.set(0, 0.30, 0.15);
  coffee.add(coffeeLbl);
  storeGroup.add(coffee);
  // Twin-bowl slushie machine
  const slushie = new THREE.Group();
  slushie.position.set(0.40, 0.98, -7.05);
  slushie.add(ibox(0.52, 0.56, 0.38, '#d8dce2', { y: 0.28, thick: 0.010 }));
  slushie.add(icyl(0.30, 0.30, 0.14, '#33383f', { y: 0.03, seg: 16, thick: 0.006 })); // drip tray
  const bowlRed = new THREE.Mesh(new THREE.SphereGeometry(0.145, 14, 12), toon('#d94136'));
  bowlRed.position.set(-0.12, 0.66, 0.02);
  const bowlBlue = new THREE.Mesh(new THREE.SphereGeometry(0.145, 14, 12), toon('#2f6db3'));
  bowlBlue.position.set(0.12, 0.66, 0.02);
  slushie.add(ink(bowlRed, 0.008, true), ink(bowlBlue, 0.008, true));
  for (const px of [-0.12, 0.12]) {
    slushie.add(icyl(0.035, 0.035, 0.07, '#22262c', { x: px, y: 0.52, z: 0.02, thick: 0.004, edges: false }));
    slushie.add(icyl(0.022, 0.022, 0.06, '#9aa2aa', { x: px, y: 0.10, z: 0.10, thick: 0.003, edges: false }));
  }
  const slushLbl = makeSignBoard('SLUSHIE', '2 FOR $3', { w: 0.5, h: 0.16, bg: '#d94136', fg: '#ffffff', accent: '#7e1c16' });
  slushLbl.position.set(0, 0.40, 0.20);
  slushie.add(slushLbl);
  storeGroup.add(slushie);
  // CCTV monitor on wall-mounted arm above back counter
  const cctvScreenMat = new THREE.MeshBasicMaterial({ map: makeCctvTex() });
  const cctv = new THREE.Group();
  cctv.position.set(-0.55, 2.02, -7.18);
  cctv.rotation.x = 0.26;
  cctv.add(ibox(0.40, 0.30, 0.12, '#22262c', { thick: 0.008 }));
  const cctvScr = new THREE.Mesh(new THREE.PlaneGeometry(0.34, 0.22), cctvScreenMat);
  cctvScr.position.z = 0.065;
  cctv.add(cctvScr);
  storeGroup.add(cctv);
  storeGroup.add(ibox(0.05, 0.42, 0.05, '#3a4046', { x: -0.55, y: 2.32, z: -7.24, thick: 0.006, edges: false }));

  // =========================================================================
  // 2. OUTSIDE 3D STREET & INTERSECTION (`streetGroup`, z: 7.6..36)
  // =========================================================================
  const streetGroup = new THREE.Group();
  root.add(streetGroup);
  streetGroup.add(ibox(48, 0.16, 3.4, '#ffffff', { map: paverTex, x: 0, y: 0.04, z: 9.2, cast: false })); // V6 pavers
  streetGroup.add(ibox(48, 0.16, 2.6, '#ffffff', { map: paverTex, x: 0, y: 0.04, z: 23.3, cast: false })); // V6 far sidewalk
  const road = new THREE.Mesh(new THREE.PlaneGeometry(54, 28), toon('#ffffff', asphaltTex));
  road.rotation.x = -Math.PI / 2; road.position.set(0, -0.02, 22); road.receiveShadow = true;
  streetGroup.add(road);
  for (let i = -4; i <= 4; i++) {
    streetGroup.add(ibox(0.55, 0.02, 3.2, '#eceae2', { x: 6.5 + i * 1.1, y: 0.0, z: 15.5, thick: 0, edges: false, cast: false }));
    streetGroup.add(ibox(1.8, 0.02, 0.22, '#e6b83c', { x: i * 4.2, y: 0.0, z: 16.5, thick: 0, edges: false, cast: false }));
  }
  const streetBulbs = [];
  for (const lz of [10.4, 24.5]) {
    const lxs = lz === 10.4 ? [-6.5, 6.5] : [-13.5, 13.5]; // V6: two extra lamps deep down the street
    for (const lx of lxs) {
      streetGroup.add(icyl(0.08, 0.11, 4.6, '#343b42', { x: lx, y: 2.3, z: lz }));
      streetGroup.add(ibox(0.9, 0.12, 0.24, '#343b42', { x: lx + (lx < 0 ? 0.35 : -0.35), y: 4.55, z: lz }));
      const bm = new THREE.MeshBasicMaterial({ color: '#ffe39e' });
      const bulb = new THREE.Mesh(new THREE.SphereGeometry(0.18, 10, 8), bm);
      bulb.position.set(lx + (lx < 0 ? 0.65 : -0.65), 4.42, lz);
      streetGroup.add(bulb); streetBulbs.push(bm);
    }
  }
  // V6: warm sodium lamp pools on the asphalt (dusk window only, before the grid dies)
  const streetGlow = [];
  {
    const glowT = makeGlowTex();
    for (const gl of [[-6.5, 10.4], [6.5, 10.4], [-13.5, 24.5], [13.5, 24.5]]) {
      const gm = new THREE.MeshBasicMaterial({ map: glowT, color: '#ffbb60', transparent: true, opacity: 0.30, depthWrite: false, blending: THREE.AdditiveBlending });
      const glow = new THREE.Mesh(new THREE.PlaneGeometry(4.6, 4.6), gm);
      glow.rotation.x = -Math.PI / 2; glow.position.set(gl[0], 0.035, gl[1]);
      streetGroup.add(glow); streetGlow.push(gm);
    }
  }
  // Fire hydrant + sidewalk trash bin (street dressing)
  const hydrant = new THREE.Group();
  hydrant.position.set(4.6, 0, 8.75);
  hydrant.add(icyl(0.13, 0.16, 0.5, '#c8382e', { y: 0.25, seg: 12 }));
  hydrant.add(new THREE.Mesh(new THREE.SphereGeometry(0.13, 12, 10), toon('#c8382e')).translateY(0.52));
  for (const hz of [Math.PI / 2, -Math.PI / 2]) {
    const cap = icyl(0.05, 0.05, 0.1, '#c8382e', { y: 0.30, seg: 10, thick: 0.004, edges: false });
    cap.position.x = Math.cos(hz) * 0.16; cap.position.z = Math.sin(hz) * 0.16;
    hydrant.add(cap);
  }
  streetGroup.add(hydrant);
  streetGroup.add(icyl(0.24, 0.20, 0.72, '#3f5a46', { x: -4.35, y: 0.36, z: 8.85, seg: 14 }));
  streetGroup.add(icyl(0.26, 0.26, 0.06, '#2d4234', { x: -4.35, y: 0.75, z: 8.85, seg: 14, thick: 0.006, edges: false }));

  // Across-street buildings with LABELED STOREFRONTS + striped awnings!
  const bCols = ['#c88864', '#56728f', '#b89a67', '#7b5864', '#4d667a', '#9c624c'];
  const shopWindows = [];   // V6: act-driven window glow (dusk subset lit -> grid death -> dead dawn)
  const winRng = P.rng(131);
  const shops = [
    { name: 'PHARMACY', sub: 'OPEN 24 HRS', accent: '#2f7d4f', cross: true,  awning: '#2f7d4f' },
    { name: 'DINER',    sub: 'OPEN LATE',   accent: '#c84538', cross: false, awning: '#c84538' },
    { name: 'BANK',     sub: 'CITY BANK',   accent: '#1e4d78', cross: false, awning: null,     columns: true },
    { name: 'PIZZA',    sub: 'HOT & FRESH', accent: '#b8352a', cross: false, awning: '#b8352a' },
    { name: 'LAUNDRY',  sub: 'WASH & GO',   accent: '#2f6db3', cross: false, awning: '#2f6db3' },
    { name: 'HARDWARE', sub: 'TOOLS & MORE',accent: '#5a5f4a', cross: false, awning: '#5a5f4a' },
  ];
  for (let i = 0; i < 6; i++) {
    const bx = -18 + i * 7.2;
    const bh = 8.5 + (i % 3) * 3.2;
    const sh = shops[i];
    streetGroup.add(ibox(6.6, bh, 5.5, bCols[i], { x: bx, y: bh / 2, z: 27.5 }));
    streetGroup.add(ibox(6.9, 0.38, 5.8, '#3d3538', { x: bx, y: bh + 0.15, z: 27.5 }));
    // Ground-floor shopfront windows across the street
    streetGroup.add(ibox(4.8, 2.2, 0.16, '#1f2833', { x: bx, y: 1.35, z: 24.70 }));
    for (let r = 0; r < 3; r++) {
      for (let c = -1; c <= 1; c++) {
        const wm = new THREE.MeshBasicMaterial({ color: '#2c394f' });
        const wMesh = new THREE.Mesh(new THREE.PlaneGeometry(0.95, 1.35), wm);
        wMesh.position.set(bx + c * 1.85, 3.6 + r * 2.1, 24.72);
        wMesh.rotation.y = Math.PI;
        streetGroup.add(wMesh);
        shopWindows.push({ mat: wm, lit: winRng() < 0.42 ? 1 : 0, dayVar: 0.35 + 0.65 * winRng() });
      }
    }
    // Labeled storefront sign board
    const sign = makeSignBoard(sh.name, sh.sub, { w: 3.6, h: 0.62, bg: '#f4ead2', fg: '#2b1d20', accent: sh.accent });
    sign.position.set(bx, 3.02, 24.66);
    sign.rotation.y = Math.PI;
    streetGroup.add(sign);
    // Striped awning over the shopfront
    if (sh.awning) {
      const aw = ibox(4.7, 0.06, 1.25, '#ffffff', { map: makeAwningTex(sh.awning, '#f2ead8'), x: bx, y: 2.52, z: 25.28, rx: -0.30, thick: 0.006, cast: false });
      streetGroup.add(aw);
    }
    if (sh.cross) { // glowing pharmacy cross
      streetGroup.add(ibox(0.18, 1.05, 0.10, '#2fae64', { x: bx, y: 4.45, z: 24.62, thick: 0.008 }));
      streetGroup.add(ibox(0.75, 0.18, 0.10, '#2fae64', { x: bx, y: 4.62, z: 24.62, thick: 0.008 }));
    }
    if (sh.columns) { // bank columns
      for (const cx of [-2.3, 0, 2.3]) {
        streetGroup.add(icyl(0.24, 0.28, 2.6, '#ddd8ca', { x: bx + cx, y: 1.3, z: 24.95, seg: 14, thick: 0.010 }));
      }
    }
  }

  // Sunrise Broken Shopfront Glass Shards across street (`sunriseDamageGroup`, visible at t >= 145.9s!)
  const sunriseDamageGroup = new THREE.Group();
  for (let i = 0; i < 5; i++) {
    const bx = -10.8 + i * 5.4;
    for (let s = 0; s < 5; s++) {
      const sh = new THREE.Mesh(new THREE.ConeGeometry(0.22, 0.55, 3), toon('#9fd4eb'));
      sh.position.set(bx - 1.2 + s * 0.6, 0.55 + (s % 2) * 1.15, 24.58);
      sh.rotation.z = s * 1.1;
      sunriseDamageGroup.add(ink(sh, 0.01, true));
    }
  }
  streetGroup.add(sunriseDamageGroup);

  const abandonedCar = makeCar('#b9bec6', 'sedan', false);  // silver family sedan
  const swerveCar    = makeCar('#c84538', 'sport', false);  // red sport coupe w/ wing
  const patrolCar    = makeCar('#e9ecf0', 'suv', true);     // white patrol SUV w/ strobes
  // Police cruiser lightbar + door decal on patrolCar!
  patrolCar.add(ibox(0.45, 0.14, 0.22, '#ff2d24', { x: -0.24, y: 1.47, z: -0.1, thick: 0.008 }));
  patrolCar.add(ibox(0.45, 0.14, 0.22, '#2478ff', { x:  0.24, y: 1.47, z: -0.1, thick: 0.008 }));
  const polDecal = makeSignBoard('POLICE', 'UNIT 12', { w: 0.85, h: 0.24, bg: '#e8ecf2', fg: '#1f2d42', accent: '#1f2d42' });
  polDecal.rotation.y = Math.PI / 2;
  polDecal.position.set(0.96, 0.68, -0.2);
  patrolCar.add(polDecal);
  const parkedCarA = makeCar('#3f6f52', 'sedan', false); // V6: forest-green curb sedan (normal day)
  parkedCarA.position.set(-12.5, 0, 12.30); parkedCarA.rotation.y = 0.16;
  const parkedCarB = makeCar('#8a6d3b', 'suv', false);   // V6: bronze SUV parked across the way
  parkedCarB.position.set(13.8, 0, 12.65); parkedCarB.rotation.y = -0.10;
  const trafficCar = makeCar('#2e4d76', 'sedan', false); // V6: ordinary passing car (aerial opening only)
  streetGroup.add(abandonedCar, swerveCar, patrolCar, parkedCarA, parkedCarB, trafficCar);

  // =========================================================================
  // 3. BACK STORAGE CORRIDOR & PEEP-WINDOW ALLEY DOOR (`backGroup`, z: -7.6..-16.5)
  // =========================================================================
  const backGroup = new THREE.Group();
  root.add(backGroup);
  const backFloor = new THREE.Mesh(new THREE.PlaneGeometry(5.0, 9.2), toon('#ffffff', concreteTex));
  backFloor.rotation.x = -Math.PI / 2; backFloor.position.set(3.0, 0.005, -12.1);
  backGroup.add(backFloor);
  const backCeil = new THREE.Mesh(new THREE.PlaneGeometry(5.0, 9.2), toon('#535860'));
  backCeil.rotation.x = Math.PI / 2; backCeil.position.set(3.0, 3.6, -12.1);
  backGroup.add(backCeil);

  backGroup.add(ibox(0.24, 3.6, 9.2, '#7d848c', { map: concreteTex, x: 0.6, y: 1.8, z: -12.1 }));
  backGroup.add(ibox(0.24, 3.6, 9.2, '#7d848c', { map: concreteTex, x: 5.4, y: 1.8, z: -12.1 }));
  backGroup.add(ibox(1.3, 3.6, 0.24, '#6e757d', { x: 1.25, y: 1.8, z: -11.5 }));
  backGroup.add(ibox(1.7, 3.6, 0.24, '#6e757d', { x: 4.55, y: 1.8, z: -11.5 }));
  backGroup.add(ibox(1.8, 0.95, 0.24, '#6e757d', { x: 2.8, y: 3.12, z: -11.5 }));

  const emergBulbMat = new THREE.MeshBasicMaterial({ color: '#ff5238' });
  const emergBulb = new THREE.Mesh(new THREE.SphereGeometry(0.15, 12, 10), emergBulbMat);
  emergBulb.position.set(2.8, 3.38, -9.6);
  backGroup.add(ibox(0.36, 0.10, 0.36, '#33383e', { x: 2.8, y: 3.52, z: -9.6 }), emergBulb);

  // Storage shelves + LABELED stock cartons
  backGroup.add(ibox(1.2, 0.9, 1.1, '#b88652', { x: 4.45, y: 0.45, z: -13.6 }));
  backGroup.add(ibox(0.95, 0.75, 0.95, '#a87644', { x: 4.45, y: 1.28, z: -13.6, ry: 0.15 }));
  backGroup.add(ibox(1.1, 0.85, 1.0, '#c2915c', { x: 1.45, y: 0.43, z: -14.2 }));
  const cartonTexes = [
    makeShelfBoxTex('SNACKS', { bg: '#c8453a', band: '#7e211a', tag: '24 PACK' }),
    makeShelfBoxTex('DRINKS', { bg: '#2f6db3', band: '#1c4676', tag: '12 PACK' }),
    makeShelfBoxTex('CANNED', { bg: '#e08a2e', band: '#9c5610', tag: '24 PACK' }),
  ];
  const cartonMat = cartonTexes.map((tx) => toon('#c8a06a', tx));
  const carton1 = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.34, 0.4), cartonMat[0]);
  carton1.position.set(4.45, 1.28, -13.55); carton1.rotation.y = 0.15;
  const carton2 = new THREE.Mesh(new THREE.BoxGeometry(0.46, 0.3, 0.38), cartonMat[1]);
  carton2.position.set(1.45, 0.90, -14.2); carton2.rotation.y = -0.2;
  const carton3 = new THREE.Mesh(new THREE.BoxGeometry(0.44, 0.28, 0.36), cartonMat[2]);
  carton3.position.set(4.42, 0.62, -14.85); carton3.rotation.y = 0.42;
  backGroup.add(ink(carton1, 0.008, true), ink(carton2, 0.008, true), ink(carton3, 0.008, true));
  // corridor signage
  const staffSign = makeSignBoard('STAFF ONLY', 'DELIVERIES', { w: 0.95, h: 0.28, bg: '#e8b83c', fg: '#231a10', accent: '#231a10' });
  staffSign.rotation.y = Math.PI / 2;
  staffSign.position.set(0.74, 2.20, -12.4);
  backGroup.add(staffSign);

  // Back Wall (z = -16.4) + Heavy Steel/Wood Back Delivery Door with Tiny Peep Window
  backGroup.add(ibox(1.4, 3.6, 0.28, '#6e757d', { map: concreteTex, x: 1.3, y: 1.8, z: -16.4 }));
  backGroup.add(ibox(1.8, 3.6, 0.28, '#6e757d', { map: concreteTex, x: 4.5, y: 1.8, z: -16.4 }));
  backGroup.add(ibox(1.6, 0.95, 0.28, '#6e757d', { x: 2.8, y: 3.12, z: -16.4 }));

  const alleyBackdrop = new THREE.Mesh(new THREE.PlaneGeometry(6.5, 4.5), new THREE.MeshBasicMaterial({ color: '#0d1522' }));
  alleyBackdrop.position.set(2.8, 2.0, -18.8);
  backGroup.add(alleyBackdrop);

  // Hinged Back Door Pivot (x = 2.04, z = -16.32): rattles on knocks AND swings open at 176.1s!
  // Peep window center at local x = 0.76 -> world x = 2.80, y = 1.55m (ALIGNED with the mimic's face!)
  const backDoorPivot = new THREE.Group();
  backDoorPivot.position.set(2.04, 0, -16.32);
  backGroup.add(backDoorPivot);
  backDoorPivot.add(ibox(1.52, 1.32, 0.14, '#545e68', { x: 0.76, y: 0.66, z: 0 }));   // lower steel panel
  backDoorPivot.add(ibox(1.52, 0.90, 0.14, '#545e68', { x: 0.76, y: 2.30, z: 0 }));   // upper steel panel
  backDoorPivot.add(ibox(0.46, 0.50, 0.14, '#545e68', { x: 0.23, y: 1.55, z: 0 }));   // left stile
  backDoorPivot.add(ibox(0.46, 0.50, 0.14, '#545e68', { x: 1.29, y: 1.55, z: 0 }));   // right stile
  // Tiny wire-mesh glass peep window (0.60m x 0.42m at y=1.55m — right at eye height!)
  const peepPane = new THREE.Mesh(
    new THREE.PlaneGeometry(0.58, 0.42),
    new THREE.MeshBasicMaterial({ color: '#7da0b8', transparent: true, opacity: 0.30, depthWrite: false, side: THREE.DoubleSide })
  );
  peepPane.position.set(0.76, 1.55, 0.02);
  backDoorPivot.add(peepPane);
  for (const wx of [-0.15, 0, 0.15]) {
    backDoorPivot.add(ibox(0.012, 0.42, 0.02, '#2d3338', { x: 0.76 + wx, y: 1.55, z: 0.03, thick: 0, edges: false }));
  }
  backDoorPivot.add(ibox(0.22, 0.10, 0.10, '#d94136', { x: 1.34, y: 1.22, z: 0.09, thick: 0.008 })); // deadbolt latch

  // =========================================================================
  // 4. EXTERIOR NARROW BRICK DELIVERY ALLEY & STATION ENTRANCE (`alleyGroup`, z: -17..-38)
  // =========================================================================
  const alleyGroup = new THREE.Group();
  root.add(alleyGroup);
  const alleyFloor = new THREE.Mesh(new THREE.PlaneGeometry(5.6, 22.0), toon('#ffffff', asphaltTexAlley));
  alleyFloor.rotation.x = -Math.PI / 2; alleyFloor.position.set(0, 0.0, -27.5);
  alleyGroup.add(alleyFloor);
  // Tall narrow brick canyon walls (x = -2.6 and x = +2.6)
  alleyGroup.add(ibox(0.32, 6.2, 22.0, '#ffffff', { map: brickTex, x: -2.65, y: 3.1, z: -27.5 }));
  alleyGroup.add(ibox(0.32, 6.2, 22.0, '#ffffff', { map: brickTex, x:  2.65, y: 3.1, z: -27.5 }));
  // Green steel dumpster with WASTE label, crates & wall pipes for rich depth
  alleyGroup.add(ibox(1.35, 1.25, 2.1, '#335941', { x: -1.75, y: 0.63, z: -23.5 }));
  alleyGroup.add(ibox(1.40, 0.14, 2.16, '#1f2422', { x: -1.75, y: 1.32, z: -23.5 }));
  const wasteLbl = makeSignBoard('WASTE', 'NO FOOD', { w: 0.85, h: 0.24, bg: '#335941', fg: '#e8f2ea', accent: '#1f2422' });
  wasteLbl.rotation.y = Math.PI / 2;
  wasteLbl.position.set(-1.06, 0.78, -23.5);
  alleyGroup.add(wasteLbl);
  alleyGroup.add(icyl(0.07, 0.07, 18.0, '#5a626a', { x: 2.42, y: 3.4, z: -26.5, rx: Math.PI / 2 }));
  // wet puddle + labeled crates
  const puddle = new THREE.Mesh(
    new THREE.CircleGeometry(0.85, 18),
    new THREE.MeshBasicMaterial({ color: '#141c26', transparent: true, opacity: 0.55 })
  );
  puddle.rotation.x = -Math.PI / 2; puddle.position.set(0.6, 0.012, -26.4);
  puddle.scale.set(1.3, 0.8, 1);
  alleyGroup.add(puddle);
  const crateTex = makeShelfBoxTex('STOCK', { bg: '#b88652', band: '#7a5230', tag: 'HEAVY' });
  for (const [cx, cy, cz, ry] of [[-1.62, 0.26, -25.65, 0.18], [-1.25, 0.21, -25.95, -0.3]]) {
    const crate = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.42, 0.42), toon('#c8a06a', crateTex));
    crate.position.set(cx, cy, cz); crate.rotation.y = ry;
    alleyGroup.add(ink(crate, 0.008, true));
  }
  // Fire-escape ladder up the right brick wall
  for (const lx of [2.40, 2.40]) {
    alleyGroup.add(icyl(0.024, 0.024, 4.6, '#3a4046', { x: lx, y: 2.5, z: -30.6 - (lx === 2.40 ? 0 : 0.6), thick: 0.004, edges: false }));
  }
  alleyGroup.add(icyl(0.024, 0.024, 4.6, '#3a4046', { x: 2.40, y: 2.5, z: -31.2, thick: 0.004, edges: false }));
  for (let ry2 = 0.5; ry2 <= 4.5; ry2 += 0.55) {
    alleyGroup.add(icyl(0.018, 0.018, 0.6, '#3a4046', { x: 2.40, y: ry2, z: -30.9, rx: Math.PI / 2, thick: 0.003, edges: false }));
  }

  // Concrete Underground Transit Station Maintenance Entrance at z = -35.2!
  // (FIX: left wall width 1.9 so it no longer bricks over the x=-0.82..+0.80 doorway!)
  alleyGroup.add(ibox(1.9, 4.4, 0.45, '#ffffff', { map: concreteTex, x: -1.85, y: 2.2, z: -35.2 }));
  alleyGroup.add(ibox(1.9, 4.4, 0.45, '#ffffff', { map: concreteTex, x:  1.85, y: 2.2, z: -35.2 }));
  alleyGroup.add(ibox(5.4, 1.55, 0.48, '#ffffff', { map: concreteTex, x: 0, y: 3.62, z: -35.2 }));
  // Dark stairwell void behind open maintenance door
  const stairVoid = new THREE.Mesh(new THREE.PlaneGeometry(2.2, 3.0), new THREE.MeshBasicMaterial({ color: '#090d14' }));
  stairVoid.position.set(0, 1.45, -36.4);
  alleyGroup.add(stairVoid);
  const transitSign = makeSignBoard('TRANSIT STATION', 'MAINTENANCE ONLY', { w: 2.4, h: 0.54, bg: '#1e2c3a', fg: '#f5efe0', accent: '#e6a82e' });
  transitSign.position.set(0, 3.35, -34.90);
  alleyGroup.add(transitSign);

  // Hazard-trimmed door frame (yellow/black) so the hanging-open door reads instantly!
  for (const hx of [-1.02, 0.98]) {
    alleyGroup.add(ibox(0.18, 2.88, 0.06, '#ffffff', { map: hazardTex, x: hx, y: 1.44, z: -34.94, thick: 0.006 }));
  }
  alleyGroup.add(ibox(2.18, 0.30, 0.06, '#ffffff', { map: hazardTex, x: 0, y: 2.98, z: -34.94, thick: 0.006 }));
  // Caged warm emergency lamp above the alley maintenance door
  const alleyLampMat = new THREE.MeshBasicMaterial({ color: '#ffc06a' });
  const alleyLamp = new THREE.Group();
  alleyLamp.position.set(0, 3.42, -34.82);
  alleyLamp.add(ibox(0.30, 0.16, 0.10, '#33383e', { y: 0.10, thick: 0.008, edges: false }));
  const alleyBulb = new THREE.Mesh(new THREE.SphereGeometry(0.085, 12, 10), alleyLampMat);
  alleyBulb.position.y = -0.02;
  alleyLamp.add(alleyBulb);
  for (const bx of [-0.09, 0, 0.09]) {
    alleyLamp.add(icyl(0.007, 0.007, 0.20, '#2c3136', { x: bx, y: -0.02, z: 0.085, thick: 0, edges: false }));
  }
  alleyGroup.add(alleyLamp);

  // Heavy Grey Iron Maintenance Door hanging ominously ajar
  const alleyMaintDoorPivot = new THREE.Group();
  alleyMaintDoorPivot.position.set(-0.82, 0, -35.15);
  alleyMaintDoorPivot.add(ibox(1.62, 2.78, 0.12, '#4a545e', { x: 0.81, y: 1.39, z: 0 }));
  alleyMaintDoorPivot.add(ibox(0.22, 0.08, 0.16, '#d9a438', { x: 1.42, y: 1.32, z: 0.04, thick: 0.008 }));
  const doorPlate = makeSignBoard('M-7', 'TRANSIT AUTHORITY', { w: 0.34, h: 0.24, bg: '#c9ced4', fg: '#2b3238', accent: '#4a545e' });
  doorPlate.position.set(0.45, 2.30, 0.08);
  alleyMaintDoorPivot.add(doorPlate);
  alleyMaintDoorPivot.rotation.y = 0.68; // Hanging ~39° open into dark stairwell!
  alleyGroup.add(alleyMaintDoorPivot);

  // =========================================================================
  // 5. UNDERGROUND TRANSIT STATION STAIRWELL, PLATFORM 3 & TUNNEL (`undergroundGroup`, z: -50..-86)
  // =========================================================================
  const undergroundGroup = new THREE.Group();
  root.add(undergroundGroup);

  // Upper Stairwell Entrance Wall (z = -52.2, y = 2.20..5.20) + Self-Closing Heavy Maintenance Door!
  undergroundGroup.add(ibox(1.8, 3.2, 0.35, '#ffffff', { map: concreteTex, x: -1.75, y: 3.7, z: -52.2 }));
  undergroundGroup.add(ibox(1.8, 3.2, 0.35, '#ffffff', { map: concreteTex, x:  1.75, y: 3.7, z: -52.2 }));
  undergroundGroup.add(ibox(5.2, 0.8, 0.35, '#ffffff', { map: concreteTex, x: 0, y: 4.9, z: -52.2 }));
  // Pale exterior dawn glow plane behind upper maintenance doorway (gets blocked as door closes by itself!)
  const ugDoorGlowMat = new THREE.MeshBasicMaterial({ color: '#9cb8cc' });
  const ugDoorBackGlow = new THREE.Mesh(new THREE.PlaneGeometry(1.85, 2.75), ugDoorGlowMat);
  ugDoorBackGlow.position.set(0, 3.45, -51.75);
  undergroundGroup.add(ugDoorBackGlow);

  // Hazard trim framing the self-closing maintenance door + warm emergency bulkhead light!
  for (const hx of [-1.05, 1.05]) {
    undergroundGroup.add(ibox(0.18, 2.78, 0.06, '#ffffff', { map: hazardTex, x: hx, y: 3.45, z: -52.00, thick: 0.006 }));
  }
  undergroundGroup.add(ibox(2.30, 0.30, 0.06, '#ffffff', { map: hazardTex, x: 0, y: 4.98, z: -52.00, thick: 0.006 }));
  const maintSign = makeSignBoard('MAINTENANCE', 'AUTHORIZED ONLY', { w: 1.45, h: 0.34, bg: '#e8b83c', fg: '#231a10', accent: '#231a10' });
  maintSign.position.set(1.62, 3.30, -51.97);
  undergroundGroup.add(maintSign);
  const ugBulkMat = new THREE.MeshBasicMaterial({ color: '#ffc06a' });
  const ugBulk = new THREE.Group();
  // Right of the doorway center: the hinged panel sweeps from the LEFT (hinge x=-0.84) as it
  // closes, so a centered lamp is occluded almost immediately. x=0.60 keeps the warm glow
  // peeking through the shrinking right gap until the door is ~75% shut.
  ugBulk.position.set(0.60, 4.52, -51.86);
  ugBulk.add(ibox(0.32, 0.18, 0.10, '#33383e', { y: 0.12, thick: 0.008, edges: false }));
  const ugBulb = new THREE.Mesh(new THREE.SphereGeometry(0.09, 12, 10), ugBulkMat);
  ugBulk.add(ugBulb);
  for (const bx of [-0.10, 0, 0.10]) {
    ugBulk.add(icyl(0.008, 0.008, 0.22, '#2c3136', { x: bx, y: 0, z: 0.09, thick: 0, edges: false }));
  }
  // Warm halo so the bulkhead reads as a glowing lamp from down the tunnel (door occludes it as it seals).
  const glowCv = document.createElement('canvas'); glowCv.width = glowCv.height = 128;
  const gg = glowCv.getContext('2d');
  const rg = gg.createRadialGradient(64, 64, 4, 64, 64, 62);
  rg.addColorStop(0.0, 'rgba(255,198,112,0.95)');
  rg.addColorStop(0.35, 'rgba(255,172,82,0.42)');
  rg.addColorStop(1.0, 'rgba(255,150,60,0.0)');
  gg.fillStyle = rg; gg.fillRect(0, 0, 128, 128);
  const ugBulkGlowMat = new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(glowCv), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide });
  const ugBulkGlow = new THREE.Mesh(new THREE.PlaneGeometry(2.6, 2.6), ugBulkGlowMat);
  ugBulkGlow.position.set(0, -0.06, 0.12);
  ugBulk.add(ugBulkGlow);
  undergroundGroup.add(ugBulk);

  // Hinged Heavy Steel Maintenance Door at top of stairs (`ugMaintDoorPivot`: closes slowly by itself!)
  const ugMaintDoorPivot = new THREE.Group();
  ugMaintDoorPivot.position.set(-0.84, 2.10, -52.18);
  ugMaintDoorPivot.add(ibox(1.68, 2.72, 0.13, '#444e58', { x: 0.84, y: 1.36, z: 0 }));
  ugMaintDoorPivot.add(ibox(1.40, 0.14, 0.16, '#2e353c', { x: 0.84, y: 1.30, z: 0.03, thick: 0.008 }));
  undergroundGroup.add(ugMaintDoorPivot);

  // 10 Concrete Stairwell Steps with YELLOW SAFETY NOSINGS descending to the platform!
  for (let s = 0; s < 10; s++) {
    const sy = 2.10 - (s + 0.5) * 0.21;
    const sz = -52.6 - s * 0.60;
    undergroundGroup.add(ibox(3.2, 0.22, 0.64, '#ffffff', { map: concreteTex, x: 0, y: sy, z: sz, thick: 0.012 }));
    undergroundGroup.add(ibox(3.24, 0.035, 0.11, '#e2b93b', { x: 0, y: sy + 0.115, z: sz + 0.28, thick: 0.005 }));
  }
  // Stairwell concrete side walls + yellow tubular safety handrails
  undergroundGroup.add(ibox(0.28, 5.4, 8.2, '#ffffff', { map: concreteTex, x: -1.75, y: 2.5, z: -55.5 }));
  undergroundGroup.add(ibox(0.28, 5.4, 8.2, '#ffffff', { map: concreteTex, x:  1.75, y: 2.5, z: -55.5 }));
  for (const hx of [-1.52, 1.52]) {
    undergroundGroup.add(icyl(0.035, 0.035, 6.4, '#e0b034', { x: hx, y: 1.95, z: -55.4, rx: -1.24, thick: 0.008 }));
  }

  // Lower Underground Station Landing & Platform 3 Hall (x: -5.4..5.4, z: -58.5..-68.8, y: 0..4.2)
  const ugFloor = new THREE.Mesh(new THREE.PlaneGeometry(11.0, 11.0), toon('#ffffff', concreteTex));
  ugFloor.rotation.x = -Math.PI / 2; ugFloor.position.set(0, 0.0, -63.8);
  undergroundGroup.add(ugFloor);
  const ugCeil = new THREE.Mesh(new THREE.PlaneGeometry(11.0, 18.0), toon('#2c3238'));
  ugCeil.rotation.x = Math.PI / 2; ugCeil.position.set(0, 4.25, -60.5);
  undergroundGroup.add(ugCeil);

  // Grimy subway tile walls & heavy concrete support columns
  undergroundGroup.add(ibox(0.30, 4.3, 11.0, '#ffffff', { map: subTileTex, x: -5.3, y: 2.15, z: -63.8 }));
  undergroundGroup.add(ibox(0.30, 4.3, 11.0, '#ffffff', { map: subTileTex, x:  5.3, y: 2.15, z: -63.8 }));
  for (const px of [-3.2, 3.2]) {
    for (const pz of [-61.2, -66.0]) {
      undergroundGroup.add(ibox(0.58, 4.3, 0.58, '#ffffff', { map: concreteTex, x: px, y: 2.15, z: pz }));
      undergroundGroup.add(ibox(0.64, 1.1, 0.64, '#d9a438', { x: px, y: 0.55, z: pz, thick: 0.01 }));
    }
  }

  // Overhead Subway Sign: PLATFORM 3 + WAY OUT signage
  const platSign = makeSignBoard('PLATFORM 3', 'TRACKS 3 - 4', { w: 2.5, h: 0.52, bg: '#16222e', fg: '#ffffff', accent: '#2c78d4' });
  platSign.position.set(0, 3.45, -65.8);
  undergroundGroup.add(platSign);
  const wayOutSign = makeSignBoard('WAY OUT', 'STREET LEVEL', { w: 1.4, h: 0.40, bg: '#1d5c38', fg: '#eafff2', accent: '#123c26' });
  wayOutSign.rotation.y = Math.PI / 2;
  wayOutSign.position.set(-5.12, 2.55, -60.8);
  undergroundGroup.add(wayOutSign);

  // Flickering Warm-Amber Caged Emergency Bulkhead Light
  const ugLampMat = new THREE.MeshBasicMaterial({ color: '#ffbe66' });
  const ugLampBulb = new THREE.Mesh(new THREE.SphereGeometry(0.16, 12, 10), ugLampMat);
  ugLampBulb.position.set(0, 3.92, -62.5);
  undergroundGroup.add(ibox(0.42, 0.12, 0.42, '#282d33', { x: 0, y: 4.12, z: -62.5 }), ugLampBulb);

  // Wooden Crate + Crackling Emergency Walkie-Talkie / Field Radio (`ugRadio` with detailed faceplate!)
  const radioCrate = ibox(0.76, 0.50, 0.56, '#7d5636', { map: woodTex, x: -0.25, y: 0.25, z: -62.6 });
  undergroundGroup.add(radioCrate);

  const ugRadio = new THREE.Group();
  ugRadio.position.set(-0.25, 0.62, -62.55);
  const radioFace = toon('#ffffff', makeRadioFaceTex());
  const radioBody = new THREE.Mesh(
    new THREE.BoxGeometry(0.38, 0.24, 0.18),
    [toon('#2d3632'), toon('#2d3632'), toon('#232a26'), toon('#232a26'), radioFace, toon('#2d3632')]
  );
  ugRadio.add(ink(radioBody, 0.010, true));
  ugRadio.add(icyl(0.022, 0.022, 0.035, '#c8c2b4', { x: -0.13, y: 0.05, z: 0.095, rx: Math.PI / 2, thick: 0.005 })); // PWR knob
  ugRadio.add(icyl(0.022, 0.022, 0.035, '#c8c2b4', { x: -0.13, y: -0.05, z: 0.095, rx: Math.PI / 2, thick: 0.005 })); // VOL knob
  ugRadio.add(icyl(0.009, 0.012, 0.52, '#aeb6be', { x: 0.14, y: 0.34, z: -0.02, rz: -0.12, thick: 0.004 })); // whip antenna
  const handle = new THREE.Mesh(new THREE.TorusGeometry(0.10, 0.011, 8, 14, Math.PI), toon('#1c211e'));
  handle.position.set(0.02, 0.13, 0);
  ugRadio.add(handle);
  const ugRadioLedMat = new THREE.MeshBasicMaterial({ color: '#ff2b22' });
  const ugRadioLed = new THREE.Mesh(new THREE.SphereGeometry(0.024, 10, 8), ugRadioLedMat);
  ugRadioLed.position.set(0.11, -0.04, 0.098);
  ugRadio.add(ugRadioLed);
  undergroundGroup.add(ugRadio);

  // Pitch-Black Deep Subway Tunnel Portal & Tracks (`z: -68.8 .. -86.0`) + safety signage
  undergroundGroup.add(ibox(3.4, 4.3, 0.45, '#ffffff', { map: concreteTex, x: -3.7, y: 2.15, z: -68.8 }));
  undergroundGroup.add(ibox(3.4, 4.3, 0.45, '#ffffff', { map: concreteTex, x:  3.7, y: 2.15, z: -68.8 }));
  undergroundGroup.add(ibox(10.8, 1.05, 0.45, '#ffffff', { map: concreteTex, x: 0, y: 3.75, z: -68.8 }));
  const gapSign = makeSignBoard('MIND THE GAP', 'STAND CLEAR', { w: 2.2, h: 0.34, bg: '#e6b83c', fg: '#231a10', accent: '#231a10' });
  gapSign.position.set(0, 3.50, -68.55);
  undergroundGroup.add(gapSign);
  const dangerSign = makeSignBoard('DANGER', 'LIVE TRACKS — KEEP OUT', { w: 1.5, h: 0.46, bg: '#8f1d16', fg: '#ffe9dd', accent: '#5c0e0a' });
  dangerSign.position.set(2.55, 1.30, -68.53);
  undergroundGroup.add(dangerSign);

  // Deep Dark Tunnel Bore + Steel Subway Rails + Eerie Gleaming Mimic Eyes in the Abyss!
  const tunnelWallMat = toon('#151920');
  const tunFloor = new THREE.Mesh(new THREE.PlaneGeometry(4.4, 18.0), tunnelWallMat);
  tunFloor.rotation.x = -Math.PI / 2; tunFloor.position.set(0, -0.35, -77.5);
  undergroundGroup.add(tunFloor);
  for (const tx of [-2.05, 2.05]) {
    const tw = new THREE.Mesh(new THREE.BoxGeometry(0.3, 3.8, 18.0), tunnelWallMat);
    tw.position.set(tx, 1.5, -77.5); undergroundGroup.add(tw);
  }
  const tunBack = new THREE.Mesh(new THREE.PlaneGeometry(5.0, 4.5), new THREE.MeshBasicMaterial({ color: '#04060a' }));
  tunBack.position.set(0, 1.6, -85.8);
  undergroundGroup.add(tunBack);
  // Steel subway rails & wooden ties
  for (const rx of [-0.72, 0.72]) {
    undergroundGroup.add(ibox(0.08, 0.08, 16.5, '#58626e', { x: rx, y: -0.28, z: -77.0, thick: 0.006 }));
  }
  for (let tz = -69.5; tz >= -83.5; tz -= 1.1) {
    undergroundGroup.add(ibox(2.1, 0.05, 0.18, '#3b2c22', { x: 0, y: -0.32, z: tz, thick: 0, edges: false }));
  }
  // V6: Gaunt tunnel-dweller — the child-voice mimic. Ragged hunched silhouette with a faint
  // cold rim; sways far in the bore (244.5s), eyes glint through the "Dad?" beat, LUNGES at 254.5.
  const figC = document.createElement('canvas'); figC.width = 220; figC.height = 520;
  const fgc = figC.getContext('2d');
  fgc.fillStyle = 'rgba(4,6,10,0.97)';
  fgc.beginPath();
  fgc.moveTo(110, 8);
  fgc.bezierCurveTo(138, 18, 146, 52, 142, 86);
  fgc.bezierCurveTo(168, 108, 176, 150, 168, 178);
  fgc.bezierCurveTo(184, 260, 178, 330, 164, 392);
  fgc.lineTo(152, 520); fgc.lineTo(94, 520);
  fgc.bezierCurveTo(72, 400, 66, 320, 74, 240);
  fgc.bezierCurveTo(60, 190, 62, 140, 78, 104);
  fgc.bezierCurveTo(86, 48, 92, 20, 110, 8);
  fgc.closePath(); fgc.fill();
  fgc.strokeStyle = 'rgba(126,148,190,0.45)'; fgc.lineWidth = 6; fgc.stroke();
  fgc.fillStyle = '#000000';
  fgc.beginPath(); fgc.ellipse(92, 52, 10, 6, -0.2, 0, 7); fgc.fill();
  fgc.beginPath(); fgc.ellipse(126, 50, 10, 6, 0.2, 0, 7); fgc.fill();
  const figTex = new THREE.CanvasTexture(figC); figTex.colorSpace = THREE.SRGBColorSpace;
  const tunnelFigMat = new THREE.MeshBasicMaterial({ map: figTex, transparent: true, opacity: 0.62, depthWrite: false });
  const tunnelFig = new THREE.Mesh(new THREE.PlaneGeometry(0.82, 1.94), tunnelFigMat);
  tunnelFig.position.set(0.35, 0.97, -73.20);
  undergroundGroup.add(tunnelFig);
  // Eerie Mimic Eyes — now ride the silhouette's face (local space, scale with the lunge).
  const tunnelEyes = new THREE.Group();
  const eyeGlowMat = new THREE.MeshBasicMaterial({ color: '#ffd982' });
  for (const ex of [-0.09, 0.09]) {
    const em = new THREE.Mesh(new THREE.SphereGeometry(0.030, 8, 8), eyeGlowMat);
    em.position.set(ex, 0.66, 0.045);
    tunnelEyes.add(em);
  }
  tunnelFig.add(tunnelEyes);

  // V6: GRADIENT SKY DOME with soft clouds — a real sky over the street & sunrise shots.
  const skyC = document.createElement('canvas'); skyC.width = 1024; skyC.height = 512;
  const sg = skyC.getContext('2d');
  const skyGrad = sg.createLinearGradient(0, 0, 0, 512);
  skyGrad.addColorStop(0.00, '#597fa8');
  skyGrad.addColorStop(0.42, '#8fadd0');
  skyGrad.addColorStop(0.68, '#c0cdda');
  skyGrad.addColorStop(1.00, '#cbd4dd');
  sg.fillStyle = skyGrad; sg.fillRect(0, 0, 1024, 512);
  const skyR = P.rng(211);
  for (let k = 0; k < 9; k++) { // soft drifting cumulus
    const cx = skyR() * 1024, cy = 40 + skyR() * 210, cr = 46 + skyR() * 95;
    const cg = sg.createRadialGradient(cx, cy, 4, cx, cy, cr);
    cg.addColorStop(0, `rgba(250,252,255,${0.34 + 0.22 * skyR()})`);
    cg.addColorStop(1, 'rgba(250,252,255,0)');
    sg.fillStyle = cg; sg.beginPath(); sg.arc(cx, cy, cr, 0, 7); sg.fill();
  }
  const skyTex = new THREE.CanvasTexture(skyC); skyTex.colorSpace = THREE.SRGBColorSpace;
  const skyDome = new THREE.Mesh(
    new THREE.SphereGeometry(92, 28, 14),
    new THREE.MeshBasicMaterial({ map: skyTex, side: THREE.BackSide, fog: false, depthWrite: false })
  );
  skyDome.renderOrder = -10;
  root.add(skyDome);

  // =========================================================================
  // V6b: HOLLYWOOD COLD-OPEN OVERLAY GRAPHICS (nationwide spread map / title / end card / locators)
  // =========================================================================
  function makeIntroMapTex() {
    // Night emergency-broadcast infection map: dark country silhouette, blooming red clusters.
    const c = document.createElement('canvas'); c.width = 1080; c.height = 1920;
    const g = c.getContext('2d');
    const r = P.rng(313);
    g.fillStyle = '#04070d'; g.fillRect(0, 0, 1080, 1920);
    // faint tactical grid
    g.strokeStyle = 'rgba(60,110,150,0.14)'; g.lineWidth = 1;
    for (let x = 0; x <= 1080; x += 60) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, 1920); g.stroke(); }
    for (let y = 0; y <= 1920; y += 60) { g.beginPath(); g.moveTo(0, y); g.lineTo(1080, y); g.stroke(); }
    // abstract landmass silhouette
    g.fillStyle = '#0c1420'; g.strokeStyle = 'rgba(90,140,180,0.35)'; g.lineWidth = 3;
    g.beginPath();
    g.moveTo(140, 760);
    g.bezierCurveTo(300, 560, 560, 520, 760, 600);
    g.bezierCurveTo(950, 670, 1000, 840, 920, 1010);
    g.bezierCurveTo(860, 1160, 660, 1260, 520, 1240);
    g.bezierCurveTo(360, 1210, 220, 1120, 160, 980);
    g.bezierCurveTo(110, 880, 100, 820, 140, 760);
    g.closePath(); g.fill(); g.stroke();
    // blooming infection clusters
    for (let k = 0; k < 22; k++) {
      const px = 180 + r() * 700, py = 640 + r() * 540, pr = 8 + r() * 30;
      const cg = g.createRadialGradient(px, py, 1, px, py, pr);
      cg.addColorStop(0, 'rgba(255,64,40,0.95)');
      cg.addColorStop(0.5, 'rgba(210,30,20,0.55)');
      cg.addColorStop(1, 'rgba(160,20,10,0)');
      g.fillStyle = cg; g.beginPath(); g.arc(px, py, pr, 0, 7); g.fill();
      if (k % 4 === 0) { // expanding containment rings
        g.strokeStyle = 'rgba(255,90,60,0.5)'; g.lineWidth = 2;
        g.beginPath(); g.arc(px, py, pr + 12 + 14 * (k % 3), 0, 7); g.stroke();
      }
    }
    // spread arrows
    g.strokeStyle = 'rgba(255,80,50,0.75)'; g.lineWidth = 4; g.setLineDash([14, 10]);
    for (const [ax, ay, bx, by] of [[300, 820, 560, 700], [620, 900, 820, 800], [420, 1060, 640, 1150]]) {
      g.beginPath(); g.moveTo(ax, ay); g.lineTo(bx, by); g.stroke();
    }
    g.setLineDash([]);
    // header
    g.fillStyle = '#c81e14'; g.fillRect(0, 120, 1080, 12);
    g.fillStyle = '#ff2a1c'; g.textAlign = 'center';
    g.font = '900 92px Arial, sans-serif';
    g.fillText('NATIONWIDE', 540, 260);
    g.fillText('EMERGENCY', 540, 368);
    g.fillStyle = '#e8d9c8'; g.font = 'bold 46px Arial, sans-serif';
    g.fillText('INFECTION CONFIRMED — SPREADING', 540, 452);
    // live bug
    g.fillStyle = 'rgba(200,30,20,0.92)'; g.beginPath(); g.arc(120, 1460, 16, 0, 7); g.fill();
    g.fillStyle = '#ff5040'; g.font = '900 44px Arial, sans-serif'; g.textAlign = 'left';
    g.fillText('LIVE', 152, 1476);
    g.fillStyle = '#8fa4b8'; g.font = 'bold 34px Arial, sans-serif';
    g.fillText('EBS FEED — 4:17 PM', 120, 1530);
    // ticker
    g.fillStyle = 'rgba(10,12,18,0.92)'; g.fillRect(0, 1700, 1080, 120);
    g.fillStyle = '#ff4030'; g.font = 'bold 40px Arial, sans-serif'; g.textAlign = 'center';
    g.fillText('STAY INDOORS  •  AVOID THE CONFUSED  •  SHELTER IN PLACE', 540, 1772);
    // scanline vibe
    g.fillStyle = 'rgba(0,0,0,0.16)';
    for (let y = 0; y < 1920; y += 6) g.fillRect(0, y, 1080, 2);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
  }
  function makeTitleTex() {
    // Smash title card: RICK CLIPS presents — OUTBREAK.
    const c = document.createElement('canvas'); c.width = 1080; c.height = 1920;
    const g = c.getContext('2d');
    const r = P.rng(317);
    g.fillStyle = '#020204'; g.fillRect(0, 0, 1080, 1920);
    for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(255,255,255,${0.015 + 0.05 * r()})`; g.fillRect(r() * 1080, r() * 1920, 1.5, 1.5); }
    g.textAlign = 'center';
    g.fillStyle = '#93a4b8'; g.font = 'bold 52px Arial, sans-serif';
    g.fillText('R  I  C  K    C  L  I  P  S     P  R  E  S  E  N  T  S', 540, 560);
    // giant distressed OUTBREAK
    g.font = '900 236px Arial, sans-serif';
    g.fillStyle = '#5a0c08'; g.fillText('OUTBREAK', 548, 1010);
    g.fillStyle = '#c81e14'; g.fillText('OUTBREAK', 540, 1000);
    // scratch damage
    g.strokeStyle = 'rgba(0,0,0,0.55)'; g.lineWidth = 5;
    for (let k = 0; k < 14; k++) {
      const sx = 200 + r() * 680, sy = 780 + r() * 260;
      g.beginPath(); g.moveTo(sx, sy); g.lineTo(sx + (r() - 0.5) * 220, sy + (r() - 0.5) * 60); g.stroke();
    }
    g.fillStyle = '#7d8a9a'; g.font = 'bold 44px Arial, sans-serif';
    g.fillText('A  3 D  H O R R O R  S T O R Y', 540, 1130);
    g.fillStyle = '#4a5563'; g.font = 'bold 30px Arial, sans-serif';
    g.fillText('BASED ON A SURVIVOR ACCOUNT', 540, 1660);
    // vignette
    const vg = g.createRadialGradient(540, 960, 340, 540, 960, 980);
    vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.72)');
    g.fillStyle = vg; g.fillRect(0, 0, 1080, 1920);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
  }
  function makeEndTex() {
    // TO BE CONTINUED card.
    const c = document.createElement('canvas'); c.width = 1080; c.height = 1920;
    const g = c.getContext('2d');
    const r = P.rng(319);
    g.fillStyle = '#020204'; g.fillRect(0, 0, 1080, 1920);
    for (let i = 0; i < 700; i++) { g.fillStyle = `rgba(255,255,255,${0.012 + 0.04 * r()})`; g.fillRect(r() * 1080, r() * 1920, 1.5, 1.5); }
    g.textAlign = 'center';
    g.fillStyle = '#e8e2d8'; g.font = '900 118px Arial, sans-serif';
    g.fillText('TO  BE', 540, 880);
    g.fillText('CONTINUED', 540, 1030);
    g.fillStyle = '#c81e14'; g.fillRect(330, 1080, 420, 10);
    g.fillStyle = '#6d7886'; g.font = 'bold 36px Arial, sans-serif';
    g.fillText('RICK CLIPS — OUTBREAK', 540, 1180);
    const vg = g.createRadialGradient(540, 960, 300, 540, 960, 980);
    vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.75)');
    g.fillStyle = vg; g.fillRect(0, 0, 1080, 1920);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
  }
  function makeLocatorTex(l1, l2) {
    // Bottom-left cinematic location card (transparent elsewhere).
    const c = document.createElement('canvas'); c.width = 1080; c.height = 1920;
    const g = c.getContext('2d');
    g.fillStyle = 'rgba(4,6,10,0.62)';
    g.fillRect(70, 1600, 660, 150);
    g.fillStyle = '#c81e14'; g.fillRect(70, 1600, 12, 150);
    g.textAlign = 'left';
    g.fillStyle = '#f2ede4'; g.font = '900 58px Arial, sans-serif';
    g.fillText(l1, 116, 1672);
    g.fillStyle = '#9aa7b5'; g.font = 'bold 36px Arial, sans-serif';
    g.fillText(l2, 116, 1730);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
  }
  function makeStripTex(text) {
    // Cinematic bottom-third beat card: letterspaced caps on a dark gradient band, red keyline.
    const c = document.createElement('canvas'); c.width = 1080; c.height = 1920;
    const g = c.getContext('2d');
    const bg = g.createLinearGradient(0, 1480, 0, 1780);
    bg.addColorStop(0, 'rgba(2,4,8,0)');
    bg.addColorStop(0.42, 'rgba(2,4,8,0.66)');
    bg.addColorStop(1, 'rgba(2,4,8,0.82)');
    g.fillStyle = bg; g.fillRect(0, 1480, 1080, 440);
    g.fillStyle = '#c81e14'; g.fillRect(140, 1608, 14, 96);
    g.textAlign = 'left';
    g.fillStyle = '#f2ede4'; g.font = '900 58px Arial, sans-serif';
    g.fillText(text.split(' ').join('\u2002'), 190, 1676);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
  }
  // V7: pure-black full-screen texture — the 3.00s silence beat before the story begins.
  const makeBlackTex = () => {
    const c = document.createElement('canvas'); c.width = 16; c.height = 16;
    const g = c.getContext('2d'); g.fillStyle = '#000000'; g.fillRect(0, 0, 16, 16);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
  };
  const introOverlayTex = {
    black: makeBlackTex(),
    map: makeIntroMapTex(),
    title: makeTitleTex(),
    end: makeEndTex(),
    // V7 ORIGINS text cards (render-time; captions stay ASS-side)
    intro1: makeStripTex('IT BEGAN LIKE ANY OTHER DAY'),
    intro1b: makeStripTex('SCHOOL  •  OFFICE  •  AN ORDINARY MORNING'),
    intro2: makeStripTex('ONE LAB CHANGED EVERYTHING'),
    intro3: makeStripTex('IT SPREAD IN HOURS'),
    intro4: makeStripTex('SPECIMEN 47 — LIVE TEST'),
    intro5: makeStripTex('EVERY SCREEN SAID THE SAME THING'),
    locator1: makeLocatorTex('OUTBREAK — DAY 1', '4:17 PM  •  CITY LOCKDOWN IN EFFECT'),
    locator2: makeLocatorTex('DAY 2 — SUNRISE', '6:12 AM  •  THE STREET IS EMPTY'),
    black: (() => {
      const c = document.createElement('canvas'); c.width = 8; c.height = 8;
      const g = c.getContext('2d'); g.fillStyle = '#000'; g.fillRect(0, 0, 8, 8);
      const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
    })(),
  };

  // =========================================================================
  // 6. HELD CLOSE-UP PROPS (Hand-Gripped Smartphone + Volumetric Flashlight Cone)
  // =========================================================================
  const heldPhone = new THREE.Group();
  // --- Rounded real-phone body (extruded rounded slab + metal buttons) ---
  const bw = 0.24, bh = 0.43, br = 0.034;
  const bodyShape = new THREE.Shape();
  bodyShape.moveTo(-bw / 2 + br, -bh / 2);
  bodyShape.lineTo(bw / 2 - br, -bh / 2); bodyShape.quadraticCurveTo(bw / 2, -bh / 2, bw / 2, -bh / 2 + br);
  bodyShape.lineTo(bw / 2, bh / 2 - br); bodyShape.quadraticCurveTo(bw / 2, bh / 2, bw / 2 - br, bh / 2);
  bodyShape.lineTo(-bw / 2 + br, bh / 2); bodyShape.quadraticCurveTo(-bw / 2, bh / 2, -bw / 2, bh / 2 - br);
  bodyShape.lineTo(-bw / 2, -bh / 2 + br); bodyShape.quadraticCurveTo(-bw / 2, -bh / 2, -bw / 2 + br, -bh / 2);
  const phoneBody = new THREE.Mesh(
    new THREE.ExtrudeGeometry(bodyShape, { depth: 0.020, bevelEnabled: true, bevelThickness: 0.005, bevelSize: 0.004, bevelSegments: 2 }),
    toon('#171a20'));
  phoneBody.position.z = -0.0125;
  ink(phoneBody, 0.006, false); phoneBody.castShadow = false;
  // side buttons (left edge — thumb side): volume rocker x2 + power
  const btnMat = toon('#2b313a');
  const mkBtn = (by, blen) => {
    const b = new THREE.Mesh(new THREE.BoxGeometry(0.0085, blen, 0.011), btnMat);
    b.position.set(-bw / 2 - 0.0015, by, 0.0); ink(b, 0.003, false); b.castShadow = false; return b;
  };
  const btnVolUp = mkBtn(0.150, 0.052), btnVolDn = mkBtn(0.088, 0.052), btnPwr = mkBtn(0.028, 0.062);
  const alert1Tex = makePhoneScreenTex('alert1');
  const alert2Tex = makePhoneScreenTex('alert2');
  const mapTex    = makePhoneScreenTex('map1bar');
  const social0Tex = makePhoneScreenTex('social0');
  const social1Tex = makePhoneScreenTex('social1');
  const phoneScrMat = new THREE.MeshBasicMaterial({ map: alert1Tex });
  const phoneScr = new THREE.Mesh(new THREE.PlaneGeometry(0.216, 0.398), phoneScrMat);
  phoneScr.position.z = 0.0165;
  // --- Glass glare sheet: diagonal reflections streaking across the screen ---
  const [glc, glg] = cv(256, 512);
  {
    const grd = glg.createLinearGradient(0, 512, 256, 0);
    grd.addColorStop(0.00, 'rgba(255,255,255,0.30)');
    grd.addColorStop(0.34, 'rgba(255,255,255,0.13)');
    grd.addColorStop(0.46, 'rgba(255,255,255,0.0)');
    grd.addColorStop(0.80, 'rgba(255,255,255,0.0)');
    grd.addColorStop(0.94, 'rgba(255,255,255,0.08)');
    grd.addColorStop(1.00, 'rgba(255,255,255,0.0)');
    glg.fillStyle = grd; glg.fillRect(0, 0, 256, 512);
  }
  const glareTex = new THREE.CanvasTexture(glc); glareTex.colorSpace = THREE.SRGBColorSpace;
  const phoneGlareMat = new THREE.MeshBasicMaterial({
    map: glareTex, transparent: true, opacity: 0.34, depthWrite: false,
    blending: THREE.AdditiveBlending, toneMapped: false,
  });
  const phoneGlare = new THREE.Mesh(new THREE.PlaneGeometry(0.222, 0.408), phoneGlareMat);
  phoneGlare.position.z = 0.0185;
  // --- Living hand: palm behind, curled side fingers w/ fingertip pads, thumb OVER the bottom bezel ---
  const skinCol = '#f2ecdf';
  const palm = new THREE.Mesh(new THREE.BoxGeometry(0.135, 0.185, 0.052), toon(skinCol));
  palm.position.set(0.012, -0.145, -0.049); ink(palm, 0.007, false); palm.castShadow = false;
  const mkSideFinger = (fy) => {
    const f = new THREE.Group();
    const seg = icyl(0.0195, 0.0215, 0.088, skinCol, { thick: 0.005, cast: false });
    seg.rotation.z = Math.PI / 2 - 0.22; seg.position.set(0.0, 0.0, 0.0);
    const tip = new THREE.Mesh(new THREE.SphereGeometry(0.0205, 12, 10), toon('#f6f1e6'));
    tip.position.set(0.052, 0.0085, 0.0095); ink(tip, 0.004, false); tip.castShadow = false;
    f.add(seg, tip); f.position.set(0.116, fy, 0.006);
    return f;
  };
  const finger1 = mkSideFinger(0.032), finger2 = mkSideFinger(-0.030), finger3 = mkSideFinger(-0.092);
  // thumb crossing the bottom-left bezel IN FRONT of the screen (the classic one-hand grip)
  const thumb = icyl(0.0235, 0.0255, 0.105, skinCol, { thick: 0.005, cast: false, rz: 1.28 });
  thumb.position.set(-0.028, -0.196, 0.0135);
  const thumbTip = new THREE.Mesh(new THREE.SphereGeometry(0.0235, 12, 10), toon('#f6f1e6'));
  thumbTip.position.set(-0.072, -0.183, 0.0145); ink(thumbTip, 0.004, false); thumbTip.castShadow = false;
  const wristSleeve = icyl(0.058, 0.075, 0.27, '#2c5b7c', { x: 0.010, y: -0.325, z: -0.055, rz: -0.16, thick: 0.008, cast: false });
  const cuff = icyl(0.064, 0.062, 0.05, '#22384c', { x: 0.006, y: -0.205, z: -0.052, rz: -0.16, thick: 0.007, cast: false });
  heldPhone.add(phoneBody, btnVolUp, btnVolDn, btnPwr, phoneScr, phoneGlare, palm, finger1, finger2, finger3, thumb, thumbTip, wristSleeve, cuff);
  scene.add(heldPhone);

  // =========================================================================
  // 6b. V6.5 ORIGINS COLD-OPEN SETS — HIDDEN LAB (evil scientist) + NEWSROOM
  // =========================================================================
  const labGroup = new THREE.Group();
  labGroup.position.set(-40, 0, -12);
  let labAlarmMat, cageDoor;
  let labContainers = [];
  let labConsole = null;
  let labButtonBase = null;
  let labButtonCover = null;
  let labButtonMat = null;
  {
    labGroup.add(ibox(14, 0.12, 10, '#191d23', { y: -0.06, thick: 0.02, cast: false }));           // floor
    labGroup.add(ibox(14, 3.8, 0.18, '#252b34', { y: 1.9, z: -5, thick: 0.02, cast: false }));      // back wall
    labGroup.add(ibox(0.18, 3.8, 10, '#20252d', { y: 1.9, x: -7, thick: 0.02, cast: false }));      // left wall
    labGroup.add(ibox(0.18, 3.8, 10, '#20252d', { y: 1.9, x: 7, thick: 0.02, cast: false }));       // right wall
    // ceiling fluorescent strips (cold)
    for (const lx of [-2.2, 2.2]) {
      const strip = ibox(4.6, 0.07, 0.34, '#cfe4ff', { x: lx, y: 3.45, z: -1.5, thick: 0.008, cast: false });
      strip.material = new THREE.MeshBasicMaterial({ color: '#d7ecff' });
      labGroup.add(strip);
    }
    // workbench + legs
    labGroup.add(ibox(3.4, 0.09, 0.95, '#333941', { y: 0.95, z: -3.7, thick: 0.014, cast: false }));
    for (const [lx, lz] of [[-1.6, -4.1], [1.6, -4.1], [-1.6, -3.3], [1.6, -3.3]])
      labGroup.add(ibox(0.07, 0.95, 0.07, '#262b31', { x: lx, y: 0.475, z: lz, thick: 0.008, cast: false }));
    // monitors: charts, SPECIMEN-47 telemetry, DNA scanner
    const mkMonTex = (kind) => {
      const [mc, mg] = cv(256, 176);
      mg.fillStyle = '#04120c'; mg.fillRect(0, 0, 256, 176);
      mg.strokeStyle = '#0f3d2a'; mg.lineWidth = 1;
      for (let gx = 0; gx < 256; gx += 16) { mg.beginPath(); mg.moveTo(gx, 0); mg.lineTo(gx, 176); mg.stroke(); }
      for (let gy = 0; gy < 176; gy += 16) { mg.beginPath(); mg.moveTo(0, gy); mg.lineTo(256, gy); mg.stroke(); }
      mg.fillStyle = '#37ffa8'; mg.font = 'bold 15px monospace';
      if (kind === 0) {
        mg.fillText('SPECIMEN 47 — VIRULENCE', 12, 24);
        mg.fillText('98.2%   LETHALITY 91%', 12, 44);
        mg.strokeStyle = '#37ffa8'; mg.lineWidth = 2.4; mg.beginPath();
        for (let px = 0; px < 240; px++) {
          const py = 150 - 62 * Math.abs(Math.sin(px * 0.055) * Math.sin(px * 0.013));
          px === 0 ? mg.moveTo(8 + px, py) : mg.lineTo(8 + px, py);
        }
        mg.stroke();
      } else if (kind === 1) {
        mg.fillText('DISPERSAL VECTOR: AIRBORNE', 12, 24);
        mg.fillText('INCUBATION 00:04:00', 12, 44);
        // world dots going red
        for (let i = 0; i < 26; i++) {
          mg.fillStyle = i < 19 ? '#ff5f4a' : '#37ffa8';
          mg.beginPath(); mg.arc(16 + (i * 37) % 224, 66 + (i * 53) % 92, 3.4, 0, 7); mg.fill();
        }
      } else {
        mg.fillText('GENOME SPLICING ACTIVE', 12, 24);
        mg.strokeStyle = '#37ffa8'; mg.lineWidth = 3;
        for (let s = 0; s < 2; s++) {
          mg.beginPath();
          for (let px = 0; px <= 232; px += 4) {
            const py = 110 + s * 26 - 22 * Math.sin(px * 0.048);
            px === 0 ? mg.moveTo(12 + px, py) : mg.lineTo(12 + px, py);
          }
          mg.stroke();
        }
        for (let px = 12; px <= 244; px += 26) {
          mg.strokeStyle = '#1f8f5f'; mg.lineWidth = 1.6;
          mg.beginPath(); mg.moveTo(px, 110 - 22 * Math.sin(px * 0.048)); mg.lineTo(px, 136 - 22 * Math.sin(px * 0.048)); mg.stroke();
        }
      }
      const mt = new THREE.CanvasTexture(mc); mt.colorSpace = THREE.SRGBColorSpace; return mt;
    };
    for (const [mi, mx] of [[0, -1.15], [1, 0], [2, 1.15]]) {
      const mon = new THREE.Mesh(new THREE.PlaneGeometry(0.92, 0.62),
        new THREE.MeshBasicMaterial({ map: mkMonTex(mi), toneMapped: false }));
      mon.position.set(mx, 1.62, -4.05); mon.rotation.y = 0.14 - mi * 0.14;
      labGroup.add(mon);
      labGroup.add(ibox(0.98, 0.05, 0.06, '#14171b', { x: mx, y: 1.28, z: -4.02, ry: 0.14 - mi * 0.14, thick: 0.006, cast: false }));
    }
    // glowing vial rack (the weapon itself)
    const vialGlowMat = new THREE.MeshBasicMaterial({ color: '#8effc0', toneMapped: false });
    for (const [vx, vc] of [[-1.52, '#8effc0'], [-1.42, '#ffd25c'], [-1.32, '#8effc0'], [-1.22, '#ff7a5c']]) {
      labGroup.add(icyl(0.030, 0.030, 0.15, '#bfe8d2', { x: vx, y: 1.07, z: -3.62, thick: 0.004, cast: false }));
      const glow = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.024, 10), vialGlowMat);
      glow.position.set(vx, 1.155, -3.62); labGroup.add(glow);
    }
    // specimen CAGE (right side) with sliding door — this is where they keep "them"
    const cage = new THREE.Group(); cage.position.set(3.1, 0, -2.2);
    const barMat = toon('#4a5158');
    for (let bx = -0.95; bx <= 0.95; bx += 0.19) {
      const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 2.5, 8), barMat);
      bar.position.set(bx, 1.25, -0.95); cage.add(bar);
    }
    for (const bz of [-0.95, 0.0, 0.95]) {
      const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 2.5, 8), barMat);
      bar.position.set(-0.95, 1.25, bz); cage.add(bar);
    }
    cage.add(ibox(2.1, 0.09, 2.1, '#3a4046', { y: 2.52, thick: 0.01, cast: false }));
    cageDoor = new THREE.Group();
    for (let dx = -0.76; dx <= 0.76; dx += 0.19) {
      const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 2.5, 8), barMat);
      bar.position.set(dx, 1.25, 0.95); cageDoor.add(bar);
    }
    cageDoor.add(ibox(1.7, 0.08, 0.08, '#3a4046', { y: 2.45, z: 0.95, thick: 0.008, cast: false }));
    cageDoor.add(ibox(1.7, 0.08, 0.08, '#3a4046', { y: 0.06, z: 0.95, thick: 0.008, cast: false }));
    cage.add(cageDoor);
    const cageDark = ibox(1.9, 2.4, 1.9, '#07090c', { y: 1.2, thick: 0.0, edges: false, cast: false });
    cage.add(cageDark);
    labGroup.add(cage);
    // hazard stripes on floor in front of cage
    for (let hy = 0; hy < 6; hy++)
      labGroup.add(ibox(1.9 - hy * 0.12, 0.012, 0.16, hy % 2 ? '#c9a227' : '#23262b', { x: 3.1, y: 0.008, z: -0.85 + hy * 0.3, thick: 0.002, edges: false, cast: false }));
    // ---- V7: THE GLASS CONTAINERS — where the subjects turn ----
    labContainers = [];
    const containDefs = [[-0.62, -2.10], [0.75, -2.05]];
    for (const [ci, [cxx, czz]] of containDefs.entries()) {
      const cg = new THREE.Group(); cg.position.set(cxx, 0, czz);
      // frosted-glass tall cylinder (open-topped vessel)
      const glass = new THREE.Mesh(new THREE.CylinderGeometry(0.66, 0.72, 2.0, 24, 1, true),
        new THREE.MeshBasicMaterial({ color: '#2c4b3f', transparent: true, opacity: 0.30, side: THREE.DoubleSide, toneMapped: false }));
      glass.position.y = 1.22; cg.add(glass);
      // steel base + rim rings
      cg.add(icyl(0.80, 0.86, 0.14, '#39424c', { y: 0.07, thick: 0.008, cast: false }));
      cg.add(icyl(0.78, 0.78, 0.07, '#39424c', { y: 2.26, thick: 0.006, cast: false }));
      // side hose to ceiling
      cg.add(icyl(0.045, 0.045, 1.3, '#2b322a', { x: 0.55, y: 1.75, rz: Math.PI / 2 - 0.35, seg: 8, thick: 0.006, cast: false }));
      // CHEMICAL RAIN — falling droplet instanced planes inside the glass (set by updateIntroLab)
      const rainMat = new THREE.MeshBasicMaterial({ color: '#8fffc4', transparent: true, opacity: 0.9, toneMapped: false, depthWrite: false });
      const rainGeo = new THREE.PlaneGeometry(0.028, 0.11);
      const rain = new THREE.InstancedMesh(rainGeo, rainMat, 34);
      rain.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
      rain.frustumCulled = false;
      cg.add(rain);
      // venting vapor puffs at the base
      const fogMat = new THREE.MeshBasicMaterial({ color: '#b9ffd9', transparent: true, opacity: 0.16, toneMapped: false, depthWrite: false });
      const fog = new THREE.InstancedMesh(new THREE.PlaneGeometry(0.7, 0.7), fogMat, 8);
      fog.instanceMatrix.setUsage(THREE.DynamicDrawUsage); fog.frustumCulled = false;
      cg.add(fog);
      // sickly fill-glow at the bottom (grows as they turn)
      const fillMat = new THREE.MeshBasicMaterial({ color: '#59d98c', transparent: true, opacity: 0.0, toneMapped: false, depthWrite: false });
      const fill = new THREE.Mesh(new THREE.CylinderGeometry(0.62, 0.68, 2.0, 20, 1, true), fillMat);
      fill.position.y = 1.22; cg.add(fill);
      // top spotlight cone (always visible — the specimens are always lit)
      const cone = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.92, 2.35, 20, 1, true),
        new THREE.MeshBasicMaterial({ color: '#eafff4', transparent: true, opacity: 0.10, side: THREE.DoubleSide, toneMapped: false, depthWrite: false }));
      cone.position.y = 1.30; cg.add(cone);
      labGroup.add(cg);
      labContainers.push({ group: cg, rain, fog, fill, seed: ci * 1.37 + 2.0 });
    }
    // ---- V7: THE BUTTON — a heavy red master-switch console beside the containers ----
    labConsole = new THREE.Group(); labConsole.position.set(1.85, 0, -2.35);
    labConsole.add(ibox(0.66, 0.9, 0.44, '#262c34', { y: 0.45, ry: -0.10, thick: 0.012, cast: false }));
    labConsole.add(ibox(0.60, 0.05, 0.40, '#11161b', { y: 0.93, ry: -0.10, thick: 0.006, cast: false }));
    for (const [px, pz] of [[-0.14, -0.06], [0.02, 0.06]])
      labConsole.add(ibox(0.11, 0.035, 0.11, '#c9a227', { x: px, y: 0.95, z: pz, ry: -0.10, thick: 0.004, cast: false }));
    // the big covered red button — glass safety cover flips up when armed!
    labButtonBase = new THREE.Group(); labButtonBase.position.set(0.12, 0.945, -0.02); labButtonBase.rotation.y = -0.10;
    labButtonBase.add(icyl(0.09, 0.10, 0.05, '#101317', { thick: 0.004, cast: false }));
    labButtonMat = new THREE.MeshBasicMaterial({ color: '#ff2f1e', toneMapped: false });
    const labButtonCap = new THREE.Mesh(new THREE.SphereGeometry(0.065, 14, 10), labButtonMat);
    labButtonCap.position.y = 0.035; labButtonBase.add(labButtonCap);
    labConsole.add(labButtonBase);
    const cover = new THREE.Mesh(new THREE.SphereGeometry(0.105, 14, 10, 0, Math.PI * 2, 0, Math.PI / 2),
      new THREE.MeshBasicMaterial({ color: '#ffd24c', transparent: true, opacity: 0.30, toneMapped: false }));
    cover.position.y = 0.045; labButtonBase.add(cover);
    labButtonCover = cover;
    labGroup.add(labConsole);
    // ceiling alarm beacon
    labAlarmMat = new THREE.MeshBasicMaterial({ color: '#ff2a1a', toneMapped: false });
    const labAlarm = new THREE.Mesh(new THREE.SphereGeometry(0.085, 12, 10), labAlarmMat);
    labAlarm.position.set(2.4, 3.3, -2.2); labGroup.add(labAlarm);
  }
  scene.add(labGroup);

  const newsGroup = new THREE.Group();
  newsGroup.position.set(-40, 0, -48);
  let tickerTex;
  {
    newsGroup.add(ibox(13, 0.12, 9, '#14171d', { y: -0.06, thick: 0.02, cast: false }));
    newsGroup.add(ibox(13, 4.2, 0.18, '#10141b', { y: 2.1, z: -3.6, thick: 0.02, cast: false }));
    // studio backdrop: BREAKING NEWS wall (big) + red lower band
    const [nc, ng] = cv(1024, 320);
    ng.fillStyle = '#081a33'; ng.fillRect(0, 0, 1024, 320);
    // skyline silhouette
    ng.fillStyle = '#0c2444';
    for (let b = 0; b < 16; b++) {
      const bw2 = 34 + (b * 37) % 40, bh2 = 70 + (b * 61) % 150, bx2 = b * 64;
      ng.fillRect(bx2, 320 - bh2, bw2, bh2);
      ng.fillStyle = '#123058';
      for (let wy = 320 - bh2 + 12; wy < 312; wy += 22) for (let wx = bx2 + 6; wx < bx2 + bw2 - 8; wx += 14) ng.fillRect(wx, wy, 6, 9);
      ng.fillStyle = '#0c2444';
    }
    ng.fillStyle = '#c8102e'; ng.fillRect(0, 0, 1024, 86);
    ng.fillStyle = '#ffffff'; ng.font = '900 56px Arial'; ng.textAlign = 'left';
    ng.fillText('BREAKING NEWS', 36, 62);
    ng.fillStyle = '#ffffff'; ng.font = '900 40px Arial';
    ng.fillText('DEADLY VIRUS SPREADING — STAY INDOORS', 36, 148);
    ng.fillStyle = '#9fc3e8'; ng.font = 'bold 30px Arial';
    ng.fillText('HOSPITALS OVERWHELMED · SCHOOLS CLOSED · TRANSIT HALTED', 36, 196);
    ng.fillStyle = '#c8102e'; ng.font = 'bold 34px Arial';
    ng.fillText('NATIONWIDE EMERGENCY DECLARED', 36, 252);
    const newsWallTex = new THREE.CanvasTexture(nc); newsWallTex.colorSpace = THREE.SRGBColorSpace;
    const newsWall = new THREE.Mesh(new THREE.PlaneGeometry(9.6, 3.0),
      new THREE.MeshBasicMaterial({ map: newsWallTex, toneMapped: false }));
    newsWall.position.set(0, 2.15, -3.5); newsGroup.add(newsWall);
    // scrolling ticker strip (texture offset animated in main)
    const [tkc, tkg] = cv(2048, 96);
    tkg.fillStyle = '#c8102e'; tkg.fillRect(0, 0, 2048, 96);
    tkg.fillStyle = '#ffffff'; tkg.font = '900 44px Arial'; tkg.textAlign = 'left';
    tkg.fillText('BREAKING: FAST-SPREADING ILLNESS REPORTED CITYWIDE · AUTHORITIES URGE RESIDENTS TO STAY INDOORS · DO NOT APPROACH ANYONE ACTING CONFUSED OR VIOLENT · HOSPITALS OVERWHELMED · SCHOOLS AND TRANSIT CLOSED · ', 18, 62);
    tickerTex = new THREE.CanvasTexture(tkc); tickerTex.colorSpace = THREE.SRGBColorSpace;
    tickerTex.wrapS = THREE.RepeatWrapping; tickerTex.repeat.x = 0.5;
    const ticker = new THREE.Mesh(new THREE.PlaneGeometry(9.6, 0.44),
      new THREE.MeshBasicMaterial({ map: tickerTex, toneMapped: false }));
    ticker.position.set(0, 0.62, -3.48); newsGroup.add(ticker);
    // anchor desk
    newsGroup.add(ibox(3.4, 0.1, 1.15, '#2a2f3a', { y: 0.78, z: -1.25, thick: 0.014, cast: false }));
    newsGroup.add(ibox(3.4, 0.72, 0.1, '#20242e', { y: 0.42, z: -0.72, thick: 0.012, cast: false }));
    // desk papers + laptop
    newsGroup.add(ibox(0.34, 0.012, 0.26, '#e8e4da', { x: -0.95, y: 0.835, z: -1.3, ry: 0.3, thick: 0.003, cast: false }));
    newsGroup.add(ibox(0.42, 0.015, 0.3, '#191d24', { x: 0.95, y: 0.84, z: -1.3, ry: -0.16, thick: 0.004, cast: false }));
    // side LIVE screens
    for (const sx of [-4.4, 4.4]) {
      const sc = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 1.06),
        new THREE.MeshBasicMaterial({ map: newsWallTex, toneMapped: false }));
      sc.position.set(sx, 2.0, -3.44); sc.rotation.y = sx > 0 ? -0.22 : 0.22;
      newsGroup.add(sc);
    }
  }
  scene.add(newsGroup);

  // =========================================================================
  // 6b-V7. GLASS-CONTAINER CHEMICAL RAIN + MASTER BUTTON UPDATER
  // (pure render-time function of t — deterministic under any render order)
  // =========================================================================
  function updateIntroLab(t) {
    if (!labContainers.length) return;
    const drip = Math.max(0, Math.min(1, (t - 4.30) / 0.80));
    const turn = (t >= 5.70 && t < 6.60) ? 1 : 0;
    const pressed = (t >= 4.30) ? 1 : 0;
    const M = new THREE.Matrix4();
    for (const ct of labContainers) {
      const { group, rain, fog, fill, seed } = ct;
      if (drip > 0) {
        const n = Math.max(1, Math.round(34 * drip));
        for (let i = 0; i < 34; i++) {
          const ang = seed * 2.1 + i * 2.399963;
          const rr = (i / 34) * 0.58 + 0.03;
          const speed = 0.30 + ((i * 7 + Math.round(seed * 13)) % 10) * 0.055;
          const yy = 2.25 - ((t * speed + i * 0.317) % 1.0) * 2.15;
          M.makeRotationY(-group.rotation.y);
          M.setPosition(group.position.x + Math.cos(ang) * rr, yy, group.position.z + Math.sin(ang) * rr);
          if (i >= n) M.setPosition(0, -9, 0);
          rain.setMatrixAt(i, M);
        }
        rain.count = 34;
        rain.instanceMatrix.needsUpdate = true;
      } else {
        rain.count = 0;
      }
      for (let i = 0; i < 8; i++) {
        const fa = t * 0.4 + i * 0.785398 + seed;
        const fy = 0.14 + ((t * 0.12 + i * 0.125 + seed * 0.1) % 1.0) * 0.65 * drip;
        M.makeRotationY(-group.rotation.y);
        M.setPosition(group.position.x + Math.cos(fa) * 0.48, fy, group.position.z + Math.sin(fa) * 0.48);
        fog.setMatrixAt(i, M);
      }
      fog.count = drip > 0 ? 8 : 0;
      fog.instanceMatrix.needsUpdate = true;
      fill.material.opacity = turn ? 0.26 : (drip > 0 ? 0.10 : 0);
      fill.material.color.set(turn ? '#49ff8e' : '#59d98c');
    }
    if (labButtonCover) labButtonCover.rotation.x = pressed ? -1.45 : 0;
    if (labButtonBase) labButtonBase.children[1].position.y = pressed ? 0.018 : 0.035;
  }

  // =========================================================================
  // 6c. INTRO DESTRUCTION PROPS — fire glows, embers source, smoke billboards
  // =========================================================================
  const introFireGroup = new THREE.Group();
  {
    const fireMat = new THREE.MeshBasicMaterial({
      color: '#ff7a26', transparent: true, opacity: 0.85, depthWrite: false,
      blending: THREE.AdditiveBlending, toneMapped: false,
    });
    for (const [fx2, fy2, fz2, fs2] of [[-1.9, 0.75, 17.5, 1.0], [2.3, 0.95, 15.2, 1.3], [-3.2, 0.6, 14.8, 0.8]]) {
      const flame = new THREE.Mesh(new THREE.ConeGeometry(0.55 * fs2, 1.7 * fs2, 10, 3, true), fireMat);
      flame.position.set(fx2, fy2, fz2);
      introFireGroup.add(flame);
    }
  }
  scene.add(introFireGroup);
  const smokeGroup = new THREE.Group();
  {
    const [smc, smg] = cv(128, 128);
    for (let i = 0; i < 14; i++) {
      const sx2 = 24 + (i * 41) % 84, sy2 = 24 + (i * 67) % 84, sr2 = 14 + (i * 29) % 22;
      const grd2 = smg.createRadialGradient(sx2, sy2, 1, sx2, sy2, sr2);
      grd2.addColorStop(0, 'rgba(30,26,28,0.5)'); grd2.addColorStop(1, 'rgba(30,26,28,0)');
      smg.fillStyle = grd2; smg.beginPath(); smg.arc(sx2, sy2, sr2, 0, 7); smg.fill();
    }
    const smokeTex = new THREE.CanvasTexture(smc); smokeTex.colorSpace = THREE.SRGBColorSpace;
    for (const [px2, py2, pz2, ps2] of [[-1.9, 2.6, 17.5, 2.6], [2.3, 3.0, 15.2, 3.3], [-3.2, 2.4, 14.8, 2.2]]) {
      const sm = new THREE.Mesh(new THREE.PlaneGeometry(ps2, ps2),
        new THREE.MeshBasicMaterial({ map: smokeTex, transparent: true, opacity: 0.5, depthWrite: false, toneMapped: false }));
      sm.position.set(px2, py2, pz2);
      smokeGroup.add(sm);
    }
  }
  scene.add(smokeGroup);

  const shaftMat = new THREE.MeshBasicMaterial({ color: '#ffe6b8', transparent: true, opacity: 0.07, depthWrite: false, side: THREE.DoubleSide });
  const lightShafts = new THREE.Group();
  for (const sx of [-3.3, 0.0, 3.3]) {
    const sh = new THREE.Mesh(new THREE.PlaneGeometry(2.4, 5.2), shaftMat);
    sh.position.set(sx, 1.55, 5.4);
    sh.rotation.x = -0.62;
    lightShafts.add(sh);
  }
  storeGroup.add(lightShafts);

  const flashConeMat = new THREE.MeshBasicMaterial({ color: '#fff4c2', transparent: true, opacity: 0.20, depthWrite: false, side: THREE.DoubleSide });
  // Volumetric Flashlight Beam — apex (local +y, rotated to +z) must point at the target.
  const flashCone = new THREE.Mesh(new THREE.ConeGeometry(0.95, 4.2, 18, 1, true), flashConeMat);
  flashCone.rotation.x = Math.PI / 2;
  scene.add(flashCone);

  return {
    root,
    storeGroup,
    streetGroup,
    backGroup,
    alleyGroup,
    undergroundGroup,
    fluorStrips,
    fridgeLights,
    deadboltBar,
    shutterWinPivot,
    shutterDoorPivot,
    rationGroup,
    counterBackpack,
    abandonedCar,
    swerveCar,
    patrolCar,
    trafficCar,
    parkedCarA,
    parkedCarB,
    skyDome,
    shopWindows,
    streetGlow,
    tunnelFig,
    introOverlayTex,
    patrolFlashers: patrolCar.userData.flashers || null,
    sunriseDamageGroup,
    streetBulbs,
    emergBulbMat,
    backDoorPivot,
    alleyMaintDoorPivot,
    ugMaintDoorPivot,
    ugDoorBackGlow,
    ugLampMat,
    ugBulkMat,
    ugBulkGlowMat,
    alleyLampMat,
    ugRadio,
    ugRadioLedMat,
    tunnelEyes,
    heldPhone,
    phoneScrMat,
    phoneGlareMat,
    alert1Tex,
    alert2Tex,
    mapTex,
    social0Tex,
    social1Tex,
    labGroup,
    labAlarmMat,
    cageDoor,
    labContainers,
    labConsole,
    labButtonMat,
    updateIntroLab,
    newsGroup,
    tickerTex,
    introFireGroup,
    smokeGroup,
    lightShafts,
    shaftMat,
    flashCone,
    neonMat,
    posScreenMat,
    cctvScreenMat,
  };
}
