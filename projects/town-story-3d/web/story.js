// ============================================================================
// STORY.JS — "THE TOWN THAT COUNTS TO TEN" shot list + deterministic director
// 80.0s @ 30fps (2400 frames), 24 fast-paced shots (avg 3.3s).
// evaluateScene(t) is a PURE function of time: same frame -> same pixels.
// ============================================================================

const clamp01 = (v) => Math.max(0, Math.min(1, v));
const ease = (u) => u * u * u * (u * (u * 6 - 15) + 10); // smootherstep
const easeIn = (u) => u * u;
const easeOut = (u) => 1 - (1 - u) * (1 - u);
const lerp = (a, b, u) => a + (b - a) * u;
const lerp3 = (a, b, u) => [lerp(a[0], b[0], u), lerp(a[1], b[1], u), lerp(a[2], b[2], u)];

export const DURATION = 80.0;
export const FPS = 30;
export const TOTAL_FRAMES = 2400;

// ------------------------------------------------------------------ shots
// p0/p1: camera path; l0/l1: lookAt path; fov in degrees; shk: shake amp
export const SHOTS = [
  // ---- ACT 1 · THE RULE (day) ----
  { id: 0, t0: 0.0, t1: 3.2, p0: [-16, 26, -26], p1: [-4, 17, -14], l0: [0, 2, 0], l1: [4, 2, 2], fov: 46, ez: 'inout' },            // aerial town + title
  { id: 1, t0: 3.2, t1: 6.2, p0: [-8, 2.7, -3.2], p1: [-2, 1.75, -2.5], l0: [4, 1.8, 2.5], l1: [7, 1.65, 2.0], fov: 42, ez: 'inout' },  // street tracking + slow crane down
  { id: 2, t0: 6.2, t1: 10.0, p0: [3.0, 1.8, -2.2], p1: [7.5, 1.7, -1.0], l0: [10, 1.4, 4.4], l1: [13.5, 1.4, 4.6], fov: 44, ez: 'inout' }, // kid+mom arrive w/ box
  { id: 3, t0: 10.0, t1: 13.6, p0: [14.4, 1.65, 6.1], p1: [13.8, 1.58, 4.7], l0: [14, 1.55, 7.5], l1: [14, 1.62, 7.4], fov: 26, ez: 'inout' },  // Finch warns: slow dolly-in
  { id: 4, t0: 13.6, t1: 16.2, p0: [15.8, 1.6, 4.6], p1: [15.9, 1.62, 4.4], l0: [15.3, 1.5, 5.2], l1: [15.3, 1.55, 5.1], fov: 26, ez: 'inout' }, // kid dismissive smile
  // ---- ACT 2 · DUSK PANIC ----
  { id: 5, t0: 16.2, t1: 19.4, p0: [1, 1.35, -6.0], p1: [6.5, 1.15, -4.4], l0: [8, 1.4, 2], l1: [13.5, 1.2, 3.6], fov: 50, shk: 0.014 },  // dusk RUN: low fast lateral track
  { id: 6, t0: 19.4, t1: 22.2, p0: [17.5, 1.5, 4.0], p1: [17.9, 1.45, 3.6], l0: [18, 1.3, 7.6], l1: [18, 1.35, 7.6], fov: 34, shk: 0.010 },  // kid door SLAMS
  { id: 7, t0: 22.2, t1: 25.0, p0: [-7, 1.8, -2.8], p1: [-3.5, 2.0, -2.2], l0: [-2, 4.2, -5.2], l1: [2, 4.6, -5.2], fov: 46 },  // streetlights flicker ON
  // ---- ACT 3 · THE COUNT ----
  { id: 8, t0: 25.0, t1: 28.4, p0: [17.35, 1.62, 6.6], p1: [17.5, 1.58, 6.7], l0: [18.02, 1.52, 8.0], l1: [18.02, 1.5, 8.0], fov: 22 },  // kid peek in door gap
  { id: 9, t0: 28.4, t1: 31.2, p0: [17.9, 1.72, 5.6], p1: [16.7, 1.66, 5.15], l0: [-2, 1.2, 0], l1: [4, 1.1, 0], fov: 40, roll: 0.035 },  // empty street POV + slight dutch
  { id: 10, t0: 31.2, t1: 35.0, p0: [-9, 1.4, -6.0], p1: [-7.5, 1.5, -5.0], l0: [8, 2.4, 0], l1: [9, 3.0, 0], fov: 42, shk: 0.016 },  // "TEN NINE EIGHT" lamp flare
  { id: 11, t0: 35.0, t1: 39.2, p0: [10.2, 1.5, 1.4], p1: [11.15, 1.42, 0.9], l0: [12, 1.35, 2.2], l1: [12.25, 1.28, 2.35], fov: 32, shk: 0.012, roll: 0.055 }, // Finch stumbles + dutch tilt
  { id: 12, t0: 39.2, t1: 43.0, p0: [16.0, 1.8, -4.2], p1: [14.5, 1.6, -3.4], l0: [12, 2.2, 1.5], l1: [12, 2.4, 1.8], fov: 40, shk: 0.010 },  // "SEVEN SIX FIVE" lamps TURN
  { id: 13, t0: 43.0, t1: 46.2, p0: [17.3, 1.6, 6.6], p1: [17.42, 1.57, 6.65], l0: [18.02, 1.5, 8.0], l1: [18.02, 1.48, 8.0], fov: 21 },  // kid shocked peek
  { id: 14, t0: 46.2, t1: 49.6, p0: [13.6, 1.05, 3.6], p1: [12.6, 1.02, 3.0], l0: [12, 1.35, 2.2], l1: [12.1, 1.4, 2.3], fov: 30 },  // "FOUR THREE" low push
  { id: 15, t0: 49.6, t1: 52.6, p0: [13.2, 1.52, 3.1], p1: [12.45, 1.40, 2.5], l0: [12.1, 1.55, 2.2], l1: [12.15, 1.64, 2.26], fov: 20, roll: -0.03 },  // "TWO": slow creep-in on the smile
  { id: 16, t0: 52.6, t1: 53.7, p0: [12.4, 1.5, 2.7], p1: [12.4, 1.5, 2.7], l0: [12.1, 1.5, 2.2], l1: [12.1, 1.5, 2.2], fov: 24, shk: 0.05 }, // "ONE" — FLASH
  { id: 17, t0: 53.7, t1: 56.6, p0: [14.2, 1.35, 2.2], p1: [13.4, 1.25, 2.1], l0: [12.6, 0.5, 2.0], l1: [12.6, 0.4, 2.0], fov: 34 },  // aftermath: hat + cane
  // ---- ACT 4 · THE NUMBERS (morning) ----
  { id: 18, t0: 56.6, t1: 61.6, p0: [13.8, 1.5, 4.6], p1: [13.6, 1.4, 4.2], l0: [12.6, 0.7, 3.6], l1: [13.6, 1.3, 5.4], fov: 38 },  // kid finds hat, looks up
  { id: 19, t0: 61.6, t1: 65.6, p0: [8.6, 1.6, 3.6], p1: [13.2, 1.6, 3.6], l0: [8.4, 1.9, 7.8], l1: [14.0, 1.9, 7.8], fov: 40 },  // tracking: 143 145 147
  { id: 20, t0: 65.6, t1: 68.8, p0: [16.6, 1.7, 3.8], p1: [16.8, 1.65, 3.9], l0: [17.4, 1.4, 5.6], l1: [17.9, 1.35, 6.4], fov: 36 },  // turns corner — stops
  { id: 21, t0: 68.8, t1: 72.0, p0: [18.75, 1.5, 5.3], p1: [18.12, 1.44, 4.85], l0: [18, 1.7, 7.86], l1: [18, 1.76, 7.86], fov: 20 },  // plate 149: long slow creep
  { id: 22, t0: 72.0, t1: 76.0, p0: [-8, 22, -22], p1: [2, 15, -12], l0: [8, 1, 0], l1: [8, 1, 0], fov: 48 },  // aerial reveal: EVERY door numbered
  { id: 23, t0: 76.0, t1: 80.0, p0: [0, 2, 8], p1: [0, 2, 8], l0: [0, 2, 0], l1: [0, 2, 0], fov: 40 },  // end card
];

