import { camFromKeys, blinkAt, idle } from './motion.js';
import { TL } from './timeline.js';

/* FLANNAN ISLES — "The Lighthouse That Went Dark" (26 December 1900)
   11 cuts, 180 fps master (9,108 frames). Every camera move is authored in
   real frames and normalised by f30() so motion pace is independent of FPS. */
export const FPS = TL.fps, TOTAL = TL.total, DECK = 0.08;
export const SHOTS = TL.shots.map((s) => ({ id: s.id, a: s.f0, b: s.f1, light: s.light, loc: s.loc, len: s.len_f, vo: s.vo }));
export const shotAt = (f) => SHOTS.find((s) => f >= s.a && f <= s.b) || (f < SHOTS[0].a ? SHOTS[0] : SHOTS[SHOTS.length - 1]);

const base = {
  hemi: 0.9, fogNear: 30, fogFar: 360, sat: 1.08, vig: 0.22, shadowExt: 60,
  waterDeep: '#315a70', waterShal: '#739ba4', glint: '#e6dfcc', sunSize: 0, sunDisc: '#000000',
};
export const LIGHTS = {
  nightStorm: { ...base, az: 205, el: 24, hemi: 1.45, sky: '#4a6390', ground: '#1e2836', sun: '#9fb6dd', sunI: 2.5,
    fog: '#2c3d52', fogNear: 55, fogFar: 620, skyTop: '#101c34', skyHor: '#3d5473', sunSize: 0,
    gain: '#eef4ff', lift: '#070b14', sat: 1.14, vig: 0.30, waterDeep: '#152430', waterShal: '#2f5159', glint: '#b9cbd2', storm: 2.2 },
  greyDawn: { ...base, az: 84, el: 14, hemi: 1.15, sky: '#c3cfd8', ground: '#5c6470', sun: '#e9eef2', sunI: 1.9,
    fog: '#b3c2cd', fogNear: 60, fogFar: 700, skyTop: '#7d9ab5', skyHor: '#cfd9df',
    gain: '#f7fbff', lift: '#070c14', sat: 1.05, vig: 0.24, waterDeep: '#22455a', waterShal: '#6f9aa4', glint: '#e8f0ea' },
  nightSea: { ...base, az: 232, el: 13, hemi: 1.35, sky: '#41567c', ground: '#1a222e', sun: '#93aad2', sunI: 2.2,
    fog: '#28384c', fogNear: 45, fogFar: 520, skyTop: '#0c1524', skyHor: '#33465f',
    gain: '#ecf2ff', lift: '#060a12', sat: 1.12, vig: 0.31, waterDeep: '#16232c', waterShal: '#2d4f5a', glint: '#aec2cb', storm: 1.5 },
  coldMorning: { ...base, az: 96, el: 21, hemi: 1.1, sky: '#cfd9e0', ground: '#6a6d70', sun: '#fff0dc', sunI: 2.4,
    fog: '#c2ccd4', fogNear: 70, fogFar: 760, skyTop: '#6f93b4', skyHor: '#d6dee2', sunDisc: '#fff2dd', sunSize: 0.008,
    gain: '#fff9f0', lift: '#090f18', sat: 1.2, vig: 0.22, waterDeep: '#24485a', waterShal: '#84a8ae', glint: '#f0f4ec' },
  stormGrey: { ...base, az: 108, el: 32, hemi: 1.0, sky: '#aebac4', ground: '#4e565e', sun: '#dfe8ee', sunI: 1.7,
    fog: '#9fadb8', fogNear: 34, fogFar: 420, skyTop: '#5f7c96', skyHor: '#b6c2cb',
    gain: '#f2f8fc', lift: '#070c12', sat: 1.16, vig: 0.28, storm: 2.6,
    waterDeep: '#1c3844', waterShal: '#5b7f88', glint: '#e6ece8' },
  lampWarm: { ...base, az: 200, el: 28, hemi: 0.85, sky: '#6a5340', ground: '#2a2018', sun: '#ffd7a0', sunI: 1.7,
    fog: '#2a2118', fogNear: 8, fogFar: 90, skyTop: '#1b2230', skyHor: '#4a4237',
    gain: '#fff2df', lift: '#0d0a08', sat: 1.06, vig: 0.28, waterDeep: '#1b1a16', waterShal: '#2a2620', glint: '#d9c9a8' },
  lampDim: { ...base, az: 200, el: 30, hemi: 0.62, sky: '#4b4034', ground: '#1d1813', sun: '#ffcf94', sunI: 1.15,
    fog: '#221b14', fogNear: 6, fogFar: 70, skyTop: '#151b26', skyHor: '#3a352c',
    gain: '#f6e8d2', lift: '#0a0806', sat: 1.02, vig: 0.33, waterDeep: '#171512', waterShal: '#252017', glint: '#c9b997' },
  fogNight: { ...base, az: 200, el: 22, hemi: 1.75, sky: '#4c6084', ground: '#202a38', sun: '#a8bede', sunI: 2.2,
    fog: '#3a4c64', fogNear: 34, fogFar: 300, skyTop: '#131f36', skyHor: '#44596f',
    gain: '#f2f6ff', lift: '#070b13', sat: 1.08, vig: 0.32, waterDeep: '#16232c', waterShal: '#33525c', glint: '#bccbd2' },
  sunrise: { ...base, az: 96, el: 9, hemi: 1.05, sky: '#e8c8a8', ground: '#6a5a4a', sun: '#ffc27a', sunI: 3.0,
    fog: '#e0b894', fogNear: 70, fogFar: 780, skyTop: '#6d7fa8', skyHor: '#ffc98e', sunDisc: '#ffd7a8', sunSize: 0.012,
    gain: '#fff4e6', lift: '#120e14', sat: 1.24, vig: 0.24,
    waterDeep: '#2b4152', waterShal: '#8d9a96', glint: '#ffd9a8' },
};
export const lightFor = (S) => LIGHTS[S.light] || LIGHTS.greyDawn;

