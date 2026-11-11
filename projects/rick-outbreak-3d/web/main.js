// V3 Master Scene Engine: Three.js r187 + @pmndrs/postprocessing (GPU Bloom + Chromatic Shock + Vignette)
// + Biomechanical Distance-Locked Running, 100% Closed Shutters (`sheleter bnd bilkul`),
//   Situation-Accurate Expressions, Nightmare Horror Zombies & Underground Transit Finale!
import * as THREE from 'three';
import {
  EffectComposer,
  RenderPass,
  EffectPass,
  BloomEffect,
  VignetteEffect,
  ChromaticAberrationEffect,
  BrightnessContrastEffect,
  ToneMappingEffect,
  ToneMappingMode,
} from './lib/postprocessing.js';
import { buildOutbreakWorld } from './world.js';
import { ROLES, Pen, rickChar, rickBackPOV, fxRing, fxBurst } from './toon.js';
import { idle, blinkAt } from './motion.js';
import { SHOTS, evaluateScene } from './story.js';

const params = new URLSearchParams(location.search);
const W = parseInt(params.get('w') || '540', 10);
const H = parseInt(params.get('h') || '960', 10);

const outCanvas = document.getElementById('out');
outCanvas.width = W;
outCanvas.height = H;

const glCanvas = document.createElement('canvas');
const renderer = new THREE.WebGLRenderer({
  canvas: glCanvas,
  antialias: false,
  powerPreference: 'high-performance',
  stencil: false,
  depth: true,
  preserveDrawingBuffer: true,
});
renderer.setSize(W, H, false);
renderer.setPixelRatio(1);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = false;
// V6: Hollywood filmic shoulder — kills highlight blow-outs (flashlight snaps, neon, sun).
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.18;

const scene = new THREE.Scene();
scene.background = new THREE.Color('#5d84a6');
scene.fog = new THREE.Fog('#5d84a6', 10, 52);

const camera = new THREE.PerspectiveCamera(42, W / H, 0.12, 95);

// ---------- @pmndrs/postprocessing Merged Single-Pass Cinema Pipeline ----------
const composer = new EffectComposer(renderer, { frameBufferType: THREE.UnsignedByteType });
composer.addPass(new RenderPass(scene, camera));

const bloomEffect = new BloomEffect({
  intensity: 0.68,
  luminanceThreshold: 0.74,
  luminanceSmoothing: 0.22,
  mipmapBlur: false,
  resolutionScale: 0.5,
});
const chromaEffect = new ChromaticAberrationEffect({
  offset: new THREE.Vector2(0.0, 0.0),
  radialModulation: false,
  modulationOffset: 0.15,
});
const vignetteEffect = new VignetteEffect({
  eskil: false,
  offset: 0.28,
  darkness: 0.40,
});
// Global readability grade: lift shadows (user: "environment thora bright") without killing the horror mood.
const brightContrastEffect = new BrightnessContrastEffect({ brightness: 0.06, contrast: 0.02 });
const toneMappingEffect = new ToneMappingEffect({
  mode: ToneMappingMode.ACES_FILMIC,
});
composer.addPass(new EffectPass(camera, bloomEffect, chromaEffect, vignetteEffect, brightContrastEffect, toneMappingEffect));

// ---------- Scene Lighting Rig ----------
const hemi = new THREE.HemisphereLight('#fffaf0', '#384258', 0.85);
scene.add(hemi);

const sun = new THREE.DirectionalLight('#fff1d6', 1.85);
sun.position.set(8, 16, 18);
scene.add(sun);

const storeLightFront = new THREE.PointLight('#fff8eb', 1.18, 18, 1.25);
storeLightFront.position.set(0, 3.35, 2.2);
scene.add(storeLightFront);

const emergLight = new THREE.PointLight('#ff462e', 0.0, 12.5, 1.30);
emergLight.position.set(2.8, 3.15, -10.2);
const storageDimLight = new THREE.PointLight('#6482b5', 0.52, 11.5, 1.35);
storageDimLight.position.set(2.8, 3.1, -14.8);
scene.add(emergLight, storageDimLight);

const alleyLight = new THREE.PointLight('#d8e6f5', 1.35, 22, 1.2);
alleyLight.position.set(0, 5.2, -27.5);
scene.add(alleyLight);

// Warm caged emergency lamp above the ALLEY maintenance door (hazard-framed entrance!)
const alleyDoorLight = new THREE.PointLight('#ffb35c', 0.0, 9.0, 1.35);
alleyDoorLight.position.set(0, 3.15, -34.35);
scene.add(alleyDoorLight);

