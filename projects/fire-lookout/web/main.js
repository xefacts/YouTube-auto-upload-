// ============================================================================
// MAIN.JS — deterministic headless renderer for "The Fire Lookout"
// Contract: index.html?w=540&h=960 — renderAt(t) is pure; __captureBatch
// batches JPEG frames; __ready flips true after the first successful render.
// ============================================================================
import * as THREE from 'three';
import { buildWorld, box } from './world.js';
import { BlockChar } from './chars.js';
import { evaluateScene, DURATION, SHOTS, shotAt } from './story.js';

const params = new URLSearchParams(location.search);
const W = parseInt(params.get('w') || '540', 10);
const H = parseInt(params.get('h') || '960', 10);

const scene = new THREE.Scene();
scene.background = new THREE.Color('#05070a');
scene.fog = new THREE.Fog('#05070a', 30, 110);

const camera = new THREE.PerspectiveCamera(42, W / H, 0.1, 260);
scene.add(camera);

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'low-power' });
renderer.setSize(W, H);
renderer.setPixelRatio(1);
document.body.appendChild(renderer.domElement);

const loader = new THREE.TextureLoader();
loader.setPath('../'); // server root = project root; page lives at /web/

const world = buildWorld(scene, loader);

// ---------------------------------------------------------------- vignette + fade
const vigCanvas = document.createElement('canvas');
{
  const g = vigCanvas.getContext('2d');
  vigCanvas.width = 360; vigCanvas.height = 640;
  const grd = g.createRadialGradient(180, 320, 190, 180, 320, 380);
  grd.addColorStop(0, 'rgba(0,0,0,0)');
  grd.addColorStop(1, 'rgba(0,0,0,0.55)');
  g.fillStyle = grd; g.fillRect(0, 0, 360, 640);
}
const vigTex = new THREE.CanvasTexture(vigCanvas);
const vig = new THREE.Mesh(
  new THREE.PlaneGeometry(W * 1.35 / 100 * 5.6, H * 1.35 / 100 * 5.6),
  new THREE.MeshBasicMaterial({ map: vigTex, transparent: true, opacity: 0.95, depthTest: false })
);
vig.position.z = -5;
vig.renderOrder = 996;
camera.add(vig);

const fadeMat = new THREE.MeshBasicMaterial({ color: '#000000', transparent: true, opacity: 0, depthTest: false });
const fadePlane = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), fadeMat);
fadePlane.position.z = -4.5;
fadePlane.renderOrder = 997;
camera.add(fadePlane);

// ---------------------------------------------------------------- cast
const daniel = new BlockChar(scene, {
  name: 'daniel', skin: '#e8b088', shirt: '#5a6b4a', accent: '#3e4a36',
  pants: '#3a3f4a', shoes: '#2c2c30',
  hair: { style: 'block', color: '#241c14' }, scale: 0.68, variant: 'classic',
});
const manager = new BlockChar(scene, {
  name: 'manager', skin: '#d8a878', shirt: '#c05a20', accent: '#8a3c12',
  pants: '#4a4238', shoes: '#33302a', cap: '#3e3e44',
  hair: { style: 'block', color: '#c9c9c9' }, scale: 0.70, variant: 'classic',
});
const figure = new BlockChar(scene, {
  name: 'figure', skin: '#cfd4d6', shirt: '#343b4a', accent: '#22262f',
  pants: '#262c38', shoes: '#1c2028',
  hair: { style: 'block', color: '#0c0d12' }, scale: 0.72, variant: 'classic',
});
// glowing eyes on figure
const eyeMat = new THREE.MeshBasicMaterial({ color: '#ffffff' });
const eyeL = new THREE.Mesh(new THREE.SphereGeometry(0.035, 8, 8), eyeMat);
const eyeR = new THREE.Mesh(new THREE.SphereGeometry(0.035, 8, 8), eyeMat);
eyeL.position.set(-0.15, 2.78, 0.35); eyeR.position.set(0.15, 2.78, 0.35);
figure.group.add(eyeL, eyeR);
// green outline shell (inverted hull) around figure
const figShell = new THREE.Mesh(
  new THREE.BoxGeometry(1.7, 3.4, 1.2),
  new THREE.MeshBasicMaterial({ color: '#2aff7a', transparent: true, opacity: 0, side: THREE.BackSide })
);
figShell.position.y = 1.55;
figure.group.add(figShell);

