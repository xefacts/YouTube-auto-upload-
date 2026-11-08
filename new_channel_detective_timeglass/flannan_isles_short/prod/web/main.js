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
  s1: { kicker: 'OUTER HEBRIDES · DECEMBER 1900', title: 'THE LIGHTHOUSE THAT WENT DARK', titleAt: 24 },
  s2: { counter: ['1900', 'THE FLANNAN ISLES'], slate: 'TWENTY MILES WEST OF SCOTLAND', sub: 'SEVEN ACRES OF ROCK · 110 FT ABOVE THE SEA', slateAt: 30 },
  s3: { kicker: 'RELIEF SHIP · 26 DECEMBER', slate: 'NO FLAG. NO BOAT. NO ANSWER.', sub: 'THE STATION SIGNALLED NOTHING', slateAt: 26 },
  s4: { kicker: 'THE EAST LANDING', slate: 'NOBODY CAME DOWN TO MEET THEM', sub: 'THE BOAT WAITED. THE ROCK STAYED SILENT', slateAt: 34 },
  s5: { kicker: 'INSIDE · THE LANTERN ROOM', slate: 'THE LAMP WAS TRIMMED AND REFILLED', sub: 'WICKS CLEAN · CANS FULL · GLASS POLISHED', slateAt: 40 },
  s6: { kicker: 'THE PEGS', slate: 'ONE OILSKIN LEFT ON ITS PEG', sub: 'JOSEPH MOORE · RELIEF KEEPER', slateAt: 44 },
  s7: { kicker: 'THE WEST LANDING', slate: 'THE SEA CAME OVER THE RAIL', sub: 'IRONWORK TORN FROM 110 FT OF ROCK', slateAt: 50 },
  s8: { kicker: 'THE RECORD · 15 DECEMBER', slate: 'THE LAST ENTRY IN THE LOG', sub: 'BAROMETER 29.6 · WIND NW · WEATHER CLEAR', slateAt: 40 },
  s9: { kicker: 'JANUARY 1901', slate: 'A WAVE TOOK ALL THREE', sub: 'OFFICIAL INQUIRY · ROBERT MUIRHEAD', slateAt: 54 },
  s10: { kicker: 'THE STORY YOU HEARD', title: 'NONE OF IT IS IN THE RECORD', titleAt: 16,
        slate: 'THE CRIES AND THE STORM WERE ADDED IN 1912', slateAt: 60 },
  s11: { kicker: 'EILEAN MÒR · TODAY', title: 'STILL LIT · STILL MISSING', titleAt: 20,
        slate: 'THE FLASH STILL RUNS EVERY THIRTY SECONDS', sub: 'THREE MEN WERE NEVER FOUND', slateAt: 64 },
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

/* ---------- sea ---------- */
const waterU = {
  uT: { value: 0 }, uStorm: { value: 1.2 }, uCam: { value: new THREE.Vector3() },
  uDeep: { value: new THREE.Color('#1d3341') }, uShal: { value: new THREE.Color('#4d7d86') },
  uGlint: { value: new THREE.Color('#e8f0ea') }, uSun: { value: new THREE.Vector3(0.3, 0.6, 0.5) },
  uFog: { value: new THREE.Color() }, uFogNear: { value: 40 }, uFogFar: { value: 700 },
};
const SEA_SEG = +(new URLSearchParams(location.search).get('seaseg') || 110);
const seaGeo = new THREE.PlaneGeometry(2400, 2400, SEA_SEG, SEA_SEG); seaGeo.rotateX(-Math.PI / 2);
const sea = new THREE.Mesh(seaGeo, new THREE.ShaderMaterial({
  uniforms: waterU,
  vertexShader: `
    uniform float uT, uStorm; varying vec3 vW; varying float vH;
    float wv(vec2 p, vec2 d, float amp, float len, float sp){ return sin(dot(p, normalize(d)) * (6.28318/len) + uT*sp) * amp; }
    void main(){
      vec4 wp = modelMatrix * vec4(position, 1.0);
      vec2 p = wp.xz;
      float h = wv(p, vec2(1.0,0.22), 1.10, 52.0, 0.9) + wv(p, vec2(-0.35,1.0), 0.70, 29.0, 1.35)
              + wv(p, vec2(0.8,-0.55), 0.34, 15.0, 1.9) + wv(p, vec2(0.15,0.95), 0.16, 7.5, 2.8);
      h *= uStorm * 0.85;
      wp.y += h; vH = h; vW = wp.xyz;
      gl_Position = projectionMatrix * viewMatrix * wp;
    }`,
  fragmentShader: `
    uniform vec3 uDeep, uShal, uGlint, uSun, uCam, uFog; uniform float uFogNear, uFogFar, uStorm;
    varying vec3 vW; varying float vH;
    void main(){
      vec3 n = normalize(cross(dFdx(vW), dFdy(vW))); if (n.y < 0.0) n = -n;
      vec3 V = normalize(uCam - vW);
      float fres = pow(1.0 - clamp(dot(n, V), 0.0, 1.0), 3.0);
      vec3 c = mix(uDeep, uShal, clamp(vH * 0.42 + 0.45, 0.0, 1.0));
      c = mix(c, uShal * 1.22, fres * 0.55);
      float spec = pow(max(dot(reflect(-normalize(uSun), n), V), 0.0), 48.0);
      c += uGlint * spec * 0.85;
      float crest = smoothstep(0.7, 1.0, vH / max(uStorm * 0.55, 0.001));
      c = mix(c, mix(uShal, vec3(0.9,0.94,0.95), 0.5), crest * 0.28);
      float d = length(uCam - vW);
      c = mix(c, uFog, smoothstep(uFogNear, uFogFar, d));
      gl_FragColor = vec4(c, 1.0);
    }`,
}));
sea.userData.ndSkip = true; sea.frustumCulled = false; scene.add(sea);

