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
  // ---- CLEAR-WIDE remake: stable cameras, one idea per shot ----
  { id: 0, t0: 0.0, t1: 4.0, p0: [-14, 24, -24], p1: [-2, 16, -14], l0: [4, 1, 0], l1: [8, 1, 2], fov: 50, ez: 'inout' },              // aerial + title
  { id: 1, t0: 4.0, t1: 8.0, p0: [10.5, 2.2, 1.0], p1: [14.5, 2.0, 1.2], l0: [10, 1.4, 4.6], l1: [13, 1.4, 4.6], fov: 44, ez: 'inout' },  // Tommy + mom arrive
  { id: 2, t0: 8.0, t1: 12.0, p0: [14.9, 1.7, 3.5], p1: [14.5, 1.65, 3.15], l0: [14.6, 1.5, 6.6], l1: [14.5, 1.55, 6.5], fov: 34, ez: 'inout' }, // Finch warns (two-shot)
  { id: 3, t0: 12.0, t1: 15.5, p0: [15.6, 1.6, 4.3], p1: [15.75, 1.62, 4.05], l0: [15.3, 1.5, 5.2], l1: [15.3, 1.55, 5.15], fov: 30, ez: 'inout' }, // kid dismissive + dusk
  { id: 4, t0: 15.5, t1: 19.5, p0: [4.0, 1.9, -6.5], p1: [8.5, 1.75, -5.5], l0: [9, 1.3, 3.0], l1: [13, 1.3, 4.2], fov: 52, ez: 'inout' },  // dusk panic RUN (wide, stable)
  { id: 5, t0: 19.5, t1: 23.0, p0: [17.6, 1.5, 4.3], p1: [17.8, 1.45, 3.95], l0: [18, 1.4, 7.7], l1: [18, 1.42, 7.7], fov: 32, shk: 0.006 }, // kid door SLAMS
  { id: 6, t0: 23.0, t1: 26.0, p0: [-6, 2.1, -1.5], p1: [-2, 2.2, -1.2], l0: [0, 3.8, -5.2], l1: [3, 4.2, -5.2], fov: 48 },               // lamps flicker ON (wide)
  { id: 7, t0: 26.0, t1: 31.0, p0: [17.5, 1.62, 6.5], p1: [17.6, 1.58, 6.62], l0: [18.02, 1.52, 8.0], l1: [18.02, 1.5, 8.0], fov: 26 },  // Tommy peeks (clear face + street behind)
  { id: 8, t0: 31.0, t1: 36.5, p0: [-4, 2.0, -4.5], p1: [-1, 2.1, -4.0], l0: [10, 1.6, 1.5], l1: [11.5, 1.7, 1.8], fov: 50 },             // wide street: Finch enters, faltering
  { id: 9, t0: 36.5, t1: 41.0, p0: [10.6, 1.5, 1.2], p1: [11.35, 1.45, 0.9], l0: [12.1, 1.35, 2.2], l1: [12.25, 1.3, 2.3], fov: 34 },     // Finch stumbles (stable medium-wide)
  { id: 10, t0: 41.0, t1: 46.0, p0: [8.0, 2.2, -8.5], p1: [6.5, 2.0, -7.5], l0: [12, 2.2, 3.0], l1: [13, 2.6, 5.0], fov: 48 },            // lamps TURN toward Finch house (wide)
  { id: 11, t0: 46.0, t1: 50.0, p0: [17.4, 1.6, 6.55], p1: [17.5, 1.56, 6.62], l0: [18.02, 1.5, 8.0], l1: [18.02, 1.48, 8.0], fov: 24 }, // Tommy shocked peek
  { id: 12, t0: 50.0, t1: 52.6, p0: [13.1, 1.5, 3.0], p1: [12.5, 1.42, 2.6], l0: [12.12, 1.55, 2.2], l1: [12.15, 1.62, 2.25], fov: 22 },  // Finch looks up: creepy smile (slow push)
  { id: 13, t0: 52.6, t1: 53.7, p0: [12.4, 1.5, 2.7], p1: [12.4, 1.5, 2.7], l0: [12.1, 1.5, 2.2], l1: [12.1, 1.5, 2.2], fov: 24, shk: 0.03 }, // "ONE" — FLASH
  { id: 14, t0: 53.7, t1: 58.0, p0: [13.8, 1.5, 3.2], p1: [13.2, 1.3, 2.7], l0: [12.6, 0.5, 2.0], l1: [12.6, 0.4, 2.0], fov: 36 },        // aftermath: EMPTY LOT + hat
  { id: 15, t0: 58.0, t1: 64.0, p0: [13.6, 1.5, 4.4], p1: [13.4, 1.42, 4.1], l0: [12.6, 0.7, 3.6], l1: [13.4, 1.2, 5.2], fov: 38 },       // morning: Tommy finds the hat
  { id: 16, t0: 64.0, t1: 69.5, p0: [7.5, 1.7, 2.8], p1: [16.5, 1.7, 2.9], l0: [7.2, 1.9, 7.8], l1: [16.2, 1.9, 7.8], fov: 42 },          // side-track: 143, 145, GAP, 149
  { id: 17, t0: 69.5, t1: 73.5, p0: [18.6, 1.5, 4.9], p1: [18.15, 1.45, 5.0], l0: [18, 1.75, 7.86], l1: [18, 1.78, 7.86], fov: 20 },     // plate 149 push-in
  { id: 18, t0: 73.5, t1: 80.0, p0: [-4, 22, -20], p1: [6, 15, -11], l0: [10, 0, 4], l1: [10, 0, 4], fov: 55 },                          // aerial: street with the GAP + end card
];

