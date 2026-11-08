import { camFromKeys, blinkAt, idle } from './motion.js';
import { TL } from './timeline.js';

/* THE GARDNER HEIST — "Thirteen Empty Frames" (18 March 1990)
   12 cuts, 180 fps master (10,231 frames). Camera moves are authored in
   shot-relative frames and normalised per shot. */
export const FPS = TL.fps, TOTAL = TL.total, DECK = 0.04;
export const SHOTS = TL.shots.map((s) => ({ id: s.id, a: s.f0, b: s.f1, light: s.light, loc: s.loc, len: s.len_f, vo: s.vo }));
export const shotAt = (f) => SHOTS.find((s) => f >= s.a && f <= s.b) || (f < SHOTS[0].a ? SHOTS[0] : SHOTS[SHOTS.length - 1]);

const base = {
  hemi: 0.9, fogNear: 26, fogFar: 260, sat: 1.08, vig: 0.24, shadowExt: 26,
  waterDeep: '#000000', waterShal: '#000000', glint: '#000000', sunSize: 0, sunDisc: '#000000',
};
export const LIGHTS = {
  streetNight: { ...base, az: 196, el: 46, hemi: 1.15, sky: '#6b82a8', ground: '#1d2531', sun: '#c3d2ec', sunI: 2.4,
    fog: '#1b2432', fogNear: 40, fogFar: 420, skyTop: '#0a1220', skyHor: '#2d3d52',
    gain: '#eef3ff', lift: '#05070c', sat: 1.1, vig: 0.34, shadowExt: 40 },
  streetDoor: { ...base, az: 200, el: 38, hemi: 1.2, sky: '#7b8aa4', ground: '#20222a', sun: '#d0dcee', sunI: 2.3,
    fog: '#232b38', fogNear: 26, fogFar: 260, skyTop: '#0d1524', skyHor: '#37465c',
    gain: '#fff2df', lift: '#080a0e', sat: 1.12, vig: 0.32, shadowExt: 20 },
  hallNight: { ...base, az: 210, el: 40, hemi: 1.1, sky: '#7d6a52', ground: '#2a2118', sun: '#efd8b6', sunI: 2.0,
    fog: '#2a2018', fogNear: 14, fogFar: 120, skyTop: '#141821', skyHor: '#3a3228',
    gain: '#fff0da', lift: '#0a0806', sat: 1.06, vig: 0.34, shadowExt: 16 },
  cellarDim: { ...base, az: 200, el: 44, hemi: 1.15, sky: '#5b6773', ground: '#1b2126', sun: '#c3d0dc', sunI: 1.9,
    fog: '#232a30', fogNear: 8, fogFar: 60, skyTop: '#0c1116', skyHor: '#2a323a',
    gain: '#e8f0f6', lift: '#05070a', sat: 0.95, vig: 0.4, shadowExt: 12 },
  dutchNight: { ...base, az: 200, el: 36, hemi: 1.05, sky: '#5f6f6a', ground: '#1a2220', sun: '#e4ecdf', sunI: 2.2,
    fog: '#222c28', fogNear: 16, fogFar: 110, skyTop: '#0b1214', skyHor: '#2b3a36',
    gain: '#f6f9f2', lift: '#060a0a', sat: 1.14, vig: 0.32, shadowExt: 16 },
  dutchDawn: { ...base, az: 88, el: 12, hemi: 1.5, sky: '#a8bccd', ground: '#4d555f', sun: '#e2ecf4', sunI: 2.6,
    fog: '#9fb2c2', fogNear: 22, fogFar: 180, skyTop: '#6f8aa4', skyHor: '#c8d5dd',
    gain: '#f4faff', lift: '#080c12', sat: 0.98, vig: 0.3, shadowExt: 18 },
  dutchDay: { ...base, az: 96, el: 34, hemi: 1.45, sky: '#9a8462', ground: '#3f3325', sun: '#ffdcae', sunI: 2.8,
    fog: '#2e2720', fogNear: 18, fogFar: 140, skyTop: '#243040', skyHor: '#4c4034',
    gain: '#fff4e4', lift: '#0b0908', sat: 1.16, vig: 0.26, shadowExt: 16 },
};
export const lightFor = (S) => LIGHTS[S.light] || LIGHTS.dutchNight;

