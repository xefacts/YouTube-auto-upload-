// ============================================================================
// STORY.JS — "The Fire Lookout" — shot list + pure state functions of time.
// 59 hard cuts over 146.5s, Zack-style grammar: vary size/angle every cut,
// macro detail shots, green=reveal / red=danger annotations, no lip-sync.
// ============================================================================
import * as THREE from 'three';

export const DURATION = 146.5;

const clamp01 = (v) => Math.max(0, Math.min(1, v));
const lerp = (a, b, u) => a + (b - a) * u;
const ease = (u) => u * u * (3 - 2 * u);
const easeIn = (u) => u * u;
const easeOut = (u) => 1 - (1 - u) * (1 - u);

// camera positions are world-space; INT shots sit at FLOOR height (7.5)
const F = 7.5; // cab floor world height

// MACRO stage slots: stage groups live at x=40, y=2, z in {0,6,12,18,24,30}
const MS = { cctv: 0, notebook: 6, warning: 12, phoneMsg: 18, phonePhoto: 24, nosvc: 30 };
const macroCam = (slot, dist = 8.5, fov = 44, drift = 0.06) => ({
  pos: [40, 2, slot + dist], look: [40, 2, slot - drift], fov, macro: true,
});

// helper for interior cams (relative x, y above floor, z -> world)
const icam = (x, y, z, a, b, c, d) => {
  if (d !== undefined) return { pos: [x, F + y, z], look: [a, F + b, c], fov: d };
  return { pos: [x, F + y, z], look: [x, F + y - 0.05, z - 2], fov: a ?? 42 };
};
const ecam = (x, y, z, lx, ly, lz, fov = 42) => ({ pos: [x, y, z], look: [lx, ly, lz], fov });

