// Face system: a face = eyes + brows + mouth + extras, drawn on a canvas decal that wraps the head.
// Expressions are named presets. Blinking and talking swap single parts at render time.
import * as THREE from 'three';
import { canvasTex } from './util.js';

export const FW = 512, FH = 320; // decal canvas (covers ~103° of the head, 0.72 units tall)

export const EXPRESSIONS = {
  smile: { eyes: 'dot', brows: 'none', mouth: 'smile' },
  grin: { eyes: 'dot', brows: 'none', mouth: 'grin' },
  happy: { eyes: 'closed', brows: 'none', mouth: 'grin' },
  laugh: { eyes: 'closed', brows: 'up', mouth: 'laugh' },
  smirk: { eyes: 'half', brows: 'one', mouth: 'smirk' },
  surprised: { eyes: 'dot', brows: 'up', mouth: 'o' },
  shock: { eyes: 'wide', brows: 'up', mouth: 'bigO' },
  scared: { eyes: 'wide', brows: 'sad', mouth: 'wavy', extras: ['sweat'] },
  sad: { eyes: 'dot', brows: 'sad', mouth: 'frown' },
  cry: { eyes: 'cry', brows: 'sad', mouth: 'sadOpen', extras: ['tears'] },
  angry: { eyes: 'dot', brows: 'angry', mouth: 'frown' },
  furious: { eyes: 'squeeze', brows: 'angry', mouth: 'teeth', extras: ['vein'], tint: '#e8432f' },
  sleepy: { eyes: 'half', brows: 'none', mouth: 'flat' },
  asleep: { eyes: 'shut', brows: 'none', mouth: 'o' },
  yawn: { eyes: 'shut', brows: 'up', mouth: 'yawn' },
  strain: { eyes: 'squeeze', brows: 'angry', mouth: 'teeth', extras: ['sweat'], tint: '#e8432f' },
  sus: { eyes: 'side', brows: 'flat', mouth: 'flat' },
  love: { eyes: 'heart', brows: 'up', mouth: 'smile', extras: ['blush'] },
  dead: { eyes: 'x', brows: 'none', mouth: 'wavy' },
  wink: { eyes: 'wink', brows: 'one', mouth: 'grin' },
  nervous: { eyes: 'dot', brows: 'sad', mouth: 'wavy', extras: ['sweat'] },
  blank: { eyes: 'tiny', brows: 'none', mouth: 'flat' },
  evil: { eyes: 'half', brows: 'angry', mouth: 'grin' },
  cool: { eyes: 'dot', brows: 'none', mouth: 'smirk', extras: ['shades'] },
  disgust: { eyes: 'half', brows: 'angry', mouth: 'tongue' },
  proud: { eyes: 'closed', brows: 'up', mouth: 'smile', extras: ['blush'] },
  dizzy: { eyes: 'spiral', brows: 'none', mouth: 'wavy' },
  cringe: { eyes: 'squeeze', brows: 'sad', mouth: 'teeth' },
  talk: { eyes: 'dot', brows: 'none', mouth: 'open' },
};
export const EXPRESSION_NAMES = Object.keys(EXPRESSIONS);

