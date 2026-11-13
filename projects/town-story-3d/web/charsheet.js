// ============================================================================
// CHARSHEET.JS — character design sheets (1080x1920) for TRUE Roblox R6 chars.
// ?variant=A|B|C  →  A: CLASSIC R6, B: PREMIUM OUTFIT, C: CINEMATIC BIG-HEAD
// Renders full body + 3 expression closeups per character onto #sheet.
// ============================================================================
import * as THREE from 'three';
import { BlockChar } from './chars.js';

const params = new URLSearchParams(location.search);
const VARIANT = (params.get('variant') || 'A').toUpperCase();
const VKEY = { A: 'classic', B: 'premium', C: 'cinematic' }[VARIANT] || 'classic';

const TITLES = {
  A: ['VARIANT A — CLASSIC R6', 'PURE ROBLOX BLOCKS  •  FLAT BRIGHT PLASTIC  •  1:2:1'],
  B: ['VARIANT B — PREMIUM OUTFIT', 'R6 + BELT  •  COLLAR  •  STRIPES  •  SHOES  •  GLOW COLORS'],
  C: ['VARIANT C — CINEMATIC BIG-HEAD', 'R6 + 30% BIGGER HEAD  •  MAX EXPRESSION  •  FILM CLOSEUPS'],
};

const W = 1080, H = 1920;
const sheet = document.getElementById('sheet');
const g2 = sheet.getContext('2d');

// ---- Anton font ----
const anton = new FontFace('Anton', 'url(./fonts/Anton-Regular.ttf)');
await anton.load();
document.fonts.add(anton);
await document.fonts.load('80px Anton');

const SS = 0.8; // sheet display scale (uniform presence)

// ---- cast (film configs; variant injected) ----
const CAST = [
  {
    label: 'TOMMY', sub: 'THE NEW KID — DOOR 149', pose: 'wave', pt: 0.8,
    exprs: ['smile', 'worried', 'shocked'],
    cfg: { name: 'kid', skin: '#f2c96e', shirt: '#3f76e0', accent: '#f5d76e', pants: '#2b3345', shoes: '#ececf2', cap: '#e04a38', scale: SS, freckles: true },
  },
  {
    label: 'MOM', sub: 'JUST MOVED IN — UNAWARE', pose: 'stand', pt: 0.0,
    exprs: ['smile', 'scared', 'worried'],
    cfg: { name: 'mom', skin: '#eec27f', shirt: '#52b074', accent: '#f0e6d2', pants: '#3a4a5c', shoes: '#7a5a48', hair: { style: 'bun', color: '#4a3220' }, scale: SS },
  },
  {
    label: 'MR. FINCH', sub: 'THE WARNING — DOOR 147', pose: 'point', pt: 0.0,
    exprs: ['neutral', 'creepy', 'shocked'],
    cfg: { name: 'finch', skin: '#e8c8a0', shirt: '#9a774f', accent: '#6a5238', pants: '#4a4a55', shoes: '#3a3a40', hair: { style: 'block', color: '#c9c9c9' }, scale: SS, cane: true },
  },
  {
    label: 'TOWNSFOLK', sub: 'THEY RUN BEFORE NINE', pose: 'run', pt: 0.35,
    exprs: ['scared', 'worried', 'neutral'],
    cfg: { name: 'ex1', skin: '#d8a878', shirt: '#e0813a', accent: '#3a2a1a', pants: '#3c4a5c', shoes: '#333333', hair: { style: 'block', color: '#2a2018' }, scale: SS },
  },
];
for (const c of CAST) c.cfg.variant = VKEY;

// ---- reusable WebGL renderer (transparent bg) ----
function makeGL(w, h) {
  const r = new THREE.WebGLRenderer({ alpha: true, antialias: true, preserveDrawingBuffer: true });
  r.setSize(w, h);
  r.outputColorSpace = THREE.SRGBColorSpace;
  r.toneMapping = THREE.ACESFilmicToneMapping;
  r.toneMappingExposure = 1.38;
  return r;
}