// ---------------------------------------------------------------- SHOTS
// each: [t0, t1, cam, move]
// move: 'push' (slow dolly in), 'pull', 'panL', 'panR', 'tiltU', 'tiltD', 'hold', 'drift'
export const SHOTS = [
  // ---- HOOK: security footage (generated image asset + HUD) ----
  [0.00, 3.30, macroCam(MS.cctv, 9.4, 46), 'push'],
  [3.30, 6.80, macroCam(MS.cctv, 7.4, 44), 'push'],
  // ---- "but that came later / three weeks earlier" ----
  [6.80, 9.10, ecam(-14, 4.5, -22, -2, 9, -4, 48), 'panR'],
  [9.10, 11.30, ecam(-8, 2.2, -9.5, -2, 1.2, -13, 40), 'panL'],
  [11.30, 12.90, ecam(6.5, 1.2, 7.5, 0, 11, 0, 46), 'tiltU'],
  [12.90, 14.70, ecam(-4.6, 1.7, 5.6, -2.6, 8.2, 0.4, 38), 'push'],
  // ---- pay / money ----
  [14.70, 16.60, icam(-1.25, 1.05, 1.95, 40), 'push'],
  [16.60, 18.80, icam(-0.3, 1.5, 2.6, -1.0, 1.1, 0.6, 34), 'hold'],
  // ---- previous guard gone ----
  [18.80, 21.20, icam(0.55, 1.15, 1.35, 34), 'push'],
  [21.20, 24.50, icam(1.4, 1.7, 0.4, -1.5, 1.0, -1.8, 46), 'panL'],
  [24.50, 27.70, icam(-0.2, 1.5, 2.3, -1.25, 1.15, 0.4, 34), 'hold'],
  // ---- manager warning ----
  [27.70, 30.60, icam(0.4, 1.45, 0.9, -1.9, 1.1, -1.3, 44), 'panL'],
  [30.60, 32.50, icam(-1.05, 1.05, 0.7, 30), 'push'],
  [32.50, 34.90, icam(-1.7, 1.6, -0.2, -1.8, 1.35, -1.4, 30), 'push'],
  [34.90, 37.70, icam(-0.2, 1.0, 1.75, 32), 'push'],
  // ---- manager leaves / night falls ----
  [37.70, 40.80, ecam(7.5, 9.6, 6.0, -4, 8.6, -6, 46), 'panL'],
  [40.80, 43.00, ecam(-14, 3.2, 18, 0, 10.2, 0, 46), 'push'],
  // ---- 11:47 radio crackle ----
  [43.00, 44.80, icam(2.05, 2.0, -1.6, 34), 'push'],
  [44.80, 47.70, icam(0.05, 0.98, 1.85, 30), 'push'],
  [47.70, 49.80, icam(-0.15, 1.35, 2.2, -0.6, 1.15, 0.9, 30), 'hold'],
  // ---- notebook ----
  [49.80, 52.30, icam(0.15, 1.35, 1.9, 34), 'push'],
  [52.30, 54.90, macroCam(MS.notebook, 8.8, 40), 'push'],
  [54.90, 57.10, macroCam(MS.notebook, 6.6, 34), 'push'],
  [57.10, 58.70, macroCam(MS.notebook, 7.6, 38), 'panR'],
  [58.70, 61.70, macroCam(MS.notebook, 6.0, 32), 'pull'],
  [61.70, 65.30, macroCam(MS.warning, 8.8, 42), 'push'],
  // ---- voice speaks again (RED) ----
  [65.30, 67.10, icam(0.2, 1.3, 2.0, -0.55, 1.05, 1.3, 32), 'hold'],
  [67.10, 69.80, icam(0.1, 0.97, 1.8, 30), 'push'],
  [69.80, 72.20, icam(-0.2, 0.95, 1.7, 26), 'push'],
  [72.20, 73.90, icam(-0.75, 1.45, 2.45, -0.85, 1.2, 0.7, 26), 'push'],
  [73.90, 76.50, icam(2.2, 2.1, 1.4, -1.4, 1.0, 0.2, 52), 'panL'],
  // ---- knocks beneath the tower ----
  [76.50, 79.20, ecam(0.5, 0.9, 8.8, 0, 2.6, 0, 48), 'push'],
  // ---- flashlight / figure outside ----
  [79.20, 82.30, { pos: [0.8, 8.9, 3.2], look: [0.4, 0.9, 5.6], fov: 42 }, 'tiltD'],
  [82.30, 83.90, ecam(1.5, 1.4, 9.8, 0.2, 1.0, 5.4, 38), 'push'],
  [83.90, 86.50, ecam(2.2, 1.5, 8.2, 0.4, 1.2, 5.2, 36), 'panL'],
  [86.50, 88.20, ecam(1.4, 1.6, 7.0, 0.5, 1.4, 4.9, 32), 'push'],
  [88.20, 89.60, { pos: [40, 2.2, 41.2], look: [40, 2.0, 40.05], fov: 34 }, 'push'],   // office flashback
  [89.60, 92.70, ecam(0.9, 1.7, 6.4, 0.6, 1.5, 4.8, 28), 'push'],
  // ---- phone / no signal / figure gone ----
  [92.70, 94.60, { pos: [1.0, F + 1.2, 1.8], look: [1.35, F + 0.95, 1.25], fov: 36 }, 'push'],
  [94.60, 95.70, macroCam(MS.nosvc, 8.0, 38), 'push'],
  [95.70, 99.10, { pos: [0.8, 8.9, 3.2], look: [0.4, 0.5, 5.8], fov: 42 }, 'hold'],
  // ---- staircase ----
  [99.10, 101.10, icam(0.6, 1.3, -0.4, 1.9, 0.7, 0.9, 40), 'push'],
  [101.10, 103.90, icam(0.4, 1.1, -0.9, 1.9, 0.2, 0.9, 38), 'push'],
  [103.90, 105.60, icam(1.5, 0.55, 0.6, 1.85, 0.1, 0.75, 36), 'push'],
  [105.60, 107.00, icam(2.5, 0.35, 1.8, 1.85, 0.05, 0.9, 30), 'push'],
  [107.00, 110.10, icam(-0.3, 1.5, 2.3, 0.4, 1.2, 0.4, 30), 'hold'],
  // ---- phone buzz / message / photo ----
  [110.10, 111.60, icam(1.9, 1.15, 1.9, 1.35, 0.9, 1.25, 34), 'push'],
  [111.60, 113.80, macroCam(MS.phoneMsg, 8.8, 42), 'push'],
  [113.80, 116.40, macroCam(MS.phoneMsg, 7.2, 36), 'panR'],
  [116.40, 118.30, macroCam(MS.phonePhoto, 10.0, 44), 'push'],
  [118.30, 121.50, macroCam(MS.phonePhoto, 7.8, 36), 'push'],
  [121.50, 123.50, macroCam(MS.phonePhoto, 6.2, 30), 'push'],
  [123.50, 126.50, macroCam(MS.phonePhoto, 5.2, 26), 'push'],
  [126.50, 130.00, macroCam(MS.phoneMsg, 5.4, 28), 'panD'],
  // ---- footsteps stop / knocking ----
  [130.00, 132.50, icam(-0.9, 1.3, -0.2, -2.44, 1.05, -0.6, 40), 'push'],
  [132.50, 136.90, icam(-0.7, 1.15, 0.15, -2.44, 1.05, -0.6, 36), 'hold'],
  // ---- radio switches on / realization / end ----
  [136.90, 139.50, icam(0.0, 0.95, 1.75, 28), 'push'],
  [139.50, 142.30, icam(2.3, 2.2, 1.5, -1.3, 1.0, 0.3, 52), 'panR'],
  [142.30, 146.50, ecam(-15, 4.0, -19, 0, 10.6, 0, 46), 'pull'],
];