/* ---------- soft billboard sprite (spray / foam) ---------- */
const softSprite = (() => {
  const c = document.createElement('canvas'); c.width = c.height = 256; const q = c.getContext('2d');
  const gr = q.createRadialGradient(128, 128, 0, 128, 128, 128);
  gr.addColorStop(0, 'rgba(255,255,255,.55)'); gr.addColorStop(0.5, 'rgba(248,253,255,.22)'); gr.addColorStop(1, 'rgba(240,250,252,0)');
  q.fillStyle = gr; q.fillRect(0, 0, 256, 256);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
})();
const sprayMat = (i) => new THREE.MeshBasicMaterial({ map: softSprite, transparent: true, opacity: 0.1, depthWrite: false, color: '#eaf4f6' });
const foamSprite = softSprite;

/* ============================ THE ISLES ============================ */
const sets = {}; const ref = {};
const stage = (name) => { const g = new THREE.Group(); g.name = name; g.visible = false; scene.add(g); sets[name] = g; return g; };
const add = (geo, mat, x = 0, y = 0, z = 0, parent = scene, opts = {}) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = opts.cast ?? true; m.receiveShadow = true; parent.add(m); return m; };
const cyl = (p, r1, r2, h, m, x, y, z, seg = 14) => add(new THREE.CylinderGeometry(r1, r2, h, seg), m, x, y, z, p);
const bx = (p, w, h, d, m, x, y, z) => add(new THREE.BoxGeometry(w, h, d), m, x, y, z, p);
const pl = (p, w, d, m, x, y, z) => { const o = add(new THREE.PlaneGeometry(w, d), m, x, y, z, p, { cast: false }); o.rotation.x = -Math.PI / 2; return o; };
const post = (p, a, b, r, m) => { const A = new THREE.Vector3(...a), B = new THREE.Vector3(...b), v = B.clone().sub(A); const o = add(new THREE.CylinderGeometry(r, r, v.length(), 8), m, ...A.clone().add(B).multiplyScalar(.5).toArray(), p); o.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), v.normalize()); return o; };