export function getShotAt(t) {
  for (const s of SHOTS) if (t >= s.t0 && t < s.t1) return s;
  return SHOTS[SHOTS.length - 1];
}

// ------------------------------------------------------------- sky/lights
// key times: [t, bg, fog, sunI, sunCol, lampOn]
const SKY_KEYS = [
  [0.0, '#6fc3f7', '#c9e8fb', 1.2, '#fff4dd', 0],
  [12.0, '#6fc3f7', '#c9e8fb', 1.2, '#fff4dd', 0],
  [14.0, '#eb9a58', '#e8b088', 0.62, '#ffb066', 0],
  [18.5, '#2b3160', '#3a4160', 0.10, '#8899cc', 1],
  [21.5, '#10142e', '#1a2038', 0.16, '#9aa8d8', 1],
  [53.7, '#0d1128', '#171d33', 0.16, '#9aa8d8', 1],
  [57.6, '#8fd4f9', '#c9ecfb', 1.1, '#fff2d8', 0],
  [72.0, '#7cc4f2', '#c9e8fb', 1.1, '#ffe9c4', 0],
  [75.0, '#3a4468', '#4a5474', 0.22, '#c4b28a', 0.6],
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

  // --- street life during the arrival (background walkers) ---
  if (t >= 4.0 && t < 8.0) {
    ex1.vis = true; const u = ease((t - 4.0) / 4.0);
    ex1.x = lerp(-6, 2, u); ex1.z = -4.2; ex1.ry = Math.PI / 2; ex1.mode = 'walk';
    ex2.vis = true; const u2 = ease((t - 4.0) / 4.0);
    ex2.x = lerp(9, 1, u2); ex2.z = -4.6; ex2.ry = -Math.PI / 2; ex2.mode = 'walk';
    ex3.vis = true; ex3.x = lerp(-1, 0.5, ease((t - 4.4) / 3.4)); ex3.z = 4.4; ex3.ry = Math.PI / 2; ex3.mode = 'walk';
  }
  // --- arrival: Tommy + mom walk in with the box ---
  if (t >= 4.0 && t < 8.0) {
    const u = ease((t - 4.0) / 4.0);
    kid.vis = true; kid.x = lerp(6.5, 12.6, u); kid.z = 4.6; kid.ry = Math.PI / 2; kid.mode = 'walk'; kid.expr = 'smile';
    mom.vis = true; mom.x = lerp(5.6, 11.6, u); mom.z = 4.6; mom.ry = Math.PI / 2; mom.mode = 'walk'; mom.expr = 'neutral';
  }
  // --- Finch warning (8-12) + kid dismissive (12-15.5) ---
  if (t >= 8.0 && t < 15.5) {
    finch.vis = true; finch.x = 14.0; finch.z = 7.7; finch.ry = Math.PI; finch.expr = 'worried';
    finch.talk = t >= 8.2 && t < 11.6;
    finch.mode = (t >= 8.6 && t < 11.2) ? 'point' : 'stand';
    kid.vis = true; kid.x = 15.3; kid.z = 5.3; kid.ry = -0.5; kid.mode = 'stand';
    kid.expr = t < 12.0 ? 'worried' : 'smile';
    mom.vis = true; mom.x = 16.3; mom.z = 5.5; mom.ry = -0.9; mom.expr = 'neutral'; mom.mode = 'stand';
  }
  // --- dusk panic run: everyone sprints home ---
  if (t >= 15.5 && t < 19.5) {
    const u = easeIn((t - 15.5) / 4.0);
    ex1.vis = true; ex1.x = lerp(-4, -14, u); ex1.z = lerp(-3.8, -4.4, u); ex1.ry = -Math.PI / 2; ex1.mode = 'run'; ex1.expr = 'scared';
    ex2.vis = true; ex2.x = lerp(8, 1, u); ex2.z = -4.4; ex2.ry = -Math.PI / 2; ex2.mode = 'run'; ex2.expr = 'scared';
    ex3.vis = true; ex3.x = lerp(2, 9.5, u); ex3.z = lerp(4.4, 5.0, u); ex3.ry = Math.PI / 2; ex3.mode = 'run'; ex3.expr = 'scared';
    mom.vis = true; mom.x = lerp(11.6, 17.2, u); mom.z = 4.6; mom.ry = Math.PI / 2; mom.mode = 'run'; mom.expr = 'worried';
    kid.vis = true; kid.x = lerp(12.6, 18.1, u); kid.z = 4.7; kid.ry = Math.PI / 2; kid.mode = 'run'; kid.expr = 'worried';
  }
  // --- door slam: family inside ---
  if (t >= 19.5 && t < 23.0) {
    kid.vis = false; mom.vis = false;
  }
  // --- THE PEEK: Tommy in his doorway, lit by the porch light ---
  if (t >= 23.0 && t < 53.7) {
    kid.vis = true; kid.x = 18.02; kid.z = 8.35; kid.ry = Math.PI + 0.06;
    kid.mode = 'stand';
    kid.expr = t < 27.6 ? 'worried' : (t < 41.0 ? 'scared' : 'shocked');
  }
  // --- Finch outside on the street during the count ---
  if (t >= 31.0 && t < 52.6) {
    finch.vis = true;
    if (t < 34.5) { // enters, already faltering
      const u = ease((t - 31.0) / 3.5);
      finch.x = lerp(15.5, 12.6, u); finch.z = lerp(4.4, 2.4, u);
      finch.ry = lerp(-2.2, -2.6, u); finch.mode = 'walk'; finch.expr = 'worried';
    } else if (t < 37.6) {
      finch.x = 12.4; finch.z = 2.3; finch.ry = -2.6; finch.mode = 'stumble'; finch.expr = 'scared';
    } else {
      finch.x = 12.15; finch.z = 2.25; finch.ry = -2.7;
      finch.mode = t < 50.0 ? 'stumble' : 'stand';
      finch.expr = t < 50.0 ? 'scared' : 'creepy';
    }
  }
  // Finch GONE at the flash (52.6)
  // --- morning: Tommy finds the hat ---
  if (t >= 58.0 && t < 64.0) {
    kid.vis = true;
    if (t < 59.8) {
      const u = ease((t - 58.0) / 1.8);
      kid.x = lerp(11.2, 12.5, u); kid.z = lerp(4.6, 3.3, u); kid.ry = lerp(Math.PI / 2, -0.4, u);
      kid.mode = 'walk'; kid.expr = 'worried';
    } else {
      kid.x = 12.55; kid.z = 3.25; kid.ry = -0.4;
      kid.mode = 'reach-down'; kid.expr = t < 60.8 ? 'worried' : 'shocked';
    }
  }
  // --- plate tracking walk ---
  if (t >= 64.0 && t < 69.5) {
    kid.vis = true;
    const u = ease((t - 64.0) / 5.5);
    kid.x = lerp(6.8, 17.3, u); kid.z = 4.6; kid.ry = Math.PI / 2;
    kid.mode = 'walk'; kid.expr = 'worried';
  }
  // --- frozen at his own door ---
  if (t >= 69.5 && t < 73.5) {
    kid.vis = true; kid.x = 17.9; kid.z = 5.4; kid.ry = 0.65;
    kid.mode = 'stand'; kid.expr = 'shocked';
  }
  return { kid, mom, finch, ex1, ex2, ex3 };
}