// ---------------------------------------------------------------- SKY / LIGHT KEYS
// [t, bg, fog, sun, moon, amb]
const LIGHT_KEYS = [
  [0.0, '#0a0f14', '#0a0f14', 0.0, 0.0, 0.30],
  [6.8, '#0a0f14', '#0a0f14', 0.0, 0.0, 0.30],
  [7.2, '#2a3550', '#2a3550', 0.15, 0.0, 0.42],
  [9.2, '#5a6a80', '#5a6a80', 0.75, 0.0, 0.55],
  [13.0, '#7a7a6a', '#6a6a5a', 0.9, 0.0, 0.60],
  [18.9, '#4a4a50', '#4a4a50', 0.45, 0.0, 0.50],
  [22.0, '#333a4a', '#333a4a', 0.22, 0.05, 0.45],
  [28.0, '#232a3c', '#232a3c', 0.12, 0.12, 0.42],
  [38.0, '#1a2130', '#1a2130', 0.05, 0.25, 0.38],
  [41.2, '#0e1420', '#0e1420', 0.0, 0.62, 0.30],
  [95.0, '#0e1420', '#0e1420', 0.0, 0.62, 0.30],
  [130.0, '#0c1118', '#0c1118', 0.0, 0.55, 0.28],
  [142.5, '#0c1118', '#0c1118', 0.0, 0.5, 0.26],
  [146.5, '#05070a', '#05070a', 0.0, 0.2, 0.15],
];
export function lightState(t) {
  let i = 0;
  while (i < LIGHT_KEYS.length - 2 && t >= LIGHT_KEYS[i + 1][0]) i++;
  const a = LIGHT_KEYS[i], b = LIGHT_KEYS[i + 1];
  const u = ease(clamp01((t - a[0]) / Math.max(0.001, b[0] - a[0])));
  const mix = (c1, c2) => '#' + new THREE.Color(c1).lerp(new THREE.Color(c2), u).getHexString();
  return {
    bg: mix(a[1], b[1]),
    fog: mix(a[2], b[2]),
    sun: lerp(a[3], b[3], u),
    moon: lerp(a[4], b[4], u),
    amb: lerp(a[5], b[5], u),
    night: clamp01((t - 38.0) / 3.2), // 1.0 from ~41.2 onward
    fade: clamp01((t - 143.3) / 2.9), // end fade to black
  };
}

// ---------------------------------------------------------------- CHARACTERS
// world positions
const DOOR_W = [-1.7, F, -1.25];      // Daniel near door (inside)
const DESK_W = [-1.25, F, 0.55];      // Daniel at desk standing
const CHAIR_W = [-1.25, F, 0.35];
const WINDOW_W = [-1.05, F, 1.55];
const WALL_W = [0.35, F, -0.9];
const STAIR_W = [1.3, F, 0.35];