const BLK = '#151515';
function eyes(g, type, side) { // side: -1 left (viewer's left), +1 right
  const x = FW / 2 + side * 76, y = 128;
  g.lineCap = 'round'; g.lineJoin = 'round'; g.strokeStyle = BLK; g.fillStyle = BLK;
  const dot = (rx = 15, ry = 24) => { g.fillStyle = BLK; g.beginPath(); g.ellipse(x, y, rx, ry, 0, 0, 7); g.fill(); g.fillStyle = '#fff'; g.beginPath(); g.ellipse(x - 5, y - 9, 5, 6, 0, 0, 7); g.fill(); };
  switch (type) {
    case 'dot': dot(); break;
    case 'tiny': g.beginPath(); g.arc(x, y, 8, 0, 7); g.fill(); break;
    case 'closed': g.lineWidth = 11; g.beginPath(); g.arc(x, y + 10, 19, Math.PI * 1.12, Math.PI * 1.88); g.stroke(); break;
    case 'shut': g.lineWidth = 10; g.beginPath(); g.moveTo(x - 20, y + 4); g.quadraticCurveTo(x, y + 14, x + 20, y + 4); g.stroke(); break;
    case 'half': dot(15, 18); g.fillStyle = '#00000000'; g.lineWidth = 9; g.beginPath(); g.moveTo(x - 22, y - 8); g.lineTo(x + 22, y - 8); g.stroke(); break;
    case 'wide': g.fillStyle = '#fff'; g.lineWidth = 8; g.beginPath(); g.ellipse(x, y, 30, 34, 0, 0, 7); g.fill(); g.stroke(); g.fillStyle = BLK; g.beginPath(); g.arc(x, y + 4, 9, 0, 7); g.fill(); break;
    case 'side': g.fillStyle = '#fff'; g.lineWidth = 7; g.beginPath(); g.ellipse(x, y, 26, 20, 0, 0, 7); g.fill(); g.stroke(); g.fillStyle = BLK; g.beginPath(); g.arc(x + 13, y + 2, 10, 0, 7); g.fill(); break;
    case 'squeeze': g.lineWidth = 11; g.beginPath(); g.moveTo(x - side * 22, y - 16); g.lineTo(x + side * 18, y); g.lineTo(x - side * 22, y + 16); g.stroke(); break;
    case 'x': g.lineWidth = 10; g.beginPath(); g.moveTo(x - 17, y - 17); g.lineTo(x + 17, y + 17); g.moveTo(x + 17, y - 17); g.lineTo(x - 17, y + 17); g.stroke(); break;
    case 'heart': g.fillStyle = '#ff3b6b'; g.beginPath(); g.moveTo(x, y + 22); g.bezierCurveTo(x - 40, y - 4, x - 18, y - 34, x, y - 12); g.bezierCurveTo(x + 18, y - 34, x + 40, y - 4, x, y + 22); g.fill(); break;
    case 'cry': dot(14, 20); g.fillStyle = '#7cc6ff'; g.beginPath(); g.ellipse(x, y + 18, 18, 9, 0, 0, Math.PI); g.fill(); break;
    case 'wink': if (side < 0) dot(); else { g.lineWidth = 11; g.beginPath(); g.arc(x, y + 10, 19, Math.PI * 1.12, Math.PI * 1.88); g.stroke(); } break;
    case 'spiral': g.lineWidth = 6; g.beginPath(); for (let a = 0; a < Math.PI * 6; a += .2) { const r = 2 + a * 2.2; g.lineTo(x + Math.cos(a) * r, y + Math.sin(a) * r); } g.stroke(); break;
    default: dot();
  }
}
function brows(g, type) {
  if (type === 'none') return;
  g.strokeStyle = BLK; g.lineWidth = 10; g.lineCap = 'round';
  for (const s of [-1, 1]) {
    const x = FW / 2 + s * 76, y = 72; g.beginPath();
    if (type === 'up') { g.moveTo(x - 22, y + 2); g.quadraticCurveTo(x, y - 14, x + 22, y + 2); }
    else if (type === 'angry') { g.moveTo(x - s * 26, y - 10); g.lineTo(x + s * 20, y + 10); }
    else if (type === 'sad') { g.moveTo(x - s * 26, y + 8); g.lineTo(x + s * 20, y - 8); }
    else if (type === 'flat') { g.moveTo(x - 22, y + 4); g.lineTo(x + 22, y + 4); }
    else if (type === 'one') { if (s < 0) { g.moveTo(x - 22, y + 6); g.lineTo(x + 22, y + 6); } else { g.moveTo(x - 22, y + 2); g.quadraticCurveTo(x, y - 16, x + 22, y - 4); } }
    g.stroke();
  }
}
function mouth(g, type) {
  const x = FW / 2, y = 228; g.strokeStyle = BLK; g.fillStyle = BLK; g.lineCap = 'round'; g.lineJoin = 'round'; g.lineWidth = 11;
  const openShape = (w, top, bot, tongue = true) => { g.fillStyle = BLK; g.beginPath(); g.moveTo(x - w, y + top); g.quadraticCurveTo(x, y + top + 4, x + w, y + top); g.quadraticCurveTo(x + w * .9, y + bot, x, y + bot); g.quadraticCurveTo(x - w * .9, y + bot, x - w, y + top); g.fill(); if (tongue) { g.save(); g.clip(); g.fillStyle = '#e8566a'; g.beginPath(); g.ellipse(x, y + bot - 6, w * .55, 16, 0, 0, 7); g.fill(); g.restore(); } };
  switch (type) {
    case 'smile': g.beginPath(); g.arc(x, y - 52, 62, .23 * Math.PI, .77 * Math.PI); g.stroke(); break;
    case 'grin': openShape(56, -22, 34); break;
    case 'laugh': openShape(62, -26, 46); break;
    case 'open': g.beginPath(); g.ellipse(x, y, 26, 22, 0, 0, 7); g.fill(); break;
    case 'o': g.beginPath(); g.ellipse(x, y + 2, 15, 19, 0, 0, 7); g.fill(); break;
    case 'bigO': g.beginPath(); g.ellipse(x, y + 4, 26, 36, 0, 0, 7); g.fill(); break;
    case 'yawn': g.beginPath(); g.ellipse(x, y + 2, 30, 46, 0, 0, 7); g.fill(); g.fillStyle = '#e8566a'; g.beginPath(); g.ellipse(x, y + 30, 18, 12, 0, 0, 7); g.fill(); break;
    case 'flat': g.beginPath(); g.moveTo(x - 30, y); g.lineTo(x + 30, y); g.stroke(); break;
    case 'frown': g.beginPath(); g.arc(x, y + 50, 50, 1.25 * Math.PI, 1.75 * Math.PI); g.stroke(); break;
    case 'sadOpen': g.beginPath(); g.moveTo(x - 40, y + 26); g.quadraticCurveTo(x, y - 26, x + 40, y + 26); g.closePath(); g.fill(); break;
    case 'wavy': g.beginPath(); g.moveTo(x - 46, y + 4); for (let i = 1; i <= 8; i++) g.lineTo(x - 46 + i * 11.5, y + (i % 2 ? -8 : 6)); g.stroke(); break;
    case 'teeth': g.fillStyle = '#fff'; g.lineWidth = 8; g.beginPath(); g.roundRect(x - 54, y - 18, 108, 38, 10); g.fill(); g.stroke(); g.beginPath(); for (let xx = x - 32; xx < x + 50; xx += 22) { g.moveTo(xx, y - 18); g.lineTo(xx, y + 20); } g.moveTo(x - 54, y + 1); g.lineTo(x + 54, y + 1); g.stroke(); break;
    case 'smirk': g.beginPath(); g.moveTo(x - 46, y + 2); g.quadraticCurveTo(x + 10, y + 22, x + 48, y - 18); g.stroke(); break;
    case 'tongue': g.beginPath(); g.moveTo(x - 40, y); g.lineTo(x + 40, y); g.stroke(); g.fillStyle = '#e8566a'; g.beginPath(); g.ellipse(x + 8, y + 16, 16, 18, 0, 0, Math.PI); g.fill(); break;
    default: g.beginPath(); g.arc(x, y - 52, 62, .23 * Math.PI, .77 * Math.PI); g.stroke();
  }
}
function extras(g, list) {
  for (const e of list) {
    if (e === 'blush') { g.fillStyle = 'rgba(255,90,110,.45)'; for (const s of [-1, 1]) { g.beginPath(); g.ellipse(FW / 2 + s * 120, 196, 30, 14, 0, 0, 7); g.fill(); } }
    if (e === 'freckles') { g.fillStyle = 'rgba(120,60,20,.6)'; for (const s of [-1, 1]) for (let i = 0; i < 4; i++) { g.beginPath(); g.arc(FW / 2 + s * (100 + (i % 2) * 18), 184 + (i >> 1) * 14, 4, 0, 7); g.fill(); } }
    if (e === 'sweat') { g.fillStyle = 'rgba(90,180,255,.95)'; const x = FW / 2 + 150, y = 40; g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + 26, y + 44, x, y + 52); g.quadraticCurveTo(x - 26, y + 44, x, y); g.fill(); }
    if (e === 'tears') { g.fillStyle = 'rgba(110,190,255,.9)'; for (const s of [-1, 1]) g.fillRect(FW / 2 + s * 76 - 8, 150, 16, 120); }
    if (e === 'vein') { g.strokeStyle = '#c0182a'; g.lineWidth = 8; const x = FW / 2 + 140, y = 40; g.beginPath(); for (const [a, b, c, d] of [[-14, -4, -4, -4], [-4, -14, -4, -4], [14, 4, 4, 4], [4, 14, 4, 4]]) { g.moveTo(x + a, y + b); g.quadraticCurveTo(x + c * 2, y + d * 2, x + a / 3 + c, y + b / 3 + d); } g.stroke(); }
    if (e === 'glasses') { g.strokeStyle = '#111'; g.lineWidth = 9; g.beginPath(); for (const s of [-1, 1]) g.roundRect(FW / 2 + s * 76 - 40, 96, 80, 66, 16); g.moveTo(FW / 2 - 36, 122); g.lineTo(FW / 2 + 36, 122); g.stroke(); }
    if (e === 'shades') { g.fillStyle = '#0d0d0f'; g.beginPath(); for (const s of [-1, 1]) g.roundRect(FW / 2 + s * 76 - 46, 100, 92, 58, [8, 8, 26, 26]); g.fill(); g.fillRect(FW / 2 - 40, 108, 80, 12); g.fillStyle = 'rgba(255,255,255,.35)'; g.fillRect(FW / 2 - 108, 110, 30, 8); g.fillRect(FW / 2 + 44, 110, 30, 8); }
    if (e === 'stache') { g.fillStyle = '#2a1a0e'; const x = FW / 2, y = 186; g.beginPath(); g.moveTo(x, y); g.bezierCurveTo(x - 30, y - 16, x - 76, y - 6, x - 86, y + 26); g.bezierCurveTo(x - 56, y + 6, x - 26, y + 18, x, y + 12); g.bezierCurveTo(x + 26, y + 18, x + 56, y + 6, x + 86, y + 26); g.bezierCurveTo(x + 76, y - 6, x + 30, y - 16, x, y); g.fill(); }
  }
}