function studioScene() {
  const sc = new THREE.Scene();
  const hemi = new THREE.HemisphereLight('#e8f4ff', '#4a3f5a', 1.65);
  sc.add(hemi);
  const key = new THREE.DirectionalLight('#fff4e0', 2.6);
  key.position.set(2.4, 4.2, 3.2);
  sc.add(key);
  const rimC = new THREE.PointLight('#38d4ff', 7.0, 14, 1.1);   // cyan rim
  rimC.position.set(-2.4, 2.6, -1.4);
  sc.add(rimC);
  const rimM = new THREE.PointLight('#ff4fd8', 6.5, 14, 1.1);   // magenta rim
  rimM.position.set(2.6, 2.2, -1.8);
  sc.add(rimM);
  const fill = new THREE.PointLight('#ffd98a', 2.2, 10, 1.2);
  fill.position.set(0.5, 1.2, 2.8);
  sc.add(fill);
  const disc = new THREE.Mesh(
    new THREE.CircleGeometry(1.7, 44),
    new THREE.MeshLambertMaterial({ color: '#232a3a' })
  );
  disc.rotation.x = -Math.PI / 2;
  sc.add(disc);
  const ring = new THREE.Mesh(
    new THREE.RingGeometry(1.7, 1.82, 48),
    new THREE.MeshBasicMaterial({ color: '#38d4ff', transparent: true, opacity: 0.65 })
  );
  ring.rotation.x = -Math.PI / 2;
  ring.position.y = 0.005;
  sc.add(ring);
  return sc;
}

// render one character cell -> canvas
function renderChar(gl, sc, cam, cfg, pose, pt, expr, closeup) {
  for (const c of [...sc.children]) {
    if (c.userData && c.userData.isChar) sc.remove(c);
  }
  const char = new BlockChar(sc, cfg);
  char.group.userData.isChar = true;
  char.setVisible(true);
  char.setPose(pose, pt);
  char.setExpression(expr);
  if (closeup) {
    const headY = char.head.position.y * (cfg.scale || 1);
    cam.position.set(0, headY + 0.01, 1.0);
    cam.lookAt(0, headY, 0);
    cam.fov = 44;
  } else {
    cam.position.set(0.4, 1.45, 3.65);
    cam.lookAt(0, 1.2, 0);
    cam.fov = 41;
  }
  cam.updateProjectionMatrix();
  gl.render(sc, cam);
  const out = document.createElement('canvas');
  out.width = gl.domElement.width;
  out.height = gl.domElement.height;
  out.getContext('2d').drawImage(gl.domElement, 0, 0);
  return out;
}

// ---------------- draw the sheet ----------------
function roundRect(x, y, w, h, r) {
  g2.beginPath();
  g2.moveTo(x + r, y);
  g2.arcTo(x + w, y, x + w, y + h, r);
  g2.arcTo(x + w, y + h, x, y + h, r);
  g2.arcTo(x, y + h, x, y, r);
  g2.arcTo(x, y, x + w, y, r);
  g2.closePath();
}

// bg gradient
{
  const grd = g2.createLinearGradient(0, 0, 0, H);
  grd.addColorStop(0, '#12151f');
  grd.addColorStop(0.5, '#151a29');
  grd.addColorStop(1, '#0d101a');
  g2.fillStyle = grd;
  g2.fillRect(0, 0, W, H);
  g2.strokeStyle = 'rgba(80,110,160,0.10)';
  g2.lineWidth = 1;
  for (let x = 0; x <= W; x += 60) { g2.beginPath(); g2.moveTo(x, 0); g2.lineTo(x, H); g2.stroke(); }
  for (let y = 0; y <= H; y += 60) { g2.beginPath(); g2.moveTo(0, y); g2.lineTo(W, y); g2.stroke(); }
  for (const [gx, gy, col] of [[140, 260, 'rgba(56,212,255,0.10)'], [950, 900, 'rgba(255,79,216,0.08)'], [200, 1650, 'rgba(255,217,138,0.07)']]) {
    const rg = g2.createRadialGradient(gx, gy, 0, gx, gy, 380);
    rg.addColorStop(0, col); rg.addColorStop(1, 'rgba(0,0,0,0)');
    g2.fillStyle = rg; g2.fillRect(0, 0, W, H);
  }
}