// Warm emergency bulkhead light above the SELF-CLOSING underground door!
const ugBulkLight = new THREE.PointLight('#ffb050', 0.0, 11.0, 1.3);
ugBulkLight.position.set(0.55, 4.35, -51.60);
scene.add(ugBulkLight);

const ugMainLight = new THREE.PointLight('#ffba66', 1.55, 18, 1.25);
ugMainLight.position.set(0, 3.75, -62.2);
const ugStairLight = new THREE.PointLight('#98b8d4', 1.10, 14, 1.3);
ugStairLight.position.set(0, 4.1, -53.2);
const ugRadioGlow = new THREE.PointLight('#ff2b22', 0.0, 3.5, 1.4);
ugRadioGlow.position.set(-0.25, 0.72, -62.45);
scene.add(ugMainLight, ugStairLight, ugRadioGlow);

const flashSpot = new THREE.SpotLight('#fff6d6', 0.0, 15.0, 0.52, 0.55, 1.2);
scene.add(flashSpot, flashSpot.target);

// V6: red/blue STROBE WASH — a real light bathing the horde & street around the patrol SUV.
const strobeWash = new THREE.PointLight('#ff3040', 0.0, 20.0, 1.15);
strobeWash.position.set(-2.4, 2.6, 19.6);
scene.add(strobeWash);

// V6: cold backlight behind the tunnel-dweller silhouette (reads the shape in the black bore).
const figBackLight = new THREE.PointLight('#7f96c4', 0.0, 8.0, 1.6);
figBackLight.position.set(0.35, 1.9, -75.8);
scene.add(figBackLight);

const phoneGlow = new THREE.PointLight('#ff3528', 0.0, 3.2, 1.4);
scene.add(phoneGlow);

// ---------- Build Unified V3 3D World ----------
const world = buildOutbreakWorld(scene);
// V6: screens & neon stay crisp under ACES filmic tone mapping.
world.phoneScrMat.toneMapped = false;
world.neonMat.toneMapped = false;
world.posScreenMat.toneMapped = false;
world.cctvScreenMat.toneMapped = false;

// Blood pool decal for the hit-and-run (flat dark red circle on the asphalt)
const bloodPoolMat = new THREE.MeshBasicMaterial({ color: '#521119', transparent: true, opacity: 0.0, depthWrite: false });
const bloodPool = new THREE.Mesh(new THREE.CircleGeometry(0.55, 26), bloodPoolMat);
bloodPool.rotation.x = -Math.PI / 2;
bloodPool.position.y = 0.02;
bloodPool.visible = false;
scene.add(bloodPool);

// ---------- Build Articulated 2D/3D Character Rig Pool ----------
function makeCharRig(roleKey, roleCfg, heightM = 1.76) {
  const cw = 600, ch = 1000;
  const c = document.createElement('canvas');
  c.width = cw; c.height = ch;
  const ctx = c.getContext('2d');
  const pen = new Pen(ctx);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.minFilter = THREE.LinearFilter;
  tex.magFilter = THREE.LinearFilter;

  const aspect = cw / ch;
  const mat = new THREE.MeshBasicMaterial({
    map: tex,
    transparent: true,
    alphaTest: 0.05,
    side: THREE.DoubleSide,
  });
  const group = new THREE.Group();
  const card = new THREE.Mesh(new THREE.PlaneGeometry(heightM * aspect, heightM), mat);
  card.position.y = heightM * 0.50;
  group.add(card);

  const shMat = new THREE.MeshBasicMaterial({ color: '#140f14', transparent: true, opacity: 0.38, depthWrite: false });
  const shadow = new THREE.Mesh(new THREE.CircleGeometry(0.34, 20), shMat);
  shadow.rotation.x = -Math.PI / 2;
  shadow.position.y = 0.015;
  shadow.scale.set(1.0, 0.68, 1.0);
  group.add(shadow);

  scene.add(group);
  return { roleKey, roleCfg, c, ctx, pen, tex, mat, group, card, shadow, cw, ch, baseCardY: card.position.y };
}

const charRigs = {
  you:     makeCharRig('you',       ROLES.you,       1.76),
  police:  makeCharRig('police',    ROLES.police,    1.79),
  woman:   makeCharRig('woman',     ROLES.woman,     1.69),
  carMan:  makeCharRig('carMan',    ROLES.carMan,    1.76),
  runA:    makeCharRig('runnerA',   ROLES.runnerA,   1.74),
  runB:    makeCharRig('runnerB',   ROLES.runnerB,   1.71),
  survMan: makeCharRig('survMan',   ROLES.survMan,   1.77),
  survBoy: makeCharRig('survBoy',   ROLES.survBoy,   1.30), // Authentic child height!
  infA:    makeCharRig('infectedA', ROLES.infectedA, 1.79),
  infB:    makeCharRig('infectedB', ROLES.infectedB, 1.76),
  infC:    makeCharRig('infectedC', ROLES.infectedC, 1.77),
};

