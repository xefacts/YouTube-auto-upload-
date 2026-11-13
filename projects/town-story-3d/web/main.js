// ============================================================================
// MAIN.JS — deterministic headless renderer for "The Town That Counts To Ten"
// Contract: index.html?w=540&h=960 — renderAt(t) is pure; __captureBatch batches
// JPEG frames; __ready flips true after the first successful render.
// ============================================================================
import * as THREE from 'three';
import { buildTown, box } from './town.js';
import { BlockChar } from './chars.js';
import { evaluateScene, DURATION, SHOTS } from './story.js';

const params = new URLSearchParams(location.search);
const RW = parseInt(params.get('w') || '540', 10);
const RH = parseInt(params.get('h') || '960', 10);

const canvas = document.getElementById('out');
canvas.width = RW; canvas.height = RH;
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setSize(RW, RH, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.12;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xc6e4f7, 30, 120);
const camera = new THREE.PerspectiveCamera(45, RW / RH, 0.1, 300);
scene.add(camera);

// ------------------------------------------------------------------ lights
const hemi = new THREE.HemisphereLight(0xdfeeff, 0x6a7a58, 0.85);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff4dd, 1.15);
sun.position.set(-18, 26, -12);
scene.add(sun);
// night lamp glow (3 real point lights near the action)
const lampLights = [];
for (const lx of [-8, 0, 8, 16, 24]) {
  const pl = new THREE.PointLight(0xffc76a, 0, 20, 1.1);
  pl.position.set(lx + 1.2, 4.4, -4.4);
  scene.add(pl);
  lampLights.push(pl);
}
// porch light over the kid's doorway (the peek shots)
const porchLight = new THREE.PointLight(0xffcf8a, 0, 10, 1.2);
porchLight.position.set(17.8, 2.4, 6.9);
scene.add(porchLight);

// ------------------------------------------------------------------ world
const world = buildTown(scene);

// finch's hat + dropped cane (aftermath props)
const hatGroup = new THREE.Group();
{
  const crown = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.16, 0.16, 12), new THREE.MeshLambertMaterial({ color: '#4a4f5c' }));
  crown.position.y = 0.08;
  const brim = new THREE.Mesh(new THREE.CylinderGeometry(0.26, 0.26, 0.03, 14), new THREE.MeshLambertMaterial({ color: '#3c4050' }));
  hatGroup.add(crown, brim);
  hatGroup.position.set(12.62, 0.02, 2.02);
  hatGroup.rotation.y = 0.8;
  hatGroup.visible = false;
  scene.add(hatGroup);
}
const groundCane = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 1.0, 8), new THREE.MeshLambertMaterial({ color: '#8a6a45' }));
groundCane.rotation.z = Math.PI / 2 - 0.06;
groundCane.position.set(12.95, 0.05, 2.14);
groundCane.visible = false;
scene.add(groundCane);

// ------------------------------------------------------------------ cast
const cast = {
  kid: new BlockChar(scene, { name: 'kid', skin: '#f2c96e', shirt: '#3f76e0', accent: '#f5d76e', pants: '#2b3345', shoes: '#ececf2', cap: '#e04a38', scale: 0.62, freckles: true, variant: 'classic' }),
  mom: new BlockChar(scene, { name: 'mom', skin: '#eec27f', shirt: '#52b074', accent: '#f0e6d2', pants: '#3a4a5c', shoes: '#7a5a48', hair: { style: 'bun', color: '#4a3220' }, scale: 0.74, variant: 'classic' }),
  finch: new BlockChar(scene, { name: 'finch', skin: '#e8c8a0', shirt: '#9a774f', accent: '#6a5238', pants: '#4a4a55', shoes: '#3a3a40', hair: { style: 'block', color: '#c9c9c9' }, scale: 0.71, cane: true, variant: 'classic' }),
  ex1: new BlockChar(scene, { name: 'ex1', skin: '#d8a878', shirt: '#e0813a', accent: '#3a2a1a', pants: '#3c4a5c', shoes: '#333', hair: { style: 'block', color: '#2a2018' }, scale: 0.75, variant: 'classic' }),
  ex2: new BlockChar(scene, { name: 'ex2', skin: '#f0d0a0', shirt: '#8a63d8', accent: '#e8d8f0', pants: '#40384a', shoes: '#e8e8e8', hair: { style: 'bun', color: '#6a4a2a' }, scale: 0.71, variant: 'classic' }),
  ex3: new BlockChar(scene, { name: 'ex3', skin: '#c89868', shirt: '#4fb3bc', accent: '#2a5a60', pants: '#38424e', shoes: '#555', cap: '#3a8a4a', scale: 0.70, variant: 'classic' }),
};