// envelope of cash on desk (money beat)
const envelope = box(0.3, 0.03, 0.2, '#d8d0b8', { x: -1.45, y: 0.8 + 0.7, z: 0.9, ry: 0.3 });
scene.add(envelope); // repositioned below to interior coords
envelope.position.set(-1.45, 8.325, 0.9); // desk-top height inside cab

// ---------------------------------------------------------------- helpers
const AMBER = new THREE.Color('#ffb44a');
const RED = new THREE.Color('#ff2a18');
const clamp01 = (v) => Math.max(0, Math.min(1, v));
const lerp = (a, b, u) => a + (b - a) * u;

const STAGE_WINDOWS = [
  [world.stageCctv, [[0.0, 6.8]]],
  [world.stageNotebook, [[52.3, 61.7]]],
  [world.stageWarning, [[61.7, 65.3]]],
  [world.stagePhoneMsg, [[111.6, 116.4], [126.5, 130.0]]],
  [world.stagePhonePhoto, [[116.4, 126.5]]],
  [world.stagePhoneNoSvc, [[94.6, 95.7]]],
];

function setCam(shot, t) {
  const { cam, move, u } = shot;
  let px = cam.pos[0], py = cam.pos[1], pz = cam.pos[2];
  let lx = cam.look[0], ly = cam.look[1], lz = cam.look[2];
  // dolly move: start 7% behind
  if (move === 'push') {
    px = lerp(px + (px - lx) * 0.09, px, u);
    py = lerp(py + (py - ly) * 0.09, py, u);
    pz = lerp(pz + (pz - lz) * 0.09, pz, u);
  } else if (move === 'pull') {
    px = lerp(px - (px - lx) * 0.08, px, u);
    py = lerp(py - (py - ly) * 0.08, py, u);
    pz = lerp(pz - (pz - lz) * 0.08, pz, u);
  } else if (move === 'panL' || move === 'panR') {
    const sgn = move === 'panL' ? 1 : -1;
    lx += (u - 0.5) * 1.1 * sgn;
  } else if (move === 'tiltU' || move === 'tiltD') {
    const sgn = move === 'tiltU' ? 1 : -1;
    ly += (u - 0.5) * 1.4 * sgn;
  } else if (move === 'panD') {
    ly -= u * 0.55;
  }
  // organic handheld sway
  const swx = Math.sin(t * 0.9 + shot.i * 2.1) * 0.035;
  const swy = Math.cos(t * 0.7 + shot.i * 1.3) * 0.03;
  camera.position.set(px + swx, py + swy, pz);
  camera.lookAt(lx, ly, lz);
  camera.fov = cam.fov;
  camera.updateProjectionMatrix();
  // glitch: hard x offset jumps
  if (shot.i <= 1) {
    const st = propStatesCache;
    if (st && st.cctvGlitch) { camera.position.x += (Math.sin(t * 61.7) > 0 ? 0.05 : -0.04); camera.position.y += 0.02; }
  }
}

let propStatesCache = null;