/* ---------------- cameras: keys are shot-relative frames ---------------- */
const CAMS = {
  // S1 — low over the swell, storm, the tower blinks out
  s1: [{ f: 0, pos: [152, 20, 208], look: [0, 47, 0], fov: 25 },
       { f: 1007, pos: [120, 30, 168], look: [-2, 49, 0], fov: 21, ease: 'smooth', path: [[136, 24, 190]] }],
  // S2 — grey day wide, the whole rock, dark lantern
  s2: [{ f: 0, pos: [72, 20, 92], look: [0, 40, 0], fov: 32 },
       { f: 638, pos: [58, 27, 76], look: [0, 42, 0], fov: 28, ease: 'smooth' }],
  // S3 — bow of the relief boat, night, sea running
  s3: [{ f: 0, pos: [-74, 7.5, 46], look: [-12, 30, 4], fov: 38 },
       { f: 737, pos: [-62, 10.5, 38], look: [-10, 32, 2], fov: 33, ease: 'smooth', path: [[-69, 9, 43]] }],
  // S4 — cold morning at the east landing, nobody on the steps
  s4: [{ f: 0, pos: [-76, 11, 20], look: [-24, 30, 2], fov: 40 },
       { f: 800, pos: [-66, 15, 14], look: [-22, 32, 0], fov: 34, ease: 'smooth', path: [[-71, 13, 17]] }],
  // S5 — lantern room: the apparatus, trimmed and filled
  s5: [{ f: 0, pos: [2.5, 2.35, 2.5], look: [0.0, 1.62, 0.0], fov: 40 },
       { f: 674, pos: [-2.3, 2.1, 2.6], look: [0.0, 1.66, 0.0], fov: 36, ease: 'smooth', path: [[0.2, 2.0, 2.9]] }],
  // S6 — pegs: three oilskins, one left
  s6: [{ f: 0, pos: [1.15, 1.9, 0.5], look: [-0.1, 1.58, -3.35], fov: 40 },
       { f: 710, pos: [0.8, 1.87, 0.1], look: [-0.15, 1.56, -3.35], fov: 33, ease: 'smooth' }],
  // S7 — the west landing, the sea coming over the rock
  s7: [{ f: 0, pos: [-96, 18, 54], look: [-26, 13, 4], fov: 38 },
       { f: 1061, pos: [-82, 23, 44], look: [-25, 15, 3], fov: 32, ease: 'smooth', path: [[-89, 20, 49]] }],
  // S8 — the keeper's table: logbook, barometer, slate
  s8: [{ f: 0, pos: [1.85, 2.15, 0.55], look: [1.1, 1.05, 2.3], fov: 40 },
       { f: 773, pos: [1.55, 1.7, 1.15], look: [1.05, 1.0, 2.35], fov: 34, ease: 'easeOut' }],
  // S9 — the verdict: Muirhead and Moore by the tower
  s9: [{ f: 0, pos: [15.0, 37.7, 22.6], look: [7.9, 36.55, 9.6], fov: 44 },
       { f: 755, pos: [13.2, 37.6, 20.4], look: [8.1, 36.5, 9.6], fov: 38, ease: 'smooth', path: [[14.2, 37.4, 21.6]] }],
  // S10 — the legend: three figures in the fog
  s10: [{ f: 0, pos: [16.8, 37.7, 24.0], look: [9.0, 36.5, 9.5], fov: 42 },
        { f: 881, pos: [14.8, 37.6, 21.7], look: [9.2, 36.45, 9.6], fov: 36, ease: 'smooth' }],
  // S11 — sunrise: the light still burning
  s11: [{ f: 0, pos: [116, 34, 142], look: [0, 44, 0], fov: 26 },
        { f: 845, pos: [88, 46, 108], look: [0, 45, 0], fov: 22, ease: 'smooth', path: [[102, 40, 126]] }],
};
const absKeys = {};
export const camAt = (f) => {
  const S = shotAt(f);
  const K = absKeys[S.id] || (absKeys[S.id] = (() => {
    const k = (S.len - 1) / (CAMS[S.id][CAMS[S.id].length - 1].f || 1);
    return CAMS[S.id].map((c) => ({ ...c, f: S.a + Math.round(c.f * k) }));
  })());
  return camFromKeys(K, f, { creep: 0.0011, kicks: S.id === 's7' ? [{ f: S.a + 250, a: 1.0 }, { f: S.a + 640, a: 0.8 }] : [] });
};