export function getShotAt(t) {
  for (const s of SHOTS) if (t >= s.t0 && t < s.t1) return s;
  return SHOTS[SHOTS.length - 1];
}

// ------------------------------------------------------------- sky/lights
// key times: [t, bg, fog, sunI, sunCol, lampOn]
const SKY_KEYS = [
  [0.0, '#6fc3f7', '#c9e8fb', 1.2, '#fff4dd', 0],
  [14.0, '#6fc3f7', '#c9e8fb', 1.2, '#fff4dd', 0],
  [17.5, '#eb9a58', '#e8b088', 0.62, '#ffb066', 0],
  [21.5, '#2b3160', '#3a4160', 0.10, '#8899cc', 1],
  [24.0, '#10142e', '#1a2038', 0.16, '#9aa8d8', 1],
  [53.7, '#0d1128', '#171d33', 0.16, '#9aa8d8', 1],
  [56.6, '#8fd4f9', '#c9ecfb', 1.1, '#fff2d8', 0],
  [72.0, '#7cc4f2', '#c9e8fb', 1.1, '#ffe9c4', 0],
  [76.0, '#3a4468', '#4a5474', 0.22, '#c4b28a', 0.6],
  [80.0, '#22283f', '#333a52', 0.05, '#c4b28a', 1],
];
function hexLerp(a, b, u) {
  const pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16);
  const r = Math.round(lerp((pa >> 16) & 255, (pb >> 16) & 255, u));
  const g = Math.round(lerp((pa >> 8) & 255, (pb >> 8) & 255, u));
  const bl = Math.round(lerp(pa & 255, pb & 255, u));
  return (r << 16) | (g << 8) | bl;
}