// ---------------------------------------------------------------- renderAt
function renderAt(t) {
  const st = evaluateScene(t);
  propStatesCache = st.props;
  const L = st.light, P = st.props, C = st.chars;

  // backdrop + fog + bg
  scene.background.set(L.bg);
  scene.fog.color.set(L.fog);
  world.sun.intensity = L.sun * 1.25;
  world.moonLight.intensity = L.moon * 1.8;
  world.amb.intensity = L.amb * 0.5;
  world.hemi.intensity = 0.42 + 0.5 * (1 - L.night);
  world.moon.material.opacity = L.night * 0.95;
  for (const s of world.stars.children) s.material.opacity = L.night * (0.5 + 0.5 * Math.sin(t * 2.0 + s.position.x));
  world.backdrop.material.opacity = clamp01(1 - L.night * 1.6) * (t > 6.6 && t < 41 ? 0.85 : 0);
  for (const mq of world.mists) {
    mq.material.opacity = P.mist * 1.7 * (0.7 + 0.3 * Math.sin(t * 0.6 + mq.position.x));
    mq.lookAt(camera.position.x, mq.position.y, camera.position.z);
  }

  // fade to black (ending)
  fadeMat.opacity = L.fade;

  // truck
  world.truck.visible = P.truckVis;
  world.truck.position.x = P.truckX;

  // ---- interior ----
  // radio dial
  const dialC = P.radioRed ? RED : AMBER;
  world.radioDialMat.color.copy(dialC);
  const pulse = P.radioVoice ? 0.65 + 0.35 * Math.abs(Math.sin(t * 7.3)) : 0.8;
  world.radioDialMat.emissive.copy(dialC).multiplyScalar(pulse);
  // radio antenna sway on voice
  world.radio.children[6].rotation.z = -0.3 + (P.radioVoice ? Math.sin(t * 9.0) * 0.12 : 0);
  // lantern
  world.lanternLight.intensity = 0.9 + P.lantern * 1.2;
  world.lampGlassMat.emissive.set('#ffb35a').multiplyScalar(0.4 + P.lantern * 0.6);
  // cab fill glow at night
  world.cabGlow.intensity = 0.7 + 1.5 * L.night;
  world.glassMat.emissive.set('#ffb066').multiplyScalar(L.night);
  world.glassMat.opacity = 0.16 + L.night * 0.5;
  // notebook
  world.nbCover.rotation.x = P.nbOpen ? -1.35 : 0;
  world.nbPage.visible = P.nbOpen;
  world.notebook.position.y = (P.nbInHand ? 0.83 + 0.35 : 0.83);
  world.notebook.rotation.x = P.nbInHand ? -0.4 : 0;
  // phone screen (desk phone)
  world.phoneScreen.visible = P.phoneScreenOn;
  world.screenMat.map = world.screenTexes.msg;
  if (P.phoneBuzz) {
    world.phone.position.x = 1.35 + Math.sin(t * 55) * 0.012;
    world.phone.position.z = 1.25 + Math.cos(t * 49) * 0.012;
  } else {
    world.phone.position.set(1.35, 0.815, 1.25);
  }
  // door
  world.doorPivot.rotation.y = P.doorOpen * 1.05;
  if (P.knocking) {
    world.doorPivot.position.z = -0.6 + Math.sin(t * 34) * 0.035 * (Math.abs(Math.sin(t * 7)) > 0.6 ? 1 : 0);
    world.doorPivot.rotation.y = Math.sin(t * 30) * 0.02;
  } else {
    world.doorPivot.position.z = -0.6;
  }
  // below-hatch glow
  world.belowGlow.intensity = P.belowGlow * 6.0;
  // flashlight beam + figure light
  world.beam.material.opacity = P.beam;
  world.beamPool.material.opacity = P.beam * 0.85;
  world.figLight.intensity = P.beam > 0 ? 9.0 : 0;
  world.underRed.intensity = P.knocks3 ? 7.0 + Math.sin(t * 11) * 1.8 : 0;
  world.officeLight.intensity = (t >= 88.2 && t < 89.6) ? 2.6 : 0;
  // warning red frame
  world.warnRedFrame.material.opacity = P.warnRed;
  // jacket flashback outline
  world.jacketOutline.material.opacity = P.jacketOutline;
  // CCTV HUD
  world.cctvHud.material.opacity = P.cctvHud;
  world.cctvGrain.material.opacity = P.cctvHud * 0.55;
  world.cctvGrain.position.x = Math.sin(t * 13) * 0.03;

  // macro stages visibility
  for (const [grp, ranges] of STAGE_WINDOWS) grp.visible = ranges.some(([a, b]) => t >= a && t < b);

  // ---- characters ----
  const apply = (rig, cs) => {
    rig.setVisible(cs.vis);
    if (!cs.vis) return;
    rig.group.position.set(cs.x, cs.y, cs.z);
    rig.group.rotation.y = cs.ry;
    rig.setPose(cs.mode, t, { phase: 1.7 });
    rig.setExpression(cs.expr, t * 7.0);
  };
  apply(daniel, C.d);
  apply(manager, C.m);
  apply(figure, C.fig);
  figShell.material.opacity = P.figOutline * (0.75 + 0.25 * Math.sin(t * 6));
  // figure slightly unnaturally still when not walking
  if (C.fig.vis && C.fig.mode !== 'walk') figure.setPose('stand', 0.0);

  // camera
  setCam(st.shot, t);

  renderer.render(scene, camera);
  return t;
}

// ---------------------------------------------------------------- boot
window.__captureBatch = function (startFrame, count, fps = 30) {
  const out = [];
  for (let i = 0; i < count; i++) {
    renderAt((startFrame + i) / fps);
    out.push(renderer.domElement.toDataURL('image/jpeg', 0.88));
  }
  return out;
};
window.__SHOTS = SHOTS;
window.__DURATION = DURATION;
window.__world = world;
window.__cast = { daniel, manager, figure };
window.__dbg = { camera, scene, renderer, renderAt, THREE };
window.__ready = true;

renderAt(parseFloat(params.get('t') || '1.0'));
