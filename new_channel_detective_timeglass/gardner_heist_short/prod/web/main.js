import * as THREE from './lib/three.module.js';
import * as T from './toon.js';
import * as P from './paint.js';
import { SHOTS, TOTAL, shotAt, camAt, dofAt, LIGHTS, lightFor, actorsAt, worldAt, fxAt, DECK } from './story.js';

const W = 720, H = 1280;
const SC = Math.min(3, Math.max(0.6, +(new URLSearchParams(location.search).get('sc') || 1)));
const PW = Math.round(W * SC), PH = Math.round(H * SC);
const MS = +(new URLSearchParams(location.search).get('ms') ?? 0);
const SM = +(new URLSearchParams(location.search).get('sm') ?? 1024);
const canvas = document.getElementById('c');
const capCanvas = document.getElementById('caption'), capCtx = capCanvas.getContext('2d');
canvas.width = PW; canvas.height = PH;
const CAPW = 1080, CAPH = 1920, CAPS = CAPW / W;   // overlay always drawn at master res: crisp type at any 3D scale
capCanvas.width = CAPW; capCanvas.height = CAPH;

/* ============================ overlay design ============================ */
const FONT = '900 %dpx "Arial Black", Arial, sans-serif';
const outlined = (txt, x, y, font, fill, lw, align = 'center', sp) => {
  capCtx.save(); capCtx.font = font; capCtx.textAlign = align; capCtx.textBaseline = 'middle';
  capCtx.lineJoin = 'round'; capCtx.lineWidth = lw; capCtx.strokeStyle = '#0b0d12'; capCtx.fillStyle = fill;
  if (sp !== undefined && 'letterSpacing' in capCtx) capCtx.letterSpacing = sp + 'px';
  capCtx.strokeText(txt, x, y); capCtx.fillText(txt, x, y);
  if ('letterSpacing' in capCtx) capCtx.letterSpacing = '0px';
  capCtx.restore();
};
const OV = {
  s1:  { kicker: 'BOSTON · 18 MARCH 1990', title: 'THE NIGHT THE MUSEUM WAS ROBBED', titleAt: 24 },
  s2:  { kicker: '1:24 A.M. · THE SIDE DOOR', slate: 'TWO POLICE OFFICERS', sub: 'A DISTURBANCE CALL · NOBODY ASKED WHICH ONE', slateAt: 30 },
  s3:  { kicker: 'THE NIGHT GUARD', slate: 'HE OPENED THE DOOR', sub: 'THIRTY SECONDS LATER HE WAS ON THE FLOOR', slateAt: 30 },
  s4:  { kicker: 'THE BASEMENT', slate: 'TWO GUARDS · ONE ROLL OF TAPE', sub: 'NOT ONE ALARM WAS PRESSED', slateAt: 28 },
  s5:  { kicker: 'THE DUTCH ROOM · 2:00 A.M.', slate: 'THIRTEEN WORKS · EIGHTY-ONE MINUTES', sub: 'THEY WALKED STRAIGHT TO THE RIGHT WALL', slateAt: 34 },
  s6:  { kicker: 'JOHANNES VERMEER · THE CONCERT', slate: 'ONE OF ABOUT THIRTY-FOUR IN THE WORLD', sub: 'PAINTED c. 1664 · 72 × 65 CM', slateAt: 40 },
  s7:  { kicker: 'NO TIME TO UNSCREW A FRAME', slate: 'THEY CUT THE CANVAS OUT', sub: 'THE GOLD STAYED ON THE WALL', slateAt: 30 },
  s8:  { kicker: '2:45 A.M.', slate: 'THIRTEEN EMPTY FRAMES', sub: 'EVERYTHING OF VALUE · NOTHING OF WEIGHT', slateAt: 34 },
  s9:  { kicker: 'THE GETAWAY', slate: 'TWO CARS · INTO THE DARK', sub: 'NOTHING WAS REPORTED UNTIL MORNING', slateAt: 30 },
  s10: { kicker: 'MORNING · 18 MARCH 1990', slate: 'NO ARRESTS · NOTHING RECOVERED', sub: 'TEN MILLION DOLLARS STILL ON OFFER', slateAt: 32 },
  s11: { kicker: 'THE DUTCH ROOM · TODAY', title: 'STILL EMPTY', titleAt: 18, slate: 'THE MUSEUM HANGS THE FRAMES ANYWAY', slateAt: 60 },
  s12: { kicker: 'BOSTON · THIRTY-SIX YEARS ON', title: 'STILL WAITING', titleAt: 16, slate: 'PAINTINGS THAT NEVER CAME HOME', slateAt: 54 },
};

const easeOut = (t) => { t = Math.max(0, Math.min(1, t)); return 1 - Math.pow(1 - t, 3); };
function drawCaption(f) {
  capCtx.setTransform(CAPS, 0, 0, CAPS, 0, 0);
  capCtx.clearRect(0, 0, W, H);
  const S = shotAt(f), O = OV[S.id]; if (!O) return;
  const local = f - S.a;

  if (O.kicker) {
    const a = easeOut(Math.min(1, local / 16));
    capCtx.save(); capCtx.globalAlpha = a;
    outlined(O.kicker, W / 2, 178, FONT.replace('%d', 19), '#f5c542', 6, 'center', 3.2);
    capCtx.restore();
  }
  if (O.title) {
    const t0 = O.titleAt || 20;
    const a = local < t0 ? easeOut(local / 10) : 1;
    let tfs = 46;
    capCtx.font = FONT.replace('%d', tfs);
    const tw0 = capCtx.measureText(O.title).width;
    if (tw0 > 648) tfs = Math.max(26, Math.floor(46 * 648 / tw0));
    capCtx.save(); capCtx.globalAlpha = a;
    outlined(O.title, W / 2, 222, FONT.replace('%d', tfs), '#ffffff', Math.max(8, Math.round(tfs * 0.19)));
    capCtx.restore();
    // gold rule draws itself in
    const rw = 128 * a;
    capCtx.save(); capCtx.strokeStyle = '#f5c542'; capCtx.lineWidth = 5; capCtx.lineCap = 'round';
    capCtx.beginPath(); capCtx.moveTo(W / 2 - rw, 262); capCtx.lineTo(W / 2 + rw, 262); capCtx.stroke(); capCtx.restore();
  }
  if (O.counter) {
    outlined(O.counter[0], 44, 96, FONT.replace('%d', 78), '#f5c542', 12, 'left');
    outlined(O.counter[1], 48, 156, FONT.replace('%d', 21), '#ffffff', 6, 'left', 3.6);
  }
  if (O.slate) {
    const t0 = O.slateAt || 30, a = easeOut(Math.max(0, Math.min(1, (local - t0) / 14)));
    if (a > 0.01) {
      capCtx.save(); capCtx.globalAlpha = a;
      let fs = 32; capCtx.font = FONT.replace('%d', fs);
      const tw = capCtx.measureText(O.slate).width;
      if (tw > 560) fs = Math.max(20, Math.floor(32 * 560 / tw));
      capCtx.font = FONT.replace('%d', fs);
      const bw = Math.min(640, capCtx.measureText(O.slate).width + 76);
      const bx0 = 34, by0 = 946, bh = O.sub ? 118 : 78;
      capCtx.beginPath(); capCtx.roundRect(bx0, by0, bw, bh, 10);
      capCtx.fillStyle = 'rgba(9,11,17,.80)'; capCtx.fill();
      capCtx.fillStyle = '#f5c542'; capCtx.fillRect(bx0, by0 + 10, 5, bh - 20);
      capCtx.restore();
      capCtx.save(); capCtx.globalAlpha = a;
      outlined(O.slate, bx0 + 24, by0 + 34, FONT.replace('%d', fs), '#ffffff', Math.max(5, Math.round(fs * 0.2)), 'left', 1.4);
      if (O.sub) outlined(O.sub, bx0 + 24, by0 + 82, FONT.replace('%d', 16), '#cfd6de', 4.5, 'left', 2.2);
      capCtx.restore();
    }
  }
}

/* ============================ renderer ============================ */
const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(PW, PH, false);
renderer.shadowMap.enabled = !(new URLSearchParams(location.search).get('ns')); renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.NoToneMapping;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, W / H, 0.08, 2600);
const rx = (a) => a * Math.PI / 180;

const grad = (() => { const d = new Uint8Array([96, 96, 96, 255, 255, 255, 255, 255]); const t = new THREE.DataTexture(d, 2, 1); t.minFilter = t.magFilter = THREE.NearestFilter; t.needsUpdate = true; return t; })();
const toon = (opts) => new THREE.MeshToonMaterial({ gradientMap: grad, ...opts });
const texM = (c, rx_ = 1, ry_ = 1, color = '#ffffff') => toon({ map: P.tex(c, rx_, ry_), color });