// ------------------------------------------------------------- characters
// deterministic positions per beat
function charStates(t) {
  const kid = { vis: false, x: 0, z: 0, ry: 0, mode: 'stand', expr: 'neutral' };
  const mom = { vis: false, x: 0, z: 0, ry: 0, mode: 'stand', expr: 'neutral' };
  const finch = { vis: false, x: 0, z: 0, ry: 0, mode: 'stand', expr: 'neutral', talk: false };
  const ex1 = { vis: false, x: 0, z: 0, ry: 0, mode: 'walk', expr: 'neutral' };
  const ex2 = { vis: false, x: 0, z: 0, ry: 0, mode: 'walk', expr: 'neutral' };
  const ex3 = { vis: false, x: 0, z: 0, ry: 0, mode: 'walk', expr: 'neutral' };

  // --- day street life (shots 1) ---
  if (t >= 3.2 && t < 6.2) {
    ex1.vis = true; const u = ease((t - 3.2) / 3.0);
    ex1.x = lerp(-6, 2, u); ex1.z = -4.2; ex1.ry = Math.PI / 2; ex1.mode = 'walk';
    ex2.vis = true; const u2 = ease((t - 3.2) / 3.0);
    ex2.x = lerp(9, 1, u2); ex2.z = -4.6; ex2.ry = -Math.PI / 2; ex2.mode = 'walk';
    ex3.vis = true; ex3.x = lerp(-1, 0.5, ease((t - 3.6) / 2.6)); ex3.z = 4.4; ex3.ry = Math.PI / 2; ex3.mode = 'walk';
  }
  // --- arrival (shot 2) ---
  if (t >= 6.2 && t < 10.0) {
    const u = ease((t - 6.2) / 3.8);
    kid.vis = true; kid.x = lerp(6.5, 12.6, u); kid.z = 4.6; kid.ry = Math.PI / 2; kid.mode = 'walk'; kid.expr = 'smile';
    mom.vis = true; mom.x = lerp(5.6, 11.6, u); mom.z = 4.6; mom.ry = Math.PI / 2; mom.mode = 'walk'; mom.expr = 'neutral';
  }
  // --- finch warning (shot 3) + kid reaction (shot 4) ---
  if (t >= 10.0 && t < 16.2) {
    finch.vis = true; finch.x = 14.0; finch.z = 7.7; finch.ry = Math.PI; finch.expr = 'worried';
    finch.talk = t >= 10.0 && t < 13.4;
    finch.mode = 'stand';
    kid.vis = true; kid.x = 15.3; kid.z = 5.3; kid.ry = -0.5; kid.mode = 'stand';
    kid.expr = t < 13.6 ? 'worried' : 'smile';
    mom.vis = true; mom.x = 16.3; mom.z = 5.5; mom.ry = -0.9; mom.expr = 'neutral'; mom.mode = 'stand';
    if (t >= 10.4 && t < 12.8) { finch.mode = 'point'; }
  }
  // --- dusk panic run (shot 5): everyone sprints home ---
  if (t >= 16.2 && t < 19.4) {
    const u = easeIn((t - 16.2) / 3.2);
    ex1.vis = true; ex1.x = lerp(-4, -14, u); ex1.z = lerp(-3.8, -4.4, u); ex1.ry = -Math.PI / 2; ex1.mode = 'run'; ex1.expr = 'scared';
    ex2.vis = true; ex2.x = lerp(8, 1, u); ex2.z = -4.4; ex2.ry = -Math.PI / 2; ex2.mode = 'run'; ex2.expr = 'scared';
    ex3.vis = true; ex3.x = lerp(2, 9.5, u); ex3.z = lerp(4.4, 5.0, u); ex3.ry = Math.PI / 2; ex3.mode = 'run'; ex3.expr = 'scared';
    mom.vis = true; mom.x = lerp(11.6, 17.2, easeIn((t - 16.2) / 3.2)); mom.z = 4.6; mom.ry = Math.PI / 2; mom.mode = 'run'; mom.expr = 'worried';
    kid.vis = true; kid.x = lerp(12.6, 18.1, easeIn((t - 16.2) / 3.2)); kid.z = 4.7; kid.ry = Math.PI / 2; kid.mode = 'run'; kid.expr = 'worried';
  }
  // --- door slam (shot 6): kid vanishes inside ---
  if (t >= 19.4 && t < 22.2) {
    kid.vis = false; mom.vis = false;
  }
  // --- THE PEEK: kid in his dark doorway, lit by the streetlight ---
  if (t >= 22.2 && t < 53.7) {
    kid.vis = true; kid.x = 18.02; kid.z = 8.35; kid.ry = Math.PI + 0.06;
    kid.mode = 'stand';
    kid.expr = t < 31.2 ? 'worried' : (t < 43.0 ? 'scared' : (t < 49.6 ? 'shocked' : 'shocked'));
  }
  // --- count night: finch on the street ---
  if (t >= 31.2 && t < 53.0) {
    finch.vis = true;
    if (t < 35.0) { // enters, already faltering
      const u = ease((t - 31.2) / 3.8);
      finch.x = lerp(15.5, 12.6, u); finch.z = lerp(4.4, 2.4, u);
      finch.ry = lerp(-2.2, -2.6, u); finch.mode = 'walk'; finch.expr = 'worried';
    } else if (t < 37.6) {
      finch.x = 12.4; finch.z = 2.3; finch.ry = -2.6; finch.mode = 'stumble'; finch.expr = 'scared';
    } else {
      finch.x = 12.15; finch.z = 2.25; finch.ry = -2.7;
      finch.mode = t < 49.6 ? 'stumble' : 'stand';
      finch.expr = t < 49.6 ? 'scared' : 'creepy';
    }
  }
  // finch GONE after the flash
  // --- morning: kid finds the hat (shot 18) ---
  if (t >= 56.6 && t < 61.6) {
    kid.vis = true;
    if (t < 58.4) {
      const u = ease((t - 56.6) / 1.8);
      kid.x = lerp(11.2, 12.5, u); kid.z = lerp(4.6, 3.3, u); kid.ry = lerp(Math.PI / 2, -0.4, u);
      kid.mode = 'walk'; kid.expr = 'worried';
    } else {
      kid.x = 12.55; kid.z = 3.25; kid.ry = -0.4;
      kid.mode = 'reach-down'; kid.expr = t < 59.6 ? 'worried' : 'shocked';
    }
  }
  // --- door-count tracking (shot 19) ---
  if (t >= 61.6 && t < 65.6) {
    kid.vis = true;
    const u = ease((t - 61.6) / 4.0);
    kid.x = lerp(6.8, 13.6, u); kid.z = 4.6; kid.ry = Math.PI / 2;
    kid.mode = 'walk'; kid.expr = 'worried';
  }
  // --- turns his corner (shot 20) ---
  if (t >= 65.6 && t < 68.8) {
    kid.vis = true;
    const u = ease((t - 65.6) / 3.2);
    kid.x = lerp(13.8, 17.3, u); kid.z = 4.6; kid.ry = Math.PI / 2;
    kid.mode = t < 67.4 ? 'walk' : 'stand';
    kid.expr = t < 67.4 ? 'worried' : 'shocked';
    if (t >= 67.6) kid.ry = lerp(Math.PI / 2, 0.5, easeOut(clamp01((t - 67.6) / 1.0)));
  }
  // --- 149 push-in: kid frozen at his door (shot 21) ---
  if (t >= 68.8 && t < 72.0) {
    kid.vis = true; kid.x = 17.9; kid.z = 5.4; kid.ry = 0.65;
    kid.mode = 'stand'; kid.expr = 'shocked';
  }
  return { kid, mom, finch, ex1, ex2, ex3 };
}