/* ---------------- cameras: keys are shot-relative frames ---------------- */
const CAMS = {
  // S1 — crane from above the street down to the side door
  s1: [{ f: 0, pos: [0.5, 13.0, 27.0], look: [12.0, 6.5, -5.0], fov: 38 },
       { f: 1185, pos: [21.6, 3.1, 6.4], look: [15.4, 1.9, -4.8], fov: 42, ease: 'smooth', path: [[8.0, 10.0, 20.0], [16.4, 5.2, 11.5]] }],
  // S2 — the side door and the intercom
  s2: [{ f: 0, pos: [23.2, 1.95, -0.4], look: [15.9, 1.45, -4.6], fov: 46 },
       { f: 610, pos: [22.1, 1.9, -1.5], look: [15.95, 1.4, -4.6], fov: 40, ease: 'smooth' }],
  // S3 — the hall: guard at the desk, the two at the door
  s3: [{ f: 0, pos: [2.2, 2.1, 1.2], look: [-2.3, 1.5, 6.4], fov: 50 },
       { f: 1028, pos: [1.4, 2.0, 3.0], look: [-2.5, 1.5, 6.2], fov: 42, ease: 'smooth', path: [[1.8, 2.05, 2.1]] }],
  // S4 — the cellar: two guards taped against the pipes
  s4: [{ f: 0, pos: [3.1, 1.75, 3.3], look: [-0.35, 1.15, -2.4], fov: 50 },
       { f: 975, pos: [2.3, 1.6, 2.3], look: [-0.35, 1.1, -2.45], fov: 44, ease: 'smooth', path: [[2.8, 1.68, 2.9]] }],
  // S5 — into the Dutch Room, both torches sweeping the wall
  s5: [{ f: 0, pos: [4.3, 1.85, 5.6], look: [-4.30, 1.9, 2.1], fov: 46 },
       { f: 886, pos: [3.7, 1.8, 4.6], look: [-4.30, 1.85, 1.9], fov: 44, ease: 'smooth', path: [[4.0, 1.82, 5.1]] }],
  // S6 — the Vermeer, one of thirty-four
  s6: [{ f: 0, pos: [2.6, 2.45, 1.3], look: [-4.34, 2.52, -0.8], fov: 34 },
       { f: 919, pos: [1.05, 2.43, 0.05], look: [-4.34, 2.5, -0.8], fov: 34, ease: 'smooth', path: [[1.9, 2.44, 0.75]] }],
  // S7 — the canvas comes out of the frame
  s7: [{ f: 0, pos: [1.55, 2.5, -0.8], look: [-4.34, 2.5, -0.8], fov: 36 },
       { f: 919, pos: [0.55, 2.44, -0.8], look: [-4.34, 2.44, -0.8], fov: 34, ease: 'smooth', path: [[1.05, 2.47, -0.8]] }],
  // S8 — wide: thirteen empty frames
  s8: [{ f: 0, pos: [3.6, 2.2, 5.4], look: [-4.30, 2.2, 2.1], fov: 56 },
       { f: 539, pos: [2.9, 2.15, 4.4], look: [-4.30, 2.15, 1.9], fov: 52, ease: 'smooth' }],
  // S9 — the car pulls away
  s9: [{ f: 0, pos: [12.0, 5.2, 25.0], look: [19.6, 1.3, 8.4], fov: 42 },
       { f: 573, pos: [15.0, 3.9, 21.4], look: [20.3, 1.2, 8.3], fov: 36, ease: 'smooth', path: [[13.6, 4.6, 23.3]] }],
  // S10 — dawn on the empty wall
  s10: [{ f: 0, pos: [3.02, 2.45, 2.0], look: [-4.30, 2.42, 1.8], fov: 52 },
        { f: 1045, pos: [1.1, 2.42, -1.1], look: [-4.30, 2.4, -0.7], fov: 42, ease: 'smooth', path: [[2.3, 2.44, 0.6]] }],
  // S11 — today, visitors under the empty frames
  s11: [{ f: 0, pos: [4.9, 2.0, 4.6], look: [-3.9, 2.15, 1.7], fov: 50 },
        { f: 729, pos: [4.0, 1.95, 3.9], look: [-3.9, 2.1, 1.6], fov: 46, ease: 'smooth' }],
  // S12 — the empty Vermeer frame, held
  s12: [{ f: 0, pos: [2.6, 2.5, -0.4], look: [-4.34, 2.45, -0.4], fov: 40 },
        { f: 599, pos: [3.6, 2.45, -0.15], look: [-4.34, 2.4, -0.5], fov: 33, ease: 'smooth' }],
};