const mats = {
  rock: (() => {   // rough basalt: no brick courses, just chipped planes + lichen
    const c = document.createElement('canvas'); c.width = c.height = 512; const g = c.getContext('2d'), r = P.rng ? null : null;
    g.fillStyle = '#454f59'; g.fillRect(0, 0, 512, 512);
    let seed = 12345; const rnd = () => (seed = (seed * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;
    for (let i = 0; i < 1400; i++) {
      const x = rnd() * 512, y = rnd() * 512, w = 10 + rnd() * 34, h = 5 + rnd() * 16;
      const l = 27 + rnd() * 12;
      g.fillStyle = `hsla(${198 + rnd() * 22},${7 + rnd() * 8}%,${l}%,.55)`;
      g.beginPath(); g.ellipse(x, y, w, h, rnd() * 3, 0, 7); g.fill();
    }
    for (let i = 0; i < 260; i++) {   // cracks / bedding lines
      const x = rnd() * 512, y = rnd() * 512;
      g.strokeStyle = `rgba(18,22,26,${0.25 + rnd() * 0.4})`; g.lineWidth = 1 + rnd() * 2.2;
      g.beginPath(); g.moveTo(x, y); g.lineTo(x + (rnd() - 0.5) * 120, y + (rnd() - 0.5) * 26); g.stroke();
    }
    for (let i = 0; i < 150; i++) {   // sea-wet dark patches + lichen
      const x = rnd() * 512, y = rnd() * 512;
      g.fillStyle = rnd() > 0.8 ? 'rgba(112,122,88,.16)' : 'rgba(20,26,30,.16)';
      g.beginPath(); g.ellipse(x, y, 8 + rnd() * 26, 5 + rnd() * 14, rnd() * 3, 0, 7); g.fill();
    }
    return texM(c, 5, 3);
  })(),
  rockDark: toon({ color: '#3a444e' }),
  rockChunk: (() => { const m = toon({ color: '#59626a' }); m.flatShading = true; return m; })(),
  isleGrass: texM(P.grass(66), 4, 4, '#6d7561'),
  white: toon({ color: '#f2ece0' }),
  towerShade: toon({ color: '#ddd4c4' }),
  baseStone: texM(P.stone(51, 210, 6, 34), 2.5, 1.6),
  doorWood: texM(P.planks(23), 1, 2, '#6a4a30'),
  iron: toon({ color: '#4a5058' }),
  ironDark: toon({ color: '#33383f' }),
  brass: toon({ color: '#c19a4e' }),
  woodDark: toon({ color: '#4a3221' }),
  wood: texM(P.planks(5), 2, 2),
  glass: toon({ color: '#cfe6ee', transparent: true, opacity: 0.22, depthWrite: false }),
  lampGlow: toon({ color: '#ffe9b0', emissive: '#ffb457', emissiveIntensity: 1.15 }),
  lampDark: toon({ color: '#6d675c' }),
  floorStone: texM(P.stone(33, 36, 8, 52), 2, 2),
  wallWarm: texM(P.plaster(31, 34), 2, 2),
  plank: texM(P.planks(61), 5, 5),
  paper: toon({ color: '#ede3cf' }),
  ink: toon({ color: '#2c2c33' }),
  coat: toon({ color: '#a2967f' }),
  coatDark: toon({ color: '#7d7462' }),
  rag: toon({ color: '#7f6a52' }),
};

/* ---------- sky ---------- */
const skyU = { top: { value: new THREE.Color() }, hor: { value: new THREE.Color() }, sunDir: { value: new THREE.Vector3() }, sunCol: { value: new THREE.Color() }, sunSize: { value: 0 } };
const sky = new THREE.Mesh(new THREE.SphereGeometry(1800, 32, 16), new THREE.ShaderMaterial({
  uniforms: skyU, side: THREE.BackSide, depthWrite: false, fog: false,
  vertexShader: `varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
  fragmentShader: `uniform vec3 top, hor, sunDir, sunCol; uniform float sunSize; varying vec3 vP;
    void main(){ float h = clamp(vP.y,0.,1.); vec3 c = mix(hor, top, pow(h,.55)); if(vP.y<0.) c = hor;
      float s = dot(normalize(vP), normalize(sunDir)); c += sunCol * (smoothstep(1.-sunSize, 1.-sunSize*.6, s) + .3*pow(max(s,0.),22.)*step(.001,sunSize));
      gl_FragColor = vec4(c,1.); }`,
}));
sky.userData.sky = true; scene.add(sky);

/* ---------- lights ---------- */
const hemi = new THREE.HemisphereLight('#ffffff', '#ffffff', 1); scene.add(hemi);
const sun = new THREE.DirectionalLight('#ffffff', 2); sun.castShadow = true;
sun.shadow.mapSize.set(SM, SM); sun.shadow.bias = -0.0009; sun.shadow.normalBias = 0.05; sun.shadow.radius = 2;
scene.add(sun); scene.add(sun.target);
scene.fog = new THREE.Fog('#ffffff', 40, 700);
const lampLight = new THREE.PointLight('#ffce7a', 3.2, 46, 2); lampLight.position.set(0, 2.0, 0); scene.add(lampLight);
const roomFill = new THREE.PointLight('#ffd9a1', 0, 14, 2); scene.add(roomFill);
const pegFill = new THREE.PointLight('#ffe0b0', 0, 6, 2); scene.add(pegFill);

/* ============================ THE GARDNER ============================ */
Object.assign(mats, {
  parquet: texM(P.planks(9), 7, 7, '#8b5a33'),
  parquet2: texM(P.planks(17), 7, 7, '#7a4c2b'),
  tile: texM(P.stone(21, 18, 30, 44, 96, 96), 6, 6, '#b26a44'),
  wallCream: texM(P.plaster(31, 44), 2.2, 2.2, '#e6d8c0'),
  wallGreen: texM(P.plaster(37, 152), 2.2, 2.2, '#3c5a4a'),
  wallRed: texM(P.plaster(41, 6), 2.2, 2.2, '#7c2f2c'),
  marbleW: texM(P.marble(12), 2, 2, '#efe8dc'),
  concrete: texM(P.stone(63, 205, 6, 52, 128, 128), 3, 3, '#9aa0a4'),
  goldBar: toon({ color: '#c9a13f', emissive: '#2a1c05', emissiveIntensity: 0.35 }),
  goldDeep: toon({ color: '#9c7524' }),
  paintWood: toon({ color: '#2b3a33' }),
  asphalt: toon({ color: '#23262c' }),
  curb: toon({ color: '#5b6068' }),
  brick: texM(P.stone(51, 12, 24, 58, 128, 64), 3, 2, '#b98a72'),
  glassNight: toon({ color: '#0e1622', emissive: '#0b1220', emissiveIntensity: 0.5 }),
  lampWarn: toon({ color: '#ffe3ae', emissive: '#ffb44e', emissiveIntensity: 1.6 }),
  tape: toon({ color: '#cfd3d6' }),
  canvasRoll: toon({ color: '#d8c9a8' }),
  wineRed: toon({ color: '#7d2b2f' }),
});

/* ---------- procedural Dutch-Golden-Age paintings ---------- */
const artCanvas = (seed, kind) => {
  const c = document.createElement('canvas'); c.width = 320; c.height = 400;
  const g = c.getContext('2d'); const r = P.rng(seed * 977 + 13);
  const stroke = (x, y, w, h, col, n, a = 0.5) => {
    for (let i = 0; i < n; i++) {
      g.fillStyle = col; g.globalAlpha = a * (0.4 + r() * 0.6);
      g.beginPath(); g.ellipse(x + (r() - 0.5) * w, y + (r() - 0.5) * h, 3 + r() * 14, 1.5 + r() * 5, r() * 3, 0, 7); g.fill();
    }
    g.globalAlpha = 1;
  };
  let grad = g.createLinearGradient(0, 0, 0, 400);
  if (kind === 'storm') {
    grad.addColorStop(0, '#2b3440'); grad.addColorStop(0.45, '#20262e'); grad.addColorStop(1, '#131417');
    g.fillStyle = grad; g.fillRect(0, 0, 320, 400);
    stroke(160, 120, 300, 150, '#4c5a66', 90, 0.5);
    g.fillStyle = '#8fa2ad'; g.globalAlpha = 0.30;
    g.beginPath(); g.moveTo(120, 0); g.lineTo(210, 0); g.lineTo(90, 260); g.lineTo(40, 300); g.closePath(); g.fill(); g.globalAlpha = 1;
    // sea
    grad = g.createLinearGradient(0, 230, 0, 400);
    grad.addColorStop(0, '#2c3a44'); grad.addColorStop(1, '#101318');
    g.fillStyle = grad; g.fillRect(0, 230, 320, 170);
    stroke(160, 300, 340, 150, '#5c707c', 130, 0.35);
    // boat
    g.fillStyle = '#3a2b1f'; g.beginPath(); g.moveTo(96, 286); g.lineTo(232, 286); g.lineTo(206, 320); g.lineTo(116, 320); g.closePath(); g.fill();
    g.fillStyle = '#6b5236'; g.fillRect(158, 214, 7, 76);
    g.fillStyle = '#8d7a5e'; g.beginPath(); g.moveTo(162, 216); g.quadraticCurveTo(214, 250, 166, 274); g.closePath(); g.fill();
    for (const [x, y, s] of [[128, 268, 1], [150, 272, 1.05], [186, 276, 0.95]]) {
      g.fillStyle = '#c8a97e'; g.beginPath(); g.arc(x, y - 14 * s, 7 * s, 0, 7); g.fill();
      g.fillStyle = '#31465c'; g.beginPath(); g.ellipse(x, y + 2, 10 * s, 15 * s, 0, 0, 7); g.fill();
      stroke(x + 4, y - 6, 16, 16, '#c9a878', 8, 0.5);
    }
  } else if (kind === 'concert') {
    grad.addColorStop(0, '#4a3a28'); grad.addColorStop(1, '#1a1410');
    g.fillStyle = grad; g.fillRect(0, 0, 320, 400);
    g.fillStyle = '#c9a86a'; g.globalAlpha = 0.5; g.fillRect(214, 40, 72, 120); g.fillRect(20, 40, 60, 120); g.globalAlpha = 1;
    g.fillStyle = '#3d2f22'; g.fillRect(0, 250, 320, 150);
    stroke(160, 150, 330, 220, '#8a6a42', 80, 0.35);
    // musician
    g.fillStyle = '#7d2f33'; g.beginPath(); g.ellipse(196, 246, 44, 58, 0, 0, 7); g.fill();
    g.fillStyle = '#e3bb8f'; g.beginPath(); g.arc(196, 176, 21, 0, 7); g.fill();
    g.fillStyle = '#2b211a'; g.beginPath(); g.arc(196, 168, 23, 3.2, 6.2); g.fill();
    g.fillStyle = '#3b2b1e'; g.fillRect(120, 236, 96, 14);
    // listener
    g.fillStyle = '#2f3f52'; g.beginPath(); g.ellipse(84, 258, 36, 54, 0, 0, 7); g.fill();
    g.fillStyle = '#e8c49a'; g.beginPath(); g.arc(84, 194, 18, 0, 7); g.fill();
    g.fillStyle = '#241a14'; g.beginPath(); g.arc(84, 186, 20, 3.2, 6.2); g.fill();
    g.fillStyle = '#c9a86a'; g.fillRect(40, 300, 240, 10);
  } else if (kind === 'portrait') {
    grad.addColorStop(0, '#3b3227'); grad.addColorStop(1, '#14110e');
    g.fillStyle = grad; g.fillRect(0, 0, 320, 400);
    stroke(160, 170, 320, 340, '#6a563c', 60, 0.25);
    for (const [x, col, sw] of [[112, '#141210', 52], [212, '#191512', 46]]) {
      g.fillStyle = col; g.beginPath(); g.ellipse(x, 268, sw, 96, 0, 0, 7); g.fill();
      g.fillStyle = '#e2ba90'; g.beginPath(); g.arc(x, 168, 22, 0, 7); g.fill();
      g.fillStyle = '#1c1611'; g.beginPath(); g.arc(x, 158, 24, 3.1, 6.3); g.fill();
      g.fillStyle = '#e8e2d4'; g.fillRect(x - 10, 196, 20, 16);
    }
    g.fillStyle = '#2b2118'; g.fillRect(60, 352, 200, 48);
  } else if (kind === 'obelisk') {
    grad.addColorStop(0, '#9d9a86'); grad.addColorStop(0.55, '#6f7a6c'); grad.addColorStop(1, '#3c3a2c');
    g.fillStyle = grad; g.fillRect(0, 0, 320, 400);
    stroke(160, 130, 340, 160, '#c9c2a4', 60, 0.3);
    g.fillStyle = '#54604a'; g.fillRect(0, 250, 320, 150);
    stroke(160, 320, 340, 120, '#6f7a5c', 70, 0.4);
    g.fillStyle = '#cfc7b0'; g.fillRect(150, 120, 22, 170);
    g.beginPath(); g.moveTo(150, 120); g.lineTo(161, 92); g.lineTo(172, 120); g.closePath(); g.fill();
    g.fillStyle = '#3d4436'; g.beginPath(); g.ellipse(60, 240, 34, 26, 0, 0, 7); g.fill();
  } else if (kind === 'tortoni') {
    grad.addColorStop(0, '#57402c'); grad.addColorStop(1, '#1c1510');
    g.fillStyle = grad; g.fillRect(0, 0, 320, 400);
    g.fillStyle = '#c9a86a'; g.globalAlpha = 0.35; g.fillRect(0, 0, 320, 210); g.globalAlpha = 1;
    g.fillStyle = '#2c2018'; g.fillRect(0, 262, 320, 138);
    g.fillStyle = '#e6c096'; g.beginPath(); g.arc(150, 150, 30, 0, 7); g.fill();
    g.fillStyle = '#20180f'; g.beginPath(); g.arc(150, 138, 32, 3.1, 6.3); g.fill();
    g.fillStyle = '#252f3c'; g.beginPath(); g.ellipse(150, 226, 52, 68, 0, 0, 7); g.fill();
    g.fillStyle = '#efe9dc'; g.fillRect(88, 286, 130, 12);
    g.fillStyle = '#b98a58'; g.beginPath(); g.ellipse(212, 280, 22, 12, 0, 0, 7); g.fill();
  } else { // degas sketch
    g.fillStyle = '#ded2b8'; g.fillRect(0, 0, 320, 400);
    g.strokeStyle = '#6b5a44'; g.lineWidth = 3;
    g.beginPath(); g.arc(160, 120, 26, 0, 7); g.stroke();
    g.beginPath(); g.moveTo(160, 146); g.quadraticCurveTo(196, 208, 178, 268); g.lineTo(126, 300); g.moveTo(160, 160); g.lineTo(104, 214); g.moveTo(160, 160); g.lineTo(214, 208); g.stroke();
    for (let i = 0; i < 40; i++) stroke(160 + (r() - 0.5) * 200, 200 + (r() - 0.5) * 200, 60, 60, '#8a7458', 6, 0.25);
  }
  // varnish: warm glaze + craquelure + vignette
  g.fillStyle = 'rgba(120,80,30,0.16)'; g.fillRect(0, 0, 320, 400);
  for (let i = 0; i < 60; i++) {
    g.strokeStyle = `rgba(20,14,8,${0.05 + r() * 0.12})`; g.lineWidth = 0.8;
    g.beginPath(); const x = r() * 320, y = r() * 400; g.moveTo(x, y); g.lineTo(x + (r() - 0.5) * 40, y + (r() - 0.5) * 40); g.stroke();
  }
  const vg = g.createRadialGradient(160, 190, 60, 160, 190, 260);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.55)');
  g.fillStyle = vg; g.fillRect(0, 0, 320, 400);
  return c;
};

/* ---------- kill the inherited lighthouse lights ---------- */
lampLight.intensity = 0; roomFill.intensity = 0; pegFill.intensity = 0;

/* ---------- geometry helpers ---------- */
const sets = {}; const ref = { arts: [] };
const stage = (name) => { const g = new THREE.Group(); g.name = name; g.visible = false; scene.add(g); sets[name] = g; return g; };
const add = (geo, mat, x = 0, y = 0, z = 0, parent = scene, opts = {}) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = opts.cast ?? true; m.receiveShadow = true; parent.add(m); return m; };
const cyl = (p, r1, r2, h, m, x, y, z, seg = 14) => add(new THREE.CylinderGeometry(r1, r2, h, seg), m, x, y, z, p);
const bx = (p, w, h, d, m, x, y, z) => add(new THREE.BoxGeometry(w, h, d), m, x, y, z, p);
const pl = (p, w, d, m, x, y, z) => { const o = add(new THREE.PlaneGeometry(w, d), m, x, y, z, p, { cast: false }); o.rotation.x = -Math.PI / 2; return o; };
const quad = (p, w, h, m, x, y, z, ry = 0) => { const o = add(new THREE.PlaneGeometry(w, h), m, x, y, z, p, { cast: false }); o.rotation.y = ry; return o; };

/* ---------- a gilt frame with a canvas in it ---------- */
const framedArt = (parent, { x, y, z, ry = 0, w = 1.7, h = 2.0, seed = 1, kind = 'concert', empty = false, plaque = true }) => {
  const g = new THREE.Group(); g.position.set(x, y, z); g.rotation.y = ry; parent.add(g);
  const t = 0.13, d = 0.11;
  // outer moulding
  bx(g, w + t * 2, t, d, mats.goldBar, 0, h / 2 + t / 2, 0);
  bx(g, w + t * 2, t, d, mats.goldBar, 0, -h / 2 - t / 2, 0);
  bx(g, t, h, d, mats.goldBar, -w / 2 - t / 2, 0, 0);
  bx(g, t, h, d, mats.goldBar, w / 2 + t / 2, 0, 0);
  // inner lip
  bx(g, w + 0.04, 0.05, d * 0.7, mats.goldDeep, 0, h / 2 - 0.02, 0.01);
  bx(g, w + 0.04, 0.05, d * 0.7, mats.goldDeep, 0, -h / 2 + 0.02, 0.01);
  // back board (dark green/grey wall colour shows through an empty frame)
  const back = quad(g, w, h, empty ? mats.paintWood : mats.paintWood, 0, 0, -0.035);
  // the painting itself
  const tex = new THREE.CanvasTexture(artCanvas(seed, kind));
  tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4;
  const canvas = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshToonMaterial({ map: tex, gradientMap: grad }));
  canvas.position.set(0, 0, 0.012); canvas.receiveShadow = true; g.add(canvas);
  // nails + plaque left behind when it is gone
  if (empty) {
    for (const s of [-1, 1]) add(new THREE.SphereGeometry(0.018, 6, 5), mats.iron, s * (w * 0.3), h * 0.34, 0.02, g, { cast: false });
  }
  if (plaque) bx(g, 0.3, 0.11, 0.02, mats.brass, 0, -h / 2 - t - 0.18, 0.01);
  ref.arts.push({ g, canvas, w, h, seed, kind });
  return { g, canvas, w, h };
};

/* ============================ STREET ============================ */
{
  const g = stage('street');
  // road + kerb + pavement
  pl(g, 150, 150, mats.asphalt, 0, 0, 12).receiveShadow = true;
  bx(g, 90, 0.22, 7.0, mats.curb, 0, 0.11, 3.4);
  bx(g, 90, 0.3, 0.35, mats.concrete, 0, 0.15, 6.9);
  // the museum: a long Venetian palazzo wall
  const WX = 0, WZ = -6.5, WW = 56, WH = 15.5;
  bx(g, WW, WH, 1.4, mats.brick, WX, WH / 2, WZ);
  bx(g, WW + 0.6, 1.5, 1.8, mats.marbleW, WX, 0.75, WZ + 0.1);      // rusticated base
  bx(g, WW + 1.0, 0.7, 2.2, mats.marbleW, WX, WH - 0.4, WZ);        // cornice
  bx(g, WW + 1.4, 0.5, 2.9, mats.brick, WX, WH + 0.05, WZ);         // upper lip
  bx(g, WW, 2.6, 0.2, mats.marbleW, WX, WH + 1.6, WZ);              // attic storey
  // window bays
  for (const [wx, wy, ww, wh] of [
    [-20, 6.4, 3.0, 4.6], [-13, 6.4, 3.0, 4.6], [13, 6.4, 3.0, 4.6], [20, 6.4, 3.0, 4.6],
    [-20, 11.4, 2.6, 3.4], [-13, 11.4, 2.6, 3.4], [13, 11.4, 2.6, 3.4], [20, 11.4, 2.6, 3.4],
  ]) {
    bx(g, ww + 0.5, wh + 0.5, 0.24, mats.marbleW, wx, wy, WZ + 0.72);          // surround
    bx(g, ww, wh, 0.16, mats.glassNight, wx, wy, WZ + 0.82);                    // glass
    const arch = add(new THREE.CylinderGeometry(ww / 2, ww / 2, 0.16, 18, 1, false, 0, Math.PI), mats.glassNight, wx, wy + wh / 2, WZ + 0.82, g, { cast: false });
    arch.rotation.set(Math.PI / 2, 0, 0); arch.rotation.z = Math.PI / 2;
    const archF = add(new THREE.CylinderGeometry(ww / 2 + 0.25, ww / 2 + 0.25, 0.24, 18, 1, true, 0, Math.PI), mats.marbleW, wx, wy + wh / 2, WZ + 0.72, g, { cast: false });
    archF.rotation.set(Math.PI / 2, 0, 0);
    bx(g, 0.14, wh, 0.2, mats.marbleW, wx, wy, WZ + 0.9);                       // mullion
    bx(g, ww, 0.14, 0.2, mats.marbleW, wx, wy, WZ + 0.9);
    bx(g, ww + 0.9, 0.22, 0.5, mats.marbleW, wx, wy - wh / 2 - 0.3, WZ + 0.9); // sill
  }
  // portico + steps
  for (let i = 0; i < 5; i++) bx(g, 12 - i * 0.6, 0.22, 2.6 - i * 0.32, mats.marbleW, 0, 0.11 + i * 0.22, -1.4 + i * 0.3);
  for (const cx of [-3.9, -1.3, 1.3, 3.9]) {
    cyl(g, 0.36, 0.4, 5.6, mats.marbleW, cx, 4.0, -2.3, 14);
    bx(g, 0.95, 0.22, 0.95, mats.marbleW, cx, 1.22, -2.3);
    bx(g, 0.95, 0.22, 0.95, mats.marbleW, cx, 6.85, -2.3);
  }
  bx(g, 10.4, 1.0, 3.2, mats.marbleW, 0, 7.5, -2.5);
  bx(g, 10.9, 0.35, 3.6, mats.marbleW, 0, 8.15, -2.5);
  const portL = new THREE.PointLight('#ffd2a0', 40, 26, 2);
  portL.position.set(0, 6.2, 0.5); g.add(portL);
  // main doors + fanlight
  bx(g, 4.6, 4.2, 0.3, mats.paintWood, 0, 3.2, WZ + 0.78);
  for (const s of [-1, 1]) bx(g, 2.1, 3.9, 0.2, mats.paintWood, s * 1.1, 3.05, WZ + 0.9);
  for (const s of [-1, 1]) add(new THREE.CylinderGeometry(0.05, 0.05, 0.5, 8), mats.brass, s * 0.35, 3.0, WZ + 1.02, g);
  const fan = add(new THREE.CircleGeometry(2.3, 20, 0, Math.PI), mats.lampWarn, 0, 5.3, WZ + 0.86, g, { cast: false });
  // side door (the one that gets knocked on) + lamp + intercom
  const SX = 15.6;
  bx(g, 2.4, 3.4, 0.28, mats.marbleW, SX, 1.85, WZ + 0.7);
  bx(g, 1.5, 2.9, 0.22, mats.paintWood, SX, 1.6, WZ + 0.86);
  add(new THREE.CylinderGeometry(0.05, 0.05, 0.32, 8), mats.brass, SX + 0.5, 1.5, WZ + 0.98, g);
  bx(g, 0.34, 0.5, 0.1, mats.iron, SX + 1.05, 1.55, WZ + 0.86);          // intercom
  for (let k = 0; k < 4; k++) bx(g, 0.16, 0.05, 0.03, mats.brass, SX + 1.05, 1.72 - k * 0.1, WZ + 0.92);
  // warm wall lamp over the side door: this is what lights the heist approach
  const doorLamp = new THREE.PointLight('#ffd9a0', 26, 14, 2);
  doorLamp.position.set(SX, 3.2, WZ + 1.35); g.add(doorLamp);
  const doorSpill = new THREE.PointLight('#ffca86', 12, 9, 2);
  doorSpill.position.set(SX, 1.6, WZ + 2.6); g.add(doorSpill);
  bx(g, 0.5, 0.26, 0.5, mats.ironDark, SX, 3.5, WZ + 0.95);               // lamp bracket
  const dl = add(new THREE.SphereGeometry(0.22, 10, 8), mats.lampWarn, SX, 3.35, WZ + 1.15, g, { cast: false });
  const pool = add(new THREE.CircleGeometry(3.2, 24), new THREE.MeshBasicMaterial({ color: '#ffcf94', transparent: true, opacity: 0.16, depthWrite: false }), SX, 0.09, WZ + 2.6, g, { cast: false });
  pool.rotation.x = -Math.PI / 2; pool.userData.ndSkip = true;
  bx(g, 2.9, 0.24, 1.5, mats.marbleW, SX, 0.12, WZ + 1.7);                // threshold step
  // street lamps
  for (const lx of [-14, 8.5, 26]) {
    cyl(g, 0.1, 0.15, 4.4, mats.ironDark, lx, 2.2, 5.2, 10);
    bx(g, 0.42, 0.3, 0.42, mats.ironDark, lx, 4.5, 5.2);
    add(new THREE.SphereGeometry(0.22, 10, 8), mats.lampWarn, lx, 4.36, 5.2, g, { cast: false });
  }
  // parked red hatchback
  const car = new THREE.Group(); car.position.set(19.5, 0, 8.4); car.rotation.y = -0.18; g.add(car);
  bx(car, 4.3, 0.72, 1.9, mats.wineRed, 0, 0.72, 0);
  bx(car, 2.5, 0.62, 1.78, mats.wineRed, -0.15, 1.36, 0);
  bx(car, 2.2, 0.5, 1.62, mats.glassNight, -0.15, 1.4, 0);
  for (const [wx, wz] of [[-1.4, 0.95], [1.4, 0.95], [-1.4, -0.95], [1.4, -0.95]]) {
    const wh = add(new THREE.CylinderGeometry(0.36, 0.36, 0.24, 12), mats.ironDark, wx, 0.36, wz, car);
    wh.rotation.x = Math.PI / 2;
  }
  for (const s of [-1, 1]) {
    bx(car, 0.12, 0.18, 0.36, mats.lampWarn, 2.16, 0.86, s * 0.62);      // headlights
    bx(car, 0.1, 0.14, 0.3, mats.wineRed, -2.16, 0.9, s * 0.6);           // tail lights
    bx(car, 1.5, 0.5, 0.06, mats.glassNight, -0.1, 1.3, s * 0.9);         // side glass
  }
  bx(car, 0.34, 0.5, 0.04, mats.glassNight, -0.15, 1.35, 1.02);
  bx(car, 0.34, 0.5, 0.04, mats.glassNight, -0.15, 1.35, -1.02);
  bx(car, 2.3, 0.1, 0.16, mats.ironDark, -0.15, 1.66, 0);                 // roof rails
  bx(car, 0.44, 0.16, 0.14, mats.tape, 2.2, 0.52, 0);                     // plate
  for (const s of [-1, 1]) add(new THREE.SphereGeometry(0.11, 8, 7), mats.lampWarn, 2.2, 0.86, s * 0.62, car, { cast: false });
  // a head-and-shoulders silhouette in the driver's seat
  const drv = add(new THREE.SphereGeometry(0.2, 10, 8), mats.ink, 0.35, 1.28, 0.36, car, { cast: false });
  drv.scale.set(1, 1.15, 0.7);
  // bare trees + hedge
  for (const [tx, tz, s] of [[-25, 3.5, 1.15], [30, 4.2, 1.0], [-6.4, 8.6, 0.8]]) {
    cyl(g, 0.16 * s, 0.26 * s, 3.4 * s, mats.woodDark, tx, 1.7 * s, tz, 8);
    for (let i = 0; i < 5; i++) {
      const a = i * 1.7;
      const br = cyl(g, 0.05 * s, 0.09 * s, 1.9 * s, mats.woodDark, tx + Math.cos(a) * 0.6 * s, 3.5 * s, tz + Math.sin(a) * 0.6 * s, 6);
      br.rotation.set(Math.sin(a) * 0.55, 0, Math.cos(a) * 0.55);
    }
  }
  bx(g, 90, 0.9, 1.4, mats.paintWood, 0, 0.45, 7.6);    // far hedge line
}

/* ============================ ENTRY HALL ============================ */
{
  const g = stage('hall');
  const W = 15, D = 17, Hh = 5.4;
  pl(g, W, D, mats.tile, 0, 0.02, 0);
  bx(g, W, 0.2, 0.2, mats.marbleW, 0, 0.1, D / 2 - 0.1);
  add(new THREE.PlaneGeometry(W, D), mats.wallCream, 0, Hh, 0, g, { cast: false }).rotation.x = Math.PI / 2;
  // walls (inner faces)
  quad(g, W, Hh, mats.wallCream, 0, Hh / 2, -D / 2 + 0.02, 0);
  quad(g, W, Hh, mats.wallCream, 0, Hh / 2, D / 2 - 0.02, Math.PI);
  quad(g, D, Hh, mats.wallCream, -W / 2 + 0.02, Hh / 2, 0, Math.PI / 2);
  quad(g, D, Hh, mats.wallCream, W / 2 - 0.02, Hh / 2, 0, -Math.PI / 2);
  // cornice + dado
  for (const [x, z, ry, len] of [[0, -D / 2 + 0.1, 0, W], [0, D / 2 - 0.1, 0, W], [-W / 2 + 0.1, 0, Math.PI / 2, D], [W / 2 - 0.1, 0, Math.PI / 2, D]]) {
    bx(g, len, 0.28, 0.24, mats.marbleW, x, Hh - 0.35, z).rotation.y = ry;
    bx(g, len, 1.1, 0.16, mats.wallRed, x, 0.55, z).rotation.y = ry;
  }
  // grand staircase at the far end
  for (let i = 0; i < 9; i++) bx(g, 7 - i * 0.12, 0.24, 1.0 + i * 0.0, mats.marbleW, 0, 0.12 + i * 0.24, -D / 2 + 1.0 + i * 0.55);
  for (let i = 0; i < 9; i++) bx(g, 0.22, 0.95, 0.22, mats.marbleW, -3.2, 0.48 + i * 0.24, -D / 2 + 1.1 + i * 0.42);
  for (let i = 0; i < 9; i++) bx(g, 0.22, 0.95, 0.22, mats.marbleW, 3.2, 0.48 + i * 0.24, -D / 2 + 1.1 + i * 0.42);
  bx(g, 7, 0.16, 0.16, mats.goldBar, 0, 1.6, -D / 2 + 2.2).rotation.x = 0.42;
  // landing + arch
  bx(g, 8.4, 0.3, 2.4, mats.marbleW, 0, 2.2, -D / 2 + 5.6);
  bx(g, 8.8, 4.0, 0.4, mats.wallCream, 0, 2.0, -D / 2 + 6.9);
  // doorway to the street (south wall) with a lit transom
  bx(g, 4.0, 4.4, 0.3, mats.paintWood, 0, 2.2, D / 2 - 0.05);
  for (const s of [-1, 1]) bx(g, 1.7, 4.0, 0.2, mats.paintWood, s * 0.95, 2.0, D / 2 - 0.15);
  quad(g, 3.4, 0.7, mats.lampWarn, 0, 4.6, D / 2 - 0.2, Math.PI);
  // guard desk
  bx(g, 2.6, 0.09, 1.15, mats.woodDark, -2.9, 0.78, 6.0);
  for (const [lx, lz] of [[-1.2, -0.45], [1.2, -0.45], [-1.2, 0.45], [1.2, 0.45]]) bx(g, 0.1, 0.76, 0.1, mats.woodDark, -2.9 + lx, 0.38, 6.0 + lz);
  bx(g, 0.62, 0.42, 0.5, mats.ironDark, -3.5, 1.03, 5.9);            // monitor
  quad(g, 0.5, 0.33, mats.glassNight, -3.5, 1.03, 5.64, Math.PI);
  bx(g, 0.34, 0.08, 0.26, mats.iron, -2.3, 0.87, 5.95);              // phone
  bx(g, 0.3, 0.04, 0.22, mats.paper, -2.0, 0.85, 6.25);               // logbook
  bx(g, 0.5, 0.5, 0.06, mats.woodDark, -1.7, 1.2, 6.7);             // chair back
  for (const [sx, sz] of [[-0.18, 0], [0.18, 0]]) { cyl(g, 0.03, 0.03, 0.5, mats.ironDark, -1.7 + sx, 0.25, 6.8, 6); }
  // sconces + a big rug
  for (const [x, z, ry] of [[-W / 2 + 0.2, 2.0, Math.PI / 2], [W / 2 - 0.2, 2.0, -Math.PI / 2], [-W / 2 + 0.2, -3.0, Math.PI / 2]]) {
    bx(g, 0.3, 0.5, 0.18, mats.brass, x, 3.1, z).rotation.y = ry;
    add(new THREE.SphereGeometry(0.13, 8, 7), mats.lampWarn, x + (ry > 0 ? 0.1 : -0.1), 3.1, z, g, { cast: false });
  }
  const rug = pl(g, 6, 4.2, mats.wallRed, 0, 0.03, 2.2); rug.receiveShadow = true;
  framedArt(g, { x: -W / 2 + 0.15, y: 2.6, z: -1.0, ry: Math.PI / 2, w: 1.3, h: 1.6, seed: 5, kind: 'portrait', plaque: false });
  framedArt(g, { x: W / 2 - 0.15, y: 2.6, z: 0.5, ry: -Math.PI / 2, w: 1.2, h: 1.5, seed: 8, kind: 'obelisk', plaque: false });
  ref.deskLamp = new THREE.PointLight('#ffd9a0', 14, 12, 2);
  ref.deskLamp.position.set(-2.9, 1.5, 5.8); g.add(ref.deskLamp); ref.deskLamp.visible = false;
}

/* ============================ CELLAR ============================ */
{
  const g = stage('cellar');
  const W = 9, D = 7.5, Hh = 2.9;
  pl(g, W, D, mats.concrete, 0, 0.02, 0);
  add(new THREE.PlaneGeometry(W, D), mats.concrete, 0, Hh, 0, g, { cast: false }).rotation.x = Math.PI / 2;
  quad(g, W, Hh, mats.concrete, 0, Hh / 2, -D / 2 + 0.02, 0);
  quad(g, W, Hh, mats.concrete, 0, Hh / 2, D / 2 - 0.02, Math.PI);
  quad(g, D, Hh, mats.concrete, -W / 2 + 0.02, Hh / 2, 0, Math.PI / 2);
  quad(g, D, Hh, mats.concrete, W / 2 - 0.02, Hh / 2, 0, -Math.PI / 2);
  // pipe run along the north wall + boiler
  for (const [py, pr] of [[2.35, 0.09], [2.05, 0.06], [1.75, 0.05]]) {
    const p = cyl(g, pr, pr, W - 0.6, mats.iron, 0, py, -D / 2 + 0.28, 8);
    p.rotation.z = Math.PI / 2;
  }
  for (let i = 0; i < 6; i++) bx(g, 0.1, 0.55, 0.1, mats.ironDark, -W / 2 + 0.9 + i * 1.4, 2.0, -D / 2 + 0.28);
  bx(g, 1.6, 1.9, 1.2, mats.ironDark, 3.4, 0.95, -D / 2 + 0.9);
  cyl(g, 0.2, 0.2, 1.1, mats.iron, 3.4, 2.4, -D / 2 + 0.9, 10);
  // door at the south + a bare bulb
  bx(g, 1.3, 2.2, 0.14, mats.ironDark, -2.6, 1.1, D / 2 - 0.1);
  add(new THREE.CylinderGeometry(0.03, 0.03, 0.5, 6), mats.ironDark, 0, 2.7, 0.6, g);
  add(new THREE.SphereGeometry(0.09, 8, 7), mats.lampWarn, 0, 2.42, 0.6, g, { cast: false });
  // crates, mop bucket, fuse box
  bx(g, 0.8, 0.7, 0.7, mats.woodDark, -3.5, 0.36, -1.2);
  bx(g, 0.7, 0.5, 0.6, mats.woodDark, -3.4, 1.0, -1.15);
  cyl(g, 0.22, 0.18, 0.4, mats.iron, 3.6, 0.2, 2.2, 12);
  // roll of tape on the floor
  const tr = add(new THREE.CylinderGeometry(0.13, 0.13, 0.09, 18), mats.tape, 0.15, 0.05, -1.35, g);
  tr.rotation.set(Math.PI / 2, 0.4, 0);
  bx(g, 0.5, 0.7, 0.12, mats.iron, -1.2, 1.7, D / 2 - 0.12);
  ref.cellarBulb = new THREE.PointLight('#ffe0b6', 16, 12, 2);
  ref.cellarBulb.position.set(0, 2.35, 0.6); g.add(ref.cellarBulb);
}

/* ============================ THE DUTCH ROOM ============================ */
{
  const g = stage('dutch');
  const W = 9, D = 11, Hh = 4.9;
  pl(g, W, D, mats.parquet, 0, 0.02, 0);
  pl(g, W - 0.5, D - 0.5, mats.parquet2, 0, 0.03, 0);
  add(new THREE.PlaneGeometry(W, D), mats.wallCream, 0, Hh, 0, g, { cast: false }).rotation.x = Math.PI / 2;
  for (const [x, z, ry] of [[0, -D / 2 + 0.02, 0], [0, D / 2 - 0.02, Math.PI], [-W / 2 + 0.02, 0, Math.PI / 2], [W / 2 - 0.02, 0, -Math.PI / 2]]) {
    quad(g, W, Hh, mats.wallGreen, x, Hh / 2, z, ry);
  }
  for (const [x, z, ry, len] of [[0, -D / 2 + 0.08, 0, W], [0, D / 2 - 0.08, 0, W], [-W / 2 + 0.08, 0, Math.PI / 2, D], [W / 2 - 0.08, 0, Math.PI / 2, D]]) {
    bx(g, len, 0.26, 0.22, mats.marbleW, x, Hh - 0.34, z).rotation.y = ry;
    bx(g, len, 0.16, 0.2, mats.goldDeep, x, Hh - 0.56, z).rotation.y = ry;
    bx(g, len, 1.2, 0.14, mats.paintWood, x, 0.6, z).rotation.y = ry;
    bx(g, len, 0.08, 0.18, mats.goldDeep, x, 1.22, z).rotation.y = ry;
  }
  // fireplace on the north wall
  bx(g, 3.6, 2.3, 0.6, mats.marbleW, 0, 1.15, -D / 2 + 0.36);
  bx(g, 2.3, 1.15, 0.2, mats.ink, 0, 0.62, -D / 2 + 0.68);
  bx(g, 4.0, 0.24, 0.92, mats.marbleW, 0, 2.42, -D / 2 + 0.46);
  for (const s of [-1, 1]) bx(g, 0.3, 2.3, 0.32, mats.marbleW, s * 1.8, 1.15, -D / 2 + 0.52);
  bx(g, 3.3, 0.1, 1.3, mats.marbleW, 0, 0.06, -D / 2 + 1.05);
  ref.fire = new THREE.PointLight('#ff9a4a', 9, 12, 2);
  ref.fire.position.set(0, 0.75, -D / 2 + 1.15); g.add(ref.fire);
  // long table + chairs
  bx(g, 3.2, 0.11, 1.8, mats.woodDark, 2.6, 0.78, 1.4);
  for (const [lx, lz] of [[-1.4, -0.75], [1.4, -0.75], [-1.4, 0.75], [1.4, 0.75]]) bx(g, 0.14, 0.76, 0.14, mats.woodDark, 2.6 + lx, 0.38, 1.4 + lz);
  for (const [cx, cz, cr] of [[1.6, 2.8, 0.2], [3.6, 2.6, -0.2], [1.9, -0.1, 3.1], [3.5, -0.1, 2.9]]) {
    const ch = new THREE.Group(); ch.position.set(cx, 0, cz); ch.rotation.y = cr; g.add(ch);
    bx(ch, 0.62, 0.07, 0.62, mats.woodDark, 0, 0.46, 0);
    bx(ch, 0.62, 0.82, 0.07, mats.woodDark, 0, 0.86, -0.29);
    for (const [sx, sz] of [[-0.25, -0.25], [0.25, -0.25], [-0.25, 0.25], [0.25, 0.25]]) bx(ch, 0.06, 0.46, 0.06, mats.woodDark, sx, 0.23, sz);
    bx(ch, 0.58, 0.1, 0.52, mats.wallRed, 0, 0.52, 0.02);
  }
  // windows on the east wall, night beyond
  for (const wz of [-2.6, 1.2]) {
    bx(g, 0.26, 3.7, 2.0, mats.marbleW, W / 2 - 0.1, 3.1, wz);
    quad(g, 1.7, 3.3, mats.glassNight, W / 2 - 0.2, 3.1, wz, -Math.PI / 2);
    bx(g, 0.18, 3.4, 0.12, mats.marbleW, W / 2 - 0.22, 3.1, wz);
    bx(g, 0.18, 0.12, 1.8, mats.marbleW, W / 2 - 0.22, 3.1, wz);
    bx(g, 0.12, 4.1, 0.85, mats.wallRed, W / 2 - 0.28, 3.1, wz - 1.4);
    bx(g, 0.12, 4.1, 0.85, mats.wallRed, W / 2 - 0.28, 3.1, wz + 1.4);
  }
  // ---- the hero wall: WEST (x = -W/2), all Dutch-room cameras look this way ----
  const HX = -W / 2 + 0.16;
  ref.vermeer = framedArt(g, { x: HX, y: 2.5, z: -0.8, ry: Math.PI / 2, w: 1.8, h: 2.05, seed: 3, kind: 'concert' });
  ref.storm   = framedArt(g, { x: HX, y: 2.75, z: 2.1, ry: Math.PI / 2, w: 2.3, h: 2.75, seed: 7, kind: 'storm' });
  ref.lady    = framedArt(g, { x: HX, y: 2.45, z: -3.6, ry: Math.PI / 2, w: 1.45, h: 1.9, seed: 11, kind: 'portrait' });
  // north wall: obelisk + tortoni, flanking the fireplace
  ref.obelisk = framedArt(g, { x: -3.1, y: 2.4, z: -D / 2 + 0.18, ry: 0, w: 1.3, h: 1.65, seed: 13, kind: 'obelisk' });
  ref.tortoni = framedArt(g, { x: 3.1, y: 2.35, z: -D / 2 + 0.18, ry: 0, w: 1.1, h: 1.35, seed: 17, kind: 'tortoni' });
  // south wall: the two Degas sheets + a portrait
  ref.degas   = framedArt(g, { x: -0.9, y: 2.0, z: D / 2 - 0.18, ry: Math.PI, w: 0.9, h: 1.05, seed: 19, kind: 'degas' });
  ref.degas2  = framedArt(g, { x: 0.3, y: 2.0, z: D / 2 - 0.18, ry: Math.PI, w: 0.9, h: 1.05, seed: 23, kind: 'degas' });
  ref.portrait2 = framedArt(g, { x: 2.0, y: 2.3, z: D / 2 - 0.18, ry: Math.PI, w: 1.05, h: 1.3, seed: 29, kind: 'portrait' });
  // bench + wall lights + door
  bx(g, 2.5, 0.1, 0.62, mats.wallRed, 3.3, 0.45, 3.9);
  for (const s of [-1, 1]) bx(g, 0.12, 0.42, 0.52, mats.woodDark, 3.3 + s * 1.05, 0.22, 3.9);
  for (const [wx, wz, ry] of [[-W / 2 + 0.2, 0.9, Math.PI / 2], [-W / 2 + 0.2, -2.6, Math.PI / 2], [W / 2 - 0.2, 3.4, -Math.PI / 2], [0.6, D / 2 - 0.2, Math.PI]]) {
    bx(g, 0.3, 0.44, 0.16, mats.brass, wx, 3.7, wz).rotation.y = ry;
    add(new THREE.SphereGeometry(0.12, 8, 7), mats.lampWarn, wx + (ry > 1.6 && ry < 2.2 ? 0.13 : (ry < -1.5 ? -0.13 : 0)), 3.7, wz + (Math.abs(ry) > 2.9 ? -0.13 : 0), g, { cast: false });
  }
  bx(g, 3.4, 4.4, 0.3, mats.paintWood, 2.9, 2.2, D / 2 - 0.1);
  quad(g, 2.8, 4.0, mats.paintWood, 2.9, 2.05, D / 2 - 0.24, Math.PI);
  bx(g, 0.14, 0.14, 0.14, mats.brass, 2.0, 2.0, D / 2 - 0.3);
  ref.dutchAmb = new THREE.PointLight('#ffdfb4', 22, 20, 2);
  ref.dutchAmb.position.set(0.9, 3.4, 1.6); g.add(ref.dutchAmb);
  const wall1 = new THREE.PointLight('#ffd9a4', 9, 8, 2); wall1.position.set(-3.2, 3.2, -1.6); g.add(wall1);
}

/* ---------- torches (thieves' flashlights) ---------- */
ref.torches = [];
for (let i = 0; i < 2; i++) {
  const sp = new THREE.SpotLight('#fff2cf', 0, 26, 0.34, 0.55, 1.6);
  sp.castShadow = false; scene.add(sp); scene.add(sp.target);
  ref.torches.push({ sp, cone: sp });
}


/* ============================ post ============================ */
const PSC = Math.min(1, Math.max(0.4, +(new URLSearchParams(location.search).get('psc') || 1)));   // post-res scale
const IW = Math.round(PW * PSC), IH = Math.round(PH * PSC);
const rtColor = new THREE.WebGLRenderTarget(IW, IH, { samples: MS, type: THREE.HalfFloatType });
const rtNd = new THREE.WebGLRenderTarget(IW, IH, { type: THREE.HalfFloatType, minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter });
const rtInk = new THREE.WebGLRenderTarget(IW, IH, { type: THREE.HalfFloatType, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter });
const fsCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1), fsGeo = new THREE.PlaneGeometry(2, 2);
const fs = (mat) => { const s = new THREE.Scene(); s.add(new THREE.Mesh(fsGeo, mat)); return s; };
const ndMat = new THREE.ShaderMaterial({
  vertexShader: `varying vec3 vN; varying float vD; void main(){ vN = normalize(normalMatrix*normal); vec4 mv = modelViewMatrix*vec4(position,1.); vD = -mv.z; gl_Position = projectionMatrix*mv; }`,
  fragmentShader: `varying vec3 vN; varying float vD; void main(){ vec3 n = normalize(vN); if(!gl_FrontFacing) n = -n; gl_FragColor = vec4(n*.5+.5, vD); }`,
  side: THREE.DoubleSide,
});
const inkU = { col: { value: rtColor.texture }, nd: { value: rtNd.texture }, res: { value: new THREE.Vector2(IW, IH) }, px: { value: 1.8 },
  sat: { value: 1.1 }, lift: { value: new THREE.Color(0, 0, 0) }, gain: { value: new THREE.Color(1, 1, 1) }, vig: { value: 0.24 } };
const inkScene = fs(new THREE.ShaderMaterial({ uniforms: inkU, vertexShader: `varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position.xy,0.,1.); }`,
  fragmentShader: `uniform sampler2D col, nd; uniform vec2 res; uniform float px, sat, vig; uniform vec3 lift, gain; varying vec2 vUv;
  float edgeAt(vec2 uv, float r){
    vec4 c = texture2D(nd, uv); if (dot(c.rgb,c.rgb) < .01) return 0.; float d = c.a; vec3 n = c.rgb*2.-1.;
    float e = 0.; float rr = r * clamp(7./d, .6, 1.3);
    for (int i=0;i<8;i++){ float a = float(i)*.785398; float k = 1.;
      vec2 o = vec2(cos(a), sin(a))*rr*k/res; vec4 s = texture2D(nd, uv+o);
      float ds = s.a; bool card = dot(s.rgb,s.rgb) < .01;
      if (card && ds > 0.) continue;
      if (card) ds = 1e4;
      vec3 ns = s.rgb*2.-1.;
      e = max(e, smoothstep(.006, .02, (ds - d)/d));
      if (!card && abs(ds-d)/d < .06) e = max(e, smoothstep(.88, .72, dot(n, ns)) * .9);
    }
    return e * (1. - smoothstep(180., 600., d)*.75);
  }
  void main(){
    vec3 c = texture2D(col, vUv).rgb;
    float e = edgeAt(vUv, px);
    c = mix(c, vec3(.012,.01,.014), e);
    float l = dot(c, vec3(.299,.587,.114)); c = mix(vec3(l), c, sat);
    c = c*gain + lift;
    vec2 q = vUv-.5; c *= 1. - vig*dot(q*vec2(1.,.75), q*vec2(1.,.75))*2.2;
    gl_FragColor = vec4(c,1.); }` }));
const dofU = { src: { value: rtInk.texture }, nd: { value: rtNd.texture }, res: { value: new THREE.Vector2(IW, IH) }, focus: { value: 5 }, cinf: { value: 0 }, near: { value: 1 } };
const dofScene = fs(new THREE.ShaderMaterial({ uniforms: dofU, vertexShader: `varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position.xy,0.,1.); }`,
  fragmentShader: `uniform sampler2D src, nd; uniform vec2 res; uniform float focus, cinf, near; varying vec2 vUv;
  float coc(vec2 uv){ float d = texture2D(nd, uv).a; if (d <= 0.) d = 2000.; float k = 1. - focus/d; return k > 0. ? cinf*k : min(-k*cinf*near, cinf*1.4); }
  void main(){ float c0 = coc(vUv);
    if (cinf < .5 || c0 < .6) { gl_FragColor = linearToOutputTexel(vec4(texture2D(src, vUv).rgb, 1.)); return; }
    vec3 acc = vec3(0.); float wsum = 0.;
    for (int i=0;i<18;i++){ float fi = float(i); float r = sqrt((fi+.5)/18.); float a = fi*2.39996;
      vec2 o = vec2(cos(a), sin(a))*r*c0/res; float cs = coc(vUv+o);
      float w = smoothstep(r*c0-1.5, r*c0+.5, cs + .5);
      acc += texture2D(src, vUv+o).rgb*w; wsum += w; }
    gl_FragColor = linearToOutputTexel(vec4(acc/max(wsum,1e-3), 1.)); }` }));
dofScene.children[0].material.toneMapped = false;

/* ============================ cards ============================ */
const CW = 1200, CH = 2000, CM = 2.25;
const cardGeo = new THREE.PlaneGeometry(CM * 0.6, CM); cardGeo.translate(0, CM / 2 - CM * 0.025, 0);
const blobTex = P.tex(P.radial('20,14,30', 0.6));
class Card {
  constructor() {
    [this.c, this.g] = (() => { const c = document.createElement('canvas'); c.width = CW; c.height = CH; return [c, c.getContext('2d')]; })();
    this.t = new THREE.CanvasTexture(this.c); this.t.colorSpace = THREE.SRGBColorSpace; this.t.anisotropy = 4;
    this.mat = new THREE.MeshBasicMaterial({ map: this.t, transparent: true, alphaTest: 0.35, depthWrite: false });
    this.nd = new THREE.ShaderMaterial({
      uniforms: { map: { value: this.t } },
      vertexShader: `varying vec2 vUv; varying float vD; void main(){ vUv=uv; vec4 mv = modelViewMatrix*vec4(position,1.); vD=-mv.z; gl_Position=projectionMatrix*mv; }`,
      fragmentShader: `uniform sampler2D map; varying vec2 vUv; varying float vD; void main(){ if(texture2D(map,vUv).a<.35) discard; gl_FragColor=vec4(0.,0.,0.,vD); }`,
      side: THREE.DoubleSide,
    });
    this.mesh = new THREE.Mesh(cardGeo, this.mat);
    this.mesh.userData.nd = this.nd;
    this.blob = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: blobTex, transparent: true, depthWrite: false, fog: true }));
    this.blob.rotation.x = -Math.PI / 2; this.blob.userData.ndSkip = true; this.blob.renderOrder = 1;
    scene.add(this.mesh); scene.add(this.blob); this.key = ''; this.mesh.visible = this.blob.visible = false;
  }
  draw(key, fn) {
    if (key === this.key) return; this.key = key;
    const g = this.g; g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, CW, CH); g.setTransform(CW / 600, 0, 0, CH / 1000, 0, 0);
    const p = new T.Pen(g); fn(p); this.t.needsUpdate = true;
  }
}
const cards = []; const getCard = (i) => cards[i] || (cards[i] = new Card());

/* ============================ per-frame ============================ */
function drawActors(list, cam) {
  cards.forEach((c) => { c.mesh.visible = c.blob.visible = false; });
  list.forEach((a, i) => {
    const c = getCard(i);
    c.draw(a.key, a.draw);
    c.mesh.visible = true; c.mesh.position.set(a.x, a.y, a.z);
    const s = a.s || 1; c.mesh.scale.set(s * (a.flip ? -1 : 1), s, s);
    c.mesh.rotation.set(0, Math.atan2(cam.position.x - a.x, cam.position.z - a.z) + (a.yaw || 0), a.roll || 0);
    c.mat.color.set(a.tint || '#ffffff'); c.mat.opacity = a.alpha ?? 1;
    c.mat.transparent = (a.alpha ?? 1) < 1;
    c.mesh.userData.ndSkip = (a.alpha ?? 1) < 1;
    c.mesh.castShadow = false;   // 2D billboards: the ground blob does the grounding
    c.mesh.renderOrder = a.order || 3;
    if (a.blob !== false && a.y < DECK + 0.5) { c.blob.visible = true; c.blob.position.set(a.x, (a.ground ?? DECK) + 0.02, a.z); c.blob.scale.set(0.95 * s, 0.6 * s, 1); }
  });
}

const swapForNd = (on) => {
  scene.traverse((o) => {
    if (!o.isMesh) return;
    if (on) {
      o.userData.mat0 = o.material;
      if (o.userData.ndSkip) { o.userData.vis0 = o.visible; o.visible = false; return; }
      if (o === sky || o.userData.sky) { o.userData.vis0 = o.visible; o.visible = false; return; }
      o.material = o.userData.nd || ndMat;
    } else {
      o.material = o.userData.mat0;
      if (o.userData.vis0 !== undefined) { o.visible = o.userData.vis0; delete o.userData.vis0; }
    }
  });
};

/* ============================ per-frame (lights) ============================ */
const tmpV = new THREE.Vector3();
function applyLight(L) {
  hemi.color.set(L.sky); hemi.groundColor.set(L.ground); hemi.intensity = L.hemi;
  sun.color.set(L.sun); sun.intensity = L.sunI;
  scene.fog.color.set(L.fog); scene.fog.near = L.fogNear; scene.fog.far = L.fogFar;
  skyU.top.value.set(L.skyTop); skyU.hor.value.set(L.skyHor); skyU.sunCol.value.set(L.sunDisc || '#000'); skyU.sunSize.value = L.sunSize || 0;
  inkU.sat.value = L.sat; inkU.gain.value.set(L.gain || '#ffffff'); inkU.lift.value.set(L.lift || '#000000'); inkU.vig.value = L.vig ?? 0.24;
}
function placeSun(L, focus) {
  const az = rx(L.az), el = rx(L.el);
  tmpV.set(Math.cos(el) * Math.cos(az), Math.sin(el), Math.cos(el) * Math.sin(az));
  skyU.sunDir.value.copy(tmpV);
  sun.position.copy(focus).addScaledVector(tmpV, 120); sun.target.position.copy(focus);
  const ext = L.shadowExt || 40, sc = sun.shadow.camera;
  sc.left = -ext; sc.right = ext; sc.top = ext; sc.bottom = -ext; sc.near = 1; sc.far = 320; sc.updateProjectionMatrix();
}

/* ============================ per-frame (world) ============================ */
const EMPTY_FROM = {
  s8: ['vermeer', 'storm', 'lady', 'obelisk'],
  s10: ['vermeer', 'storm', 'lady', 'obelisk', 'tortoni', 'degas', 'degas2', 'portrait2'],
};
EMPTY_FROM.s11 = EMPTY_FROM.s10; EMPTY_FROM.s12 = EMPTY_FROM.s10;

function worldState(S, f, t) {
  for (const [name, g] of Object.entries(sets)) g.visible = name === S.loc;
  const k = Math.max(0, Math.min(1, (f - S.a) / Math.max(1, S.b - S.a)));

  /* --- paintings: on the wall, being cut, or gone --- */
  const gone = EMPTY_FROM[S.id] || [];
  for (const [key, art] of Object.entries(ref)) {
    if (!art || !art.canvas) continue;
    art.canvas.visible = !gone.includes(key);
    art.canvas.position.set(0, 0, 0.012);
    art.canvas.rotation.set(0, 0, 0);
  }
  if (S.id === 's7' && ref.vermeer) {           // the canvas is peeled down out of its frame
    const p = Math.min(1, Math.max(0, (k - 0.22) / 0.44));
    const e = p * p * (3 - 2 * p);
    ref.vermeer.canvas.visible = k < 0.86;
    ref.vermeer.canvas.position.set(0.05 * e, -ref.vermeer.h * 0.46 * e, 0.012 + 0.34 * e);
    ref.vermeer.canvas.rotation.set(0, 0.16 * e, -0.30 * e);
  }

  /* --- room lights --- */
  const dutch = S.loc === 'dutch';
  const cellar = S.loc === 'cellar', hall = S.loc === 'hall', street = S.loc === 'street';
  if (ref.fire) {
    ref.fire.visible = dutch;
    const fl = 0.72 + 0.28 * Math.sin(t * 9.1) * Math.sin(t * 3.3 + 1.7);
    ref.fire.intensity = (S.light === 'dutchDawn' ? 3.2 : 8.0) * fl;
  }
  if (ref.dutchAmb) ref.dutchAmb.visible = dutch;
  if (ref.cellarBulb) { ref.cellarBulb.visible = cellar; ref.cellarBulb.intensity = 16 + Math.sin(t * 21) * 1.1; }
  if (ref.deskLamp) ref.deskLamp.visible = hall;

  /* --- flashlights --- */
  const tor = dutch && (S.id === 's5' || S.id === 's6' || S.id === 's7' || S.id === 's8');
  ref.torches.forEach(({ sp, cone }) => {
    sp.visible = cone.visible = tor;
    if (!tor) return;
  });

  /* --- fireflies of dust in the torch light --- */
  if (ref.motes) ref.motes.visible = dutch;
}

window.torchState = (list) => {   // list: [{from:[x,y,z], to:[x,y,z]}] from story.js
  ref.torches.forEach(({ sp, cone }, i) => {
    const s = list[i]; if (!s) { sp.visible = cone.visible = false; return; }
    sp.position.set(...s.from); sp.target.position.set(...s.to);
    sp.target.updateMatrixWorld();
    const A = new THREE.Vector3(...s.from), Bp = new THREE.Vector3(...s.to);
    const v = Bp.clone().sub(A), len = v.length();
    cone.position.copy(A).addScaledVector(v, 0.5);
    cone.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), v.clone().normalize());
    cone.scale.set(1, len / 5.2, 1);
  });
};
window.torchLevel = (v) => { ref.torches.forEach(({ sp, cone }) => { sp.intensity = 26 * v; cone.material.opacity = 0.075 * v; }); };

/* ============================ render ============================ */
window.renderFrame = (f) => {
  const S = shotAt(f), L = lightFor(S), C = window.__freeCam || camAt(f), t = f / 30;
  window.__lastF = f;
  applyLight(L);
  camera.position.set(...C.pos); camera.up.set(0, 1, 0); camera.lookAt(...C.look); camera.rotateZ(rx(C.roll || 0));
  camera.fov = C.fov; camera.updateProjectionMatrix(); camera.updateMatrixWorld();
  worldState(S, f, t);
  if (window.torchState && window.__torch) window.torchState(window.__torch(f));
  placeSun(L, new THREE.Vector3(...(C.shadowAt || C.look)));
  if (window.NOACT) drawActors([], camera); else drawActors([...actorsAt(f, T), ...fxAt(f, T)], camera);
  sky.position.copy(camera.position);
  renderer.setRenderTarget(rtColor); renderer.setClearColor(0x000000, 1); renderer.clear(); renderer.render(scene, camera);
  const fog = scene.fog; scene.fog = null; const sm = renderer.shadowMap.enabled; renderer.shadowMap.enabled = false; renderer.shadowMap.autoUpdate = false;
  swapForNd(true); renderer.setRenderTarget(rtNd); renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(scene, camera); swapForNd(false);
  scene.fog = fog; renderer.shadowMap.enabled = sm; renderer.shadowMap.autoUpdate = true;
  const D = dofAt(f);
  inkU.px.value = 2.0;
  renderer.setRenderTarget(rtInk); renderer.render(inkScene, fsCam);
  dofU.focus.value = D.focus; dofU.cinf.value = D.cinf * (H / 1920); dofU.near.value = D.near ?? 1;
  renderer.setRenderTarget(null); renderer.render(dofScene, fsCam);
  drawCaption(f);
  return true;
};
window.__probeCam = (pos, look, fov, pts) => {   // try a camera without touching story.js
  camera.position.set(...pos); camera.up.set(0, 1, 0); camera.lookAt(...look);
  camera.fov = fov; camera.updateProjectionMatrix(); camera.updateMatrixWorld();
  return window.__proj(pts);
};
window.__actorNdc = () => {     // where the current shot's actors land on screen
  const S = shotAt(__lastF), out = [];
  for (const a of actorsAt(__lastF, T)) {
    const v = new THREE.Vector3(a.x, a.y + 1.0, a.z).project(camera);
    out.push({ key: a.key, ndc: [+v.x.toFixed(2), +v.y.toFixed(2), +v.z.toFixed(2)], pos: [a.x, a.y, a.z], s: a.s, alpha: a.alpha });
  }
  return out;
};
window.__proj = (pts) => {     // world point -> NDC (-1..1), for framing checks
  const out = [];
  for (const p of pts) { const v = new THREE.Vector3(...p); v.project(camera); out.push([+v.x.toFixed(2), +v.y.toFixed(2), +v.z.toFixed(2)]); }
  return out;
};
window.__scene = scene; window.__THREE = THREE; window.__cam = camera;
window.TOTAL = TOTAL;
window.fadeAmt = (f) => Math.min(1, Math.max(0, Math.min(f / 30, (TOTAL - 1 - f) / 40)));
window.ready = true;