// ------------------------------------------------------------- doors
function doorStates(t) {
  // closed 0 .. open 1 (open = rot +1.1 toward street)
  const d = { n143: 0, n145: 0, finch: 0, kid: 0 };
  if (t >= 16.2 && t < 19.6) d.kid = 0.95; // family bursts in
  if (t >= 19.6 && t < 20.0) d.kid = lerp(0.95, 0, easeIn((t - 19.6) / 0.4)); // SLAM
  if (t >= 18.2 && t < 20.2) d.n143 = 0.9;
  if (t >= 20.2 && t < 20.55) d.n143 = lerp(0.9, 0, easeIn((t - 20.2) / 0.35));
  if (t >= 19.0 && t < 20.6) d.n145 = 0.9;
  if (t >= 20.6 && t < 20.95) d.n145 = lerp(0.9, 0, easeIn((t - 20.6) / 0.35));
  // kid peeking through the ajar door during the count
  if (t >= 22.2 && t < 53.7) d.kid = 0.65;
  // morning: all closed
  return d;
}

// ------------------------------------------------------------- lamps
function lampState(t) {
  // returns {on, flicker, aimU} — aimU: 0 default down, 1 aimed at Finch
  const on = t >= 20.5;
  let flicker = 0;
  if (t >= 22.2 && t < 23.4) flicker = 1; // flicker-on moment
  if (t >= 31.2 && t < 33.0) flicker = 0.6; // the voice makes them stutter
  const aimU = ease(clamp01((t - 39.2) / 2.6));
  const blaze = t >= 52.6 && t < 54.6 ? 1 : 0; // ONE flash
  return { on, flicker, aimU, blaze };
}