const absKeys = {};
export const camAt = (f) => {
  const S = shotAt(f);
  const K = absKeys[S.id] || (absKeys[S.id] = (() => {
    const k = (S.len - 1) / (CAMS[S.id][CAMS[S.id].length - 1].f || 1);
    return CAMS[S.id].map((c) => ({ ...c, f: S.a + Math.round(c.f * k) }));
  })());
  return camFromKeys(K, f, { creep: 0.0014, kicks: S.id === 's9' ? [{ f: S.a + 380, a: 0.7 }] : [] });
};

const DOF = {
  s1: { c: 0, t: [15.7, 2.1, -5.6] }, s2: { c: 7, t: [15.7, 1.9, -5.5] }, s3: { c: 6, t: [-2.6, 1.5, 5.6] },
  s4: { c: 5, t: [-0.35, 1.15, -2.4] }, s5: { c: 4, t: [-4.3, 2.7, 2.1] }, s6: { c: 8, t: [-4.3, 2.5, -0.8] },
  s7: { c: 11, t: [-4.3, 2.5, -0.8] }, s8: { c: 0, t: [-4.3, 2.6, 2.1] }, s9: { c: 4, t: [19.8, 1.2, 8.35] },
  s10: { c: 2, t: [-4.3, 2.6, 1.4] }, s11: { c: 4, t: [-3.6, 2.4, 2.1] }, s12: { c: 9, t: [-4.3, 2.5, -0.8] },
};


export const dofAt = (f) => {
  const S = shotAt(f), C = camAt(f), D = DOF[S.id];
  const d = Math.hypot(C.pos[0] - D.t[0], C.pos[1] - D.t[1], C.pos[2] - D.t[2]);
  return { focus: d, cinf: D.c, near: 1 };
};

export const worldAt = (f) => ({ location: shotAt(f).loc });

/* ---------------- cast ---------------- */
export const CAST = {
  guardA: { tunic: '#2c3a4a', skin: '#f0c8a2', hair: '#33261f', cap: '#1a2432', suit: true, shirt: '#dbe3e9', tie: '#1a2432' },
  guardB: { tunic: '#26323f', skin: '#e8c09a', hair: '#2a2320', cap: '#151d28', suit: true, shirt: '#d6dee4', tie: '#151d28', moustache: '#3a2b22', stout: true },
  thiefA: { tunic: '#1e2a3c', skin: '#efc7a1', hair: '#2b211c', cap: '#131b28', suit: true, shirt: '#c8d2da', tie: '#131b28' },
  thiefB: { tunic: '#22303f', skin: '#e6bf98', hair: '#221c18', cap: '#16202c', suit: true, shirt: '#c8d2da', tie: '#16202c', moustache: '#2b211c' },
  visitorA: { tunic: '#c2733a', skin: '#f5c9a0', hair: '#5a3b2a', dress: '#3f6a8f' },
  visitorB: { tunic: '#3f6a8f', skin: '#e8c6a6', hair: '#2b211c', suit: true, shirt: '#efe9dc', tie: '#8a554d' },
  agent: { tunic: '#31404f', skin: '#e8c6a6', hair: '#2b211c', suit: true, shirt: '#e8e0d3', tie: '#5b3941' },
};
const actor = (T, key, o, pos, extra = {}) =>
  ({ key, draw: (p) => T.romanFront(p, CAST[key], o), x: pos[0], y: pos[1], z: pos[2], ...extra });
const f30 = (f) => Math.round((f / FPS) * 30);
const pose = (f, seed, expr = 'neutral', extra = {}) =>
  ({ seed, expr, blink: blinkAt(f30(f), seed), ...idle(f30(f), seed), ...extra });

