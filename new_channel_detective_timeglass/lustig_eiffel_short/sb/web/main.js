import * as THREE from './lib/three.module.js';
import * as T from './toon.js';
import * as P from './paint.js';
import { SHOTS, TOTAL, shotAt, camAt, dofAt, LIGHTS, lightFor, actorsAt, worldAt, fxAt } from './story.js';


const W = 720, H = 1280;                                   // design space (all layout math stays here)
const SC = Math.min(3, Math.max(1, +(new URLSearchParams(location.search).get('sc') || 1)));
const PW = Math.round(W * SC), PH = Math.round(H * SC);    // physical render pixels
const MS = +(new URLSearchParams(location.search).get('ms') ?? 2);   // MSAA samples
const SM = +(new URLSearchParams(location.search).get('sm') ?? 1024); // shadow map px
const canvas = document.getElementById('c');
const capCanvas=document.getElementById('caption'),capCtx=capCanvas.getContext('2d');
canvas.width = PW; canvas.height = PH; capCanvas.width = PW; capCanvas.height = PH;
/* ---------- storyboard overlay: title / chip / counter / caption / labels / gold arrow ---------- */
const easeOut = t => { t = Math.max(0, Math.min(1, t)); return 1 - Math.pow(1 - t, 3); };
const proj = p => { const v = new THREE.Vector3(p[0], p[1], p[2]); v.project(camera); return { x: (v.x * .5 + .5) * W, y: (-v.y * .5 + .5) * H, vis: v.z < 1 }; };
const outlined = (txt, x, y, font, fill, lw, align = 'center', sp, maxW) => {
  capCtx.save(); capCtx.font = font; capCtx.textAlign = align; capCtx.textBaseline = 'middle';
  capCtx.lineJoin = 'round'; capCtx.lineWidth = lw; capCtx.strokeStyle = '#0c0a10'; capCtx.fillStyle = fill;
  if (sp !== undefined && 'letterSpacing' in capCtx) capCtx.letterSpacing = sp + 'px';
  if (maxW) { capCtx.strokeText(txt, x, y, maxW); capCtx.fillText(txt, x, y, maxW); }
  else { capCtx.strokeText(txt, x, y); capCtx.fillText(txt, x, y); }
  if ('letterSpacing' in capCtx) capCtx.letterSpacing = '0px';
  capCtx.restore();
};
const FONT = '900 %dpx "Arial Black", Arial, sans-serif';
const OV = {
  s1: { title: 'THE MAN WHO SOLD THE EIFFEL TOWER', sub: 'PARIS \u00b7 1925', caption: 'SELLS THE EIFFEL TOWER.' },
  s2: { counter: ['1925', 'THE SETUP'], chip: 'SECRET MEETING', honesty: 'BASED ON THE 1961 ACCOUNT', caption: 'PARIS, NINETEEN TWENTY-FIVE.' },
  s3: { labels: [{ at: [-0.5, 1.1, -0.85], t: 'FORGED PAPERS', dx: 118, dy: -54 }], caption: 'SIX SCRAP DEALERS.' },
  s4: { caption: 'QUIETLY BEING SOLD FOR SCRAP.' },
  s5: { chip: 'THE BRIBE', labels: [{ at: [-0.35, 1.78, 0.15], t: 'THE BUYER', dx: -120, dy: -48 }],
        arrow: { from: [0.45, 1.12, -0.9], to: [0.95, 1.4, -0.5] }, caption: 'PAYS A BRIBE ON TOP.' },
  s6: { chip: 'HE VANISHES', caption: 'LUSTIG VANISHES.' },
  s7: { chip: 'THE PERFECT ALIBI', gold: 1, caption: 'SHAME WAS THE ALIBI.' },
  s8: { chip: 'HE DOES IT AGAIN', gold: 1, caption: 'THE EXACT SAME TRICK.' },
  s9: { counter: ['1935', 'CAUGHT'], chip: 'NOT FOR THE TOWER',
        labels: [{ at: [0.15, 1.45, 0.3], t: 'FAKE HUNDREDS', dx: 118, dy: -46, gold: 1 }], caption: 'FOR FAKE MONEY, NOT LANDMARKS.' },
  s10: { title: 'SOLD TWICE \u00b7 ADMITTED ONCE', chip: 'STILL STANDING', gold: 1, caption: 'LUSTIG NEVER PAID A FRANC.' },
};
function drawCaption(f) {
  capCtx.setTransform(SC, 0, 0, SC, 0, 0);
  capCtx.clearRect(0, 0, W, H);
  const O = OV[shotAt(f).id]; if (!O) return;
  /* title + gold rule + subtitle */
  if (O.title) {
    let tfs = 44;
    capCtx.font = FONT.replace('%d', tfs);
    const tw0 = capCtx.measureText(O.title).width;
    if (tw0 > 664) tfs = Math.max(30, Math.floor(44 * 664 / tw0));
    outlined(O.title, W / 2, 214, FONT.replace('%d', tfs), '#ffffff', Math.max(8, Math.round(tfs * 0.2)));
    capCtx.save(); capCtx.strokeStyle = '#f5c542'; capCtx.lineWidth = 5; capCtx.lineCap = 'round';
    capCtx.beginPath(); capCtx.moveTo(W / 2 - 150, 256); capCtx.lineTo(W / 2 + 150, 256); capCtx.stroke(); capCtx.restore();
    if (O.sub) outlined(O.sub, W / 2, 292, FONT.replace('%d', 22), '#f5c542', 6, 'center', 2.5, 640);
  }
  /* counter top-left */
  if (O.counter) {
    outlined(O.counter[0], 46, 96, FONT.replace('%d', 74), '#f5c542', 11, 'left');
    outlined(O.counter[1], 50, 152, FONT.replace('%d', 22), '#ffffff', 6, 'left', 3.5);
  }
  /* chip center-upper */
  if (O.chip) {
    const y = 432;
    capCtx.save(); capCtx.font = FONT.replace('%d', 34); capCtx.textAlign = 'center'; capCtx.textBaseline = 'middle';
    const w = capCtx.measureText(O.chip).width + 56;
    capCtx.beginPath(); capCtx.roundRect(W / 2 - w / 2, y - 30, w, 60, 14);
    capCtx.fillStyle = 'rgba(12,10,17,.78)'; capCtx.fill();
    capCtx.lineWidth = 3; capCtx.strokeStyle = O.gold ? '#f5c542' : 'rgba(255,255,255,.55)'; capCtx.stroke();
    capCtx.restore();
    outlined(O.chip, W / 2, y + 2, FONT.replace('%d', 34), O.gold ? '#f5c542' : '#ffffff', 6);
  }
  /* honesty label bottom-left */
  if (O.honesty) outlined(O.honesty, 34, 1244, FONT.replace('%d', 18), '#ffffff', 5, 'left', 1.5);
  /* object labels with leader lines */
  for (const L of (O.labels || [])) {
    const P = proj(L.at); if (!P.vis) continue;
    let tx = P.x + L.dx, ty = Math.min(P.y + L.dy, 830);
    capCtx.font = FONT.replace('%d', 26);
    const tw = capCtx.measureText(L.t).width + 10;
    if (L.dx < 0) tx = Math.max(tx, tw + 16); else tx = Math.min(tx, W - tw - 16);
    capCtx.save();
    capCtx.strokeStyle = 'rgba(255,255,255,.92)'; capCtx.lineWidth = 2;
    capCtx.beginPath(); capCtx.arc(P.x, P.y, 4.5, 0, 7); capCtx.fillStyle = L.gold ? '#f5c542' : '#fff'; capCtx.fill();
    capCtx.beginPath(); capCtx.moveTo(P.x, P.y); capCtx.lineTo(tx, ty + (L.dy < 0 ? 16 : -16)); capCtx.stroke();
    capCtx.restore();
    outlined(L.t, tx, ty, FONT.replace('%d', 26), '#ffffff', 7, L.dx < 0 ? 'right' : 'left', 2.5);
  }
  /* gold flow arrow: money path */
  if (O.arrow) {
    const A = proj(O.arrow.from), B = proj(O.arrow.to);
    if (A.vis && B.vis) {
      const cx = (A.x + B.x) / 2, cy = (A.y + B.y) / 2 - 46;      // slight bow upward
      capCtx.save();
      capCtx.strokeStyle = '#f5c542'; capCtx.lineWidth = 3.5; capCtx.setLineDash([11, 9]);
      capCtx.lineDashOffset = -30; capCtx.globalAlpha = 0.92;
      capCtx.beginPath(); capCtx.moveTo(A.x, A.y);
      for (let i = 1; i <= 30; i++) { const t = i / 30;
        const x = (1 - t) ** 2 * A.x + 2 * (1 - t) * t * cx + t * t * B.x;
        const y = (1 - t) ** 2 * A.y + 2 * (1 - t) * t * cy + t * t * B.y;
        capCtx.lineTo(x, y); }
      capCtx.stroke(); capCtx.setLineDash([]);
      const x0 = (1 - .965) ** 2 * A.x + 2 * (1 - .965) * .965 * cx + .965 ** 2 * B.x;
      const y0 = (1 - .965) ** 2 * A.y + 2 * (1 - .965) * .965 * cy + .965 ** 2 * B.y;
      const ang = Math.atan2(B.y - y0, B.x - x0);
      capCtx.fillStyle = '#f5c542'; capCtx.beginPath();
      capCtx.moveTo(B.x, B.y);
      capCtx.lineTo(B.x - 15 * Math.cos(ang - 0.5), B.y - 15 * Math.sin(ang - 0.5));
      capCtx.lineTo(B.x - 15 * Math.cos(ang + 0.5), B.y - 15 * Math.sin(ang + 0.5));
      capCtx.closePath(); capCtx.fill();
      const t = 0.5, px = (1 - t) ** 2 * A.x + 2 * (1 - t) * t * cx + t * t * B.x;
      const py = (1 - t) ** 2 * A.y + 2 * (1 - t) * t * cy + t * t * B.y;
      capCtx.fillStyle = '#fff'; capCtx.beginPath(); capCtx.arc(px, py, 8, 0, 7); capCtx.fill();
      capCtx.fillStyle = '#f5c542'; capCtx.beginPath(); capCtx.arc(px, py, 5.5, 0, 7); capCtx.fill();
      capCtx.restore();
    }
  }
  /* word caption bottom — auto-fit so nothing ever clips */
  if (O.caption) {
    let fs = 54;
    capCtx.font = FONT.replace('%d', fs);
    const cw = capCtx.measureText(O.caption).width;
    if (cw > 664) fs = Math.max(34, Math.floor(54 * 664 / cw));
    outlined(O.caption, W / 2, 912, FONT.replace('%d', fs), '#ffffff', Math.max(8, Math.round(fs * 0.2)));
  }
}