// ------------------------------------------------------------------ overlays
const cv2 = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return [c, c.getContext('2d')]; };
const mkCard = (draw) => {
  const [c, g] = cv2(1080, 1920);
  draw(g);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
};
const CARDS = {
  card1: mkCard((g) => {
    g.textAlign = 'center';
    g.font = '900 120px Arial, sans-serif';
    g.lineWidth = 22; g.strokeStyle = '#141824'; g.fillStyle = '#f4efe4';
    g.strokeText('IN THIS TOWN…', 540, 900); g.fillText('IN THIS TOWN…', 540, 900);
    g.fillStyle = '#d8341f';
    g.fillRect(390, 970, 300, 16);
    g.font = '900 64px Arial, sans-serif';
    g.lineWidth = 14;
    g.strokeText('EVERY NIGHT AT 9 PM', 540, 1120); g.fillText('EVERY NIGHT AT 9 PM', 540, 1120);
    g.strokeText('A VOICE COUNTS DOWN', 540, 1210); g.fillText('A VOICE COUNTS DOWN', 540, 1210);
  }),
  card2: mkCard((g) => {
    g.textAlign = 'center';
    g.font = '900 108px Arial, sans-serif';
    g.lineWidth = 22; g.strokeStyle = '#141824'; g.fillStyle = '#f4efe4';
    g.strokeText('THE TOWN', 540, 840); g.fillText('THE TOWN', 540, 840);
    g.strokeText('THAT COUNTS', 540, 960); g.fillText('THAT COUNTS', 540, 960);
    g.strokeText('TO TEN', 540, 1080); g.fillText('TO TEN', 540, 1080);
    g.fillStyle = '#d8341f';
    g.fillRect(390, 1150, 300, 16);
  }),
  end: mkCard((g) => {
    g.fillStyle = '#0a0c14'; g.fillRect(0, 0, 1080, 1920);
    g.textAlign = 'center';
    g.font = '900 96px Arial, sans-serif';
    g.lineWidth = 18; g.strokeStyle = '#000'; g.fillStyle = '#f4efe4';
    g.strokeText('TONIGHT —', 540, 860); g.fillText('TONIGHT —', 540, 860);
    g.strokeText('IT COUNTS AGAIN', 540, 970); g.fillText('IT COUNTS AGAIN', 540, 970);
    g.fillStyle = '#d8341f';
    g.fillRect(390, 1040, 300, 14);
    g.font = '900 46px Arial, sans-serif';
    g.fillStyle = '#8a94a8';
    g.fillText('THE TOWN THAT COUNTS TO TEN', 540, 1140);
  }),
};
const overlayMesh = new THREE.Mesh(
  new THREE.PlaneGeometry(2.2, 3.9),
  new THREE.MeshBasicMaterial({ transparent: true, opacity: 0, depthTest: false, toneMapped: false })
);
overlayMesh.position.set(0, 0, -2.0);
overlayMesh.renderOrder = 999;
camera.add(overlayMesh);

// ---- countdown number overlay (10..1) ----
const NUMS = {};
for (const d of ['10', '9', '8', '7', '6', '5', '4', '3', '2', '1']) {
  const [nc, ng] = (() => { const c = document.createElement('canvas'); c.width = 540; c.height = 420; return [c, c.getContext('2d')]; })();
  ng.textAlign = 'center'; ng.textBaseline = 'middle';
  ng.font = '900 300px Arial, sans-serif';
  ng.shadowColor = '#ff2828'; ng.shadowBlur = 55;
  ng.lineWidth = 26; ng.strokeStyle = '#20060a';
  ng.strokeText(d, 270, 215);
  ng.shadowBlur = 25;
  ng.fillStyle = '#ffffff';
  ng.fillText(d, 270, 215);
  const t2 = new THREE.CanvasTexture(nc);
  t2.colorSpace = THREE.SRGBColorSpace;
  NUMS[d] = t2;
}
const numMesh = new THREE.Mesh(
  new THREE.PlaneGeometry(1.285, 1.0),
  new THREE.MeshBasicMaterial({ transparent: true, opacity: 0, depthTest: false, toneMapped: false })
);
numMesh.renderOrder = 998;
camera.add(numMesh);

const flashMesh = new THREE.Mesh(
  new THREE.PlaneGeometry(2.6, 4.6),
  new THREE.MeshBasicMaterial({ color: '#ffffff', transparent: true, opacity: 0, depthTest: false, toneMapped: false })
);
flashMesh.position.set(0, 0, -1.8);
flashMesh.renderOrder = 1000;
camera.add(flashMesh);

