import { camFromKeys, blinkAt, idle } from './motion.js';
import { TL } from './timeline.js';

/* PRODUCTION STORY — "The Man Who Sold the Eiffel Tower"
   9 shots, one VO line each (timings from work/timeline.json).
   Every shot is ONE continuous camera move; holds keep creeping so nothing freezes.  */
export const FPS = TL.fps, TOTAL = TL.total_frames;

export const SHOTS = TL.shots.map(s => ({ id: s.id, a: s.f0, b: s.f1, light: s.light, loc: s.loc, len: s.len_f, chunks: s.chunks }));
export const shotAt = f => SHOTS.find(s => f >= s.a && f <= s.b) || SHOTS[SHOTS.length - 1];
export const shotLen = id => (SHOTS.find(s => s.id === id) || SHOTS[0]).len;

const base = {
  hemi: 0.9, fogNear: 30, fogFar: 360, sat: 1.08, vig: 0.22, shadowExt: 26,
  waterDeep: '#315a70', waterShal: '#739ba4', glint: '#e6dfcc', sunSize: 0, sunDisc: '#000000',
};
export const LIGHTS = {
  day: {
    ...base, az: 75, el: 46, hemi: 1.18,
    sky: '#dcecff', ground: '#c4a884', sun: '#fff3e0', sunI: 2.7,
    fog: '#b8d0ec', skyTop: '#4f8cdb', skyHor: '#b8d0ec',
    gain: '#fff8ed', lift: '#04060c', sat: 1.1, vig: 0.21, shadowExt: 24,
  },
  golden: {
    ...base, az: 8, el: 9, hemi: 1.12,
    sky: '#e8c4c0', ground: '#a07a6c', sun: '#ffb877', sunI: 3.6,
    fog: '#efb489', skyTop: '#8a6f8a', skyHor: '#ffd08a',
    sunDisc: '#ffcf9e', sunSize: 0.012,
    gain: '#fff0dc', lift: '#12142e', sat: 1.12, vig: 0.22, shadowExt: 22,
  },
  night: {
    ...base, az: 205, el: 26, hemi: 1.35,
    sky: '#4a5470', ground: '#3a4358', sun: '#a8bce0', sunI: 2.1,
    fog: '#414a61', skyTop: '#25345a', skyHor: '#68758d',
    gain: '#f0f3fb', lift: '#070b16', sat: 1.0, vig: 0.24, shadowExt: 28,
  },
};
export const lightFor = S => LIGHTS[S.light];

/* ---------------- cameras: start key -> end key inside each shot (u = 0..1) ---------------- */
// keys are expressed as fractions of the shot so the video can be re-timed at any fps
const CAMREL = {
  // S1 — Lustig MCU, tower through the window, slow push
  s1: [[0, [1.35, 1.78, 2.75], [0.12, 1.70, 0.55], 31, -1.4],
       [1, [1.02, 1.72, 2.28], [0.10, 1.63, 0.50], 30, -0.3]],
  // S2 — start tight on the forged papers, crane back to reveal six dealers
  s2: [[0, [-0.28, 2.30, 1.42], [-0.50, 1.16, -1.02], 41, 0],
       [1, [-3.30, 2.62, 3.86], [0.74, 1.36, -1.04], 47, 0, [[-1.85, 2.48, 2.62]]]],
  // S3 — newspaper insert tilts up to the window + tower
  s3: [[0, [-0.30, 1.80, 0.34], [-0.52, 1.03, -1.02], 40, 0],
       [1, [0.28, 2.02, 1.16], [-2.42, 2.62, -5.55], 43, 0]],
  // S4 — the bribe: down-table, slow push
  s4: [[0, [0.18, 2.10, 4.05], [0.16, 1.16, -0.92], 47, 1.0],
       [1, [0.34, 1.98, 3.28], [0.20, 1.20, -0.86], 45, 0.2]],
  // S5 — he vanishes: watch the door, drift in
  s5: [[0, [-3.40, 2.28, 4.05], [1.55, 1.34, -2.85], 44, 0],
       [1, [-2.45, 2.12, 3.30], [1.95, 1.30, -3.20], 42, 0]],
  // S6 — Poisson alone at night, slow orbit
  s6: [[0, [-1.15, 2.06, -3.45], [-0.40, 1.46, 0.85], 34, 0],
       [1, [-0.72, 1.96, -2.85], [-0.48, 1.44, 0.80], 33, -0.5]],
  // S7 — the exact same trick: copy of the S2 wide
  s7: [[0, [-3.92, 2.86, 4.42], [0.76, 1.34, -1.04], 47, 0],
       [1, [-3.42, 2.64, 3.92], [0.72, 1.40, -1.00], 46, 0]],
  // S8 — 1935 street arrest, push in
  s8: [[0, [-2.60, 2.00, 3.30], [0.10, 1.52, 0.00], 38, 0],
       [1, [-1.75, 1.92, 2.42], [0.10, 1.56, 0.00], 36, 0]],
  // S9 — payoff: crane up from the booth to the whole tower
  s9: [[0, [2.60, 2.02, 11.20], [-1.80, 4.30, -4.60], 54, 1.4],
       [1, [2.10, 3.32, 10.60], [-2.20, 6.60, -5.30], 55, 2.2]],
};