const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(PW, PH, false);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.NoToneMapping;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, W / H, 0.08, 1500);
const rx = (a) => a * Math.PI / 180;

// ---------- materials ----------
const grad = (() => { const d = new Uint8Array([90, 90, 90, 255, 255, 255, 255, 255]); const t = new THREE.DataTexture(d, 2, 1); t.minFilter = t.magFilter = THREE.NearestFilter; t.needsUpdate = true; return t; })();
const toon = (opts) => new THREE.MeshToonMaterial({ gradientMap: grad, ...opts });
const texM = (c, rx_ = 1, ry_ = 1, color = '#ffffff') => toon({ map: P.tex(c, rx_, ry_), color });
const M = {
  plank: texM(P.planks(1), 1, 6), beam: texM(P.beam(2), 1, 2), beamDark: texM(P.beam(3, [28, 36, 30]), 1, 2),
  rot: texM(P.rotten(4), 1, 1), rotB: texM(P.rotten(14), 1, 1),
  stone: texM(P.stone(4), 1, 1), stoneMoss: texM(P.mossy(P.stone(4), 5, 1.2), 1, 1),
  grass: texM(P.grass(6), 40, 40), dirt: texM(P.dirt(7), 6, 30), plaster: texM(P.plaster(8), 1, 1), plaster2: texM(P.plaster(18, 28), 1, 1),
  roof: texM(P.roof(9), 2, 2), marble: texM(P.marble(10), 1, 1), marbleTop: toon({ color: '#ece2cf' }),
  trunk: toon({ color: '#6a4a32' }), cypress: toon({ color: '#3f6b36' }), pine: toon({ color: '#5c8a3c' }), bush: toon({ color: '#6c9a42' }),
  hill: toon({ color: '#7aa64c' }), hillFar: toon({ color: '#86ad60' }), mount: toon({ color: '#8fa7b8' }), snow: toon({ color: '#f4f6fa' }),
  iron: toon({ color: '#5c5a57' }), bronze: toon({ color: '#b08a4a' }), wood: toon({ color: '#7a5434' }), door: toon({ color: '#5a3a24' }),
  window: toon({ color: '#2b2430' }), red: toon({ color: '#b8282b' }),
};
M.banner = new THREE.MeshToonMaterial({ gradientMap: grad, map: P.tex(P.banner()), alphaTest: 0.5, side: THREE.DoubleSide });
// helmet
const helmetIn = P.tex(P.helmetInside()); helmetIn.wrapS = helmetIn.wrapT = THREE.ClampToEdgeWrapping;
M.helmIn = new THREE.MeshToonMaterial({ gradientMap: grad, map: helmetIn, side: THREE.BackSide });
M.helmOut = toon({ color: '#8f8a7e' });