export function charStates(t) {
  const d = { vis: false, x: 0, y: F, z: 0, ry: 0, mode: 'stand', expr: 'neutral' };
  const m = { vis: false, x: 0, y: F, z: 0, ry: 0, mode: 'stand', expr: 'neutral' };
  const fig = { vis: false, x: 0, y: 0, z: 0, ry: 0, mode: 'stand' };

  // --- Daniel exterior arrival ---
  if (t >= 12.9 && t < 14.7) {
    d.vis = true; d.x = -3.4; d.z = 5.4; d.y = 0;
    d.ry = Math.PI / 2 - 0.5; d.mode = 'stand'; d.expr = 'neutral';
  }
  // interior dusk
  if (t >= 14.7 && t < 18.8) {
    d.vis = true;
    if (t < 16.6) { d.x = -1.25; d.z = 1.4; d.ry = Math.PI + 0.25; d.mode = 'stand'; d.expr = 'smile'; }
    else { d.x = -1.05; d.z = 1.6; d.ry = Math.PI + 0.15; d.mode = 'stand'; d.expr = 'smile'; }
  }
  // previous guard beats: Daniel off-frame mostly
  if (t >= 24.5 && t < 27.7) {
    d.vis = true; d.x = -0.2; d.z = 1.2; d.ry = Math.PI - 0.6;
    d.mode = 'shrug'; d.expr = 'smile';
  }
  // manager warning two-shot
  if (t >= 27.7 && t < 32.5) {
    d.vis = true; d.x = -1.15; d.z = -0.5; d.ry = Math.PI + 0.75;
    d.mode = 'stand'; d.expr = 'worried';
  }
  // manager closeup (32.5-34.9): Daniel out of frame
  if (t >= 34.9 && t < 37.7) {
    d.vis = true; d.x = -0.55; d.z = 1.3; d.ry = Math.PI + 0.5; d.mode = 'stand'; d.expr = 'neutral';
  }
  // catwalk watch truck leave
  if (t >= 37.7 && t < 40.8) {
    d.vis = true; d.x = -2.6; d.z = 2.3; d.y = F + 0.12; d.ry = Math.PI * 0.92;
    d.mode = 'stand'; d.expr = 'neutral';
  }
  // radio beats: Daniel at desk
  if (t >= 44.8 && t < 52.3) {
    d.vis = true;
    if (t < 47.7) { d.x = -0.55; d.z = 0.9; d.ry = Math.PI + 0.45; d.mode = 'stand'; d.expr = 'neutral'; }
    else if (t < 49.8) { d.x = -0.45; d.z = 1.0; d.ry = Math.PI + 0.4; d.mode = 'stand'; d.expr = 'worried'; }
    else { d.x = 0.1; d.z = 1.15; d.ry = Math.PI + 0.35; d.mode = 'reach-down'; d.expr = 'worried'; }
  }
  // 65.3-67.1 looks at radio
  if (t >= 65.3 && t < 67.1) {
    d.vis = true; d.x = -0.5; d.z = 1.05; d.ry = Math.PI + 0.4; d.mode = 'stand'; d.expr = 'worried';
  }
  // 72.2-73.9 frozen terrified
  if (t >= 72.2 && t < 73.9) {
    d.vis = true; d.x = -0.4; d.z = 1.5; d.ry = Math.PI + 0.3; d.mode = 'stand'; d.expr = 'shocked';
  }
  // 73.9-76.5 wide (tiny at desk)
  if (t >= 73.9 && t < 76.5) {
    d.vis = true; d.x = -1.25; d.z = 0.5; d.ry = Math.PI + 0.3; d.mode = 'stand'; d.expr = 'scared';
  }
  // 107-110.1 dread listening
  if (t >= 107.0 && t < 110.1) {
    d.vis = true; d.x = 0.3; d.z = 0.9; d.ry = Math.PI + 0.25; d.mode = 'stand'; d.expr = 'scared';
  }
  // 92.7-94.6 reaches for phone
  if (t >= 92.7 && t < 94.6) {
    d.vis = true; d.x = 0.75; d.z = 0.9; d.ry = Math.PI + 0.1; d.mode = 'reach-down'; d.expr = 'worried';
  }
  // 99.1-101.1 backed to wall
  if (t >= 99.1 && t < 101.1) {
    d.vis = true; d.x = 0.55; d.z = -1.35; d.ry = -Math.PI / 2 + 0.4; d.mode = 'cower'; d.expr = 'scared';
  }
  // 139.5-142.3 horrified realization
  if (t >= 139.5 && t < 142.3) {
    d.vis = true; d.x = 0.5; d.z = 0.2; d.ry = Math.PI + 0.9; d.mode = 'cower'; d.expr = 'shocked';
  }

  // --- Manager: doorway handoff (27.7-34.9), outside leaving (37.7-40.8) ---
  if (t >= 27.7 && t < 34.9) {
    m.vis = true;
    m.x = -2.05; m.z = -1.15; m.ry = -Math.PI / 2 + 0.55;
    m.mode = (t >= 28.6 && t < 33.4) ? 'point' : 'stand';
    m.expr = t < 32.5 ? 'neutral' : 'worried';
  }
  if (t >= 37.7 && t < 40.8) {
    m.vis = true; m.x = -14 - (t - 37.7) * 2.2; m.y = 0; m.z = -13; m.ry = -Math.PI / 2;
    m.mode = 'walk';
  }

  // --- The Figure (doppelganger outside) ---
  if (t >= 76.5 && t < 99.1) {
    fig.vis = true;
    if (t < 79.2) { fig.x = -1.2; fig.z = 3.2; fig.ry = Math.PI + 0.2; }        // barely visible far
    else if (t < 83.9) { fig.x = 0.4; fig.z = 5.6; fig.ry = Math.PI; }          // in beam pool
    else if (t < 86.5) { const u = ease((t - 83.9) / 2.6); fig.x = lerp(0.4, 1.1, u); fig.z = lerp(5.6, 4.6, u); fig.ry = Math.PI - 0.15; fig.mode = 'walk'; }
    else if (t < 88.2) { fig.x = 1.1; fig.z = 4.6; fig.ry = Math.PI - 0.1; }
    else if (t < 92.7) { fig.x = 1.0; fig.z = 4.9; fig.ry = Math.PI - 0.12; }
    // 95.7+ GONE
  }
  return { d, m, fig };
}