const CAMS = {};
for (const S of SHOTS) {
  const K = CAMREL[S.id] || [];
  CAMS[S.id] = K.map(([u, pos, look, fov, roll, path]) => {
    const k = { f: Math.round(S.a + u * (S.len - 1)), pos, look, fov, roll: roll || 0 };
    if (path) k.path = path;
    return k;
  });
}

const FLASH_SHOT = { s8: 0.55 };  // 1935 street cut
export const camAt = f => {
  const S = shotAt(f), C = camFromKeys(CAMS[S.id], f, { creep: 0.0016, kicks: [] });
  const fl = FLASH_SHOT[S.id];
  if (fl && f - S.a < 8) C.flash = fl * (1 - (f - S.a) / 8);
  return C;
};

const DOF = {
  s1: { c: 9,  t: [0.12, 1.72, 0.60] },
  s2: { c: 8,  t: [-0.50, 1.10, -0.95] },
  s3: { c: 13, t: [-0.50, 1.03, -0.90] },
  s4: { c: 14, t: [0.45, 1.08, -0.90] },
  s5: { c: 9,  t: [1.20, 1.25, -2.20] },
  s6: { c: 13, t: [-0.58, 1.74, 0.06] },
  s7: { c: 7,  t: [0.50, 1.34, -1.00] },
  s8: { c: 12, t: [0.00, 1.50, 0.00] },
  s9: { c: 0,  t: [-2.00, 5.00, -4.90] },
};
export const dofAt = f => {
  const S = shotAt(f), C = camAt(f), D = DOF[S.id];
  const d = Math.hypot(C.pos[0] - D.t[0], C.pos[1] - D.t[1], C.pos[2] - D.t[2]);
  return { focus: d, cinf: D.c, near: 1 };
};

export const worldAt = f => { const S = shotAt(f); return { location: S.loc, id: S.id }; };

/* ---------------- props: papers slide, money crosses the table, door swings,
     SOLD sticker peels then flies off ---------------- */
const ease = t => { t = Math.max(0, Math.min(1, t)); return t * t * (3 - 2 * t); };
const R = (f, a, b) => ease((f - a) / (b - a));

export const propsAt = f => {
  const S = shotAt(f), o = {};
  const L = Math.max(1, S.len - 1), at = v => S.a + Math.round(v * L);   // fraction of shot -> frame
  // S2: the forged papers slide toward the dealers while the camera cranes back
  o.paperZ = -1.10 + 0.32 * R(f, at(0.12), at(0.62));
  o.paperX = -0.50 + 0.06 * R(f, at(0.12), at(0.62));
  // S4: the bribe travels Poisson -> Lustig
  const t = R(f, at(0.12), at(0.33));
  o.moneyS = 1.2;
  o.moneyX = -0.62 + 1.52 * t;      // Poisson -> Lustig, in FRONT of both bodies
  o.moneyZ = 0.95 - 0.10 * t;
  o.moneyY = 1.30 + 0.10 * Math.sin(t * Math.PI);
  // S5: door swings open, then Lustig is gone
  o.doorY = -1.28 * R(f, at(0.12), at(0.26));
  // S1/S9: the SOLD sticker
  o.stickerTilt = S.id === 's1' ? 0.02 * R(f, 0, L) : 0.02;
  o.stickerB = 0;   // 0..1 flies off the booth
  return o;
};

/* ---------------- cast ---------------- */
const actor = (T, key, o, pos, extra = {}) =>
  ({ key: key + JSON.stringify(o), draw: p => T.romanFront(p, key, o), x: pos[0], y: pos[1], z: pos[2], ...extra });
const MPF = 60 / FPS;            // motion frames per render frame
const pose = (f, seed, expr = 'neutral', extra = {}) =>
  ({ seed, expr, blink: blinkAt(f * MPF, seed), ...idle(f * MPF, seed), ...extra });
const DEALER_POSE = (f, seed, expr) => pose(f, seed, expr, { L: 'hip', R: 'hang', facing: -0.4, look: 0.2 });