// ---------- ink / normal-depth contract ----------
const NOINK = 'noink'; // userData flag: never outlined (cards, fx, water handled specially)
const ndMat = new THREE.ShaderMaterial({
  vertexShader: `varying vec3 vN; varying float vD; void main(){ vN = normalize(normalMatrix*normal); vec4 mv = modelViewMatrix*vec4(position,1.); vD = -mv.z; gl_Position = projectionMatrix*mv; }`,
  fragmentShader: `varying vec3 vN; varying float vD; void main(){ vec3 n = normalize(vN); if(!gl_FrontFacing) n = -n; gl_FragColor = vec4(n*.5+.5, vD); }`,
  side: THREE.DoubleSide,
});
const cardNd = (map) => new THREE.ShaderMaterial({
  uniforms: { map: { value: map } },
  vertexShader: `varying vec2 vUv; varying float vD; void main(){ vUv=uv; vec4 mv = modelViewMatrix*vec4(position,1.); vD=-mv.z; gl_Position=projectionMatrix*mv; }`,
  fragmentShader: `uniform sampler2D map; varying vec2 vUv; varying float vD; void main(){ if(texture2D(map,vUv).a<.5) discard; gl_FragColor=vec4(0.,0.,0.,vD); }`,
  side: THREE.DoubleSide,
});
const waterNd = new THREE.ShaderMaterial({
  vertexShader: `varying float vD; void main(){ vec4 mv = modelViewMatrix*vec4(position,1.); vD=-mv.z; gl_Position=projectionMatrix*mv; }`,
  fragmentShader: `varying float vD; void main(){ gl_FragColor=vec4(.5,1.,.5,vD); }`,
});

// ---------- helpers ----------
const add = (geo, mat, x = 0, y = 0, z = 0, parent = scene, opts = {}) => {
  const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = opts.cast ?? true; m.receiveShadow = true; parent.add(m); return m;
};
const box = (w, h, d) => new THREE.BoxGeometry(w, h, d);
const uvScale = (geo, su, sv) => { const uv = geo.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * su, uv.getY(i) * sv); return geo; };
/** box with world-scaled UVs per face (texel density 1 tile per `t` metres) */
const tbox = (w, h, d, t = 2) => {
  const g = box(w, h, d), uv = g.attributes.uv;
  const dims = [[d, h], [d, h], [w, d], [w, d], [w, h], [w, h]];
  for (let f = 0; f < 6; f++) for (let k = 0; k < 4; k++) { const i = f * 4 + k; uv.setXY(i, uv.getX(i) * dims[f][0] / t, uv.getY(i) * dims[f][1] / t); }
  return g;
};