const cache = {};
export function faceMaterial(parts) {
  const key = [parts.eyes, parts.brows, parts.mouth, (parts.extras || []).join('+')].join('|');
  if (cache[key]) return cache[key];
  const t = canvasTex(FW, FH, (g) => {
    const ex = parts.extras || [];
    // draw order: eyes under glasses/shades
    brows(g, parts.brows || 'none');
    eyes(g, parts.eyes || 'dot', -1); eyes(g, parts.eyes || 'dot', 1);
    mouth(g, parts.mouth || 'smile');
    extras(g, ex);
  });
  cache[key] = new THREE.MeshStandardMaterial({ map: t, transparent: true, alphaTest: .08, roughness: .55, polygonOffset: true, polygonOffsetFactor: -3, depthWrite: false });
  return cache[key];
}
// resolve an expression name (+ persistent actor extras) into parts; blink/talk overrides
export function faceParts(expr, actorExtras = [], { blink = false, mouthOpen = false } = {}) {
  const base = EXPRESSIONS[expr] || EXPRESSIONS.smile;
  const p = { ...base, extras: [...(base.extras || []), ...actorExtras] };
  if (p.extras.includes('shades') && blink) blink = false;
  if (blink && !['closed', 'shut', 'x', 'heart', 'squeeze', 'spiral'].includes(p.eyes)) p.eyes = 'shut';
  if (mouthOpen) p.mouth = ({ smile: 'open', grin: 'laugh', smirk: 'open', flat: 'o', frown: 'sadOpen', wavy: 'open', teeth: 'grin', o: 'bigO', open: 'o', bigO: 'o', laugh: 'grin', sadOpen: 'frown', tongue: 'open', yawn: 'bigO' })[p.mouth] || 'open';
  return p;
}