export const actorsAt = (f, T) => {
  const S = shotAt(f), out = [];
  const add = (k, o, pos, x = {}) => out.push(actor(T, k, o, pos, x));
  switch (S.id) {
    case 's1':   // two figures walking up to the side door
      add('thiefA', pose(f, 3, 'neutral', { L: 'hip', R: 'hang', facing: 0.5 }), [16.4, 0.02, -3.3], { s: 1.0 });
      add('thiefB', pose(f, 9, 'squint', { L: 'hang', R: 'hip', facing: 0.3 }), [15.3, 0.02, -3.9], { s: 0.98 });
      break;
    case 's2':   // at the door, one hand on the intercom
      add('thiefA', pose(f, 3, 'neutral', { L: 'reach', R: 'hang', facing: 0.45, lift: 0.85 }), [16.0, 0.02, -4.25], { s: 1.0 });
      add('thiefB', pose(f, 9, 'squint', { L: 'hip', R: 'hip', facing: -0.35 }), [14.35, 0.02, -4.6], { s: 0.98 });
      break;
    case 's3':   // the guard rises behind the desk; two dark figures in the doorway
      add('guardA', pose(f, 5, 'shock', { L: 'up', R: 'hang', facing: -0.35, tilt: 1.6 }), [-2.35, 0.02, 5.85], { s: 1.0 });
      add('thiefA', pose(f, 3, 'stern', { L: 'point', R: 'hang', facing: 0.35 }), [0.55, 0.02, 8.0], { s: 1.0, alpha: 0.9 });
      add('thiefB', pose(f, 9, 'stern', { L: 'hang', R: 'hip', facing: -0.3 }), [1.75, 0.02, 8.15], { s: 0.98, alpha: 0.9 });
      break;
    case 's4':   // the two guards, taped, sitting against the pipes
      add('guardA', pose(f, 5, 'pained', { L: 'cross', R: 'cross', facing: 0.3, look: 0.1, tilt: -1.8 }), [-0.95, 0.02, -2.35], { s: 0.92, roll: 0.1 });
      add('guardB', pose(f, 11, 'pained', { L: 'cross', R: 'cross', facing: -0.25, look: -0.1, tilt: 1.4 }), [0.25, 0.02, -2.45], { s: 0.9, roll: -0.09 });
      break;
    case 's5':   // into the room
      add('thiefA', pose(f, 3, 'squint', { L: 'lift', R: 'hang', facing: 0.3, look: 0.25 }), [-2.5, 0.02, 3.4], { s: 1.0 });
      add('thiefB', pose(f, 9, 'squint', { L: 'hang', R: 'lift', facing: -0.25 }), [-1.6, 0.02, 2.5], { s: 0.98 });
      break;
    case 's6':   // beside the Vermeer
      add('thiefA', pose(f, 3, 'squint', { L: 'lift', R: 'reach', facing: 0.9, look: 0.35 }), [-4.35, 0.02, 0.75], { s: 1.0 });
      break;
    case 's7':   // hands on the canvas as it comes free
      
      
      break;
    case 's8':   // carrying rolled canvases out
      add('thiefA', pose(f, 3, 'neutral', { L: 'belly', R: 'lift', facing: 1.0 }), [-3.0, 0.02, 2.4], { s: 1.0 });
      add('thiefB', pose(f, 9, 'neutral', { L: 'lift', R: 'belly', facing: 0.7 }), [-2.2, 0.02, 1.35], { s: 0.97 });
      break;
    case 's11':  // visitors, today
      add('visitorA', pose(f, 7, 'neutral', { L: 'hip', R: 'hang', facing: -0.4, look: 0.25 }), [-2.8, 0.02, 2.3], { s: 1.0 });
      add('visitorB', pose(f, 13, 'neutral', { L: 'hang', R: 'hip', facing: 0.35, look: -0.1 }), [-2.0, 0.02, 1.5], { s: 1.02 });
      break;
    case 's12':
      break;
  }
  return out;
};

/* ---------------- torch beams (thieves' flashlights) ---------------- */
export const torchAt = (f) => {
  const S = shotAt(f);
  if (!(S.id === 's5' || S.id === 's6' || S.id === 's7' || S.id === 's8')) return [];
  const k = (f - S.a) / Math.max(1, S.b - S.a);
  if (S.id === 's5') {
    const p = Math.min(1, k * 1.4);
    return [
      { from: [-1.4, 1.6, 3.7], to: [-5.7, 2.3 + 0.5 * p, -4.2 + 2.6 * p] },
      { from: [0.1, 1.55, 2.9], to: [3.0 - 1.2 * p, 2.6, -6.6] },
    ];
  }
  if (S.id === 's6') return [{ from: [-3.7, 1.6, 0.5], to: [-5.85, 2.5, -1.0] }];
  if (S.id === 's7') return [{ from: [-3.8, 1.7, 0.6], to: [-5.85, 2.45, -1.0] }];
  return [{ from: [-1.4, 1.5, -2.6], to: [-5.8, 2.4, -1.0] }];
};
if (typeof window !== 'undefined') window.__torch = torchAt;

export const fxAt = () => [];