export const actorsAt = (f, T) => {
  const S = shotAt(f), out = [], L = Math.max(1, S.len - 1);
  const add = (who, o, pos, x = {}) => out.push(actor(T, who, o, pos, x));
  switch (S.id) {
    case 's1':
      add('lustig', pose(f, 3, 'smile', { L: 'hip', R: 'hang', facing: 0.35, look: 0.1, headTilt: 2 }), [0.15, 0, 0.75]);
      break;
    case 's2':
    case 's7': {
      const second = S.id === 's7';
      add('lustig', pose(f, 3, 'stern', { L: 'reach', R: 'hip', facing: -0.6, look: 0.3, lift: 0.35 }), [1.95, 0, -1.0]);
      add('dealerA', DEALER_POSE(f, 5, second ? 'neutral' : 'grin'), [-1.5, 0, -1.95]);
      add('dealerB', DEALER_POSE(f, 9, second ? 'grin' : 'neutral'), [-0.1, 0, -1.95], { s: 0.97 });
      add('dealerC', DEALER_POSE(f, 13, 'grin'), [1.25, 0, -1.95], { s: 1.02 });
      add('poisson', pose(f, 15, 'grin', { L: 'hip', R: 'point', facing: 0.5, look: -0.2 }), [-1.2, 0, 0.2], { s: 0.98 });
      add('dealerD', pose(f, 21, second ? 'grin' : 'neutral', { L: 'hang', R: 'temple', facing: 0.3, look: -0.1 }), [0.3, 0, 0.25], { s: 1.01 });
      add('dealerE', pose(f, 23, 'grin', { L: 'hip', R: 'hang', facing: 0.45, look: -0.2 }), [1.45, 0, 0.3], { s: 0.96 });
      break;
    }
    case 's3':
      add('lustig', pose(f, 3, 'smile', { L: 'point', R: 'reach', facing: -0.5, look: 0.2, lift: 0.5 }), [1.85, 0, -0.55]);
      add('poisson', pose(f, 15, 'neutral', { L: 'hang', R: 'hip', facing: 0.4, look: 0.15 }), [-1.35, 0, 0.45], { s: 0.98 });
      break;
    case 's4':
      add('lustig', pose(f, 3, 'smile', { L: 'reach', R: 'hip', facing: -0.5, look: 0.3, lift: 0.25 }), [0.95, 0, -0.5]);
      add('poisson', pose(f, 15, 'grin', { L: 'point', R: 'hip', facing: 0.45, look: -0.15 }), [-0.35, 0, 0.15], { s: 0.98 });
      break;
    case 's5': {
      // Lustig slides out frame-right and fades once he clears the door
      const gone = R(f, S.a + 0.11 * L, S.a + 0.34 * L);
      add('lustig', pose(f, 3, 'smile', { L: 'wave', R: 'hang', facing: -0.35, look: 0.35, wv: 1.6 }),
        [2.05 + 2.35 * gone, 0, -2.15 - 2.85 * gone], { alpha: 1 - R(f, S.a + 0.24 * L, S.a + 0.36 * L), s: 1 - 0.06 * gone });
      add('poisson', pose(f, 15, 'shock', { L: 'cheek', R: 'cheek', facing: 0.3, look: -0.3 }), [-0.78, 0, -0.18], { s: 0.94 });
      break;
    }
    case 's6':
      add('poisson', pose(f, 15, 'nervous', { L: 'cheek', R: 'cheek', facing: 0.55, look: -0.30, tilt: 7 }), [-0.60, 0, 0.20], { s: 0.98 });
      break;
    case 's8':
      add('lustig', pose(f, 3, 'stern', { L: 'cross', R: 'cross', facing: 0.2, look: 0.1, tilt: -3 }), [0.15, 0, 0.1]);
      add('agentA', pose(f, 7, 'stern', { L: 'cross', R: 'hip', facing: -0.5, look: 0.2 }), [-0.95, 0, 0.55], { s: 1.03 });
      add('agentB', pose(f, 11, 'stern', { L: 'hip', R: 'cross', facing: 0.55, look: -0.2 }), [1.05, 0, 0.5], { s: 1.0 });
      break;
    case 's9':
      add('guide', pose(f, 21, 'smile', { L: 'hip', R: 'point', facing: -0.4, look: 0.3 }), [-1.1, 0, 4.6], { s: 0.98 });
      add('visitorA', pose(f, 15, 'grin', { L: 'hang', R: 'reach', facing: 0.3, look: -0.2, lift: 0.45 }), [0.15, 0, 5.3], { s: 0.95 });
      add('child', pose(f, 13, 'laugh', { L: 'up', R: 'wave', facing: 0.35, look: -0.25, wv: 1.2 }), [0.75, 0, 5.9], { s: 0.72 });
      break;
  }
  return out;
};

export const fxAt = () => [];