// ------------------------------------------------------------- doors
function doorStates(t) {
  // closed 0 .. open 1 (open = rot +1.1 toward street)
  const d = { n143: 0, n145: 0, finch: 0, kid: 0 };
  if (t >= 16.0 && t < 19.85) d.kid = 0.95; // family bursts in
  if (t >= 19.85 && t < 20.2) d.kid = lerp(0.95, 0, easeIn((t - 19.85) / 0.35)); // SLAM
  if (t >= 18.4 && t < 20.45) d.n143 = 0.9;
  if (t >= 20.45 && t < 20.8) d.n143 = lerp(0.9, 0, easeIn((t - 20.45) / 0.35));
  if (t >= 19.1 && t < 20.85) d.n145 = 0.9;
  if (t >= 20.85 && t < 21.2) d.n145 = lerp(0.9, 0, easeIn((t - 20.85) / 0.35));
  // kid peeking through the ajar door during the count
  if (t >= 22.6 && t < 53.7) d.kid = 0.65;
  // morning: all closed
  return d;
}

// ------------------------------------------------------------- lamps
function lampState(t) {
  // returns {on, flicker, aimU} — aimU: 0 default down, 1 aimed at Finch
  const on = t >= 22.8;
  let flicker = 0;
  if (t >= 23.2 && t < 25.0) flicker = 1; // flicker-on moment
  if (t >= 31.0 && t < 32.6) flicker = 0.6; // the voice makes them stutter
  const aimU = ease(clamp01((t - 39.0) / 2.4));
  const blaze = t >= 52.6 && t < 54.6 ? 1 : 0; // ONE flash
  return { on, flicker, aimU, blaze };
}

// ------------------------------------------------------------- overlays
function overlayState(t) {
  // big text cards (render-time). Captions are burned ASS-side.
  if (t < 3.4) return { tex: 'card1', op: clamp01((t - 0.25) / 0.35) * clamp01((3.4 - t) / 0.3) };
  if (t >= 70.4 && t < 73.4) return { tex: 'card2', op: clamp01((t - 70.6) / 0.4) * clamp01((73.4 - t) / 0.35) };
  if (t >= 76.6) return { tex: 'end', op: clamp01((t - 76.7) / 0.4) };
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
  [27.60, 28.70, '10'], [28.70, 29.80, '9'], [29.80, 31.00, '8'],
  [39.00, 40.10, '7'], [40.10, 41.20, '6'], [41.20, 42.40, '5'],
  [46.30, 47.30, '4'], [47.30, 48.40, '3'],
  [51.55, 51.95, '2'], [52.28, 52.55, '1'],
  [9.60, 11.00, '9PM'],
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
    props: { hat: t >= 53.7 && t < 61.2, caneDown: t >= 34.5 && t < 52.6, houseGone: t >= 52.6 },
  };
}