const B = 34.7;           // tower base height (plateau)
{
  const g = stage('isles');

  /* ---------- the rock ---------- */
  cyl(g, 15.9, 30.0, 43, mats.rock, 0, 12.5, 0, 24);
  cyl(g, 16.3, 23.0, 16, mats.rockDark, 0, 12, 0, 20);
  cyl(g, 18.2, 26.0, 20, mats.rockDark, 0, 8, 0, 18);
  cyl(g, 16.5, 18.3, 6.0, mats.rock, 0, 31, 0, 24);
  cyl(g, 15.4, 15.9, 0.9, mats.isleGrass, 0, 34.45, 0, 28);
  // ragged rim (leave the NE window open for the s9/s10 sight-line)
  for (let i = 0; i < 30; i++) {
    const a = (i / 30) * Math.PI * 2 + (i % 3) * 0.09;
    const deg = ((a * 180 / Math.PI) % 360 + 360) % 360;
    if ((deg > 282 && deg < 352) || (deg > 18 && deg < 78)) continue;
    const r = 15.1 + ((i * 7) % 5) * 0.32;
    const m = add(new THREE.IcosahedronGeometry(0.85 + ((i * 13) % 7) * 0.2, 0), mats.rockChunk, Math.cos(a) * r, 34.15 + ((i * 5) % 4) * 0.2, Math.sin(a) * r, g);
    m.rotation.set(i, i * 2.1, i * 0.7);
  }
  for (let i = 0; i < 46; i++) {
    const a = (i * 2.39996) % (Math.PI * 2), rr = 3.6 + ((i * 37) % 11) * 0.95;
    const x = Math.cos(a) * rr, z = Math.sin(a) * rr;
    if (Math.abs(x) < 2.2 && Math.abs(z) < 2.2) continue;
    const s = 0.14 + ((i * 13) % 7) * 0.06;
    const m = add(new THREE.IcosahedronGeometry(s, 0), mats.rockChunk, x, 34.85, z, g, { cast: false });
    m.scale.set(1.3, 0.55, 1.1); m.rotation.set(i, i * 1.7, i * 0.9);
  }
  for (let i = 0; i < 30; i++) {
    const a = (i * 2.39996 + 1.1) % (Math.PI * 2), rr = 4.2 + ((i * 29) % 10) * 1.0;
    const x = Math.cos(a) * rr, z = Math.sin(a) * rr;
    for (let k = 0; k < 3; k++) {
      const m = add(new THREE.ConeGeometry(0.07, 0.26 + (k % 2) * 0.1, 4), mats.isleGrass, x + (k - 1) * 0.09, 34.98, z + (k % 2) * 0.06, g, { cast: false });
      m.rotation.z = (k - 1) * 0.2;
    }
  }
  const bould = (x, y, z, r, sy = 1) => { const m = add(new THREE.IcosahedronGeometry(r, 0), mats.rockChunk, x, y, z, g); m.scale.set(1, sy, 0.92); m.rotation.set(r * 0.13, x * 0.3, z * 0.17); return m; };
  bould(19, 9, -7, 5.4, 1.3); bould(-6, 5, 19, 5.8, 1.2); bould(12, 6, 15, 4.2, 1.1);
  bould(13, 20, 10, 3.6, 1.4); bould(-12, 24, -11, 3.4, 1.4); bould(4, 30, -13, 2.8, 1.3);
  bould(15, 31, 5, 2.4, 1.2); bould(-16, 30, 6, 2.6, 1.2);
  // neighbours
  for (const [x, z, s, h] of [[-420, -210, 1.8, 30], [-190, -450, 2.2, 26], [330, -380, 2.0, 28], [-470, 150, 1.5, 22], [250, 330, 1.4, 24]]) {
    const m = add(new THREE.ConeGeometry(24 * s, h * s, 9), mats.rockDark, x, h * s * 0.42, z, g, { cast: false });
    m.scale.set(1.5, 1, 1.2);
  }

  /* ---------- lighthouse ---------- */
  const tg = new THREE.Group(); g.add(tg);
  cyl(tg, 3.9, 4.15, 0.55, mats.ironDark, 0, B + 0.27, 0, 22);            // footing
  cyl(tg, 3.55, 3.95, 3.0, mats.baseStone, 0, B + 2.05, 0, 26);            // masonry base
  cyl(tg, 3.56, 3.96, 0.5, mats.ironDark, 0, B + 0.9, 0, 26);
  cyl(tg, 2.05, 3.55, 17.6, mats.white, 0, B + 12.4, 0, 24);              // shaft
  for (const [yy, r1, r2] of [[B + 4.2, 3.42, 3.5], [B + 15.0, 2.62, 2.72], [B + 20.6, 2.2, 2.3]]) {
    cyl(tg, r1, r2, 0.42, mats.ironDark, 0, yy, 0, 24);                    // black bands
  }
  bx(tg, 1.36, 2.44, 0.14, mats.baseStone, 0, B + 2.5, 3.72);            // door surround
  bx(tg, 1.06, 2.16, 0.16, mats.doorWood, 0, B + 2.44, 3.76);                   // door leaf
  for (let k = 0; k < 4; k++) bx(tg, 0.9, 0.05, 0.03, mats.ironDark, 0, B + 1.72 + k * 0.46, 3.85);
  bx(tg, 0.06, 0.06, 0.06, mats.brass, 0.34, B + 2.4, 3.86);
  add(new THREE.SphereGeometry(0.13, 10, 8), mats.brass, 0, B + 4.0, 3.8, tg);
  bx(tg, 1.7, 0.12, 0.5, mats.baseStone, 0, B + 1.34, 3.78);                    // threshold step
  for (const [yy, ang] of [[B + 7.6, 0.5], [B + 12.6, -0.7], [B + 16.8, 1.9]]) {
    const w = bx(tg, 0.44, 1.0, 0.22, mats.ironDark, Math.sin(ang) * 2.72, yy, Math.cos(ang) * 2.72);
    w.rotation.y = ang;
  }
  // gallery
  cyl(tg, 3.15, 3.15, 0.34, mats.ironDark, 0, B + 21.5, 0, 26);
  for (let i = 0; i < 18; i++) { const a = i / 18 * Math.PI * 2; post(tg, [Math.cos(a) * 2.95, B + 21.6, Math.sin(a) * 2.95], [Math.cos(a) * 2.95, B + 22.9, Math.sin(a) * 2.95], 0.045, mats.iron); }
  for (const yy of [B + 22.35, B + 22.88]) {
    const ring = add(new THREE.TorusGeometry(2.95, 0.045, 5, 40), mats.iron, 0, yy, 0, tg); ring.rotation.x = Math.PI / 2;
  }
  // lantern room
  cyl(tg, 1.55, 1.55, 0.3, mats.ironDark, 0, B + 21.98, 0, 18);
  const lg = add(new THREE.CylinderGeometry(1.42, 1.42, 2.15, 18, 1, true), mats.glass, 0, B + 23.2, 0, tg, { cast: false }); lg.material.side = THREE.DoubleSide;
  for (let i = 0; i < 8; i++) { const a = i / 8 * Math.PI * 2; post(tg, [Math.cos(a) * 1.44, B + 22.1, Math.sin(a) * 1.44], [Math.cos(a) * 1.44, B + 24.3, Math.sin(a) * 1.44], 0.038, mats.ironDark); }
  cyl(tg, 1.62, 1.62, 0.22, mats.ironDark, 0, B + 24.35, 0, 18);
  add(new THREE.ConeGeometry(1.72, 1.15, 18), mats.ironDark, 0, B + 25.0, 0, tg);
  add(new THREE.SphereGeometry(0.16, 10, 8), mats.brass, 0, B + 25.7, 0, tg);
  ref.lampSphere = add(new THREE.SphereGeometry(0.52, 16, 12), mats.lampGlow, 0, B + 23.2, 0, tg, { cast: false });
  // the beam (two opposed cones, spinning)
  const beamMat = new THREE.MeshBasicMaterial({ color: '#ffe6b0', transparent: true, opacity: 0.055, depthWrite: false, side: THREE.DoubleSide });
  const bg = new THREE.Group(); bg.position.set(0, B + 23.2, 0); tg.add(bg); ref.beam = bg;
  for (const s of [1, -1]) {
    const c = new THREE.Mesh(new THREE.ConeGeometry(0.62, 78, 10, 1, true), beamMat);
    c.rotation.z = s * Math.PI / 2; c.position.x = s * 39; c.userData.ndSkip = true; bg.add(c);
  }
  ref.beamMats = [beamMat];

  /* ---------- west landing (the place the storm hit) ---------- */
  const LX = -33, LY = 11, LZ = 4;
  const lg2 = new THREE.Group(); g.add(lg2);
  bx(lg2, 9.5, 0.7, 7.0, mats.rockChunk, LX, LY - 0.35, LZ);
  for (let i = 0; i < 5; i++) bx(lg2, 9.5, 0.28, 0.14, mats.ironDark, LX, LY + 1.05, LZ - 3.2 + i * 1.6);
  for (let i = 0; i < 5; i++) post(lg2, [LX - 4.4, LY + 1.1, LZ - 3.2 + i * 1.6], [LX - 4.4, LY - 0.2, LZ - 3.2 + i * 1.6], 0.07, mats.ironDark);
  post(lg2, [LX - 4.4, LY + 1.1, LZ - 3.2], [LX - 4.4, LY + 1.1, LZ - 0.2], 0.07, mats.ironDark);
  // the snapped half of the rail, hanging out over the drop
  const snap = post(lg2, [LX - 4.4, LY + 1.1, LZ + 0.4], [LX - 5.9, LY + 0.05, LZ + 2.6], 0.07, mats.ironDark); snap.rotation.z = 0.2;
  post(lg2, [LX - 4.4, LY + 1.05, LZ + 0.5], [LX - 4.4, LY - 0.3, LZ + 0.5], 0.07, mats.ironDark);
  // a ladder torn loose and left hanging against the rock
  const ladd = new THREE.Group(); g.add(ladd); ladd.position.set(LX + 1.4, LY + 1.2, LZ - 3.4); ladd.rotation.set(0.22, 0.5, 0.3);
  for (let i = 0; i < 14; i++) bx(ladd, 0.9, 0.05, 0.05, mats.ironDark, 0, i * 0.32, 0);
  for (const sx of [-0.42, 0.42]) bx(ladd, 0.06, 4.4, 0.06, mats.ironDark, sx, 2.2, 0);
  // steps up the cliff to the plateau
  for (let i = 0; i < 22; i++) {
    const t = i / 21;
    bx(lg2, 2.0, 0.22, 0.52, mats.rockChunk, LX + 5.0 + t * 8.4, LY + 0.4 + t * 23.2, LZ - 1.2 + t * 1.6);
  }
  // derrick crane
  post(lg2, [LX + 2.6, LY, LZ + 2.2], [LX + 1.2, LY + 5.4, LZ + 2.2], 0.12, mats.woodDark);
  post(lg2, [LX + 2.6, LY, LZ + 2.2], [LX + 5.0, LY + 4.6, LZ + 2.2], 0.1, mats.woodDark);
  post(lg2, [LX + 1.35, LY + 5.2, LZ + 2.2], [LX + 1.35, LY + 3.6, LZ + 2.2], 0.03, mats.ironDark);

  /* ---------- the relief boat ---------- */
  const boat = new THREE.Group(); g.add(boat); ref.boat = boat;
  const hull = add(new THREE.CylinderGeometry(1.5, 0.95, 7.2, 12, 1, false, 0, Math.PI), mats.wood, 0, 0, 0, boat); hull.rotation.z = Math.PI / 2; hull.rotation.y = Math.PI / 2;
  bx(boat, 6.4, 0.16, 2.2, mats.plank, 0, 0.5, 0);
  bx(boat, 1.0, 0.9, 1.1, mats.woodDark, -1.6, 1.0, 0);
  post(boat, [1.9, 0.5, 0], [1.9, 5.2, 0], 0.07, mats.woodDark);
  add(new THREE.PlaneGeometry(2.0, 1.6), mats.rag, 2.9, 3.3, 0, boat, { cast: false });
  boat.position.set(-52, 1.0, 30); boat.rotation.y = -0.5;
  ref.boatHome = [-52, 1.0, 30];

  /* ---------- spray sheets + the s7 comber ---------- */
  for (let i = 0; i < 6; i++) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(2.4 + i * 1.7, 1.3 + i * 0.5), sprayMat(i));
    m.userData.ndSkip = true; m.position.set(LX + 2.0 + i * 1.5, 1.4 + i * 0.55, LZ + 10.5 + i * 1.3); g.add(m);
    (ref.sprayList || (ref.sprayList = [])).push({ m, ph: i * 0.72 });
  }
  // foam texture: torn lace, so the comber reads as water instead of a white sheet
  const foamTex = (() => {
    const c = document.createElement('canvas'); c.width = 512; c.height = 256; const q = c.getContext('2d');
    let sd = 7; const rnd = () => (sd = (sd * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;
    for (let i = 0; i < 190; i++) {
      const x = rnd() * 512, y = Math.pow(rnd(), 0.5) * 256;
      const r = 3 + rnd() * 16, a = 0.05 + rnd() * 0.28 * (1 - y / 256);
      q.fillStyle = `rgba(240,249,252,${a})`; q.beginPath(); q.arc(x, y, r, 0, 7); q.fill();
    }
    for (let i = 0; i < 70; i++) {
      const x = rnd() * 512, y = rnd() * 120, h = 40 + rnd() * 110;
      q.strokeStyle = `rgba(255,255,255,${0.05 + rnd() * 0.13})`; q.lineWidth = 1 + rnd() * 2;
      q.beginPath(); q.moveTo(x, y); q.lineTo(x + (rnd() - 0.5) * 10, y + h); q.stroke();
    }
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
  })();
  const waveM = new THREE.Mesh(new THREE.PlaneGeometry(8, 5), new THREE.MeshBasicMaterial({ map: foamTex, transparent: true, opacity: 0, depthWrite: false }));
  waveM.userData.ndSkip = true; waveM.frustumCulled = false; g.add(waveM); ref.wave = waveM;
  // a second, smaller crest behind it for depth
  const waveM2 = waveM.clone(); waveM2.material = waveM.material.clone(); waveM2.scale.set(0.7, 0.62, 1); g.add(waveM2); ref.wave2 = waveM2;
  // a low sheet of white water running along the base of the landing
  const surge = new THREE.Mesh(new THREE.PlaneGeometry(20, 6), new THREE.MeshBasicMaterial({ map: foamTex, transparent: true, opacity: 0, depthWrite: false }));
  surge.userData.ndSkip = true; surge.rotation.x = -Math.PI / 2; g.add(surge); ref.surge = surge;

  /* ---------- rain ---------- */
  const N = 340, rp = new Float32Array(N * 6);
  for (let i = 0; i < N; i++) (ref.drops || (ref.drops = [])).push({ x: (Math.random() - 0.5) * 90, y: Math.random() * 54, z: (Math.random() - 0.5) * 90, v: 26 + Math.random() * 20 });
  const rgeo = new THREE.BufferGeometry(); rgeo.setAttribute('position', new THREE.BufferAttribute(rp, 3));
  const rain = new THREE.LineSegments(rgeo, new THREE.LineBasicMaterial({ color: '#dceaf4', transparent: true, opacity: 0.34, depthWrite: false }));
  rain.userData.ndSkip = true; rain.frustumCulled = false; g.add(rain); ref.rain = rain; ref.rainPos = rp;
}

/* ============================ LANTERN ROOM ============================ */
const ROOM_R = 3.7;
{
  const g = stage('lamp');
  const floor = add(new THREE.CircleGeometry(ROOM_R, 36), mats.plank, 0, 0.01, 0, g, { cast: false }); floor.rotation.x = -Math.PI / 2;
  const wall = new THREE.Mesh(new THREE.CylinderGeometry(ROOM_R, ROOM_R, 3.2, 36, 1, true), mats.wallWarm);
  wall.material.side = THREE.DoubleSide; wall.position.y = 1.6; wall.receiveShadow = true; g.add(wall);
  const dado = new THREE.Mesh(new THREE.CylinderGeometry(ROOM_R - 0.02, ROOM_R - 0.02, 1.05, 36, 1, true), mats.plank);
  dado.material.side = THREE.DoubleSide; dado.position.y = 0.52; g.add(dado);
  const rail = add(new THREE.TorusGeometry(ROOM_R - 0.03, 0.05, 5, 40), mats.woodDark, 0, 1.05, 0, g); rail.rotation.x = Math.PI / 2;
  const ceil = add(new THREE.CircleGeometry(ROOM_R, 36), mats.plank, 0, 3.2, 0, g, { cast: false }); ceil.rotation.x = Math.PI / 2;

  // the apparatus — pedestal, brass rings, glass, mantle
  cyl(g, 0.52, 0.66, 0.34, mats.ironDark, 0, 0.17, 0, 20);
  cyl(g, 0.3, 0.36, 0.85, mats.brass, 0, 0.77, 0, 18);
  cyl(g, 0.62, 0.5, 0.1, mats.brass, 0, 1.22, 0, 20);
  ref.lampSphere = add(new THREE.SphereGeometry(0.2, 14, 10), mats.lampGlow, 0, 1.62, 0, g, { cast: false });
  const gl = add(new THREE.CylinderGeometry(0.6, 0.6, 1.05, 18, 1, true), mats.glass, 0, 1.66, 0, g, { cast: false }); gl.material.side = THREE.DoubleSide;
  for (const yy of [1.2, 2.02]) { const t = add(new THREE.TorusGeometry(0.6, 0.035, 5, 26), mats.brass, 0, yy, 0, g); t.rotation.x = Math.PI / 2; }
  cyl(g, 0.72, 0.62, 0.12, mats.brass, 0, 2.16, 0, 20);
  add(new THREE.ConeGeometry(0.66, 0.34, 18), mats.ironDark, 0, 2.38, 0, g);

  // the keeper's table (south side) — logbook, barometer, ink
  bx(g, 1.7, 0.08, 0.9, mats.wood, 1.1, 0.86, 2.35);
  for (const [lx, lz] of [[-0.72, -0.34], [0.72, -0.34], [-0.72, 0.34], [0.72, 0.34]]) bx(g, 0.09, 0.86, 0.09, mats.woodDark, 1.1 + lx, 0.43, 2.35 + lz);
  const book = bx(g, 0.46, 0.05, 0.34, mats.woodDark, 1.06, 0.925, 2.33); book.rotation.y = 0.1;
  const pg = bx(g, 0.43, 0.012, 0.31, mats.paper, 1.06, 0.955, 2.33); pg.rotation.y = 0.1;
  const inkG = new THREE.Group(); inkG.position.set(1.06, 0.966, 2.33); inkG.rotation.y = 0.1; g.add(inkG);
  for (let k = 0; k < 8; k++) bx(inkG, 0.26 - (k % 3) * 0.04, 0.004, 0.006, mats.ink, -0.02, 0, -0.12 + k * 0.031);
  cyl(g, 0.15, 0.15, 0.06, mats.brass, 0.6, 0.93, 2.22, 18);
  add(new THREE.CircleGeometry(0.12, 18), mats.paper, 0.6, 0.965, 2.22, g).rotation.x = -Math.PI / 2;
  add(new THREE.CircleGeometry(0.03, 12), mats.brass, 0.6, 0.97, 2.22, g).rotation.x = -Math.PI / 2;
  const st = bx(g, 0.34, 0.22, 0.34, mats.woodDark, 1.65, 0.55, 2.9); st.rotation.y = 0.3;
  // chalk slate on the wall over the table
  add(new THREE.PlaneGeometry(0.72, 0.92), mats.ink, 1.35, 2.2, 3.62, g, { cast: false }).rotation.y = Math.PI;
  for (let k = 0; k < 5; k++) add(new THREE.PlaneGeometry(0.5 - k * 0.04, 0.012), mats.paper, 1.35, 2.5 - k * 0.14, 3.6, g, { cast: false }).rotation.y = Math.PI;

  // pegs + oilskins on the north wall
  // peg board: a curved panel following the wall, so nothing clips through it
  const boardR = ROOM_R - 0.07, th0 = Math.PI - 0.85, thL = 1.7;
  const board = new THREE.Mesh(new THREE.CylinderGeometry(boardR, boardR, 1.75, 24, 1, true, th0, thL), mats.plank);
  board.material = mats.plank.clone(); board.material.side = THREE.DoubleSide;
  board.position.y = 1.75; g.add(board); board.receiveShadow = true;
  const pegRail = new THREE.Mesh(new THREE.CylinderGeometry(boardR - 0.01, boardR - 0.01, 0.11, 24, 1, true, th0, thL), mats.woodDark);
  pegRail.material = mats.woodDark.clone(); pegRail.material.side = THREE.DoubleSide;
  pegRail.position.y = 1.96; g.add(pegRail);
  const pegAt = (theta) => [Math.sin(theta) * (boardR - 0.06), Math.cos(theta) * (boardR - 0.06)];
  for (const [i, theta] of [Math.PI + 0.62, Math.PI, Math.PI - 0.62].entries()) {
    const hasCoat = (i === 1);
    const [px, pz] = pegAt(theta);
    const peg = cyl(g, 0.03, 0.03, 0.2, mats.brass, px * 0.98, 1.92, pz * 0.98, 8);
    peg.rotation.set(Math.PI / 2, -theta, 0);
    if (!hasCoat) continue;
    const c = new THREE.Group(); c.position.set(px * 0.86, 1.3, pz * 0.86); c.rotation.y = theta; c.scale.setScalar(1.25); g.add(c);
    bx(c, 0.34, 0.82, 0.14, mats.coat, 0, 0, 0);
    bx(c, 0.38, 0.26, 0.15, mats.coat, 0, 0.45, 0.004);
    const hood = add(new THREE.SphereGeometry(0.12, 10, 8), mats.coatDark, 0, 0.58, 0.01, c); hood.scale.set(1, 0.8, 0.8);
    bx(c, 0.1, 0.56, 0.11, mats.coat, -0.2, -0.05, 0.01);
    bx(c, 0.1, 0.56, 0.11, mats.coat, 0.2, -0.05, 0.01);
    bx(c, 0.42, 0.04, 0.02, mats.rag, 0, 0.02, 0.08);
    bx(c, 0.36, 0.04, 0.02, mats.rag, 0, -0.42, 0.07);
  }

  // stool + bucket
  bx(g, 0.36, 0.05, 0.36, mats.wood, -1.5, 0.44, 1.5);
  for (const [sx, sz] of [[-0.13, -0.13], [0.13, -0.13], [-0.13, 0.13], [0.13, 0.13]]) bx(g, 0.045, 0.44, 0.045, mats.woodDark, -1.5 + sx, 0.22, 1.5 + sz);
  cyl(g, 0.18, 0.15, 0.34, mats.ironDark, -2.55, 0.17, 2.3, 14);
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
const tmpV = new THREE.Vector3();
function applyLight(L) {
  hemi.color.set(L.sky); hemi.groundColor.set(L.ground); hemi.intensity = L.hemi;
  sun.color.set(L.sun); sun.intensity = L.sunI;
  scene.fog.color.set(L.fog); scene.fog.near = L.fogNear; scene.fog.far = L.fogFar;
  skyU.top.value.set(L.skyTop); skyU.hor.value.set(L.skyHor); skyU.sunCol.value.set(L.sunDisc || '#000'); skyU.sunSize.value = L.sunSize || 0;
  inkU.sat.value = L.sat; inkU.gain.value.set(L.gain || '#ffffff'); inkU.lift.value.set(L.lift || '#000000'); inkU.vig.value = L.vig ?? 0.24;
  waterU.uDeep.value.set(L.waterDeep); waterU.uShal.value.set(L.waterShal); waterU.uGlint.value.set(L.glint);
  waterU.uFog.value.set(L.fog); waterU.uFogNear.value = L.fogNear * 0.7; waterU.uFogFar.value = L.fogFar;
  waterU.uStorm.value = L.storm ?? 1.0;
}
function placeSun(L, focus) {
  const az = rx(L.az), el = rx(L.el);
  tmpV.set(Math.cos(el) * Math.cos(az), Math.sin(el), Math.cos(el) * Math.sin(az));
  skyU.sunDir.value.copy(tmpV); waterU.uSun.value.copy(tmpV);
  sun.position.copy(focus).addScaledVector(tmpV, 140); sun.target.position.copy(focus);
  const ext = L.shadowExt || 60, sc = sun.shadow.camera;
  sc.left = -ext; sc.right = ext; sc.top = ext; sc.bottom = -ext; sc.near = 1; sc.far = 380; sc.updateProjectionMatrix();
}

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

function worldState(S, f, t) {
  for (const [name, g] of Object.entries(sets)) g.visible = name === S.loc;
  const isles = S.loc === 'isles';
  waterU.uT.value = t;
  // lamp: lit in s1 (until it dies mid-shot), dark s2-s10, lit again at sunrise
  let lit = 0;
  if (S.id === 's1') lit = f > S.a + (S.b - S.a) * 0.62 ? 0 : 1;
  else if (S.id === 's2' || S.id === 's3' || S.id === 's4') lit = 0;
  else if (S.id === 's11') lit = 1;
  else lit = 0;
  const lampOn = S.loc === 'lamp' ? 1 : lit;
  if (ref.lampSphere) {
    const inRoom = S.loc === 'lamp';
    ref.lampSphere.material = (inRoom || lit) ? mats.lampGlow : mats.lampDark;
  }
  lampLight.intensity = S.loc === 'lamp' ? 2.9 * (0.96 + 0.04 * Math.sin(t * 9.1)) : (lit ? 2.2 : 0);
  if (S.loc === 'lamp') { const k = S.id === 's8' ? 0.5 : 0.7; roomFill.intensity = 0.75 * k; roomFill.position.set(camera.position.x * 0.5, 2.6, camera.position.z * 0.5); }
  else roomFill.intensity = 0;
  if (S.id === 's6' || S.id === 's8') { pegFill.intensity = 2.0; pegFill.position.set(-0.5, 2.3, -1.2); } else pegFill.intensity = 0;
  if (ref.beam) {
    ref.beam.rotation.y = t * 0.55;
    ref.beamMats.forEach((m) => { m.opacity = lit * (0.030 + 0.012 * Math.sin(t * 2.1)); });
  }
  if (ref.boat) {
    ref.boat.visible = isles;
    ref.boat.position.set(ref.boatHome[0], ref.boatHome[1] + Math.sin(t * 1.9) * 0.42, ref.boatHome[2]);
    ref.boat.rotation.z = Math.sin(t * 1.55) * 0.07;
    ref.boat.rotation.x = Math.sin(t * 1.2) * 0.04;
  }
  if (ref.rain) {
    const heavy = (S.id === 's1' || S.id === 's3' || S.id === 's7');
    const p = ref.rainPos, h = 54;
    for (let i = 0; i < ref.drops.length; i++) {
      const d = ref.drops[i];
      const yy = ((d.y - t * d.v * 6) % h + h) % h;
      const k = i * 6, on = heavy ? 1 : 0;
      p[k] = (d.x * on) + camera.position.x; p[k + 1] = yy * on + camera.position.y - 18; p[k + 2] = (d.z * on) + camera.position.z;
      p[k + 3] = p[k] + 0.45; p[k + 4] = p[k + 1] - 2.1; p[k + 5] = p[k + 2];
    }
    ref.rain.geometry.attributes.position.needsUpdate = true;
    ref.rain.visible = heavy;
  }
  for (const s of (ref.sprayList || [])) {
    const k = Math.sin(t * 1.6 + s.ph) * 0.5 + 0.5;
    s.m.position.y = 0.7 + k * (2.6 + (waterU.uStorm.value) * 1.2);
    s.m.scale.setScalar(0.8 + k * 1.1);
    s.m.visible = (S.id === 's1' || S.id === 's3' || S.id === 's7');
    s.m.material.opacity = (S.id === 's7' ? 0.09 : 0.06) * (0.35 + k * 0.6);
    s.m.lookAt(camera.position);
  }
  if (ref.wave) {
    const inS = S.id === 's7';
    const k = inS ? Math.min(1, (f - S.a) / 300) : 0;
    const cyc = (Math.sin(t * 1.25) * 0.5 + 0.5);
    ref.wave.visible = inS; ref.wave2.visible = inS;
    if (inS) {
      ref.wave.position.set(-36.0, 3.6 + cyc * 3.4, 12.5 + cyc * 0.8);
      ref.wave.lookAt(camera.position.x, ref.wave.position.y - 2.0, camera.position.z);
      ref.wave.scale.set(0.85 + cyc * 0.15, 0.6 + cyc * 0.3, 1);
      ref.wave.material.opacity = (0.20 + cyc * 0.22) * Math.min(1, k * 4 + 0.3);
      ref.wave2.position.set(-42.0, 1.8 + cyc * 1.8, 9.0);
      ref.wave2.lookAt(camera.position.x, ref.wave2.position.y - 1.6, camera.position.z);
      ref.wave2.material.opacity = (0.10 + cyc * 0.14) * Math.min(1, k * 4 + 0.3);
      ref.surge.visible = inS;
      ref.surge.position.set(-36, 1.2 + cyc * 1.4, 14);
      ref.surge.material.opacity = (0.10 + cyc * 0.12) * Math.min(1, k * 4 + 0.3);
      ref.surge.scale.set(1, 1 + cyc * 0.35, 1);
    }
  }
}

window.renderFrame = (f) => {
  const S = shotAt(f), L = lightFor(S), C = camAt(f), t = f / 30;
  applyLight(L);
  camera.position.set(...C.pos); camera.up.set(0, 1, 0); camera.lookAt(...C.look); camera.rotateZ(rx(C.roll || 0));
  camera.fov = C.fov; camera.updateProjectionMatrix(); camera.updateMatrixWorld();
  waterU.uCam.value.copy(camera.position);
  worldState(S, f, t);
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
window.__scene = scene; window.__THREE = THREE; window.__cam = camera;
window.TOTAL = TOTAL;
window.fadeAmt = (f) => Math.min(1, Math.max(0, Math.min(f / 30, (TOTAL - 1 - f) / 40)));
window.ready = true;