// header
g2.fillStyle = '#f5d76e';
g2.font = '80px Anton';
g2.textAlign = 'center';
g2.fillText('THE TOWN THAT COUNTS TO TEN', W / 2, 100);
g2.fillStyle = '#ffffff';
g2.font = '46px Anton';
g2.fillText(TITLES[VARIANT][0], W / 2, 160);
g2.fillStyle = 'rgba(160,190,230,0.85)';
g2.font = '24px Anton';
g2.fillText(TITLES[VARIANT][1], W / 2, 198);

// rows
const glBody = makeGL(400, 400);
const glFace = makeGL(240, 240);
const sc = studioScene();
const camB = new THREE.PerspectiveCamera(41, 1, 0.1, 50);
const camF = new THREE.PerspectiveCamera(44, 1, 0.1, 50);

const rowY0 = 240, rowH = 396;
CAST.forEach((ch, i) => {
  const y = rowY0 + i * rowH;
  g2.fillStyle = 'rgba(255,255,255,0.035)';
  roundRect(24, y, W - 48, rowH - 22, 22);
  g2.fill();
  g2.strokeStyle = 'rgba(120,160,220,0.22)';
  g2.lineWidth = 2;
  g2.stroke();

  const bodyC = renderChar(glBody, sc, camB, ch.cfg, ch.pose, ch.pt, 'neutral', false);
  g2.save();
  g2.beginPath(); roundRect(44, y + 14, 340, 342, 16); g2.clip();
  g2.fillStyle = 'rgba(10,14,22,0.55)';
  g2.fillRect(44, y + 14, 340, 342);
  g2.drawImage(bodyC, 44, y + 14, 340, 342);
  g2.restore();

  g2.textAlign = 'left';
  g2.fillStyle = '#ffffff';
  g2.font = '52px Anton';
  g2.fillText(ch.label, 412, y + 66);
  g2.fillStyle = ch.cfg.cap || ch.cfg.hair.color || '#8ab4f8';
  g2.font = '26px Anton';
  g2.fillText(ch.sub, 413, y + 102);

  ch.exprs.forEach((ex, k) => {
    const fx = 412 + k * 214, fy = y + 122, fw = 198, fh = 198;
    const faceC = renderChar(glFace, sc, camF, ch.cfg, 'stand', 0, ex, true);
    g2.save();
    g2.beginPath(); roundRect(fx, fy, fw, fh, 16); g2.clip();
    g2.fillStyle = 'rgba(10,14,22,0.55)';
    g2.fillRect(fx, fy, fw, fh);
    g2.drawImage(faceC, fx, fy, fw, fh);
    g2.restore();
    g2.strokeStyle = 'rgba(120,160,220,0.35)';
    g2.lineWidth = 2;
    roundRect(fx, fy, fw, fh, 16); g2.stroke();
    g2.fillStyle = '#9fc4ef';
    g2.font = '22px Anton';
    g2.textAlign = 'center';
    g2.fillText(ex.toUpperCase(), fx + fw / 2, fy + fh - 10);
  });

  const chips = [ch.cfg.shirt, ch.cfg.accent || '#ffffff', ch.cfg.pants, ch.cfg.cap || ch.cfg.hair.color, ch.cfg.skin];
  chips.forEach((cc, k) => {
    g2.fillStyle = cc;
    roundRect(412 + k * 44, y + 340, 34, 22, 6);
    g2.fill();
  });
});

// footer
g2.textAlign = 'center';
g2.fillStyle = '#f5d76e';
g2.font = '34px Anton';
g2.fillText('TRUE ROBLOX R6  —  HEAD 1×1×1  •  TORSO 2×2×1  •  LIMBS 1×2×1', W / 2, 1856);
g2.fillStyle = 'rgba(160,190,230,0.8)';
g2.font = '24px Anton';
g2.fillText('PICK A VARIANT  —  CITY COLORFUL-LIGHTING POLISH → NEXT', W / 2, 1892);

glBody.dispose();
glFace.dispose();
window.__sheet = true;
