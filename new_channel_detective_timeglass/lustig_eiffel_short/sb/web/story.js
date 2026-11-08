import { camFromKeys, blinkAt, q, idle } from './motion.js';

/* STICKYBOARD STORY — "The Man Who Sold the Eiffel Tower"
   10 static shots × 100 story-frames; stills are rendered at each shot's
   mid-point (i*100+50). One continuous camera per shot, light per shot. */
export const FPS = 30, TOTAL = 1000, DECK = 0.08;

export const SHOTS = [
  { id: 's1', a: 0,   b: 99,  light: 'golden', loc: 'suite' },
  { id: 's2', a: 100, b: 199, light: 'day',    loc: 'suite' },
  { id: 's3', a: 200, b: 299, light: 'day',    loc: 'suite' },
  { id: 's4', a: 300, b: 399, light: 'day',    loc: 'suite' },
  { id: 's5', a: 400, b: 499, light: 'day',    loc: 'suite' },
  { id: 's6', a: 500, b: 599, light: 'golden', loc: 'suite' },
  { id: 's7', a: 600, b: 699, light: 'night',  loc: 'suite' },
  { id: 's8', a: 700, b: 799, light: 'day',    loc: 'suite' },
  { id: 's9', a: 800, b: 899, light: 'day',    loc: 'street' },
  { id: 's10', a: 900, b: 999, light: 'golden', loc: 'booth' },
];
export const shotAt = f => SHOTS.find(s => f >= s.a && f <= s.b) || SHOTS[SHOTS.length - 1];

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

/* ---------------- cameras: one key per shot (static storyboard framing) ------- */
const CAMS = {
  // S1 Lustig MCU, window + tower behind → title shot
  s1:  [{ f: 0, pos: [1.35, 1.78, 2.75], look: [0.12, 1.7, 0.55], fov: 31 }],
  // S2 crane-down wide: table + six dealers + window
  s2:  [{ f: 100, pos: [-4.0, 2.9, 4.5], look: [0.75, 1.35, -1.05], fov: 47 }],
  // S3 papers across the table (MS)
  s3:  [{ f: 200, pos: [-0.45, 2.45, 1.75], look: [-0.5, 1.35, -1.35], fov: 40 }],
  // S4 newspaper insert, tilt down on the desk
  s4:  [{ f: 300, pos: [1.2, 2.1, 1.25], look: [-0.25, 1.0, -1.05], fov: 40 }],
  // S5 high-angle money hand-over
  s5:  [{ f: 400, pos: [0.3, 1.85, 3.5], look: [0.4, 1.05, -0.9], fov: 46 }],
  // S6 empty chair + door, Lustig gone
  s6:  [{ f: 500, pos: [-2.3, 2.0, 3.0], look: [1.4, 1.3, -2.4], fov: 42 }],
  // S7 Poisson alone, night-blue (3/4 orbit point)
  s7:  [{ f: 600, pos: [1.7, 1.95, 1.75], look: [-0.55, 1.78, 0.0], fov: 34 }],
  // S8 identical framing to S2 (the visual-rhyme joke)
  s8:  [{ f: 700, pos: [-4.0, 2.9, 4.5], look: [0.75, 1.35, -1.05], fov: 47 }],
  // S9 1935 street arrest, push-in
  s9:  [{ f: 800, pos: [-2.9, 1.95, 3.6], look: [0.05, 1.5, 0.0], fov: 38 }],
  // S10 booth queue → crane up the tower
  s10: [{ f: 900, pos: [2.5, 2.0, 11.0], look: [-1.8, 4.4, -4.5], fov: 54 }],
};
export const camAt = f => {
  const S = shotAt(f), K = CAMS[S.id];
  return camFromKeys(K, f, { creep: 0.0016, kicks: [] });
};

const DOF = {
  s1: { c: 10, t: [0.12, 1.7, 0.6] }, s2: { c: 6, t: [0.5, 1.35, -1.0] },
  s3: { c: 13, t: [-0.5, 1.03, -0.9] }, s4: { c: 15, t: [-0.25, 1.0, -1.05] },
  s5: { c: 14, t: [0.45, 1.08, -0.9] }, s6: { c: 9, t: [0.6, 1.3, -1.2] },
  s7: { c: 14, t: [-0.55, 1.78, 0.05] }, s8: { c: 6, t: [0.5, 1.35, -1.0] },
  s9: { c: 13, t: [0.0, 1.5, 0.0] }, s10: { c: 0, t: [-1.8, 4.4, -4.5] },
};
export const dofAt = f => {
  const S = shotAt(f), C = camAt(f), D = DOF[S.id];
  const d = Math.hypot(C.pos[0] - D.t[0], C.pos[1] - D.t[1], C.pos[2] - D.t[2]);
  return { focus: d, cinf: D.c, near: 1 };
};

export const worldAt = f => ({ location: shotAt(f).loc });

/* ---------------- cast (static poses per shot) ---------------- */
const actor = (T, key, o, pos, extra = {}) =>
  ({ key: key + JSON.stringify(o), draw: p => T.romanFront(p, key, o), x: pos[0], y: pos[1], z: pos[2], ...extra });