const DOF = {
  s1: { c: 3, t: [0, 46, 0] }, s2: { c: 0, t: [0, 40, 0] }, s3: { c: 9, t: [-14, 30, 4] },
  s4: { c: 0, t: [10, 20, 12] }, s5: { c: 7, t: [0, 1.62, 0] }, s6: { c: 7, t: [0.0, 1.58, -3.3] },
  s7: { c: 6, t: [-29, 15, 5] }, s8: { c: 11, t: [1.1, 1.0, 2.32] }, s9: { c: 8, t: [7.0, 35.9, 9.9] },
  s10: { c: 9, t: [8.1, 35.95, 9.6] }, s11: { c: 0, t: [0, 44, 0] },
};
export const dofAt = (f) => {
  const S = shotAt(f), C = camAt(f), D = DOF[S.id];
  const d = Math.hypot(C.pos[0] - D.t[0], C.pos[1] - D.t[1], C.pos[2] - D.t[2]);
  return { focus: d, cinf: D.c, near: 1 };
};

export const worldAt = (f) => ({ location: shotAt(f).loc });

/* ---------------- cast ---------------- */
export const CAST = {
  ducat:     { tunic: '#2a3138', skin: '#f0d3b4', hair: '#2b2420', beard: '#3a3129', cap: '#1b2024' },
  marshall:  { tunic: '#33403c', skin: '#f5d6b8', hair: '#4a3526', moustache: '#4a3526', cap: '#20282a' },
  macarthur: { tunic: '#3b3a33', skin: '#ecc9a4', hair: '#2f2a24', moustache: '#3d332b', cap: '#242a2c', stout: true },
  moore:     { tunic: '#2f3f4a', skin: '#f2cca8', hair: '#3a2c22', cap: '#1e2a30' },
  muirhead:  { tunic: '#20303c', skin: '#f0cba8', hair: '#3b2f26', cap: '#141d24', glasses: true, suit: true, shirt: '#e8e2d4', tie: '#5a3a3a' },
  harvie:    { tunic: '#1f2b36', skin: '#eec9a6', hair: '#2a2420', cap: '#101820', suit: true, shirt: '#e6e0d2', tie: '#3f4d5a' },
};
const actor = (T, key, o, pos, extra = {}) =>
  ({ key, draw: (p) => T.romanFront(p, CAST[key], o), x: pos[0], y: pos[1], z: pos[2], ...extra });
const f30 = (f) => Math.round((f / FPS) * 30);      // motion math is authored at 30 fps
const pose = (f, seed, expr = 'neutral', extra = {}) =>
  ({ seed, expr, blink: blinkAt(f30(f), seed), ...idle(f30(f), seed), ...extra });

export const actorsAt = (f, T) => {
  const S = shotAt(f), out = [];
  const add = (k, o, pos, x = {}) => out.push(actor(T, k, o, pos, x));
  switch (S.id) {
    case 's3': // keeper in the bow, watching the dark rock
      add('moore', pose(f, 5, 'stern', { L: 'hang', R: 'reach', facing: 0.35, look: -0.2, lift: 0.5 }), [-52, 2.2, 31], { s: 1.0 });
      break;
    case 's9': // Muirhead + Moore on the path under the tower
      add('muirhead', pose(f, 7, 'stern', { L: 'hip', R: 'point', facing: -0.55, look: 0.3, tilt: 1.6 }), [7.0, 34.9, 10.2], { s: 1.0 });
      add('moore', pose(f, 5, 'nervous', { L: 'cross', R: 'cross', facing: 0.5, look: -0.2, tilt: -1.2 }), [8.9, 34.9, 8.9], { s: 0.99 });
      break;
    case 's10': { // the three, as the legend draws them
      const g = { alpha: 0.62, tint: '#8fb6d2', shadow: false };
      add('ducat', pose(f, 3, 'shock', { L: 'up', R: 'up', facing: 0.25, look: -0.1 }), [7.3, 34.9, 10.4], { ...g, s: 1.0 });
      add('marshall', pose(f, 9, 'shock', { L: 'up', R: 'up', facing: -0.2, look: 0.15 }), [8.9, 34.9, 9.3], { ...g, s: 0.98 });
      add('macarthur', pose(f, 13, 'shock', { L: 'cheek', R: 'cheek', facing: 0.1, look: 0 }), [10.4, 34.9, 8.2], { ...g, s: 0.96 });
      break;
    }
  }
  return out;
};
export const fxAt = () => [];