// ------------------------------------------------------------------ director
const V3 = new THREE.Vector3();
function renderAt(t) {
  const st = evaluateScene(t);

  // camera
  camera.fov = st.cam.fov; camera.updateProjectionMatrix();
  let px = st.cam.p[0], py = st.cam.p[1], pz = st.cam.p[2];
  if (st.cam.shake > 0) {
    const sk = st.cam.shake * 0.4; // gentler, smoother shake
    px += Math.sin(t * 37.0) * sk;
    py += Math.cos(t * 31.0) * sk * 0.6;
    pz += Math.sin(t * 29.0 + 1.3) * sk * 0.5;
  }
  camera.position.set(px, py, pz);
  camera.lookAt(V3.set(st.cam.l[0], st.cam.l[1], st.cam.l[2]));

  // sky / fog / lights
  scene.background = new THREE.Color(st.sky.bg);
  scene.fog.color = new THREE.Color(st.sky.fog);
  sun.intensity = st.sky.sunI;
  sun.color = new THREE.Color(st.sky.sunCol);
  hemi.intensity = 0.5 + 0.42 * (1 - st.sky.night);
  world.stars.material.opacity = Math.max(0, st.sky.night - 0.45) * 1.6;
  for (const cl of world.clouds) cl.children.forEach((m) => { m.material.opacity = 0.92 * (1 - st.sky.night); });

  // lamps
  const night = st.sky.night > 0.5;
  const L = st.lamps;
  for (const lp of world.lamps) {
    const lit = L.on && (L.flicker <= 0 || Math.sin(t * 43.0 + lp.x * 3.1) > (L.flicker > 0.7 ? 0.3 : -0.8));
    const bright = L.blaze ? 1.0 : 1;
    lp.lensMat.color.set(lit ? (L.blaze ? '#ffffff' : '#ffd98a') : '#3c3f45');
    // aim heads toward Finch during the count
    const hx = lp.x + 1.45;
    const dx = 12.15 - hx, dz = 2.25 - (-5.3);
    lp.head.rotation.y = L.aimU * Math.atan2(dx, dz);
    lp.head.rotation.z = L.aimU > 0 ? lerpZ(0.32, 0.04, L.aimU) : 0.32;
  }
  for (const pl of lampLights) {
    const lit = L.on && (L.flicker <= 0 || Math.sin(t * 43.0 + pl.position.x * 3.1) > -0.6);
    pl.intensity = lit ? (L.blaze ? 11.0 : 5.2) : 0;
  }
  for (const lp of world.lamps) {
    lp.glowMat.opacity = L.on ? (L.blaze ? 0.95 : (L.flicker > 0 ? (Math.sin(t * 43.0 + lp.x * 3.1) > 0 ? 0.7 : 0.1) : 0.7)) : 0;
  }
  porchLight.intensity = (t >= 22.2 && t < 53.7) ? 5.0 : 0;
  // hero-house windows glow warm at night
  world.heroWinMat.color.set(night ? '#ffd98a' : '#2b3f66');
  world.heroWinMat.emissive.set(night ? '#7a4a18' : '#000000');

  // facades day/night swap
  for (const b of world.buildings) {
    const want = night ? b.night : b.day;
    if (b.mat.map !== want) { b.mat.map = want; b.mat.needsUpdate = true; }
  }

  // doors
  for (const [name, d] of Object.entries(world.heroDoors)) {
    const amt = st.doors[name] || 0;
    d.pivot.rotation.y = amt * 1.05;
  }

  // characters
  for (const [name, cs] of Object.entries(st.chars)) {
    const rig = cast[name];
    if (!rig) continue;
    rig.setVisible(cs.vis);
    if (!cs.vis) continue;
    rig.setAt(cs.x, cs.z, cs.ry);
    rig.setPose(cs.mode, t, { phase: name.length * 1.7 });
    rig.setExpression(cs.talk ? 'talk' : cs.expr, t * 9.0);
    if (rig.cane) rig.cane.visible = !st.props.caneDown;
  }

  // aftermath props
  hatGroup.visible = st.props.hat;
  groundCane.visible = st.props.caneDown;

  // overlays
  if (st.overlay) {
    overlayMesh.material.map = CARDS[st.overlay.tex];
    overlayMesh.material.opacity = st.overlay.op;
    overlayMesh.visible = st.overlay.op > 0.001;
  } else {
    overlayMesh.visible = false;
  }
  // countdown number (independent of cards)
  if (st.num) {
    if (numMesh.material.map !== NUMS[st.num.d]) {
      numMesh.material.map = NUMS[st.num.d];
      numMesh.material.needsUpdate = true;
    }
    numMesh.material.opacity = st.num.op;
    // size/pos follow the camera fov so the number always sits upper-center
    const vh = 2 * 1.9 * Math.tan((camera.fov * Math.PI) / 360);
    const sc = vh * 0.40 * (1.22 - 0.22 * st.num.pop);
    numMesh.scale.set(sc, sc, 1);
    numMesh.position.set(0, vh * 0.27, -1.9);
    numMesh.visible = true;
  } else {
    numMesh.visible = false;
  }
  flashMesh.material.opacity = st.flash;

  renderer.render(scene, camera);
  return canvas;
}
function lerpZ(a, b, u) { return a + (b - a) * u; }

window.__captureBatch = function (startFrame, count, fps = 30) {
  const out = new Array(count);
  for (let i = 0; i < count; i++) {
    const c = renderAt((startFrame + i) / fps);
    out[i] = c.toDataURL('image/jpeg', 0.92).split(',')[1];
  }
  return out;
};
window.__SHOTS = SHOTS;
window.__DURATION = DURATION;

window.__dbg = { camera, scene, renderer, renderAt, THREE };
renderAt(parseFloat(params.get('t') || '1.0'));
window.__ready = true;