// 2D Cartoon FX Card
const fxCanvas = document.createElement('canvas');
fxCanvas.width = 600; fxCanvas.height = 600;
const fxCtx = fxCanvas.getContext('2d');
const fxPen = new Pen(fxCtx);
const fxTex = new THREE.CanvasTexture(fxCanvas);
fxTex.colorSpace = THREE.SRGBColorSpace;
const fxMat = new THREE.MeshBasicMaterial({ map: fxTex, transparent: true, depthWrite: false, side: THREE.DoubleSide });
const fxMesh = new THREE.Mesh(new THREE.PlaneGeometry(2.2, 2.2), fxMat);
scene.add(fxMesh);

let lastSkyHex = '';

// V6: CINEMATIC OVERLAY PLANE (cold-open map / OUTBREAK title / DAY cards / TO BE CONTINUED).
const overlayMat = new THREE.MeshBasicMaterial({
  map: null, transparent: true, opacity: 0, depthTest: false, depthWrite: false, fog: false, toneMapped: false,
});
const overlayMesh = new THREE.Mesh(new THREE.PlaneGeometry(0.86, 1.52), overlayMat);
overlayMesh.renderOrder = 999;
scene.add(overlayMesh);

// V6: ATMOSPHERE PARTICLES — dust motes in light shafts, wind-blown street paper, sunrise ash.
const PART_N = 64;
const partPos = new Float32Array(PART_N * 3);
const partSeed = new Float32Array(PART_N * 4); // speed, drift, sway, phase
{
  const pr = (s) => Math.abs((Math.sin(s * 127.1) * 43758.5453) % 1);
  for (let i = 0; i < PART_N; i++) {
    partSeed[i * 4] = 0.2 + pr(i * 3.1) * 0.9;
    partSeed[i * 4 + 1] = 0.1 + pr(i * 7.7) * 0.5;
    partSeed[i * 4 + 2] = (pr(i * 11.3) - 0.5) * 0.6;
    partSeed[i * 4 + 3] = pr(i * 5.9) * 6.283;
  }
}
const partGeo = new THREE.BufferGeometry();
partGeo.setAttribute('position', new THREE.BufferAttribute(partPos, 3));
const partMat = new THREE.PointsMaterial({
  color: '#ffe9c8', size: 0.052, transparent: true, opacity: 0, depthWrite: false, sizeAttenuation: true,
});
const particles = new THREE.Points(partGeo, partMat);
particles.frustumCulled = false;
scene.add(particles);
let partMode = '';
let partLastT = -1;