const pose = (f, seed, expr = 'neutral', extra = {}) =>
  ({ seed, expr, blink: blinkAt(f, seed), ...idle(f, seed), ...extra });

const DEALER_POSE = (f, seed, expr) => pose(f, seed, expr, { L: 'hip', R: 'hang', facing: -0.4, look: 0.2 });

export const actorsAt = (f, T) => {
  const S = shotAt(f), out = [];
  const add = (who, o, pos, x = {}) => out.push(actor(T, who, o, pos, x));
  switch (S.id) {
    case 's1':
      add('lustig', pose(f, 3, 'smile', { L: 'hip', R: 'hang', facing: 0.35, look: 0.1, headTilt: 2 }), [0.15, 0, 0.75]);
      break;
    case 's2':
    case 's8': {
      // six dealers around the table + Lustig at the head (S8 = same poses, different shirts = visual rhyme)
      const d = S.id === 's2' ? 0 : 1;
      add('lustig', pose(f, 3, 'stern', { L: 'reach', R: 'hip', facing: -0.6, look: 0.3, lift: 0.35 }), [1.95, 0, -1.0]);
      add('dealerA', DEALER_POSE(f, 5, d ? 'neutral' : 'grin'), [-1.5, 0, -1.95]);
      add('dealerB', DEALER_POSE(f, 9, d ? 'grin' : 'neutral'), [-0.1, 0, -1.95], { s: 0.97 });
      add('dealerC', DEALER_POSE(f, 13, 'grin'), [1.25, 0, -1.95], { s: 1.02 });
      add('poisson', pose(f, 15, 'grin', { L: 'hip', R: 'point', facing: 0.5, look: -0.2 }), [-1.2, 0, 0.2], { s: 0.98 });
      add('dealerD', pose(f, 21, 'neutral', { L: 'hang', R: 'temple', facing: 0.3, look: -0.1 }), [0.3, 0, 0.25], { s: 1.01 });
      add('dealerE', pose(f, 23, 'grin', { L: 'hip', R: 'hang', facing: 0.45, look: -0.2 }), [1.45, 0, 0.3], { s: 0.96 });
      break;
    }
    case 's3':
      add('lustig', pose(f, 3, 'stern', { L: 'point', R: 'hip', facing: -0.5, look: 0.25 }), [2.1, 0, -1.15]);
      add('poisson', pose(f, 15, 'neutral', { L: 'hang', R: 'reach', facing: 0.4, look: -0.1, lift: 0.3 }), [-1.0, 0, 0.15], { s: 0.98 });
      add('dealerA', DEALER_POSE(f, 5, 'neutral'), [-2.0, 0, -1.6], { s: 0.99 });
      break;
    case 's4':
      add('lustig', pose(f, 3, 'stern', { L: 'reach', R: 'hang', facing: -0.35, look: 0.2, lift: 0.55 }), [1.6, 0, -0.6]);
      add('poisson', pose(f, 15, 'neutral', { L: 'hip', R: 'hang', facing: 0.4, look: 0.1 }), [-1.3, 0, 0.4], { s: 0.98 });
      break;
    case 's5':
      add('lustig', pose(f, 3, 'smile', { L: 'reach', R: 'hip', facing: -0.5, look: 0.3, lift: 0.25 }), [0.95, 0, -0.5]);
      add('poisson', pose(f, 15, 'grin', { L: 'point', R: 'hip', facing: 0.45, look: -0.15 }), [-0.35, 0, 0.15], { s: 0.98 });
      break;
    case 's6':
      add('poisson', pose(f, 15, 'shock', { L: 'cheek', R: 'cheek', facing: 0.3, look: -0.3 }), [-0.7, 0, 0.2], { s: 0.98 });
      break;
    case 's7':
      add('poisson', pose(f, 15, 'nervous', { L: 'temple', R: 'temple', facing: 0.3, look: -0.25, tilt: 5 }), [-0.6, 0, 0.2], { s: 0.98 });
      break;
    case 's9':
      add('lustig', pose(f, 3, 'stern', { L: 'cross', R: 'cross', facing: 0.2, look: 0.1, tilt: -3 }), [0.15, 0, 0.1]);
      add('agentA', pose(f, 7, 'stern', { L: 'cross', R: 'hip', facing: -0.5, look: 0.2 }), [-0.95, 0, 0.55], { s: 1.03 });
      add('agentB', pose(f, 11, 'stern', { L: 'hip', R: 'cross', facing: 0.55, look: -0.2 }), [1.05, 0, 0.5], { s: 1.0 });
      break;
    case 's10':
      add('guide', pose(f, 21, 'smile', { L: 'hip', R: 'point', facing: -0.4, look: 0.3 }), [-1.1, 0, 4.6], { s: 0.98 });
      add('visitorA', pose(f, 15, 'grin', { L: 'hang', R: 'reach', facing: 0.3, look: -0.2, lift: 0.45 }), [0.15, 0, 5.3], { s: 0.95 });
      add('child', pose(f, 13, 'laugh', { L: 'up', R: 'wave', facing: 0.35, look: -0.25, wv: 1.2 }), [0.75, 0, 5.9], { s: 0.72 });
      break;
  }
  return out;
};

export const fxAt = () => [];