// ---------------------------------------------------------------- PROPS / FX
export function propStates(t) {
  const radioVoice = (t >= 44.8 && t < 50.0) || (t >= 67.1 && t < 73.9) || (t >= 136.9 && t < 142.5);
  const radioRed = (t >= 67.1 && t < 73.9) || (t >= 136.9 && t < 142.5);
  const knocks3 = t >= 76.5 && t < 79.2;
  const knocking = t >= 132.5 && t < 136.9;
  return {
    // truck: arrival (9.1-11.3), leaving (37.7-40.8)
    truckX: t < 20 ? lerp(-28, -3.5, ease(clamp01((t - 9.1) / 2.2))) : lerp(-3.5, -22, ease(clamp01((t - 37.7) / 3.1))),
    truckVis: (t >= 9.1 && t < 11.3) || (t >= 37.7 && t < 40.8),
    // radio dial: amber normally, red + pulse when voice
    radioOn: t >= 40.8,
    radioVoice, radioRed,
    // notebook
    nbOpen: t >= 52.3,
    nbInHand: t >= 49.8 && t < 52.3,
    // lantern warm at night, dimmer pre-night
    lantern: 0.55 + 0.45 * clamp01((t - 16) / 4),
    // phone
    phoneScreenOn: (t >= 110.1 && t < 130.0),
    phoneScreen: 'msg', // switched per-shot in main via shot id
    phoneBuzz: t >= 110.1 && t < 111.6,
    // clock only shows 11:47 (static)
    // door knock shake
    knocking,
    knocks3,
    // hatch danger glow
    belowGlow: t >= 101.1 && t < 110.1 ? ease(clamp01((t - 101.1) / 2.4)) * (0.7 + 0.3 * Math.sin(t * 6)) : (t >= 130 && t < 142 ? 0.5 + 0.4 * Math.sin(t * 7) : 0),
    // flashlight beam
    beam: t >= 79.2 && t < 99.1 ? 0.34 + 0.05 * Math.sin(t * 1.3) : 0,
    // CCTV hud + grain
    cctvHud: t < 6.8 ? 0.85 : 0,
    cctvGlitch: t < 6.8 ? (Math.sin(t * 9.1) > 0.86 || (t > 5.9 && t < 6.1)) : false,
    // red frame pulse on warning page
    warnRed: t >= 61.7 && t < 65.3 ? 0.25 + 0.2 * Math.sin(t * 5.2) : 0,
    // green reveal outline on jacket (flashback)
    jacketOutline: t >= 88.2 && t < 89.6 ? 0.55 : 0,
    // green outline on figure (86.5-88.2)
    figOutline: t >= 86.5 && t < 88.2 ? 0.55 : 0,
    // red outline on photo figure (118.3-126.5)
    photoRed: t >= 118.3 && t < 126.5 ? 0.4 + 0.25 * Math.sin(t * 4.4) : 0,
    // mist outside at night
    mist: clamp01((t - 41.0) / 3) * 0.3,
    // interior door open ajar early (21.2-24.5 beat) — door slightly open till manager leaves
    doorOpen: t >= 18.8 && t < 34.9 ? 0.55 : 0,
  };
}

// ---------------------------------------------------------------- evaluate
export function evaluateScene(t) {
  return {
    light: lightState(t),
    chars: charStates(t),
    props: propStates(t),
    shot: shotAt(t),
  };
}

export function shotAt(t) {
  let i = 0;
  while (i < SHOTS.length - 1 && t >= SHOTS[i + 1][0]) i++;
  const [t0, t1, cam, move] = SHOTS[i];
  return { i, t0, t1, cam, move, u: clamp01((t - t0) / Math.max(0.001, t1 - t0)) };
}