// ---------- sky ----------
const skyU = { top: { value: new THREE.Color() }, hor: { value: new THREE.Color() }, sunDir: { value: new THREE.Vector3() }, sunCol: { value: new THREE.Color() }, sunSize: { value: 0 } };
const sky = new THREE.Mesh(new THREE.SphereGeometry(1200, 32, 16), new THREE.ShaderMaterial({
  uniforms: skyU, side: THREE.BackSide, depthWrite: false, fog: false,
  vertexShader: `varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
  fragmentShader: `uniform vec3 top, hor, sunDir, sunCol; uniform float sunSize; varying vec3 vP;
    void main(){ float h = clamp(vP.y,0.,1.); vec3 c = mix(hor, top, pow(h, .55)); if(vP.y<0.) c = hor;
      float s = dot(normalize(vP), normalize(sunDir)); c += sunCol * (smoothstep(1.-sunSize, 1.-sunSize*.6, s) + .35*pow(max(s,0.), 24.)*step(.001,sunSize));
      gl_FragColor = vec4(c,1.); }`,
}));
sky.userData.sky = true; scene.add(sky);

// ---------- lights ----------
const hemi = new THREE.HemisphereLight('#ffffff', '#ffffff', 1); scene.add(hemi);
const sun = new THREE.DirectionalLight('#ffffff', 2); sun.castShadow = true;
sun.shadow.mapSize.set(SM, SM); sun.shadow.bias = -0.0006; sun.shadow.normalBias = 0.03; sun.shadow.radius = 2;
scene.add(sun); scene.add(sun.target);
scene.fog = new THREE.Fog('#ffffff', 40, 600);

// ---------- storyboard world: 1925 hotel suite, 1935 street, present-day booth + Eiffel Tower ----------
const DECK = 0.08, world = new THREE.Group(); scene.add(world);
const clouds = [];
const waterU = { t: { value: 0 }, deep: { value: new THREE.Color('#315a70') }, shal: { value: new THREE.Color('#739ba4') }, glint: { value: new THREE.Color('#e6dfcc') } };
const mats = {
  floor: texM(P.planks(61), 6, 6), wall: texM(P.plaster(31, 38), 3, 2), wallWarm: texM(P.plaster(18, 42), 3, 2),
  bench: texM(P.planks(62), 4, 1), wood: toon({ color: '#7a5434' }), woodDark: toon({ color: '#5a3a24' }),
  cream: toon({ color: '#e8dcc0' }), paper: toon({ color: '#f3ead6' }), paperHi: toon({ color: '#fbf6e9' }),
  wax: toon({ color: '#b8342b' }), news: toon({ color: '#e6ddc6' }), ink: toon({ color: '#3a3a40' }),
  bill: toon({ color: '#89936c' }), billLine: toon({ color: '#d4c69c' }), gold: toon({ color: '#b28a4f' }),
  iron: toon({ color: '#4a5058' }), ironDark: toon({ color: '#3a3f46' }),
  rug: toon({ color: '#7a4a44' }), door: toon({ color: '#6b4a30' }), lamp: toon({ color: '#f4e3b0', emissive: '#f4d78a', emissiveIntensity: .6 }),
  glass: toon({ color: '#c4e2ea', transparent: true, opacity: 0.22 }),
  stone: texM(P.stone(44), 3, 3), facade: texM(P.plaster(33, 40), 4, 2), cobble: texM(P.stone(47, 34, 18, 62), 4, 4),
  grass: texM(P.grass(6), 40, 40), path: texM(P.stone(46, 40, 12, 74), 3, 6),
  trunk: toon({ color: '#6a4a32' }), leafA: toon({ color: '#4d6f50' }), leafB: toon({ color: '#647d59' }),
  brick: texM(P.stone(45, 12, 30, 52), 3, 2), roof: texM(P.roof(9), 3, 2), kiosk: toon({ color: '#c9b48a' }),
  rope: toon({ color: '#a8352f' }), brass: toon({ color: '#c9a24a' }), city: toon({ color: '#8d97a6' }),
};
const sets = {}; const ref = {};
const stage = (name) => { const g = new THREE.Group(); g.name = name; g.visible = false; world.add(g); sets[name] = g; return g; };
const bx = (p, w, h, d, m, x, y, z, t = 1) => add(tbox(w, h, d, t), m, x, y, z, p);
const pl = (p, w, d, m, x, y, z) => { const o = add(new THREE.PlaneGeometry(w, d), m, x, y, z, p, { cast: false }); o.rotation.x = -Math.PI / 2; return o; };
const cyl = (p, r1, r2, h, m, x, y, z, seg = 12) => add(new THREE.CylinderGeometry(r1, r2, h, seg), m, x, y, z, p);
const post = (p, a, b, r, m) => { const A = new THREE.Vector3(...a), B = new THREE.Vector3(...b), v = B.clone().sub(A), o = add(new THREE.CylinderGeometry(r, r, v.length(), 8), m, ...A.clone().add(B).multiplyScalar(.5).toArray(), p); o.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), v.normalize()); return o; };
function tree3(p, x, z, h = 4, seed = 0) { cyl(p, .16, .23, h * .42, M.trunk, x, h * .21, z, 8); for (let i = 0; i < 3; i++) { const m = add(new THREE.ConeGeometry(h * (.31 - i * .045), h * .42, 7), i === 0 ? mats.leafA : mats.leafB, x, h * (.5 + i * .19), z, p); m.rotation.z = ((seed + i) % 3 - 1) * .06; } }
function money3(p, x, y, z, s = 1) { const g = new THREE.Group(); g.position.set(x, y, z); g.scale.setScalar(s); p.add(g); for (let k = 0; k < 7; k++) { const yy = .012 + k * .012; bx(g, .34, .009, .17, mats.bill, (k % 2) * .008, yy, 0, .6); for (let q = -1; q <= 1; q++) bx(g, .22, .002, .003, mats.billLine, (k % 2) * .008, yy + .006, q * .035, 1); bx(g, .035, .014, .18, mats.gold, (k % 2) * .008, yy, .005, 1); } return g; }
/* Eiffel Tower: splayed legs + two platforms + tapering spire — the silhouette reads at any distance */
function eiffel(p, x, z, h) {
  const g = new THREE.Group(); g.position.set(x, 0, z); p.add(g);
  const iron = mats.iron, u = h / 19;                      // u = scale unit (u=1 at h=19)
  const legs = (y0, y1, s0, s1, rad) => { for (const [sx, sz] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) post(g, [sx * s0, y0, sz * s0], [sx * s1, y1, sz * s1], rad, iron); };
  legs(0, h * .34, 3.5 * u, 1.9 * u, .22 * u);            // level 1 — the splay (Eiffel ratio)
  bx(g, 6.4 * u, .34 * u, 6.4 * u, mats.ironDark, 0, h * .35, 0, 1);
  legs(h * .37, h * .66, 1.9 * u, .85 * u, .15 * u);      // level 2
  bx(g, 3.2 * u, .3 * u, 3.2 * u, mats.ironDark, 0, h * .67, 0, 1);
  legs(h * .69, h * .93, .85 * u, .28 * u, .1 * u);       // level 3
  for (const yy of [0.14, 0.24, 0.5, 0.6, 0.8, 0.88]) {    // lattice decks
    const w = yy < .35 ? 6.9 * u : yy < .66 ? 3.4 * u : 1.5 * u;
    bx(g, w, .07 * u, w, mats.ironDark, 0, h * yy, 0, 1);
  }
  // arch hint between the front legs
  for (let i = 0; i < 5; i++) { const t = i / 4, s = Math.sin(t * Math.PI);
    const b = bx(g, 1.1 * u, .16 * u, .14 * u, iron, (3.5 - t * 1.5) * u * .5, h * (.07 + .18 * s), 3.4 * u * (1 - t * .4), 1);
    b.rotation.z = (i < 2 ? 1 : -1) * .5; }
  add(new THREE.ConeGeometry(.5 * u, h * .1, 8), iron, 0, h * .97, 0, g);
  post(g, [0, h * 1.0, 0], [0, h * 1.07, 0], .03 * u, mats.ironDark);
  return g;
}

// ============================ SUITE (1925 hotel room) ============================
{
  const g = stage('suite');
  pl(g, 16, 15, mats.floor, 0, 0, -1);
  pl(g, 10, 8, mats.rug, 0.4, 0.015, -1);                       // rug under table
  // back wall with a REAL window hole (x -4.8..0.4, y 1.4..3.7) so the tower shows through
  bx(g, 2.7, 4.6, .3, mats.wall, -6.15, 2.3, -6, 3).castShadow = false;      // left of hole
  bx(g, 7.1, 4.6, .3, mats.wall, 3.95, 2.3, -6, 3).castShadow = false;       // right of hole
  bx(g, 15, .9, .3, mats.wall, 0, 4.15, -6, 3).castShadow = false;           // above hole
  bx(g, 15, 1.4, .3, mats.wall, 0, .7, -6, 3).castShadow = false;            // below hole
  bx(g, .3, 4.6, 13, mats.wallWarm, -7.2, 2.3, -1, 3).castShadow = false;
  bx(g, .3, 4.6, 13, mats.wallWarm, 7.2, 2.3, -1, 3).castShadow = false;
  bx(g, 15, .25, 13, mats.cream, 0, 4.6, -1, 3).castShadow = false;
  // window frame + mullions + sill
  bx(g, 5.6, .2, .42, mats.wood, -2.2, 3.8, -5.85, 1);
  bx(g, 5.6, .2, .42, mats.wood, -2.2, 1.3, -5.85, 1);
  bx(g, .2, 2.7, .42, mats.wood, -4.9, 2.55, -5.85, 1);
  bx(g, .2, 2.7, .42, mats.wood, .5, 2.55, -5.85, 1);
  bx(g, .1, 2.3, .3, mats.wood, -2.2, 2.55, -5.9, 1);
  bx(g, 5.2, .1, .3, mats.wood, -2.2, 2.55, -5.9, 1);
  bx(g, 5.8, .14, .6, mats.wood, -2.2, 1.32, -5.7, 1);        // sill
  // door (back-right) + frame
  bx(g, 1.3, .16, .3, mats.woodDark, 4.6, 2.32, -5.8, 1);
  bx(g, .16, 2.4, .3, mats.woodDark, 3.95, 1.15, -5.8, 1);
  bx(g, .16, 2.4, .3, mats.woodDark, 5.25, 1.15, -5.8, 1);
  bx(g, 1.1, 2.2, .12, mats.door, 4.6, 1.1, -5.82, 1);
  add(new THREE.SphereGeometry(.05, 8, 6), mats.brass, 4.18, 1.1, -5.72, g);
  // chandelier
  post(g, [0, 4.6, -1], [0, 3.5, -1], .02, mats.ironDark);
  add(new THREE.SphereGeometry(.16, 10, 8), mats.lamp, 0, 3.35, -1, g);
  // wall frames (blank canvases — no text)
  for (const fy of [2.4]) { bx(g, .08, 1.1, .9, mats.woodDark, 7.0, fy, -2.6, 1); bx(g, .06, .9, .7, mats.cream, 6.95, fy, -2.6, 1); }
  bx(g, .08, .9, .7, mats.woodDark, -7.0, 2.6, 1.6, 1); bx(g, .06, .7, .5, mats.cream, -6.95, 2.6, 1.6, 1);
  // table + legs
  bx(g, 3.2, .12, 1.5, mats.bench, 0, .95, -1, 1);
  for (const [lx, lz] of [[-1.4, -1.6], [1.4, -1.6], [-1.4, -.4], [1.4, -.4]]) bx(g, .12, .9, .12, mats.woodDark, lx, .45, lz, 1);
  // papers with wax seal (FORGED PAPERS)
  const pw = new THREE.Group(); g.add(pw); pw.position.set(-0.5, 1.03, -0.85); pw.rotation.y = .18;
  bx(pw, .5, .012, .68, mats.paperHi, 0, 0, 0, 1);
  const pw2 = new THREE.Group(); g.add(pw2); pw2.position.set(-0.42, 1.045, -0.78); pw2.rotation.y = -.12;
  bx(pw2, .5, .012, .68, mats.paper, 0, 0, 0, 1);
  cyl(pw2, .05, .05, .014, mats.wax, .1, .012, .16, 10);
  // money stack (bribe)
  ref.money = money3(g, 0.45, 1.04, -0.9, 1);
  // newspaper prop (no readable text — masthead block only)
  bx(g, .74, .016, .52, mats.news, -0.5, 1.03, -1.25, 1);
  bx(g, .6, .006, .1, mats.ink, -0.5, 1.043, -1.44, 1);
  bx(g, .28, .006, .3, mats.ink, -0.6, 1.043, -1.2, 1);
  // empty chair (S6 joke) at Lustig's head position
  const ch = new THREE.Group(); g.add(ch); ch.position.set(2.5, 0, -1.0); ch.rotation.y = -Math.PI / 2 + .3;
  bx(ch, .5, .09, .5, mats.wood, 0, .5, 0, 1);
  bx(ch, .5, .6, .09, mats.wood, 0, .85, -.24, 1);
  for (const [lx, lz] of [[-.2, -.2], [.2, -.2], [-.2, .2], [.2, .2]]) bx(ch, .07, .5, .07, mats.woodDark, lx, .25, lz, 1);
  // Eiffel tower outside the window (world at z=-46, seen through the hole)
  eiffel(world, -15, -38, 19);   // positioned on S1's window sightline
  // distant city blocks behind tower (depth)
  for (const [cx, ch2, cz] of [[-14, 6, -52], [-8, 8, -56], [4, 5, -54], [10, 7, -50], [16, 4, -55]]) bx(world, 6, ch2, 5, mats.city, cx, ch2 / 2, cz, 2).castShadow = false;
}

// ============================ STREET (1935 arrest) ============================
{
  const g = stage('street');
  pl(g, 30, 24, mats.cobble, 0, 0, 2);
  // facade with windows + door
  bx(g, 22, 6.5, .6, mats.facade, 0, 3.25, -4.5, 3).castShadow = false;
  bx(g, 22.6, .5, 1.2, mats.stone, 0, 6.7, -4.5, 1);
  for (let r = 0; r < 2; r++) for (let c = 0; c < 7; c++) {
    const wx = -8.4 + c * 2.8, wy = 2.1 + r * 2.2;
    bx(g, 1.1, 1.5, .16, toon({ color: '#2b3a4a' }), wx, wy, -4.15, 1);
    bx(g, 1.3, 1.7, .12, mats.stone, wx, wy, -4.2, 1);
  }
  bx(g, 1.5, 2.7, .2, mats.door, -8.4, 1.35, -4.1, 1);
  // awning + lamp post + crate
  bx(g, 4.2, .1, 1.6, toon({ color: '#a8352f' }), 4.6, 3.4, -3.4, 1).rotation.x = .28;
  post(g, [7.6, 0, 1.4], [7.6, 3.2, 1.4], .07, mats.ironDark);
  add(new THREE.SphereGeometry(.14, 10, 8), mats.lamp, 7.6, 3.35, 1.4, g);
  bx(g, .9, .7, .7, mats.wood, -3.6, .35, -2.6, 1);
  // money in Lustig's arms
  ref.money2 = money3(g, 0.15, 1.1, 0.3, .9);
}

// ============================ BOOTH (present day + full tower) ============================
{
  const g = stage('booth');
  pl(g, 90, 90, mats.grass, 0, 0, 0);
  pl(g, 3.4, 26, mats.path, -1.2, .02, 8);
  // ticket booth
  bx(g, 1.6, 2.3, 1.5, mats.kiosk, -2.6, 1.15, 3.6, 1);
  bx(g, 1.9, .3, 1.8, toon({ color: '#a8352f' }), -2.6, 2.45, 3.6, 1);
  bx(g, 1.0, .8, .1, toon({ color: '#2b3a4a' }), -2.6, 1.5, 4.38, 1);
  bx(g, 1.3, .16, .5, mats.wood, -2.6, .95, 4.5, 1);
  // queue stanchions + rope (VENDU vibes without text)
  for (const [sx, sz] of [[-.6, 4.9], [.7, 5.6], [2.0, 6.2]]) { cyl(g, .05, .06, .9, mats.brass, sx, .45, sz, 10); add(new THREE.SphereGeometry(.07, 10, 8), mats.brass, sx, .93, sz, g); }
  post(g, [-.6, .86, 4.9], [.7, .86, 5.6], .025, mats.rope);
  post(g, [.7, .86, 5.6], [2.0, .86, 6.2], .025, mats.rope);
  // full tower + city + trees
  eiffel(g, -2.5, -16, 17);
  for (const [cx, ch2, cz] of [[-12, 5, -30], [-4, 7, -34], [7, 6, -32], [14, 4, -28]]) bx(g, 5, ch2, 5, mats.city, cx, ch2 / 2, cz, 2).castShadow = false;
  for (const [tx, tz, h, sd] of [[-9, 2, 4.4, 1], [6.5, -4, 4.8, 2], [-7, -8, 4.0, 3], [8.5, 4, 4.2, 4]]) tree3(g, tx, tz, h, sd);
}
const helmet = new THREE.Group(); scene.add(helmet); // retained engine slot; no helmet is used in this story
// ---------- cards ----------
const CW = 1200, CH = 2000, CM = 2.25; // canvas px, card height in metres (design 600x1000 -> 2.25 m)
const cardGeo = new THREE.PlaneGeometry(CM * 0.6, CM); cardGeo.translate(0, CM / 2 - CM * 0.025, 0);
const blobTex = P.tex(P.radial('20,14,30', 0.6));
class Card {
  constructor(scale = 1) {
    [this.c, this.g] = (() => { const c = document.createElement('canvas'); c.width = CW; c.height = CH; return [c, c.getContext('2d')]; })();
    this.t = new THREE.CanvasTexture(this.c); this.t.colorSpace = THREE.SRGBColorSpace; this.t.anisotropy = 4;
    this.mat = new THREE.MeshBasicMaterial({ map: this.t, transparent: true, alphaTest: 0.02, side: THREE.DoubleSide, fog: true });
    this.mesh = new THREE.Mesh(cardGeo, this.mat); this.mesh.userData.nd = cardNd(this.t); this.mesh.castShadow = true;
    this.mesh.customDepthMaterial = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, map: this.t, alphaTest: 0.5 });
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

// ---------- render targets & post ----------
const rtColor = new THREE.WebGLRenderTarget(PW, PH, { samples: MS, type: THREE.HalfFloatType });
const rtNd = new THREE.WebGLRenderTarget(PW, PH, { type: THREE.HalfFloatType, minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter });
const rtInk = new THREE.WebGLRenderTarget(PW, PH, { type: THREE.HalfFloatType });
const fsCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1), fsGeo = new THREE.PlaneGeometry(2, 2);
const fs = (mat) => { const s = new THREE.Scene(); s.add(new THREE.Mesh(fsGeo, mat)); return s; };
const inkU = { col: { value: rtColor.texture }, nd: { value: rtNd.texture }, res: { value: new THREE.Vector2(PW, PH) }, px: { value: 1.6 }, fogCol: { value: new THREE.Color() },
  sat: { value: 1.08 }, lift: { value: new THREE.Color(0, 0, 0) }, gain: { value: new THREE.Color(1, 1, 1) }, vig: { value: 0.22 }, flash: { value: 0 } };
const inkScene = fs(new THREE.ShaderMaterial({ uniforms: inkU, vertexShader: `varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position.xy,0.,1.); }`,
  fragmentShader: `uniform sampler2D col, nd; uniform vec2 res; uniform float px, sat, vig, flash; uniform vec3 fogCol, lift, gain; varying vec2 vUv;
  float edgeAt(vec2 uv, float r){
    vec4 c = texture2D(nd, uv); if (dot(c.rgb,c.rgb) < .01) return 0.; float d = c.a; vec3 n = c.rgb*2.-1.;
    float e = 0.; float rr = r * clamp(7./d, .62, 1.25);
    for (int i=0;i<16;i++){ float a = float(i)*.785398 + (i>7 ? .39 : 0.); float k = i>7 ? .5 : 1.;
      vec2 o = vec2(cos(a), sin(a))*rr*k/res; vec4 s = texture2D(nd, uv+o);
      float ds = s.a; bool card = dot(s.rgb,s.rgb) < .01;
      if (card && ds > 0.) continue;            // character cards: never outlined by the world ink
      if (card) ds = 1e4;                        // sky
      vec3 ns = s.rgb*2.-1.;
      e = max(e, smoothstep(.006, .02, (ds - d)/d));                           // depth jump, near side only
      if (!card && abs(ds-d)/d < .06) e = max(e, smoothstep(.88, .72, dot(n, ns)) * .9); // crease
    }
    return e * (1. - smoothstep(140., 520., d)*.8);
  }
  void main(){
    vec3 c = texture2D(col, vUv).rgb;
    float e = edgeAt(vUv, px);
    c = mix(c, vec3(.012,.01,.014), e);
    if (flash < -0.5) c = vec3(e);
    float l = dot(c, vec3(.299,.587,.114)); c = mix(vec3(l), c, sat);
    c = c*gain + lift;
    vec2 q = vUv-.5; c *= 1. - vig*dot(q*vec2(1.,.75), q*vec2(1.,.75))*2.2;
    c = mix(c, vec3(1.), flash);
    gl_FragColor = vec4(c,1.); }` }));
const dofU = { src: { value: rtInk.texture }, nd: { value: rtNd.texture }, res: { value: new THREE.Vector2(PW, PH) }, focus: { value: 5 }, cinf: { value: 0 }, near: { value: 1 } };
const dofScene = fs(new THREE.ShaderMaterial({ uniforms: dofU, vertexShader: `varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position.xy,0.,1.); }`,
  fragmentShader: `uniform sampler2D src, nd; uniform vec2 res; uniform float focus, cinf, near; varying vec2 vUv;
  float coc(vec2 uv){ float d = texture2D(nd, uv).a; if (d <= 0.) d = 2000.; float k = 1. - focus/d; return k > 0. ? cinf*k : min(-k*cinf*near, cinf*1.4); }
  void main(){
    float c0 = coc(vUv);
    if (cinf < .5 || c0 < .6) { gl_FragColor = linearToOutputTexel(vec4(texture2D(src, vUv).rgb, 1.)); return; }
    vec3 acc = vec3(0.); float wsum = 0.;
    for (int i=0;i<48;i++){ float fi = float(i); float r = sqrt((fi+.5)/48.); float a = fi*2.39996;
      vec2 o = vec2(cos(a), sin(a))*r*c0/res; float cs = coc(vUv+o);
      float w = smoothstep(r*c0-1.5, r*c0+.5, cs + .5);
      acc += texture2D(src, vUv+o).rgb*w; wsum += w; }
    gl_FragColor = linearToOutputTexel(vec4(acc/max(wsum,1e-3), 1.)); }` }));
// final copy with sRGB handled by the renderer output (we render to screen with linear->sRGB in the shader chunk)
dofScene.children[0].material.toneMapped = false;

// ---------- per-frame state ----------
const tmpV = new THREE.Vector3();
function applyLight(L, f) {
  hemi.color.set(L.sky); hemi.groundColor.set(L.ground); hemi.intensity = L.hemi;
  sun.color.set(L.sun); sun.intensity = L.sunI;
  scene.fog.color.set(L.fog); scene.fog.near = L.fogNear; scene.fog.far = L.fogFar;
  skyU.top.value.set(L.skyTop); skyU.hor.value.set(L.skyHor); skyU.sunCol.value.set(L.sunDisc || '#000'); skyU.sunSize.value = L.sunSize || 0;
  inkU.sat.value = L.sat; inkU.gain.value.set(L.gain || '#ffffff'); inkU.lift.value.set(L.lift || '#000000');
  waterU.deep.value.set(L.waterDeep); waterU.shal.value.set(L.waterShal); waterU.glint.value.set(L.glint);
}
function placeSun(L, focus) {
  // sun direction from azimuth/elevation in world space
  const az = rx(L.az), el = rx(L.el); tmpV.set(Math.cos(el) * Math.cos(az), Math.sin(el), Math.cos(el) * Math.sin(az));
  skyU.sunDir.value.copy(tmpV);
  sun.position.copy(focus).addScaledVector(tmpV, 80); sun.target.position.copy(focus);
  const ext = L.shadowExt || 30, sc = sun.shadow.camera; sc.left = -ext; sc.right = ext; sc.top = ext; sc.bottom = -ext; sc.near = 1; sc.far = 200; sc.updateProjectionMatrix();
}

function worldState(S, f) {
  for (const [name, g] of Object.entries(sets)) g.visible = name === S.location;
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
    c.mesh.castShadow = a.shadow !== false;
    c.mesh.renderOrder = a.order || 2;
    if (a.blob !== false && a.y < DECK + 0.5) { c.blob.visible = true; c.blob.position.set(a.x, (a.ground ?? DECK) + 0.02, a.z); c.blob.scale.set(0.95 * s, 0.6 * s, 1); }
  });
}

const helmetState = (h) => {
  helmet.visible = !!h; if (!h) return;
  helmet.position.set(h.x, h.y, h.z); helmet.rotation.set(h.rx || 0, h.ry || 0, h.rz || 0); helmet.scale.setScalar(h.s || 0.17);
};

const swapForNd = (on) => {
  scene.traverse((o) => {
    if (!o.isMesh) return;
    if (on) {
      o.userData.mat0 = o.material;
      if (o.userData.ndSkip) { o.userData.vis0 = o.visible; o.visible = false; return; }
      if (o === sky || o.userData.sky) { o.userData.vis0 = o.visible; o.visible = false; return; }
      o.material = o.userData.nd || ndMat;
    } else {
      o.material = o.userData.mat0; if (o.userData.vis0 !== undefined) { o.visible = o.userData.vis0; delete o.userData.vis0; }
    }
  });
};

window.renderFrame = (f) => {
  const S = shotAt(f), L = lightFor(S, f), C = camAt(f);
  applyLight(L, f);
  camera.position.set(...C.pos); camera.up.set(0, 1, 0); camera.lookAt(...C.look); camera.rotateZ(rx(C.roll || 0));
  camera.fov = C.fov; camera.updateProjectionMatrix(); camera.updateMatrixWorld();
  const W_ = worldAt(f); worldState(W_, f);
  placeSun(L, new THREE.Vector3(...(C.shadowAt || C.look)));
  drawActors([...actorsAt(f, T), ...fxAt(f, T)], camera);
  helmetState(W_.helmet);
  sky.position.copy(camera.position);
  for (const c of clouds) c.quaternion.copy(camera.quaternion);
  // pass A: colour
  renderer.setRenderTarget(rtColor); renderer.setClearColor(0x000000, 1); renderer.clear(); renderer.render(scene, camera);
  // pass B: normal + depth
  const fog = scene.fog; scene.fog = null; const sm = renderer.shadowMap.enabled; renderer.shadowMap.enabled = false; renderer.shadowMap.autoUpdate = false;
  swapForNd(true); renderer.setRenderTarget(rtNd); renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(scene, camera); swapForNd(false);
  scene.fog = fog; renderer.shadowMap.enabled = sm; renderer.shadowMap.autoUpdate = true;
  if (window.DEBUG_ND) { const dm = new THREE.MeshBasicMaterial({ map: rtNd.texture }); const ds = fs(dm); renderer.setRenderTarget(null); renderer.render(ds, fsCam); return true; }
  // ink + grade
  const D = dofAt(f);
  inkU.px.value = 2.0; inkU.flash.value = window.DEBUG_E ? -1 : (C.flash || 0); inkU.vig.value = L.vig ?? 0.22;
  renderer.setRenderTarget(rtInk); renderer.render(inkScene, fsCam);
  // lens
  dofU.focus.value = D.focus; dofU.cinf.value = D.cinf * (H / 1920); dofU.near.value = D.near ?? 1;
  renderer.setRenderTarget(null); renderer.render(dofScene, fsCam);
  drawCaption(f);
  return true;
};
window.TOTAL = TOTAL;
window.ready = true;