export function renderAt(t) {
  const st = evaluateScene(t);
  const z = st.shot.zone;

  // 1. Fast Dynamic Camera + Dutch Horror Roll
  camera.fov = st.fov;
  camera.position.set(st.camPos[0], st.camPos[1], st.camPos[2]);
  camera.lookAt(st.camLook[0], st.camLook[1], st.camLook[2]);
  if (st.camRoll) {
    camera.rotateZ((st.camRoll * Math.PI) / 180);
  }
  camera.updateProjectionMatrix();

  const ca = st.impactPulse * 0.0046;
  chromaEffect.offset.set(ca, ca * 0.65);

  // V6: cinematic overlay rides 1.2m in front of the lens (covers every fov).
  if (st.introOverlay && world.introOverlayTex) {
    const ot = world.introOverlayTex[st.introOverlay.tex];
    if (ot && overlayMat.map !== ot) { overlayMat.map = ot; overlayMat.needsUpdate = true; }
    overlayMat.opacity = st.introOverlay.op;
    overlayMesh.visible = true;
    const dir = new THREE.Vector3();
    camera.getWorldDirection(dir);
    overlayMesh.position.copy(camera.position).addScaledVector(dir, 1.2);
    overlayMesh.quaternion.copy(camera.quaternion);
  } else {
    overlayMesh.visible = false;
  }

  // V6: atmosphere particle field.
  {
    const dt = Math.max(0, Math.min(0.05, t - partLastT));
    partLastT = t;
    let mode = 'none';
    if (z === 'street' && t >= 145.96 && t < 188.4) mode = 'ash';
    else if (z === 'street' && t < 145.96) mode = 'paper';
    else if (z === 'underground') mode = 'ugdust';
    else if (z === 'store') mode = 'motes';
    if (mode !== partMode) { // reseed positions for the new volume
      partMode = mode;
      for (let i = 0; i < PART_N; i++) {
        const r1 = Math.sin(i * 91.7 + t * 0.13) * 0.5 + 0.5;
        const r2 = Math.sin(i * 47.3 + t * 0.17) * 0.5 + 0.5;
        const r3 = Math.sin(i * 33.9 + t * 0.11) * 0.5 + 0.5;
        if (mode === 'paper' || mode === 'ash') {
          partPos[i*3] = -20 + r1 * 40; partPos[i*3+1] = 0.15 + r2 * 2.4; partPos[i*3+2] = 9 + r3 * 20;
        } else if (mode === 'ugdust') {
          partPos[i*3] = -1.6 + r1 * 3.2; partPos[i*3+1] = 0.4 + r2 * 3.0; partPos[i*3+2] = -66 + r3 * 10;
        } else {
          partPos[i*3] = -1.5 + r1 * 4.5; partPos[i*3+1] = 0.3 + r2 * 2.9; partPos[i*3+2] = 1 + r3 * 6;
        }
      }
    }
    const cfg = mode === 'paper' ? { op: 0.50, size: 0.11, col: '#cfc9ba' }
      : mode === 'ash' ? { op: 0.38, size: 0.075, col: '#8b8f98' }
      : mode === 'ugdust' ? { op: 0.22, size: 0.045, col: '#ffd9a8' }
      : { op: 0.32, size: 0.05, col: '#ffe9c8' };
    partMat.opacity = cfg.op;
    partMat.size = cfg.size;
    partMat.color.set(cfg.col);
    particles.visible = mode !== 'none';
    if (particles.visible) {
      for (let i = 0; i < PART_N; i++) {
        const sd = partSeed[i * 4], ph = partSeed[i * 4 + 3];
        if (mode === 'paper') {
          partPos[i*3] += (0.55 + sd * 0.75) * dt * (1 + 0.4 * Math.sin(t * 1.7 + ph));
          partPos[i*3+1] += Math.sin(t * 3.1 + ph) * 0.5 * dt;
          if (partPos[i*3] > 20) partPos[i*3] = -20;
          if (partPos[i*3+1] < 0.1 || partPos[i*3+1] > 2.6) partPos[i*3+1] = 0.15 + (ph / 6.283) * 2.3;
        } else if (mode === 'ash') {
          partPos[i*3] += (0.22 + sd * 0.3) * dt;
          partPos[i*3+1] -= (0.10 + sd * 0.16) * dt;
          if (partPos[i*3+1] < 0.05) partPos[i*3+1] = 2.8;
          if (partPos[i*3] > 20) partPos[i*3] = -20;
        } else {
          partPos[i*3] += Math.sin(t * 0.7 + ph) * 0.05 * dt;
          partPos[i*3+1] += (0.02 + sd * 0.05) * dt * (mode === 'ugdust' ? 0.5 : 1);
          if (partPos[i*3+1] > 3.2) partPos[i*3+1] = 0.3;
        }
      }
      partGeo.attributes.position.needsUpdate = true;
    }
  }

  // 2. Zone Visibility & Atmosphere
  if (st.skyHex !== lastSkyHex) {
    scene.background.set(st.skyHex);
    scene.fog.color.set(st.skyHex);
    lastSkyHex = st.skyHex;
  }
  if (z === 'underground') {
    scene.fog.near = 4.5;
    scene.fog.far  = 24.5;
  } else if (z === 'back') {
    scene.fog.near = 3.8;
    scene.fog.far  = 21.0;
  } else if (z === 'alley') {
    scene.fog.near = 6.0;
    scene.fog.far  = 34.0;
  } else {
    scene.fog.near = 10.0;
    scene.fog.far  = z === 'street' ? 60.0 : 46.0;
  }

  world.storeGroup.visible       = (z === 'store' || z === 'street');
  world.streetGroup.visible      = (z === 'store' || z === 'street');
  world.backGroup.visible        = (z === 'back' || st.shot.id === 37 || st.shot.id === 60);
  world.alleyGroup.visible       = (z === 'alley');
  world.undergroundGroup.visible = (z === 'underground');

  world.lightShafts.visible = (z === 'store' && st.shaftOpacity > 0.005);
  world.shaftMat.opacity = st.shaftOpacity;

  sun.visible = (z === 'store' || z === 'street' || z === 'alley');
  sun.intensity = st.sunInt;
  hemi.intensity = st.ambInt;

  storeLightFront.visible = (z === 'store');
  storeLightFront.intensity = st.storeLightInt;

  emergLight.visible = (z === 'back' && st.emergInt > 0.02);
  emergLight.intensity = st.emergInt;
  storageDimLight.visible = (z === 'back');
  world.emergBulbMat.color.set(st.emergInt > 0.8 ? '#ff6442' : '#4a1c18');

  alleyLight.visible = (z === 'alley');
  alleyDoorLight.visible = (z === 'alley');
  if (z === 'alley') {
    const alFlick = 0.92 + 0.08 * Math.sin(t * 15.0) * Math.cos(t * 6.1);
    alleyDoorLight.intensity = 1.70 * alFlick;
    world.alleyLampMat.color.set(alFlick > 0.86 ? '#ffc878' : '#c88a3e');
  }

  // Emergency bulkhead above the self-closing maintenance door (dims as it seals shut!)
  ugBulkLight.visible = (z === 'underground');
  ugBulkLight.intensity = 3.1 * (1.0 - 0.55 * st.ugDoorCloseU);
  world.ugBulkMat.color.set(st.ugDoorCloseU > 0.97 ? '#5a3418' : '#ffc06a');
  world.ugBulkGlowMat.opacity = Math.max(0, 1.0 - 0.92 * st.ugDoorCloseU);

  ugMainLight.visible = (z === 'underground');
  // Subtle eerie underground lamp flicker
  const ugFlicker = 0.88 + 0.12 * Math.sin(t * 17.0) * Math.cos(t * 7.3);
  ugMainLight.intensity = 1.95 * ugFlicker;
  world.ugLampMat.color.set(ugFlicker > 0.85 ? '#ffc26e' : '#a87838');

  ugStairLight.visible = (z === 'underground');
  ugStairLight.intensity = 1.95 * (1.0 - 0.55 * st.ugDoorCloseU);
  world.ugDoorBackGlow.visible = (st.ugDoorCloseU < 0.99);

  // Underground Radio Red LED & Glow (V6: smooth glow envelope — no LED pops at 213.4/231.8/254.45)
  const rgL = st.radioGlowLevel || 0;
  ugRadioGlow.visible = (z === 'underground' && !st.radioOff && rgL > 0.01);
  if (st.radioOff) {
    world.ugRadioLedMat.color.set('#140707');
    ugRadioGlow.intensity = 0.0;
  } else if (rgL > 0.01) {
    const cr = 0.55 + 0.45 * Math.abs(Math.sin(t * 38.0));
    world.ugRadioLedMat.color.setRGB(1.0, 0.18 * cr, 0.10 * cr);
    ugRadioGlow.intensity = (1.15 + 1.10 * cr) * rgL;
  } else {
    world.ugRadioLedMat.color.set('#d9241e');
    ugRadioGlow.intensity = 0.0;
  }

  world.tunnelEyes.visible = (z === 'underground' && st.tunnelEyesVisible);

  const tubeCol = st.storeLightInt > 0.7 ? '#fffef5' : (st.storeLightInt > 0.15 ? '#556273' : '#1e242c');
  for (const tm of world.fluorStrips) tm.color.set(tubeCol);

  const frCol = st.fridgeOn > 0.5 ? '#d4f8ff' : '#1b262e';
  for (const fm of world.fridgeLights) fm.color.set(frCol);

  // V6: street lamps live ONLY in the dusk window — the grid dies with the power cut at 83.35.
  const bulbOn = (t >= 46.85 && t < 83.35);
  const bulbCol = bulbOn ? '#ffe5a3' : '#9aa4ad';
  for (const bm of world.streetBulbs) bm.color.set(bulbCol);
  for (const gm of world.streetGlow) gm.opacity = bulbOn ? 0.30 : 0.0;
  // V6: sky dome follows the act tint; hidden in enclosed zones.
  if (world.skyDome) {
    world.skyDome.visible = (z === 'street' || z === 'alley' || z === 'store');
    world.skyDome.material.color.set(st.skyDomeTint);
  }
  // V6: across-street windows — day glass, warm dusk subset, grid death, dead dawn.
  if (world.shopWindows) {
    const wl = st.windowsLit;
    const isDawnAct = t >= 145.96 && t < 188.4;
    for (const w of world.shopWindows) {
      if (wl > 0.01) {
        w.mat.color.set('#141b26').lerp(new THREE.Color('#ffd88a'), wl * w.lit);
      } else if (isDawnAct) {
        w.mat.color.set('#2a3140');
      } else {
        w.mat.color.set('#3a4c63').multiplyScalar(0.55 + 0.75 * w.dayVar);
      }
    }
  }

  // Powered props: OPEN 24 HRS neon + POS register screen + CCTV monitor (dark after power cut at 83.35s!)
  const powered = t < 83.35;
  world.neonMat.color.set(powered ? '#ffffff' : '#241d26');
  world.posScreenMat.color.set(powered ? '#ffffff' : '#141a16');
  world.cctvScreenMat.color.set(powered ? '#ffffff' : '#10141a');

  // Volumetric Flashlight Beam (V6: ramped — no snap-on blow-out, no cliff-off blackout)
  world.flashCone.visible = st.flashLevel > 0.02;
  flashSpot.visible = st.flashLevel > 0.02;
  world.flashCone.material.opacity = 0.20 * st.flashLevel;
  if (st.flashLevel > 0.02) {
    flashSpot.intensity = 2.30 * st.flashLevel;
    const flPos = new THREE.Vector3();
    const flTgt = new THREE.Vector3();
    if (st.shot.id === 35) {
      flashSpot.position.set(2.95, 1.52, 3.30);
      flPos.set(3.15, 1.35, 3.70); // hand height, just camera-right of lens
      flTgt.set(3.62, 1.10, 4.12); // the ration cans
    } else {
      flashSpot.position.set(st.camPos[0] + 0.18, st.camPos[1] - 0.16, st.camPos[2] - 0.20);
      flTgt.set(st.camLook[0], st.camLook[1], st.camLook[2]);
      flPos.set(st.camPos[0] + 0.20, st.camPos[1] - 0.18, st.camPos[2] - 1.95);
    }
    flashSpot.target.position.copy(flTgt);
    flashSpot.target.updateMatrixWorld();
    // Aim: cone apex (local +y) sits at flPos, base opens toward flTgt.
    // setFromUnitVectors replaces the whole quaternion every frame — no lookAt() state leakage.
    const dir = flTgt.clone().sub(flPos).normalize();
    world.flashCone.position.copy(flPos).addScaledVector(dir, 2.1);
    world.flashCone.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.clone().negate());
  }

  // 3. Dynamic World Props (`sheleter bnd bilkul`: full 0.0 -> 1.0 top-drum unroll flush to floor y=0.00m!)
  world.deadboltBar.position.x = -0.18 + 0.18 * st.deadboltU;

  world.shutterWinPivot.visible = st.shutterWinU > 0.01;
  world.shutterWinPivot.scale.y = Math.max(0.02, st.shutterWinU);

  world.shutterDoorPivot.visible = st.shutterDoorU > 0.01;
  world.shutterDoorPivot.scale.y = Math.max(0.02, st.shutterDoorU);

  world.backDoorPivot.position.z = -16.32 + st.backDoorRattle;
  world.backDoorPivot.rotation.y = st.backDoorOpenAngle;

  world.ugMaintDoorPivot.rotation.y = st.ugMaintDoorAngle;

  world.counterBackpack.visible = st.packVis;
  world.sunriseDamageGroup.visible = st.sunriseDamageVis;

  world.abandonedCar.position.set(st.abandonedCarPos[0], st.abandonedCarPos[1], st.abandonedCarPos[2]);
  world.abandonedCar.rotation.y = st.abandonedCarRot;

  world.swerveCar.visible = st.swerveCarVis;
  if (st.swerveCarVis) {
    world.swerveCar.position.set(st.swerveCarPos[0], st.swerveCarPos[1], st.swerveCarPos[2]);
    world.swerveCar.rotation.y = st.swerveCarRot;
  }

  world.trafficCar.visible = st.trafficCarVis;
  if (st.trafficCarVis) {
    world.trafficCar.position.set(st.trafficCarPos[0], st.trafficCarPos[1], st.trafficCarPos[2]);
    world.trafficCar.rotation.y = st.trafficCarRot;
  }

  if (st.tunnelFig) {
    world.tunnelFig.visible = true;
    world.tunnelFig.position.set(st.tunnelFig.x, 0.97 * st.tunnelFig.s, st.tunnelFig.z);
    world.tunnelFig.scale.set(st.tunnelFig.s, st.tunnelFig.s, 1);
    world.tunnelFig.rotation.z = st.tunnelFig.rot || 0;
    world.tunnelFig.material.opacity = st.tunnelFig.op;
  } else {
    world.tunnelFig.visible = false;
  }

  world.patrolCar.visible = st.patrolCarVis;
  strobeWash.visible = st.patrolCarVis;
  strobeWash.intensity = st.patrolCarVis ? 2.1 : 0.0;
  strobeWash.color.set(Math.floor(t * 7.0) % 2 === 0 ? '#ff3040' : '#2b6bff');
  if (st.tunnelFig) {
    figBackLight.visible = true;
    figBackLight.intensity = 1.60 * st.tunnelFig.op;
    figBackLight.position.set(st.tunnelFig.x, 1.9, st.tunnelFig.z - 2.6);
  } else {
    figBackLight.visible = false;
  }
  if (st.patrolCarVis && world.patrolFlashers) {
    const strobe = Math.floor(t * 7.0) % 2 === 0;
    world.patrolFlashers[0].material.color.set(strobe ? '#ff2230' : '#5a0a10');
    world.patrolFlashers[1].material.color.set(strobe ? '#0a1440' : '#2b6bff');
    world.patrolFlashers.forEach((f) => { f.visible = true; });
  } else if (world.patrolFlashers) {
    world.patrolFlashers.forEach((f) => { f.visible = false; });
  }

  // Blood pool under the hit-and-run victim
  if (st.bloodPool) {
    bloodPool.visible = true;
    bloodPool.position.set(st.bloodPool.x, 0.02, st.bloodPool.z);
    bloodPool.scale.setScalar(Math.max(0.001, st.bloodPool.s));
    bloodPoolMat.opacity = 0.85 * st.bloodPool.a;
  } else {
    bloodPool.visible = false;
  }
  if (st.patrolCarVis) {
    world.patrolCar.position.set(st.patrolCarPos[0], st.patrolCarPos[1], st.patrolCarPos[2]);
    world.patrolCar.rotation.y = st.patrolCarRot;
  }

  // Hand-Gripped Smartphone Close-Up Inserts
  world.heldPhone.visible = st.phoneState.visible;
  phoneGlow.visible = st.phoneState.visible;
  if (st.phoneState.visible) {
    world.phoneScrMat.map =
      st.phoneState.mode === 'alert1' ? world.alert1Tex :
      st.phoneState.mode === 'alert2' ? world.alert2Tex : world.mapTex;
    world.heldPhone.position.set(st.phoneState.pos[0], st.phoneState.pos[1], st.phoneState.pos[2]);
    world.heldPhone.lookAt(camera.position);
    world.heldPhone.rotateZ((st.phoneState.vib || 0) * 5.0);
    phoneGlow.position.set(st.phoneState.pos[0], st.phoneState.pos[1], st.phoneState.pos[2] - 0.15);
    phoneGlow.intensity = st.phoneState.mode === 'map1bar' ? 0.85 : 1.35;
  }

  // 4. Every-Frame Biomechanical Character Rig Update (Distance-Locked Stride, ZERO Sliding!)
  const fExact = t * 30.0;
  for (const [key, rig] of Object.entries(charRigs)) {
    const cs = st.chars[key];
    if (!cs || !cs.visible) {
      rig.group.visible = false;
      continue;
    }
    rig.group.visible = true;
    const jx = cs.shake ? Math.sin(t * 44) * cs.shake : 0;
    const jy = cs.shake ? Math.cos(t * 39) * cs.shake * 0.5 : 0;
    rig.group.position.set(cs.pos[0] + jx, Math.max(0.0, cs.pos[1] + jy), cs.pos[2]);

    const dx = st.camPos[0] - cs.pos[0];
    const dz = st.camPos[2] - cs.pos[2];
    rig.group.rotation.set(0, Math.atan2(dx, dz) + (cs.headShakeYaw || 0), 0);
    rig.card.scale.x = cs.flipX ? -1 : 1;
    rig.mat.color.set(st.cardTint);

    // Painful takedown / hit-by-car: roll the card over and slam it down onto the asphalt.
    const fallU = cs.fallU || 0;
    if (fallU > 0.001) {
      const fu = fallU * fallU * (3 - 2 * fallU);
      rig.card.rotation.z = -1.46 * fu;
      rig.card.position.y = rig.baseCardY - (rig.baseCardY - 0.40) * fu;
      rig.shadow.scale.set(1 + 0.7 * fu, 0.68 * (1 - 0.45 * fu), 1);
    } else {
      rig.card.rotation.z = 0;
      rig.card.position.y = rig.baseCardY;
      rig.shadow.scale.set(1, 0.68, 1);
    }

    rig.shadow.visible = !(z === 'back' && cs.pos[2] < -16.4);

    const idl = idle(fExact, rig.roleCfg.seed);
    const blk = blinkAt(Math.round(fExact), rig.roleCfg.seed);
    // Exact distance-locked stride phase (`cs.dist` = full 2-step cycles traveled!)
    const stepVal = cs.dist > 0 ? ((cs.dist % 1) + 0.0002) : 0;
    const spkVal = cs.talk || 0;
    const bRate = cs.isRunning ? 1.35 : 0.52;
    const breathWave = Math.sin(t * Math.PI * 2 * bRate + rig.roleCfg.seed);
    const jawAnim = rig.roleCfg.infected
      ? (cs.dist === 0 && !cs.talk ? 0.35 : (0.58 + 0.42 * Math.abs(Math.sin(t * 7.2 + rig.roleCfg.seed))))
      : 0;

    rig.ctx.clearRect(0, 0, rig.cw, rig.ch);
    if (cs.view === 'back' || cs.view === 'backFull') {
      rickBackPOV(rig.pen, rig.roleKey, {
        headTilt: idl.headTilt,
        bob: idl.bob,
        step: stepVal,
        isRunning: !!cs.isRunning,
        breath: breathWave,
        fullBody: cs.view === 'backFull',
        hasBackpack: !!cs.hasBackpack,
      });
    } else {
      let Larm = 'hang', Rarm = 'hang';
      if (cs.armPose === 'phoneBuzz')      { Larm = 'hang'; Rarm = 'phoneBuzz'; }
      else if (cs.armPose === 'flashlight'){ Larm = 'hang'; Rarm = 'flashlight'; }
      else if (cs.armPose === 'pullShutter'){ Larm = 'pullShutter'; Rarm = 'pullShutter'; }
      else if (cs.armPose === 'lockDoor')  { Larm = 'hang'; Rarm = 'lockDoor'; }
      else if (cs.armPose === 'plead')     { Larm = 'hang'; Rarm = 'plead'; }
      else if (cs.armPose === 'shush')     { Larm = 'hang'; Rarm = 'shush'; }
      else if (cs.armPose === 'grabSleeve'){ Larm = 'grabSleeve'; Rarm = 'grabSleeve'; }
      else if (rig.roleCfg.infected)       { Larm = 'zombieReach'; Rarm = 'zombieReach'; }
      else if (cs.isRunning)               { Larm = 'run'; Rarm = 'run'; }
      else if (cs.shake > 0.006)           { Larm = 'shake'; Rarm = 'shake'; }

      const facing = cs.view === 'side' ? 0.65 : (cs.view === 'threeQuarter' ? 0.34 : 0.0);
      rickChar(rig.pen, rig.roleKey, {
        expr: cs.expr || 'calm_work',
        blink: blk,
        facing,
        L: Larm,
        R: Rarm,
        tilt: idl.tilt * 0.5,
        headTilt: idl.headTilt,
        bob: idl.bob,
        step: stepVal,
        isRunning: !!cs.isRunning,
        reverseWalk: !!cs.reverseWalk,
        crouchSit: !!cs.crouchSit,
        hasBackpack: !!cs.hasBackpack,
        breath: breathWave,
        speakOpen: spkVal,
        phoneBuzz: cs.phoneBuzz || 0,
        shakeAmt: cs.shake ? t : 0,
        jawAnim,
      });
    }
    rig.tex.needsUpdate = true;
  }

  // 5. Cartoon FX Cards
  fxMesh.visible = false;
  if (st.fx.swerveBurst >= 0) {
    fxMesh.visible = true;
    fxMesh.scale.setScalar(1.55);
    fxMesh.position.set(2.8, 1.15, 15.2);
    fxMesh.lookAt(camera.position);
    fxCtx.clearRect(0, 0, 600, 600);
    fxRing(fxPen, st.fx.swerveBurst);
    fxBurst(fxPen, st.fx.swerveBurst, '#ffcf48', 10, 40, 210);
    fxTex.needsUpdate = true;
  } else if (st.fx.glassSlam >= 0) {
    fxMesh.visible = true;
    fxMesh.scale.setScalar(0.78);
    fxMesh.position.set(0.55, 1.38, 7.45);
    fxMesh.lookAt(camera.position);
    fxCtx.clearRect(0, 0, 600, 600);
    fxRing(fxPen, st.fx.glassSlam);
    fxTex.needsUpdate = true;
  } else if (st.fx.doorKnock >= 0) {
    fxMesh.visible = true;
    fxMesh.scale.setScalar(0.68);
    fxMesh.position.set(2.80, 1.45, -16.15);
    fxMesh.lookAt(camera.position);
    fxCtx.clearRect(0, 0, 600, 600);
    fxRing(fxPen, st.fx.doorKnock);
    fxTex.needsUpdate = true;
  }

  composer.render(1 / 30);
  return glCanvas;
}

window.__renderAt = renderAt;
window.__evaluateScene = evaluateScene;
window.__scene = scene;
window.__camera = camera;
window.__rawRender = () => composer.render(1 / 30);
window.__world = () => world;
window.__outCanvas = outCanvas;
window.__glCanvas = glCanvas;
window.__captureBatch = function(startFrame, count, fps = 30) {
  const out = new Array(count);
  for (let i = 0; i < count; i++) {
    const c = renderAt((startFrame + i) / fps);
    out[i] = c.toDataURL('image/jpeg', 0.92).split(',')[1];
  }
  return out;
};
window.__SHOTS = SHOTS;
window.__ready = true;

renderAt(parseFloat(params.get('t') || '2.0'));