// ------------------------------------------------------------- overlays
function overlayState(t) {
  // big text cards (render-time). Captions are burned ASS-side.
  if (t < 3.0) return { tex: 'card1', op: clamp01((t - 0.25) / 0.35) * clamp01((3.0 - t) / 0.3) };
  if (t >= 72.0 && t < 76.0) return { tex: 'card2', op: clamp01((t - 72.35) / 0.4) * clamp01((76.0 - t) / 0.35) };
  if (t >= 76.0) return { tex: 'end', op: 1 };
  return null;
}

function flashState(t) {
  if (t >= 52.42 && t < 52.49) return 0.32;                     // strobe blink 1
  if (t >= 52.52 && t < 52.60) return 0.58;                     // strobe blink 2
  if (t >= 52.6 && t < 53.05) return 1;                          // FULL WHITE
  if (t >= 53.05 && t < 54.2) return 1 - easeOut((t - 53.05) / 1.15);
  return 0;
}

// ------------------------------------------------------------- evaluate
// big countdown numbers shown on screen with the Voice (clarity)
const NUM_OVERLAYS = [
  [31.30, 32.40, '10'], [32.40, 33.50, '9'], [33.50, 34.70, '8'],
  [39.30, 40.40, '7'], [40.40, 41.50, '6'], [41.50, 42.70, '5'],
  [46.30, 47.30, '4'], [47.30, 48.50, '3'],
  [52.00, 52.42, '2'], [52.42, 52.62, '1'],
  [11.40, 12.90, '9PM'],
];
function numState(t) {
  for (const [t0, t1, d] of NUM_OVERLAYS) {
    if (t >= t0 && t < t1) {
      const u = (t - t0) / (t1 - t0);
      return { d, op: u > 0.82 ? (1 - u) / 0.18 : 1, pop: Math.min(1, u / 0.12) };
    }
  }
  return null;
}

export function evaluateScene(t) {
  t = Math.max(0, Math.min(DURATION - 0.0001, t));
  const shot = getShotAt(t);
  const u = clamp01((t - shot.t0) / (shot.t1 - shot.t0));
  const eu = shot.ez === 'in' ? easeIn(u) : shot.ez === 'out' ? easeOut(u) : ease(u);
  const cam = {
    p: lerp3(shot.p0, shot.p1, eu),
    l: lerp3(shot.l0, shot.l1, eu),
    fov: lerp(shot.fov || 45, shot.fov || 45, eu),
    shake: shot.shk || 0,
    roll: lerp(shot.r0 || 0, shot.r1 || 0, eu) || (shot.roll || 0),
  };
  // sky interpolation
  let k0 = SKY_KEYS[0], k1 = SKY_KEYS[SKY_KEYS.length - 1];
  for (let i = 0; i < SKY_KEYS.length - 1; i++) {
    if (t >= SKY_KEYS[i][0] && t < SKY_KEYS[i + 1][0]) { k0 = SKY_KEYS[i]; k1 = SKY_KEYS[i + 1]; break; }
  }
  const ku = clamp01((t - k0[0]) / Math.max(0.001, k1[0] - k0[0]));
  const sky = {
    bg: hexLerp(k0[1], k1[1], ku),
    fog: hexLerp(k0[2], k1[2], ku),
    sunI: lerp(k0[3], k1[3], ku),
    sunCol: hexLerp(k0[4], k1[4], ku),
    lampOn: lerp(k0[5], k1[5], ku),
    night: 1 - clamp01((lerp(k0[3], k1[3], ku)) / 1.15), // 0 day .. 1 night
  };
  return {
    t, shot, cam, sky,
    chars: charStates(t),
    doors: doorStates(t),
    lamps: lampState(t),
    overlay: overlayState(t),
    num: numState(t),
    flash: flashState(t),
    // finch's dropped hat/cane appear right after the flash
    props: { hat: t >= 53.7, caneDown: t >= 37.6 },
  };
}
