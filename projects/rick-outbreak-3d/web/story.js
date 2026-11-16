// V3 Master Fast-Paced Horror Choreography & Camera Cut Timeline (0.00s -> 260.35s, 82 Kinetic Cuts!)
// 100% Synced to UNEDITED ElevenLabs v4 Voiceover (`words_v3.json`, 660 words, 260.32s / 7,810 frames @ 30fps)
// Featuring:
// - Fast dynamic camera movement (`camera motion fast`: whip-pans, rapid push-ins, sprint tracking, Dutch shock tilts)
// - Velocity-locked biomechanical running (`Logon ka bhagna ka movement sahi kro`: zero sliding, zero moonwalking)
// - 100% completely closed storefront shutters (`sheleter bnd bilkul`: unrolls flush to floor y=0.00m!)
// - Situation-accurate main-character & survivor facial acting + nightmare horror zombies!

const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);
const lerp = (a, b, t) => a + (b - a) * t;
const smooth = (t) => t * t * (3 - 2 * t);
// C2-continuous glide (zero velocity AND acceleration at both ends) — rulebook "smootherstep".
const smootherstep = (t) => t * t * t * (t * (t * 6 - 15) + 10);
// V6: smooth hex color crossfade for the blended lighting rig.
const hexLerp = (a, b, u) => {
  const pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16);
  const r = Math.round(((pa >> 16) & 255) + ((((pb >> 16) & 255) - ((pa >> 16) & 255)) * u));
  const g = Math.round(((pa >> 8) & 255) + ((((pb >> 8) & 255) - ((pa >> 8) & 255)) * u));
  const bl = Math.round((pa & 255) + (((pb & 255) - (pa & 255)) * u));
  return `#${((r << 16) | (g << 8) | bl).toString(16).padStart(6, '0')}`;
};
const easeOut = (t, a, b) => smooth(clamp01((t - a) / Math.max(0.0001, b - a)));

/**
 * Screen-space ray solver: guarantees every moving human/zombie faces the EXACT screen direction
 * of their velocity vector (or opposite when `reverseWalk` is true, e.g. backing away from zombies!).
 */
function solveMoveFacing(pos, vel, camPos, reverseWalk = false) {
  const spd = Math.hypot(vel[0], vel[2]);
  if (spd < 0.02) return { view: 'front', flipX: false };

  // Direction character's FRONT faces in world XZ
  const faceVecX = reverseWalk ? -vel[0] : vel[0];
  const faceVecZ = reverseWalk ? -vel[2] : vel[2];

  let fx = pos[0] - camPos[0];
  let fz = pos[2] - camPos[2];
  const fl = Math.hypot(fx, fz) || 1;
  fx /= fl; fz /= fl;
  // Camera right vector in XZ plane: cross(ray, up=[0,1,0]) = [-fz, 0, fx]
  const rx = -fz, rz = fx;

  const vRight = (faceVecX * rx + faceVecZ * rz) / spd;
  const vAway  = (faceVecX * fx + faceVecZ * fz) / spd;

  if (!reverseWalk && vAway > 0.80 && Math.abs(vRight) < 0.58) {
    return { view: 'backFull', flipX: false };
  }
  if (Math.abs(vAway) > 0.52) {
    return { view: 'threeQuarter', flipX: vRight < 0 };
  }
  return { view: 'side', flipX: vRight < 0 };
}

export const SHOTS = [
  // ================= V6.5 ORIGINS COLD OPEN (0.00 - 3.36s) =================
  // VO over this: "The first warning comes at 4:17 PM."
  // Busy family life -> HIDDEN LAB (masked evil scientist) -> THE RELEASE -> breaking news
  // -> nationwide destruction -> OUTBREAK TITLE SMASH -> hard cut to the bright ordinary afternoon.
  // `lx` = per-beat cinematic light override (hard montage cuts, no slow crossfade).
  { id: 200, t0: 0.00, t1: 0.62, zone: 'street', p0: [2.6, 1.12, 15.0], p1: [0.9, 1.06, 14.6], l0: [1.2, 0.90, 13.5], l1: [-0.2, 0.85, 13.5], fov0: 44, fov1: 40, roll: 1.1, shake: 0.014,
    lx: { sky: '#8fb4d4', sun: 1.68, amb: 0.92, store: 0.85, fridge: 0.80, tint: '#fff3e2', shaft: 0.050, dome: '#d8eaf8', win: 0.00 } },
  { id: 201, t0: 0.62, t1: 1.24, zone: 'lab',   p0: [-38.1, 1.75, -9.7], p1: [-39.1, 1.62, -10.5], l0: [-40.2, 1.25, -14.9], l1: [-40.3, 1.30, -14.9], fov0: 46, fov1: 41, roll: -1.4,
    lx: { sky: '#0a0e14', sun: 0.00, amb: 0.60, store: 0.00, fridge: 0.00, tint: '#cfe4ff', shaft: 0.000, dome: '#0a0e14', win: 0.00 } },
  { id: 202, t0: 1.24, t1: 1.80, zone: 'lab',   p0: [-39.55, 1.52, -13.15], p1: [-39.66, 1.49, -13.32], l0: [-40.50, 1.56, -14.55], l1: [-40.54, 1.55, -14.60], fov0: 33, fov1: 29, roll: 1.8, shake: 0.010,
    lx: { sky: '#0a0e14', sun: 0.00, amb: 0.52, store: 0.00, fridge: 0.00, tint: '#cfe4ff', shaft: 0.000, dome: '#0a0e14', win: 0.00 } },
  { id: 203, t0: 1.80, t1: 2.42, zone: 'lab',   p0: [-35.20, 1.38, -11.20], p1: [-35.90, 1.30, -11.95], l0: [-36.85, 1.05, -14.10], l1: [-36.95, 1.00, -14.30], fov0: 49, fov1: 45, shake: 0.062, roll: -2.4,
    lx: { sky: '#0a0e14', sun: 0.00, amb: 0.48, store: 0.00, fridge: 0.00, tint: '#ffcfc4', shaft: 0.000, dome: '#0a0e14', win: 0.00 } },
  { id: 204, t0: 2.42, t1: 2.94, zone: 'news',  p0: [-38.35, 1.62, -45.5], p1: [-39.15, 1.56, -46.3], l0: [-40.0, 1.40, -49.7], l1: [-40.0, 1.35, -49.9], fov0: 44, fov1: 38, roll: 1.2,
    lx: { sky: '#0a0d12', sun: 0.00, amb: 0.62, store: 0.00, fridge: 0.00, tint: '#ffd9d4', shaft: 0.000, dome: '#0a0d12', win: 0.00 } },
  { id: 205, t0: 2.94, t1: 3.36, zone: 'street', p0: [0.7, 1.62, 8.6],  p1: [-0.4, 1.56, 9.3],  l0: [0.0, 1.05, 16.5], l1: [0.0, 1.00, 16.8],  fov0: 50, fov1: 46, shake: 0.048, roll: 2.0,
    lx: { sky: '#2b0d08', sun: 0.20, amb: 0.68, store: 0.00, fridge: 0.00, tint: '#ffd9c4', shaft: 0.000, dome: '#431409', win: 0.00 } },
  // ================= ACT I: 4:17 PM ALERT & STREET CHAOS (0.00 - 42.60s) =================
  // Hard cut out of the nightmare: BRIGHT peaceful afternoon — the quiet world before it ended.
  { id: 0,  t0: 3.36, t1: 4.10, zone: 'street', p0: [9.5, 12.5, 22.5], p1: [4.5, 6.0, 19.5],    l0: [0.0, 1.7, 8.0],  l1: [0.4, 1.6, 9.0],   fov0: 50, fov1: 45 },
  { id: 1,  t0: 4.10, t1: 4.88, zone: 'store',  p0: [0.85, 1.80, 6.35],  p1: [2.12, 1.58, 5.35],  l0: [2.92, 1.36, 3.05],  l1: [3.06, 1.38, 3.05],  fov0: 46, fov1: 39 },
  // Phone screen close-ups: 4:17 PM Emergency Alert (full bezel + status bar + fingers in frame!)
  { id: 3,  t0: 4.88,  t1: 7.40,  zone: 'store',  p0: [2.86, 1.42, 2.20],  p1: [2.90, 1.40, 2.32],  l0: [3.02, 1.36, 3.10],  l1: [3.02, 1.36, 3.10],  fov0: 40, fov1: 36 },
  { id: 4,  t0: 7.40,  t1: 10.15, zone: 'store',  p0: [2.90, 1.40, 2.32],  p1: [2.88, 1.40, 2.25],  l0: [3.02, 1.36, 3.10],  l1: [3.02, 1.36, 3.10],  fov0: 36, fov1: 34, roll: 1.4 },
  { id: 5,  t0: 10.15, t1: 12.36, zone: 'store',  p0: [2.38, 1.42, 4.78],  p1: [2.62, 1.40, 4.42],  l0: [3.10, 1.38, 3.25],  l1: [3.10, 1.38, 3.25],  fov0: 36, fov1: 32 },
  { id: 6,  t0: 12.36, t1: 16.00, zone: 'store',  p0: [2.89, 1.40, 2.26],  p1: [2.91, 1.39, 2.33],  l0: [3.02, 1.36, 3.10],  l1: [3.02, 1.36, 3.10],  fov0: 37, fov1: 34, roll: -1.6 },
  { id: 7,  t0: 16.00, t1: 17.60, zone: 'store',  p0: [2.58, 1.42, 4.55],  p1: [2.25, 1.44, 5.15],  l0: [3.10, 1.38, 3.25],  l1: [2.60, 1.38, 5.50],  fov0: 35, fov1: 38 },

  // Street sequence: Traffic stops -> Man staring at nothing -> Sprints full-stride at passing car -> Swerve -> Panicked runners!
  { id: 8,  t0: 17.60, t1: 20.40, zone: 'street', p0: [3.20, 1.85, 10.40], p1: [0.60, 1.65, 11.40], l0: [-2.20, 0.95, 15.80], l1: [-1.80, 1.05, 16.00], fov0: 46, fov1: 41 },
  { id: 9,  t0: 20.40, t1: 24.00, zone: 'street', p0: [-0.45, 1.52, 12.10],p1: [-1.65, 1.38, 13.10],l0: [-2.40, 1.22, 16.20], l1: [-2.40, 1.32, 16.20], fov0: 42, fov1: 34, roll: -1.5 },
  { id: 10, t0: 24.00, t1: 26.96, zone: 'street', p0: [-1.80, 1.45, 11.80],p1: [2.40, 1.42, 11.80], l0: [-1.80, 1.05, 16.20], l1: [3.40, 1.05, 16.20],  fov0: 45, fov1: 40, shake: 0.032, roll: 2.2 },
  { id: 11, t0: 26.96, t1: 28.25, zone: 'street', p0: [2.40, 1.50, 10.90], p1: [0.80, 1.42, 10.40], l0: [3.60, 0.95, 15.60],  l1: [1.80, 0.95, 14.20],  fov0: 48, fov1: 42, shake: 0.075, roll: -3.5 },
  { id: 12, t0: 28.25, t1: 31.00, zone: 'street', p0: [-2.20, 1.36, 13.50],p1: [2.80, 1.36, 13.50], l0: [-2.40, 1.05, 9.60],  l1: [3.20, 1.05, 9.60],   fov0: 44, fov1: 41, shake: 0.025 },
  { id: 13, t0: 31.00, t1: 32.88, zone: 'store',  p0: [1.65, 1.52, 5.40],  p1: [2.35, 1.42, 4.65],  l0: [3.05, 1.30, 3.45],   l1: [3.08, 1.34, 3.35],   fov0: 44, fov1: 36, shake: 0.030 },

  // Store layout vulnerability tour ("working alone... front windows... narrow delivery alley... neither feels safe")
  { id: 14, t0: 32.88, t1: 35.60, zone: 'store',  p0: [-1.40, 1.95, 5.80], p1: [0.85, 1.65, 4.80],  l0: [2.80, 1.25, 2.80],   l1: [3.05, 1.30, 3.25],   fov0: 48, fov1: 42 },
  { id: 15, t0: 35.60, t1: 37.60, zone: 'store',  p0: [0.20, 1.52, 3.20],  p1: [-0.60, 1.46, 5.10], l0: [0.00, 1.45, 9.50],   l1: [-1.20, 1.40, 12.00], fov0: 46, fov1: 41 },
  { id: 16, t0: 37.60, t1: 40.60, zone: 'back',   p0: [2.80, 1.58, -8.40], p1: [2.80, 1.50, -12.60],l0: [2.80, 1.45, -16.32], l1: [2.80, 1.48, -16.32], fov0: 45, fov1: 39 },
  { id: 17, t0: 40.60, t1: 42.60, zone: 'store',  p0: [1.95, 1.42, 4.85],  p1: [1.35, 1.40, 5.55],  l0: [0.65, 1.35, 6.45],   l1: [0.25, 1.35, 6.85],   fov0: 40, fov1: 35, roll: 1.5 },

  // ================= ACT II: LOCKDOWN, FULL SHUTTER SLAM, WOMAN & POLICE HORDE (42.60 - 80.48s) =================
  // Locking front deadbolt
  { id: 18, t0: 42.60, t1: 44.12, zone: 'store',  p0: [0.65, 1.40, 5.75],  p1: [0.32, 1.36, 6.28],  l0: [0.00, 1.35, 7.38],   l1: [0.00, 1.35, 7.38],   fov0: 38, fov1: 29 },
  // HERO FULL-SHUTTER CLOSE SHOT ("Pull down the metal shutter" -> rolls 100% flush to floor y=0.00m!)
  { id: 19, t0: 44.12, t1: 45.80, zone: 'store',  p0: [0.45, 1.55, 2.85],  p1: [-0.15, 1.42, 3.45], l0: [-2.65, 1.55, 7.32],  l1: [-2.85, 1.15, 7.32],  fov0: 50, fov1: 46, shake: 0.018 },
  // Switching off the lights -> silent dark store
  { id: 20, t0: 45.80, t1: 48.00, zone: 'store',  p0: [-0.25, 1.44, 5.20], p1: [0.35, 1.40, 5.75],  l0: [1.20, 1.32, 7.15],   l1: [1.30, 1.32, 7.25],   fov0: 42, fov1: 36 },
  { id: 21, t0: 48.00, t1: 50.76, zone: 'store',  p0: [-1.35, 1.50, 3.60], p1: [-0.45, 1.44, 4.55], l0: [0.65, 1.30, 6.80],   l1: [0.35, 1.32, 7.10],   fov0: 46, fov1: 41 },

  // BAM! Woman hits reinforced entrance door glass!
  { id: 22, t0: 50.76, t1: 52.92, zone: 'store',  p0: [0.10, 1.40, 5.15],  p1: [0.24, 1.36, 5.95],  l0: [0.52, 1.32, 7.95],   l1: [0.55, 1.32, 7.95],   fov0: 43, fov1: 34, shake: 0.048, roll: -2.4 },
  { id: 23, t0: 52.92, t1: 56.04, zone: 'store',  p0: [0.24, 1.36, 5.95],  p1: [0.32, 1.34, 6.22],  l0: [0.55, 1.30, 7.95],   l1: [0.55, 1.30, 7.95],   fov0: 35, fov1: 31 },
  { id: 24, t0: 56.04, t1: 58.00, zone: 'store',  p0: [0.32, 1.34, 6.22],  p1: [0.36, 1.34, 6.32],  l0: [0.55, 1.30, 7.95],   l1: [0.62, 1.32, 8.15],   fov0: 32, fov1: 30 },
  { id: 25, t0: 58.00, t1: 59.88, zone: 'store',  p0: [0.36, 1.34, 6.32],  p1: [0.40, 1.34, 6.45],  l0: [0.55, 1.32, 7.95],   l1: [0.55, 1.33, 7.95],   fov0: 30, fov1: 27 },
  { id: 26, t0: 59.88, t1: 61.28, zone: 'store',  p0: [-0.65, 1.40, 6.45], p1: [-0.48, 1.38, 6.62], l0: [0.05, 1.35, 7.15],   l1: [0.02, 1.35, 7.28],   fov0: 38, fov1: 34 },

  // Across the street: Police Officer slowly backs away from lunging nightmare zombie horde!
  // (Wide pulled-back framing: police screen-right, lead infected lunging in from screen-left!)
  { id: 27, t0: 61.28, t1: 64.20, zone: 'street', p0: [0.90, 1.62, 9.40],  p1: [-0.20, 1.55, 9.60], l0: [0.20, 1.15, 17.50],  l1: [-0.70, 1.15, 17.50], fov0: 48, fov1: 46, roll: 1.8 },
  { id: 28, t0: 64.20, t1: 66.84, zone: 'street', p0: [-0.20, 1.55, 9.60], p1: [-0.90, 1.50, 10.30],l0: [-0.70, 1.15, 17.50], l1: [-1.50, 1.15, 17.50], fov0: 48, fov1: 46, shake: 0.022, roll: -2.0 },

  // Woman turns back -> Her expression changes into chilling uncanny infected stare!
  { id: 29, t0: 66.84, t1: 69.96, zone: 'store',  p0: [0.34, 1.38, 6.14],  p1: [0.42, 1.38, 6.44],  l0: [0.55, 1.46, 7.95],   l1: [0.55, 1.48, 7.95],   fov0: 34, fov1: 29, roll: -1.8 },
  { id: 30, t0: 69.96, t1: 71.88, zone: 'store',  p0: [0.42, 1.40, 6.44],  p1: [0.45, 1.40, 6.58],  l0: [0.55, 1.50, 7.95],   l1: [0.55, 1.50, 7.95],   fov0: 32, fov1: 29, roll: 2.0 },
  // YOU steps back in terror -> Slams final center door shutter 100% CLOSED TO FLOOR ("So you leave it locked")!
  { id: 31, t0: 71.88, t1: 75.92, zone: 'store',  p0: [-0.85, 1.42, 6.20], p1: [-1.15, 1.46, 4.95], l0: [0.05, 1.35, 6.40],   l1: [0.05, 1.35, 5.55],   fov0: 42, fov1: 38 },
  { id: 32, t0: 75.92, t1: 80.48, zone: 'store',  p0: [0.00, 1.54, 3.20],  p1: [0.00, 1.46, 3.85],  l0: [0.00, 1.55, 7.30],   l1: [0.00, 1.20, 7.30],   fov0: 48, fov1: 43 },

  // ================= ACT III: POWER CUT, FLASHLIGHT SUPPLIES & BACK-DOOR MIMIC (80.48 - 145.96s) =================
  { id: 33, t0: 80.48, t1: 84.28, zone: 'store',  p0: [-1.80, 1.72, 4.60], p1: [0.25, 1.58, 3.60],  l0: [1.80, 1.30, 3.80],   l1: [2.85, 1.30, 3.80],   fov0: 48, fov1: 43 },
  { id: 34, t0: 84.28, t1: 87.20, zone: 'store',  p0: [1.65, 1.52, 2.85],  p1: [2.15, 1.50, 2.90],  l0: [3.35, 1.16, 4.05],   l1: [3.60, 1.12, 4.10],   fov0: 44, fov1: 40 },
  // Flashlight sweeping exact labeled supplies: 2 PURE WATER, TOMATO SOUP / BAKED BEANS / CHUNKY TUNA cans, CHOCOLATE bar, FIRST AID KIT
  { id: 35, t0: 87.20, t1: 92.16, zone: 'store',  p0: [2.10, 1.56, 2.30],  p1: [2.42, 1.46, 2.62],  l0: [3.55, 1.12, 4.05],   l1: [3.80, 1.10, 4.10],   fov0: 42, fov1: 37 },
  { id: 36, t0: 92.16, t1: 94.04, zone: 'store',  p0: [2.25, 1.42, 4.85],  p1: [2.48, 1.40, 4.55],  l0: [3.10, 1.36, 3.35],   l1: [3.10, 1.38, 3.35],   fov0: 36, fov1: 32 },

  // Metal crash in delivery alley -> Back door rattle -> Moving down dark corridor -> 3 slow knocks!
  { id: 37, t0: 94.04, t1: 97.16, zone: 'store',  p0: [1.95, 1.46, 3.85],  p1: [2.35, 1.48, 1.65],  l0: [2.80, 1.45, -7.35],  l1: [2.80, 1.45, -7.50],  fov0: 44, fov1: 38, shake: 0.042, roll: 2.2 },
  { id: 38, t0: 97.16, t1: 99.20, zone: 'back',   p0: [2.80, 1.52, -11.80],p1: [2.80, 1.48, -13.40],l0: [2.80, 1.45, -16.32], l1: [2.80, 1.48, -16.32], fov0: 42, fov1: 36, shake: 0.018 },
  { id: 39, t0: 99.20, t1: 103.56,zone: 'back',   p0: [3.55, 1.48, -9.20], p1: [3.35, 1.44, -12.40],l0: [2.65, 1.28, -12.20], l1: [2.68, 1.32, -14.80], fov0: 44, fov1: 40 },
  { id: 40, t0: 103.56,t1: 105.76,zone: 'back',   p0: [2.76, 1.52, -13.90],p1: [2.78, 1.55, -14.65],l0: [2.80, 1.52, -16.32], l1: [2.80, 1.62, -16.32], fov0: 38, fov1: 33, shake: 0.024 },
  { id: 41, t0: 105.76,t1: 107.76,zone: 'back',   p0: [3.35, 1.42, -15.35],p1: [3.22, 1.40, -15.15],l0: [2.65, 1.36, -13.95], l1: [2.65, 1.38, -13.95], fov0: 36, fov1: 32 },

  // Looking through tiny wire-mesh window -> Motionless nightmare horror shape staring straight in!
  { id: 42, t0: 107.76,t1: 109.64,zone: 'back',   p0: [2.78, 1.60, -14.65],p1: [2.80, 1.66, -15.25],l0: [2.80, 1.56, -16.32], l1: [2.80, 1.58, -16.85], fov0: 36, fov1: 30 },
  { id: 43, t0: 109.64,t1: 113.84,zone: 'back',   p0: [2.80, 1.66, -15.25],p1: [2.80, 1.68, -15.58],l0: [2.80, 1.58, -17.10], l1: [2.80, 1.58, -17.10], fov0: 30, fov1: 24, roll: -1.8 },

  // Second Emergency Alert on phone ("Do not respond to voices coming from outside. Some affected individuals may imitate familiar speech.")
  { id: 44, t0: 113.84,t1: 115.40,zone: 'back',   p0: [3.35, 1.42, -15.20],p1: [3.20, 1.40, -14.90],l0: [2.65, 1.36, -13.95], l1: [2.65, 1.36, -13.95], fov0: 38, fov1: 34, shake: 0.025 },
  { id: 45, t0: 115.40,t1: 120.20,zone: 'back',   p0: [2.60, 1.38, -12.96],p1: [2.63, 1.37, -13.04],l0: [2.66, 1.35, -13.80], l1: [2.66, 1.35, -13.80], fov0: 38, fov1: 34 },
  { id: 46, t0: 120.20,t1: 123.80,zone: 'back',   p0: [2.63, 1.37, -12.96],p1: [2.61, 1.37, -12.91],l0: [2.66, 1.35, -13.80], l1: [2.66, 1.35, -13.80], fov0: 36, fov1: 33.5, roll: 1.5 },

  // Brother's imitated voice calls through the door -> YOU freezes -> Steps away -> Huddles behind counter all night!
  { id: 47, t0: 123.80,t1: 128.96,zone: 'back',   p0: [2.80, 1.64, -15.32],p1: [2.80, 1.66, -15.62],l0: [2.80, 1.58, -17.10], l1: [2.80, 1.58, -17.10], fov0: 29, fov1: 23, shake: 0.015, roll: -2.2 },
  { id: 48, t0: 128.96,t1: 131.20,zone: 'back',   p0: [2.80, 1.46, -15.18],p1: [2.72, 1.45, -15.02],l0: [2.65, 1.48, -13.95], l1: [2.65, 1.49, -13.95], fov0: 34, fov1: 30, roll: -1.2 },
  // YOU frozen in terror — aimed at the card art's REAL face height (y≈1.05, not 1.5) so the
  // terror expression fills frame instead of cropping to the top of the head.
  { id: 49, t0: 131.20,t1: 134.36,zone: 'back',   p0: [2.72, 1.30, -15.28],p1: [2.67, 1.28, -15.16],l0: [2.65, 1.10, -13.95], l1: [2.65, 1.12, -13.95], fov0: 36, fov1: 33 },
  { id: 50, t0: 134.36,t1: 138.52,zone: 'back',   p0: [2.78, 1.56, -14.85],p1: [2.80, 1.62, -15.35],l0: [2.80, 1.56, -16.32], l1: [2.80, 1.60, -16.85], fov0: 36, fov1: 29, shake: 0.020 },
  { id: 51, t0: 138.52,t1: 140.08,zone: 'back',   p0: [3.35, 1.46, -14.80],p1: [3.42, 1.48, -13.20],l0: [2.68, 1.32, -13.40], l1: [2.68, 1.32, -11.80], fov0: 42, fov1: 39 },
  { id: 52, t0: 140.08,t1: 145.96,zone: 'store',  p0: [0.25, 1.34, 2.55],  p1: [0.68, 1.22, 3.05],  l0: [1.35, 0.92, 4.35],   l1: [1.35, 0.92, 4.35],   fov0: 44, fov1: 36 },

  // ================= ACT IV: SUNRISE EMPTY STREET, 1-BAR OFFLINE MAP & ALLEY SPRINT (145.96 - 188.40s) =================
  { id: 53, t0: 145.96,t1: 151.52,zone: 'street', p0: [-11.0, 13.0, 22.0], p1: [-4.20, 5.5, 20.2],   l0: [5.80, 1.20, 20.50], l1: [6.20, 1.00, 20.60],  fov0: 50, fov1: 44 },
  { id: 54, t0: 151.52,t1: 154.92,zone: 'street', p0: [-3.80, 1.55, 13.80],p1: [2.40, 1.48, 14.20], l0: [-1.20, 1.10, 22.80], l1: [4.50, 1.25, 24.50],  fov0: 45, fov1: 40 },
  { id: 55, t0: 154.92,t1: 158.28,zone: 'street', p0: [3.80, 1.75, 14.50], p1: [1.20, 1.62, 11.80], l0: [-2.00, 1.40, 24.60], l1: [0.00, 1.65, 8.20],   fov0: 44, fov1: 41 },

  // 1-Bar Battery + Offline Transit Station Map -> Packing Supplies -> Unlocking Back Door -> Fast Alley Escape!
  { id: 56, t0: 158.28,t1: 161.04,zone: 'store',  p0: [2.86, 1.41, 2.19],  p1: [2.90, 1.40, 2.30],  l0: [3.02, 1.36, 3.10],   l1: [3.02, 1.36, 3.10],   fov0: 40, fov1: 35 },
  { id: 57, t0: 161.04,t1: 165.24,zone: 'store',  p0: [2.90, 1.40, 2.30],  p1: [2.88, 1.40, 2.24],  l0: [3.02, 1.36, 3.10],   l1: [3.02, 1.36, 3.10],   fov0: 35, fov1: 33 },
  { id: 58, t0: 165.24,t1: 169.72,zone: 'store',  p0: [2.35, 1.44, 4.75],  p1: [2.62, 1.40, 4.38],  l0: [3.10, 1.36, 3.25],   l1: [3.10, 1.38, 3.25],   fov0: 38, fov1: 32 },
  { id: 59, t0: 169.72,t1: 173.52,zone: 'store',  p0: [1.85, 1.58, 2.95],  p1: [2.25, 1.48, 3.18],  l0: [2.85, 1.22, 4.08],   l1: [2.65, 1.24, 4.10],   fov0: 42, fov1: 36 },
  { id: 60, t0: 173.52,t1: 176.12,zone: 'store',  p0: [2.15, 1.44, 2.20],  p1: [2.45, 1.44, -1.20], l0: [2.80, 1.35, -7.20],  l1: [2.80, 1.35, -7.50],  fov0: 44, fov1: 40 },
  { id: 61, t0: 176.12,t1: 179.96,zone: 'alley',  p0: [-0.85, 1.52, -23.80],p1: [-0.45, 1.46, -25.20],l0: [0.85, 1.28, -19.20], l1: [1.15, 1.26, -21.50],fov0: 45, fov1: 41 },
  // FAST ATHLETIC RUNNING TRACKING SHOT IN NARROW BRICK ALLEY ("You move quickly, keeping close to the walls")!
  { id: 62, t0: 179.96,t1: 182.84,zone: 'alley',  p0: [-0.95, 1.36, -21.20],p1: [-0.95, 1.36, -31.00],l0: [1.45, 1.08, -21.00], l1: [1.45, 1.08, -31.20],fov0: 46, fov1: 42, shake: 0.022 },
  // Station Maintenance Door hanging ominously open!
  { id: 63, t0: 182.84,t1: 186.60,zone: 'alley',  p0: [0.45, 1.52, -29.80], p1: [0.15, 1.44, -32.40], l0: [0.00, 1.45, -35.15], l1: [-0.10, 1.40, -35.40],fov0: 44, fov1: 36 },
  { id: 64, t0: 186.60,t1: 188.40,zone: 'alley',  p0: [-0.55, 1.42, -33.85],p1: [-0.42, 1.40, -33.55],l0: [0.65, 1.36, -32.20], l1: [0.65, 1.38, -32.20],fov0: 36, fov1: 31, roll: -1.6 },

  // ================= ACT V: UNDERGROUND TRANSIT STATION, MAN & BOY, RADIO MIMIC & CLOSING DOOR (188.40 - 260.35s) =================
  { id: 65, t0: 188.40,t1: 193.36,zone: 'underground', p0: [0.00, 1.65, -59.80], p1: [0.45, 1.45, -58.60], l0: [0.00, 2.35, -54.20], l1: [0.00, 1.45, -56.80], fov0: 46, fov1: 41 },
  { id: 66, t0: 193.36,t1: 197.68,zone: 'underground', p0: [0.85, 1.52, -58.90], p1: [0.35, 1.18, -60.60], l0: [-0.25, 0.72, -62.55],l1: [-0.25, 0.65, -62.55],fov0: 44, fov1: 36 },
  // Finding Exhausted Older Man & Young Boy sitting at bottom of stairs
  { id: 67, t0: 197.68,t1: 203.40,zone: 'underground', p0: [0.65, 1.32, -59.85], p1: [0.15, 1.12, -60.85], l0: [-0.15, 0.88, -63.10],l1: [-0.15, 0.86, -63.10],fov0: 44, fov1: 38 },
  // Man raises 1 finger to his lips ("Don't make a sound")
  { id: 68, t0: 203.40,t1: 207.80,zone: 'underground', p0: [-0.55, 1.05, -61.15],p1: [-0.78, 1.02, -61.55],l0: [-1.15, 0.96, -63.15],l1: [-1.15, 0.98, -63.15],fov0: 36, fov1: 30 },
  // YOU crouches beside them -> "Are there others?" -> Man shakes head
  { id: 69, t0: 207.80,t1: 210.96,zone: 'underground', p0: [-0.65, 1.18, -59.95],p1: [-0.35, 1.08, -60.45],l0: [1.05, 0.86, -62.85], l1: [1.10, 0.86, -62.85], fov0: 45, fov1: 40 },
  { id: 70, t0: 210.96,t1: 212.76,zone: 'underground', p0: [-0.68, 1.02, -61.45],p1: [-0.82, 1.00, -61.68],l0: [-1.15, 0.96, -63.15],l1: [-1.15, 0.96, -63.15],fov0: 32, fov1: 29 },

  // Radio crackles: "To anyone still alive. Proceed to Platform 3. Help is waiting."
  { id: 71, t0: 212.76,t1: 216.56,zone: 'underground', p0: [0.22, 0.92, -61.25], p1: [0.05, 0.80, -61.65], l0: [-0.25, 0.64, -62.55],l1: [-0.25, 0.64, -62.55],fov0: 36, fov1: 29, roll: -1.4 },
  { id: 72, t0: 216.56,t1: 220.04,zone: 'underground', p0: [0.05, 0.80, -61.65], p1: [-0.08, 0.76, -61.82],l0: [-0.20, 0.95, -64.20],l1: [-0.10, 1.25, -65.80],fov0: 34, fov1: 38 },

  // Boy looks up ("That's my dad's voice") -> Man goes pale ("No. Your dad never used that radio.")
  { id: 73, t0: 220.04,t1: 223.24,zone: 'underground', p0: [0.25, 0.92, -61.45], p1: [0.38, 0.88, -61.75], l0: [0.85, 0.76, -63.00], l1: [0.85, 0.78, -63.00], fov0: 33, fov1: 28 },
  { id: 74, t0: 223.24,t1: 227.96,zone: 'underground', p0: [-0.62, 1.02, -61.35],p1: [-0.85, 0.98, -61.72],l0: [-1.15, 0.96, -63.15],l1: [-1.12, 0.96, -63.15],fov0: 34, fov1: 27, roll: 1.6 },
  { id: 75, t0: 227.96,t1: 231.40,zone: 'underground', p0: [-0.85, 0.98, -61.72],p1: [-0.92, 0.98, -61.88],l0: [-1.12, 0.96, -63.15],l1: [-1.10, 0.96, -63.15],fov0: 27, fov1: 24, roll: -1.8 },

  // Radio crackles again: "I'm right behind you." -> Whip-turn into dark tunnel -> Child voice "Dad?" -> Boy grabs sleeve!
  { id: 76, t0: 231.40,t1: 235.56,zone: 'underground', p0: [0.12, 0.84, -61.55], p1: [-0.08, 0.74, -61.88],l0: [-0.25, 0.64, -62.55],l1: [-0.25, 0.64, -62.55],fov0: 32, fov1: 24, shake: 0.018 },
  { id: 77, t0: 235.56,t1: 238.00,zone: 'underground', p0: [-0.35, 1.05, -60.35],p1: [-0.15, 0.98, -60.85],l0: [1.00, 0.88, -62.85], l1: [1.05, 0.90, -62.85], fov0: 44, fov1: 36, shake: 0.042, roll: 2.8 },
  { id: 78, t0: 238.00,t1: 241.84,zone: 'underground', p0: [0.85, 1.18, -63.40], p1: [0.18, 1.24, -65.40], l0: [0.00, 1.22, -74.50], l1: [0.00, 1.25, -78.00], fov0: 44, fov1: 37 },
  { id: 79, t0: 241.84,t1: 247.80,zone: 'underground', p0: [0.18, 1.24, -65.40], p1: [0.00, 1.28, -67.60], l0: [0.00, 1.32, -76.50], l1: [0.00, 1.36, -76.50], fov0: 37, fov1: 26, roll: -2.0 },
  { id: 80, t0: 247.80,t1: 252.48,zone: 'underground', p0: [1.30, 1.00, -60.70], p1: [1.38, 0.96, -61.10], l0: [1.06, 0.78, -62.90], l1: [1.06, 0.80, -62.90], fov0: 36, fov1: 30, shake: 0.024 },

  // Radio switches OFF -> Heavy Maintenance Door at top of stairs slowly closes BY ITSELF!
  { id: 81, t0: 252.48,t1: 255.04,zone: 'underground', p0: [0.02, 0.78, -61.72], p1: [-0.12, 0.73, -61.95],l0: [-0.25, 0.64, -62.55],l1: [-0.25, 0.64, -62.55],fov0: 28, fov1: 23 },
  { id: 82, t0: 255.04,t1: 260.45,zone: 'underground', p0: [0.00, 1.15, -58.85], p1: [0.00, 1.48, -56.95], l0: [0.00, 3.35, -52.18], l1: [0.00, 3.40, -52.18], fov0: 44, fov1: 35, roll: -1.6 },
];

export function getShotAt(t) {
  for (let i = 0; i < SHOTS.length; i++) {
    if (t >= SHOTS[i].t0 && t < SHOTS[i].t1) return SHOTS[i];
  }
  return SHOTS[SHOTS.length - 1];
}

export function evaluateScene(t) {
  const shot = getShotAt(t);
  const u = clamp01((t - shot.t0) / Math.max(0.001, shot.t1 - shot.t0));
  const su = smootherstep(u);

  // Fast kinetic camera interpolation + urgent handheld micro-motion (`camera motion fast`)!
  const isCloseInsert = [3, 4, 6, 35, 45, 46, 56, 57, 71, 76, 81].includes(shot.id);
  const fastDrift = isCloseInsert ? 0.006 : 0.032;
  const camPos = [
    lerp(shot.p0[0], shot.p1[0], su) + Math.sin(t * 2.35) * fastDrift,
    lerp(shot.p0[1], shot.p1[1], su) + Math.cos(t * 1.95) * (fastDrift * 0.65),
    lerp(shot.p0[2], shot.p1[2], su) + Math.sin(t * 1.65 + 1.1) * (fastDrift * 0.55),
  ];
  const camLook = [
    lerp(shot.l0[0], shot.l1[0], su),
    lerp(shot.l0[1], shot.l1[1], su),
    lerp(shot.l0[2], shot.l1[2], su),
  ];
  // Rulebook: never a dead frame — locked-off holds (p0≈p1) get a slow push-in creep toward
  // the subject so ~3.7px/f median motion holds even on "static" shots.
  const holdDrift = Math.hypot(shot.p1[0] - shot.p0[0], shot.p1[1] - shot.p0[1], shot.p1[2] - shot.p0[2]);
  if (holdDrift < 0.35) {
    const dx = camLook[0] - camPos[0], dy = camLook[1] - camPos[1], dz = camLook[2] - camPos[2];
    const dl = Math.hypot(dx, dy, dz) || 1;
    const creep = 0.075 * su;
    camPos[0] += dx / dl * creep; camPos[1] += dy / dl * creep; camPos[2] += dz / dl * creep;
  }
  let fov = lerp(shot.fov0, shot.fov1, su);
  let camRoll = (shot.roll || 0) * Math.sin(u * Math.PI);

  // Impact pulses for GPU Chromatic Shock & trauma shake
  let impactPulse = 0;
  for (const [it, mag] of [
    [3.45, 0.55], [25.25, 0.85], [27.05, 1.0], [51.70, 0.95], [68.35, 0.90],
    [95.15, 0.85], [104.00, 0.55], [104.68, 0.55], [105.36, 0.65], [114.65, 0.55],
    [127.00, 0.85], [223.30, 0.70], [235.60, 1.0], [246.80, 0.85], [259.76, 0.95]
  ]) {
    const dt = Math.abs(t - it);
    if (dt < 0.28) impactPulse = Math.max(impactPulse, (1 - dt / 0.28) * mag);
  }

  const totShake = (shot.shake || 0) + impactPulse * 0.045;
  if (totShake > 0.001) {
    camPos[0] += Math.sin(t * 49) * totShake;
    camPos[1] += Math.cos(t * 43) * totShake * 0.8;
    camRoll   += Math.sin(t * 33) * totShake * 24;
  }

  // =========================================================================
  // LIGHTING, TIME-OF-DAY & ATMOSPHERE ACROSS ALL 5 ACTS
  // =========================================================================
  // V6 LIGHT RIG: five act states, C1-smoothly crossfaded over 1.1s windows centered on each
  // act boundary — the picture now "breathes" between times of day instead of hard luma cuts.
  const LIGHT_STATES = [
    // t,      sky,      sun,  amb,  store, fridge, tint,      shaft, domeTint,   windowsLit
    { t: 0.00,   sky: '#070a13', sun: 0.10, amb: 0.42, store: 0.00, fridge: 0.00, tint: '#c9d3e4', shaft: 0.000, dome: '#0d1322', win: 0.00 }, // V6 cold open nightmare
    { t: 3.36,   sky: '#5d84a6', sun: 1.55, amb: 0.78, store: 1.18, fridge: 1.00, tint: '#ffffff', shaft: 0.055, dome: '#eef3f8', win: 0.00 },
    { t: 46.85,  sky: '#1f2e46', sun: 0.50, amb: 0.56, store: 0.34, fridge: 0.85, tint: '#d8e3f2', shaft: 0.000, dome: '#77879f', win: 1.00 },
    { t: 83.35,  sky: '#0c1320', sun: 0.20, amb: 0.42, store: 0.05, fridge: 0.00, tint: '#dde6f4', shaft: 0.000, dome: '#232c3d', win: 0.00 },
    { t: 145.96, sky: '#cfa686', sun: 1.60, amb: 0.85, store: 0.32, fridge: 0.00, tint: '#f7eadc', shaft: 0.040, dome: '#ffd9b8', win: 0.00 },
    { t: 188.40, sky: '#090d14', sun: 0.00, amb: 0.46, store: 0.00, fridge: 0.00, tint: '#e3d8c8', shaft: 0.000, dome: '#0c1017', win: 0.00 },
  ];
  let li = 0;
  while (li + 1 < LIGHT_STATES.length && t >= LIGHT_STATES[li + 1].t) li++;
  const LA = LIGHT_STATES[li];
  const LB = LIGHT_STATES[Math.min(li + 1, LIGHT_STATES.length - 1)];
  const blendWin = 1.10;
  const lu = (LA === LB) ? 0 : smootherstep(clamp01((t - (LB.t - blendWin * 0.5)) / blendWin));
  let skyHex = hexLerp(LA.sky, LB.sky, lu);
  let sunInt = lerp(LA.sun, LB.sun, lu);
  let ambInt = lerp(LA.amb, LB.amb, lu);
  let storeLightInt = lerp(LA.store, LB.store, lu);
  let fridgeOn = lerp(LA.fridge, LB.fridge, lu);
  let cardTint = hexLerp(LA.tint, LB.tint, lu);
  let shaftOpacity = lerp(LA.shaft, LB.shaft, lu);
  let skyDomeTint = hexLerp(LA.dome, LB.dome, lu);
  let windowsLit = lerp(LA.win, LB.win, lu);
  // V6.5 ORIGINS: per-beat montage light override — hard cuts, Hollywood trailer rhythm.
  if (shot.lx) {
    const L = shot.lx;
    skyHex = L.sky; sunInt = L.sun; ambInt = L.amb;
    storeLightInt = L.store; fridgeOn = L.fridge; cardTint = L.tint;
    shaftOpacity = L.shaft; skyDomeTint = L.dome; windowsLit = L.win;
  }

  // =========================================================================
  // DYNAMIC WORLD PROPS (100% CLOSED SHUTTERS, DOORS, FLASHLIGHT, RADIO, CARS)
  // =========================================================================
  const deadboltU = easeOut(t, 42.85, 43.45);
  // Storefront window shutters roll 100.0% ALL THE WAY DOWN TO FLOOR (y=0.00m) at 44.12-45.65s!
  const shutterWinU = easeOut(t, 44.12, 45.65);
  // Center entrance door shutter ALSO rolls 100.0% ALL THE WAY DOWN TO FLOOR at 78.70-80.10s!
  const shutterDoorU = easeOut(t, 78.70, 80.10);

  const flashlightOn = (t >= 84.35 && t < 140.0) || (t >= 188.50 && t < 199.50);
  // V6: flashlight now ramps in over 0.45s and out over 0.60s — no instant frame blow-out,
  // no dark cliff when it dies (the 84.4s flash + 199.5s blackout glitches are gone).
  let flashLevel = 0;
  for (const flRange of [[84.35, 140.0], [188.50, 199.50]]) {
    const onT = flRange[0], offT = flRange[1];
    if (t >= onT && t < offT) {
      flashLevel = Math.max(flashLevel, clamp01(Math.min((t - onT) / 0.45, (offT - t) / 0.60)));
    }
  }
  const emergInt = (shot.zone === 'back' && t < 83.35) ? 1.15 : ((shot.zone === 'back') ? 0.55 : 0.0);

  // Back door rattle on alley crash & 3 slow knocks, then swings open at 176.2s!
  let backDoorRattle = 0;
  for (const kt of [95.2, 97.6, 104.00, 104.68, 105.36, 127.1, 136.1]) {
    const dt = t - kt;
    if (dt >= 0 && dt < 0.34) backDoorRattle = Math.sin(dt * 68) * (1 - dt / 0.34) * 0.035;
  }
  const backDoorOpenAngle = (t >= 176.20) ? -0.92 * easeOut(t, 176.20, 177.80) : 0.0;

  // Underground Maintenance Door at top of stairs: open (0.94 rad) -> closes SLOWLY BY ITSELF at 255.04-259.80s!
  const ugDoorCloseU = easeOut(t, 255.20, 259.80);
  const ugMaintDoorAngle = 0.94 * (1.0 - ugDoorCloseU);

  // Underground Radio active LED & switch-off at 254.45s
  const radioCrackling = (t >= 213.4 && t < 220.0) || (t >= 231.8 && t < 238.0);
  const radioOff = (t >= 254.45);
  // V6: smooth radio-glow envelope (0.4s fades — no LED pop at 213.4 / 231.8 / 254.45).
  let radioGlowLevel = 0;
  for (const rgRange of [[213.4, 220.0], [231.8, 238.0]]) {
    const onT = rgRange[0], offT = rgRange[1];
    if (t >= onT && t < offT) {
      radioGlowLevel = Math.max(radioGlowLevel, clamp01(Math.min((t - onT) / 0.4, (offT - t) / 0.4)));
    }
  }
  // V6: radio static texture envelope (fades in 193.4, dies with the switch-off at 254.45).
  const radioStaticLevel = (t < 193.4 || t >= 254.45) ? 0
    : clamp01(Math.min((t - 193.4) / 1.5, (254.45 - t) / 0.35, 1.0));

  // Tunnel mimic eyes gleaming deep in dark subway bore ("you hear a child's voice call out: 'Dad?'")
  // V6: full staging — gaunt silhouette sways far in the bore 244.5-254.45 (eyes glint through
  // the "Dad?" beat), vanishes the instant the radio dies, then LUNGES at the closing-door cut.
  const tunnelEyesVisible = (t >= 245.90 && t < 248.40) || (t >= 254.50 && t < 255.06);
  let tunnelFig = null;
  if (t >= 244.50 && t < 254.45) {
    const sway = Math.sin(t * 0.90) * 0.045;
    tunnelFig = {
      x: 0.35 + sway, z: -73.20, s: 1.0,
      op: 0.62 + 0.10 * Math.sin(t * 0.50),
      rot: Math.sin(t * 0.90) * 0.05,
    };
  } else if (t >= 254.50 && t < 255.06) {
    const lg = smootherstep(clamp01((t - 254.50) / 0.52));
    tunnelFig = {
      x: 0.35, z: lerp(-73.20, -63.60, lg), s: lerp(1.0, 1.30, lg),
      op: lerp(0.62, 0.96, lg), rot: lerp(0.0, -0.10, lg),
    };
  }

  // Street Vehicles choreography (abandoned car parked OFF the central sightlines at x=-5.2!)
  let abandonedCarPos = [-5.2, 0, 13.0]; // parked — no ghost slide
  // V6: one ordinary sedan cruising the near lane during the peaceful aerial establishing shot
  // (0-6s). It leaves the world at x=-25 while every camera is indoors — zero pop, pure normalcy.
  const trafficCarVis = (t >= 3.36 && t < 6.2); // V6: normal traffic ONLY in the bright post-title beat
  const trafficCarPos = [lerp(21.0, -25.0, clamp01((t - 3.36) / 2.84)), 0, 15.30];
  const trafficCarRot = -Math.PI / 2;
  let abandonedCarRot = 0.10;
  let swerveCarVis = false, swerveCarPos = [8.5, 0, 16.2], swerveCarRot = -Math.PI / 2;
  let patrolCarVis = false, patrolCarPos = [-2.4, 0, 19.6], patrolCarRot = 0.38;

  if (t >= 17.60 && t < 33.0) {
    swerveCarVis = true;
    if (t < 26.96) {
      // V6: cruising the NEAR lane (z=15.3) since shot 8's first frame. At 26.96 the car's
      // FRONT CORNER just reaches the man (center x=6.6, bumper x=4.35) — a fender CLIP that
      // launches him clear of the body. Never again through the cabin (man-inside-car bug).
      swerveCarPos = [lerp(17.8, 6.6, (t - 17.60) / 9.36), 0, 15.30];
      swerveCarRot = -Math.PI / 2;
    } else {
      const swU = easeOut(t, 26.96, 28.20);
      swerveCarPos = [lerp(6.6, -2.6, swU), 0, lerp(15.30, 13.90, swU)];
      swerveCarRot = lerp(-Math.PI / 2, -Math.PI / 2 + 0.58, swU);
    }
  } else if ((t >= 2.94 && t < 3.36) || (t >= 59.88 && t < 69.96)) {
    patrolCarVis = true; // V6.5: strobes wash the destruction beat + the Act II police standoff
  } else if (t >= 145.9) {
    // Sunrise abandoned cars scattered askew across empty street!
    abandonedCarPos = [8.5, 0, 22.5]; abandonedCarRot = 0.55;
    swerveCarVis = true; swerveCarPos = [3.8, 0, 19.0]; swerveCarRot = -1.05;
    patrolCarVis = true; patrolCarPos = [7.0, 0, 20.0]; patrolCarRot = 0.9;
  }

  // V6.5 CINEMATIC OVERLAYS: origins beat cards -> OUTBREAK title smash -> DAY cards -> TO BE CONTINUED.
  let introOverlay = null;
  if (t < 0.62) {
    introOverlay = { tex: 'intro1', op: clamp01((t - 0.08) / 0.16) * clamp01((0.56 - t) / 0.09) };
  } else if (t >= 0.62 && t < 1.24) {
    introOverlay = { tex: 'intro2', op: clamp01((t - 0.68) / 0.16) * clamp01((1.18 - t) / 0.09) };
  } else if (t >= 2.42 && t < 2.94) {
    introOverlay = { tex: 'intro3', op: clamp01((t - 2.48) / 0.16) * clamp01((2.88 - t) / 0.09) };
  } else if (t >= 2.94 && t < 3.36) {
    const fl2 = Math.sin(t * 47.0) > 0.82 ? 0.80 : 1.0; // title glitch flicker
    introOverlay = { tex: 'title', op: clamp01((t - 2.94) / 0.05) * clamp01((3.36 - t) / 0.12) * fl2 };
  } else if (t >= 3.50 && t < 6.30) {
    introOverlay = { tex: 'locator1', op: clamp01((t - 3.50) / 0.4) * clamp01((6.30 - t) / 0.5) };
  } else if (t >= 146.30 && t < 149.30) {
    introOverlay = { tex: 'locator2', op: clamp01((t - 146.30) / 0.5) * clamp01((149.30 - t) / 0.6) };
  } else if (t >= 259.55) {
    introOverlay = { tex: 'end', op: clamp01((t - 259.75) / 0.5) };
  }

  // Held Smartphone close-up inserts — V6.5 REAL PHONE:
  // feed browsing -> notification banner arrives (buzz) -> EMERGENCY ALERT slams in mid-shot.
  const buzzAmp = (t0, pulses) => {
    let a = 0;
    for (let p = 0; p < pulses; p++) {
      const dt = t - (t0 + p * 0.34);
      if (dt >= 0 && dt < 0.24) a = Math.max(a, Math.min(1, dt / 0.03) * (1 - dt / 0.24));
    }
    return a;
  };
  const phoneState = { visible: false, mode: 'alert1', pos: [3.02, 1.35, 3.10], vib: 0 };
  if ([3, 4, 6].includes(shot.id)) {
    phoneState.visible = true;
    phoneState.pos = [3.02, 1.35, 3.10];
    if (shot.id === 3) {
      if (t < 5.35) phoneState.mode = 'social0';        // scrolling the feed — ordinary life
      else if (t < 5.75) phoneState.mode = 'social1';   // notification banner + badge (buzz!)
      else phoneState.mode = 'alert1';                  // the alert FILLS THE SCREEN (with the VO!)
      phoneState.vib = buzzAmp(5.35, 2) * 0.016 + buzzAmp(5.78, 1) * 0.020;
    } else {
      phoneState.mode = 'alert1';
    }
  } else if ([45, 46].includes(shot.id)) {
    phoneState.visible = true;
    phoneState.mode = 'alert2';
    phoneState.pos = [2.66, 1.35, -13.80];
    phoneState.vib = buzzAmp(115.45, 2) * 0.014;
  } else if ([56, 57].includes(shot.id)) {
    phoneState.visible = true;
    phoneState.mode = 'map1bar';
    phoneState.pos = [3.02, 1.35, 3.10];
  }

  // =========================================================================
  // CHARACTER CHOREOGRAPHY, BIOMECHANICAL GAIT & SITUATION EXPRESSIONS
  // =========================================================================
  const mkChar = () => ({
    visible: false, pos: [0, 0, 0], view: 'front', flipX: false,
    expr: 'calm_work', dist: 0, isRunning: false, reverseWalk: false, fallU: 0,
    crouchSit: false, hasBackpack: false, armPose: null,
    talk: 0, phoneBuzz: 0, shake: 0, headShakeYaw: 0,
  });

  const chars = {
    you: mkChar(),
    police: mkChar(),
    woman: mkChar(),
    carMan: mkChar(),
    runA: mkChar(),
    runB: mkChar(),
    survMan: mkChar(),
    survBoy: mkChar(),
    infA: mkChar(),
    infB: mkChar(),
    infC: mkChar(),
    scientist: mkChar(),
    anchor: mkChar(),
  };

  // Helper to place a walking/running character with exact distance-locked stride (`dist` in meters -> stride cycle!)
  const placeMoving = (c, x0, z0, x1, z1, tA, tB, running = false, reverse = false) => {
    const p = clamp01((t - tA) / Math.max(0.001, tB - tA));
    const px = lerp(x0, x1, p);
    const pz = lerp(z0, z1, p);
    const vx = (x1 - x0) / Math.max(0.01, tB - tA);
    const vz = (z1 - z0) / Math.max(0.01, tB - tA);
    const totalMeters = Math.hypot(x1 - x0, z1 - z0) * p;
    // CRITICAL: vel must be 3-element [x, y, z] — solveMoveFacing reads vel[2]. A 2-element
    // array made spd NaN and every mover fell through to a fixed side/false facing (backwards walk!).
    const f = solveMoveFacing([px, 0, pz], [vx, 0, vz], camPos, reverse);
    c.visible = true;
    c.pos = [px, 0, pz];
    c.view = f.view;
    c.flipX = f.flipX;
    c.isRunning = running;
    c.reverseWalk = reverse;
    // Full biomechanical 2-step stride length: ~1.62m sprinting, ~1.18m walking!
    c.dist = totalMeters / (running ? 1.62 : 1.18);
  };

  const spkPulse = (a, b) => (t >= a && t <= b) ? (0.35 + 0.55 * Math.abs(Math.sin(t * 14.5))) : 0;

  // ---------------- 1. MAIN CHARACTER (`YOU`) ----------------
  const hasPack = (t >= 170.2);
  chars.you.hasBackpack = hasPack;

  if (shot.zone === 'store' && !phoneState.visible && ![15, 22, 23, 24, 25, 29, 30, 35].includes(shot.id)) {
    chars.you.visible = true;
    if (t < 3.36) {
      chars.you.pos = [3.10, 0, 3.05];
      chars.you.expr = 'calm_work';
    } else if (t < 17.60) {
      chars.you.pos = [3.08, 0, 3.05];
      chars.you.armPose = 'phoneBuzz';
      chars.you.phoneBuzz = t < 5.5 ? t : 0;
      chars.you.expr = t < 7.40 ? 'startled_shock' : 'dread_reading';
    } else if (t < 35.60) {
      chars.you.pos = [3.08, 0, 3.35];
      chars.you.armPose = t < 33.0 ? 'phoneBuzz' : null;
      chars.you.phoneBuzz = t < 32.9 ? t : 0;
      chars.you.expr = t < 32.9 ? 'extreme_panic' : 'hesitant_conflict';
    } else if (t < 42.60) {
      placeMoving(chars.you, 0.95, 5.20, 0.25, 6.55, 40.60, 42.60, false, false);
      chars.you.expr = 'extreme_panic';
    } else if (t < 44.12) {
      chars.you.pos = [-0.28, 0, 6.85];
      chars.you.view = 'side'; chars.you.flipX = false;
      chars.you.armPose = 'lockDoor';
      chars.you.expr = 'straining_effort';
    } else if (t < 45.80) {
      // Pulling down heavy metal shutter all the way to floor!
      chars.you.pos = [-2.85, 0, 6.65];
      chars.you.view = 'threeQuarter';
      chars.you.armPose = 'pullShutter';
      chars.you.expr = 'straining_effort';
    } else if (t < 48.00) {
      chars.you.pos = [1.05, 0, 6.75];
      chars.you.view = 'threeQuarter';
      chars.you.armPose = 'lockDoor';
      chars.you.expr = 'dread_reading';
    } else if (t < 50.76) {
      chars.you.pos = [0.65, 0, 6.25];
      chars.you.expr = 'frozen_terror';
    } else if (t < 61.28) {
      // Reaching hesitantly toward front door lock!
      placeMoving(chars.you, 0.15, 6.35, 0.05, 6.78, 59.88, 61.28, false, false);
      chars.you.armPose = 'lockDoor';
      chars.you.expr = 'hesitant_conflict';
    } else if (t < 75.92) {
      // Stepping back in pure terror after Woman's face changes!
      placeMoving(chars.you, 0.05, 6.55, 0.05, 5.35, 71.88, 75.92, false, true);
      chars.you.expr = 'extreme_panic';
      chars.you.shake = 0.008;
    } else if (t < 80.48) {
      // Pulling center door security shutter 100% down to floor!
      chars.you.pos = [0.42, 0, 6.55];
      chars.you.view = 'threeQuarter'; chars.you.flipX = true;
      chars.you.armPose = t >= 78.5 ? 'pullShutter' : null;
      chars.you.expr = t >= 78.5 ? 'straining_effort' : 'extreme_panic';
    } else if (t < 94.04) {
      chars.you.pos = [3.08, 0, 3.30];
      chars.you.armPose = t >= 84.3 ? 'flashlight' : null;
      chars.you.expr = 'dread_reading';
    } else if (t < 97.16) {
      placeMoving(chars.you, 2.35, 3.20, 2.65, -2.50, 94.20, 97.16, true, false);
      chars.you.armPose = 'flashlight';
      chars.you.expr = 'startled_shock';
    } else if (t >= 140.08 && t < 145.96) {
      // Staying crouched behind/beside counter all night listening to footsteps!
      chars.you.pos = [1.35, 0, 4.35];
      chars.you.crouchSit = true;
      chars.you.expr = 'frozen_terror';
    } else if (t >= 165.24 && t < 173.52) {
      chars.you.pos = [3.02, 0, 3.30];
      chars.you.armPose = t >= 169.7 ? 'lockDoor' : 'phoneBuzz';
      chars.you.expr = 'straining_effort';
    } else if (t >= 173.52 && t < 176.12) {
      placeMoving(chars.you, 2.55, 1.50, 2.75, -5.20, 173.52, 176.12, true, false);
      chars.you.expr = 'straining_effort';
    }
  } else if (shot.zone === 'back' && [39, 41, 44, 48, 49, 51].includes(shot.id)) {
    chars.you.visible = true;
    if (shot.id === 39) {
      placeMoving(chars.you, 2.68, -10.80, 2.68, -14.10, 99.20, 103.56, false, false);
      chars.you.armPose = 'flashlight';
      chars.you.expr = 'frozen_terror';
    } else if (shot.id === 41) {
      chars.you.pos = [2.65, 0, -13.95];
      chars.you.armPose = 'flashlight';
      chars.you.expr = t < 106.7 ? 'hesitant_conflict' : 'frozen_terror';
      chars.you.talk = spkPulse(105.80, 106.55); // "Hello?"
    } else if (shot.id === 44) {
      chars.you.pos = [2.65, 0, -13.95];
      chars.you.armPose = 'phoneBuzz';
      chars.you.phoneBuzz = t;
      chars.you.expr = 'startled_shock';
    } else if (shot.id === 48 || shot.id === 49) {
      chars.you.pos = [2.65, 0, -13.95];
      chars.you.expr = shot.id === 48 ? 'extreme_panic' : 'frozen_terror';
      chars.you.shake = shot.id === 48 ? 0.008 : 0;
    } else if (shot.id === 51) {
      placeMoving(chars.you, 2.68, -13.80, 2.68, -11.60, 138.52, 140.08, false, true);
      chars.you.expr = 'extreme_panic';
    }
  } else if (shot.zone === 'alley' && [61, 62, 64].includes(shot.id)) {
    chars.you.visible = true;
    if (shot.id === 61) {
      placeMoving(chars.you, 0.95, -18.50, 1.45, -21.20, 176.50, 179.96, false, false);
      chars.you.expr = 'straining_effort';
    } else if (shot.id === 62) {
      // FULL BIOMECHANICAL SPRINT IN NARROW BRICK ALLEY ("You move quickly, keeping close to the walls")!
      placeMoving(chars.you, 1.48, -20.60, 1.48, -31.60, 179.96, 182.84, true, false);
      chars.you.expr = 'straining_effort';
    } else if (shot.id === 64) {
      chars.you.pos = [0.65, 0, -32.20];
      chars.you.expr = 'frozen_terror';
    }
  } else if (shot.zone === 'underground' && [65, 69, 77, 80].includes(shot.id)) {
    chars.you.visible = true;
    if (shot.id === 65) {
      const stU = clamp01((t - 188.40) / 4.96);
      chars.you.pos = [0.0, lerp(1.65, 0.15, stU), lerp(-54.2, -58.2, stU)];
      chars.you.dist = stU * 3.8;
      // Facing solved from the actual descent velocity (0,0,-0.81) so the mirror side always
      // matches the travel direction on screen (was a hardcoded flipX that ran backwards).
      const sf65 = solveMoveFacing(chars.you.pos, [0, 0, -4.0 / 4.96], camPos, false);
      chars.you.view = sf65.view; chars.you.flipX = sf65.flipX;
      chars.you.armPose = 'flashlight';
      chars.you.expr = 'dread_reading';
    } else {
      chars.you.pos = [1.28, 0, -62.80];
      chars.you.crouchSit = true;
      chars.you.view = 'threeQuarter'; chars.you.flipX = true;
      chars.you.expr = shot.id === 69 ? 'hesitant_conflict' : 'extreme_panic';
      chars.you.talk = spkPulse(209.68, 210.85); // "Are there others?"
    }
  }

  // ---------------- 0. V6.5 ORIGINS COLD OPEN CHOREOGRAPHY (0.00 - 3.36s) ----------------
  if (shot.id === 200) {
    // Busy ordinary afternoon: a boy sprints ahead playing, his mom walks behind, a jogger passes.
    placeMoving(chars.survBoy, 2.0, 13.50, -1.0, 13.50, 0.00, 0.68, true, false);
    placeMoving(chars.woman, 3.1, 13.10, 1.9, 13.10, 0.00, 0.68, false, false);
    placeMoving(chars.runA, -2.2, 16.60, 1.9, 16.60, 0.00, 0.68, true, false);
  }
  if (shot.id === 201 || shot.id === 202) {
    // The hidden evil scientist at his bench — masked, gloved, calm. Total control.
    chars.scientist.visible = true;
    chars.scientist.pos = [-40.55, 0, -14.55];
    chars.scientist.view = shot.id === 201 ? 'backFull' : 'threeQuarter';
    chars.scientist.flipX = false;
    chars.scientist.armPose = 'labWork';
    chars.scientist.breath = 0;
  }
  if (shot.id === 203) {
    // THE RELEASE: cage door slides, three infected sprint loose into the world.
    chars.scientist.visible = true;
    chars.scientist.pos = [-41.45, 0, -13.10];
    chars.scientist.view = 'side'; chars.scientist.flipX = true;
    chars.scientist.armPose = 'labWork';
    placeMoving(chars.infA, -36.9, -14.2, -34.9, -11.2, 1.80, 2.46, true, false);
    chars.infA.armPose = 'zombieReach';
    placeMoving(chars.infB, -36.9, -14.2, -35.5, -11.9, 1.80, 2.46, true, false);
    chars.infB.armPose = 'zombieReach';
    placeMoving(chars.infC, -36.6, -14.6, -34.6, -12.4, 1.80, 2.46, true, false);
    chars.infC.armPose = 'zombieReach';
  }
  if (shot.id === 204) {
    // News anchor, live, reading the end of the world — ticker running.
    chars.anchor.visible = true;
    chars.anchor.pos = [-40.0, 0, -50.30];
    chars.anchor.view = 'front'; chars.anchor.flipX = false;
    chars.anchor.crouchSit = true;
    chars.anchor.talk = 0.30 + 0.50 * Math.abs(Math.sin(t * 11.0));
  }
  if (shot.id === 205) {
    // Nationwide destruction: fires, smoke, the horde loose in the strobing dark.
    placeMoving(chars.infA, -3.4, 16.30, 3.2, 16.30, 2.94, 3.46, true, false);
    chars.infA.armPose = 'zombieReach';
    placeMoving(chars.infB, -4.5, 17.30, 1.6, 17.30, 2.94, 3.46, true, false);
    chars.infB.armPose = 'zombieReach';
    placeMoving(chars.infC, -1.2, 15.10, 1.5, 12.60, 2.94, 3.46, true, false);
    chars.infC.armPose = 'zombieReach';
    placeMoving(chars.runA, 3.9, 15.90, 1.1, 15.90, 2.94, 3.42, true, false);
    chars.runA.expr = 'extreme_panic';
  }

  // ---------------- 2. STREET ATTACKER (`carMan`) & FLEEING CIVILIANS (`runA`, `runB`) ----------------
  if (t >= 17.60 && t < 31.00 && shot.zone === 'street') {
    if (t < 24.00) {
      // Standing dead still in the middle of the road staring blankly at nothing!
      // (Present from shot 8's FIRST frame — no mid-shot spawn pop.)
      chars.carMan.visible = true;
      chars.carMan.pos = [-2.40, 0, 16.20];
      chars.carMan.expr = 'road_trance';
    } else if (t < 26.96) {
      // SUDDEN FULL-STRIDE SPRINT AT PASSING CAR ("Then, he suddenly runs at a passing car")!
      placeMoving(chars.carMan, -2.40, 16.20, 4.35, 16.20, 24.00, 26.96, true, false);
      chars.carMan.expr = 'extreme_panic';
    } else if (t < 28.25) {
      // CLIPPED BY THE SWERVING CAR — painful tumble over the front corner, lands crumpled
      // on the asphalt ("The driver swerves... Someone screams").
      const tb = clamp01((t - 26.96) / 1.29);
      const arc = Math.sin(tb * Math.PI);
      chars.carMan.visible = true;
      chars.carMan.pos = [lerp(4.35, 3.05, tb), arc * 1.02, lerp(16.20, 17.00, tb)];
      chars.carMan.view = 'front'; chars.carMan.flipX = false;
      chars.carMan.fallU = clamp01((t - 27.02) / 0.95);
      chars.carMan.dist = 0;
      chars.carMan.expr = 'knocked_out';
    } else {
      // Motionless on the road, blood pooling under him — haunts the chase shot's background.
      chars.carMan.visible = true;
      chars.carMan.pos = [3.05, 0, 17.00];
      chars.carMan.view = 'front'; chars.carMan.flipX = false;
      chars.carMan.fallU = 1;
      chars.carMan.expr = 'knocked_out';
    }
  }

  if (t >= 28.25 && t < 31.10 && shot.zone === 'street') {
    // Showcase Biomechanical Human Running: Two terrified pedestrians sprinting down the sidewalk while horror zombie chases!
    placeMoving(chars.runA, -3.40, 9.45, 5.20, 9.45, 28.20, 31.05, true, false);
    chars.runA.expr = 'extreme_panic';
    placeMoving(chars.runB, -5.10, 10.15, 3.40, 10.15, 28.20, 31.05, true, false);
    chars.runB.expr = 'extreme_panic';
    placeMoving(chars.infA, -6.90, 9.75, 2.10, 9.75, 28.25, 31.05, true, false); // 3.05 m/s full sprint
  }

  // ---------------- 3. WOMAN AT ENTRANCE DOOR & POLICE HORDE ACROSS STREET (50.76 - 72.0s) ----------------
  if (t >= 50.76 && t < 72.00 && [22, 23, 24, 25, 29, 30].includes(shot.id)) {
    chars.woman.visible = true;
    chars.woman.pos = [0.55, 0, 7.95];
    if (t < 66.84) {
      chars.woman.expr = 'plead_terror';
      chars.woman.armPose = 'plead';
      chars.woman.shake = 0.012;
      if (shot.id === 24) {
        // Looking frantically over her shoulder!
        chars.woman.view = 'threeQuarter';
        chars.woman.flipX = (Math.sin(t * 5.0) > 0);
      }
      chars.woman.talk = spkPulse(58.05, 59.75); // "Please, let me in."
    } else {
      // "The woman turns. Her expression changes. 'Please, open the door.'"
      const turned = t >= 68.22;
      chars.woman.expr = turned ? 'woman_uncanny' : 'plead_terror';
      chars.woman.armPose = turned ? null : 'plead';
      chars.woman.shake = turned ? 0.0 : 0.008;
      chars.woman.talk = spkPulse(70.00, 71.75); // "Please, open the door."
    }
  }

  if (t >= 61.20 && t < 66.90 && shot.zone === 'street') {
    // Police Officer slowly backing away (`reverseWalk: true`) from lunging nightmare horror zombies!
    placeMoving(chars.police, -0.40, 17.50, -3.10, 17.50, 61.28, 66.84, false, true);
    chars.police.expr = 'extreme_panic';
    chars.police.armPose = 'flashlight';

    // NOTE: camera looks toward +z, so screen-x is inverted vs world-x.
    // Phase 1 (61.28-65.30): menacing shamble — walk cycle + infected lurch lean.
    placeMoving(chars.infA, 1.90, 17.35, 0.32, 17.35, 61.28, 65.30, false, false);
    placeMoving(chars.infB, 2.60, 18.05, 1.06, 18.05, 61.28, 65.30, false, false);
    placeMoving(chars.infC, 3.10, 16.85, 1.56, 16.85, 61.28, 65.30, false, false);
    if (t >= 65.30) {
      // Phase 2 — FAST MONSTERS: the trio EXPLODES into a full sprint; the lead infected
      // TACKLES the retreating officer to the ground (painful, on-camera).
      placeMoving(chars.infA, 0.32, 17.35, -2.30, 17.35, 65.30, 66.20, true, false);
      placeMoving(chars.infB, 1.06, 18.05, -0.90, 18.05, 65.30, 66.84, true, false);
      placeMoving(chars.infC, 1.56, 16.85, -0.20, 16.85, 65.30, 66.84, true, false);
      chars.police.fallU = clamp01((t - 65.90) / 0.70);
      if (t > 66.50) { chars.police.expr = 'knocked_out'; chars.police.armPose = null; }
    }
  }

  // ---------------- 4. MOTIONLESS MIMIC HORROR SHAPE AT BACK DOOR PEEP WINDOW (107.7 - 138.6s) ----------------
  if (shot.zone === 'back' && [42, 43, 47, 50].includes(shot.id)) {
    chars.infA.visible = true;
    // Positioned outside peep window (window center is x=2.80, y=1.77, z=-16.32) so head fills window!
    chars.infA.pos = [2.80, 0.24, -17.10];
    chars.infA.dist = 0; // "It doesn't move."
    chars.infA.talk = spkPulse(126.95, 128.90) || spkPulse(135.95, 138.40);
  }

  // ---------------- 5. UNDERGROUND SURVIVOR MAN & YOUNG BOY (197.68 - 255.04s) ----------------
  if (shot.zone === 'underground' && ![65, 66, 78, 79, 82].includes(shot.id)) {
    chars.survMan.visible = true;
    chars.survMan.pos = [-1.15, 0, -63.15];
    chars.survMan.crouchSit = true;

    // Boy sits RIGHT BESIDE you (x=0.85 vs your 1.28) for the tight sleeve-grab two-shot!
    chars.survBoy.visible = true;
    chars.survBoy.pos = [0.85, 0, -62.95];
    chars.survBoy.crouchSit = true;

    if (t < 203.40) {
      chars.survMan.expr = 'exhausted_hush';
      chars.survBoy.expr = 'exhausted_hush';
    } else if (t < 207.80) {
      chars.survMan.expr = 'exhausted_hush';
      chars.survMan.armPose = 'shush';
      chars.survMan.talk = spkPulse(206.28, 207.70); // "Don't make a sound."
      chars.survBoy.expr = 'exhausted_hush';
    } else if (t < 212.76) {
      chars.survMan.expr = 'exhausted_hush';
      if (t >= 211.00) chars.survMan.headShakeYaw = Math.sin((t - 211.0) * 14.0) * 0.22; // Shakes his head!
      chars.survBoy.expr = 'exhausted_hush';
    } else if (t < 220.04) {
      chars.survMan.expr = 'startled_shock';
      chars.survBoy.expr = 'startled_shock';
    } else if (t < 223.24) {
      chars.survMan.expr = 'startled_shock';
      chars.survBoy.expr = 'boy_hope';
      chars.survBoy.talk = spkPulse(221.52, 223.15); // "That's my dad's voice."
    } else if (t < 235.56) {
      // "The man beside him goes pale. He slowly turns toward the boy: 'No. Your dad never used that radio.'"
      chars.survMan.expr = 'pale_horror';
      chars.survMan.view = 'threeQuarter'; chars.survMan.flipX = false;
      chars.survMan.talk = spkPulse(228.00, 231.30);
      chars.survBoy.expr = 'startled_shock';
    } else if (t < 247.80) {
      chars.survMan.expr = 'extreme_panic';
      chars.survBoy.expr = 'extreme_panic';
    } else {
      // "The boy beside you grabs your sleeve: 'Don't answer. That's not me.'"
      chars.survMan.expr = 'extreme_panic';
      chars.survBoy.expr = 'plead_terror';
      chars.survBoy.view = 'threeQuarter'; chars.survBoy.flipX = false;
      chars.survBoy.armPose = 'grabSleeve';
      chars.survBoy.talk = spkPulse(250.00, 252.40);
    }
  }

  // Cartoon 2D FX triggers (clean bursts on car swerve & glass hit)
  const fx = {
    swerveBurst: (t >= 27.02 && t <= 27.62) ? (t - 27.02) / 0.60 : -1,
    glassSlam:   (t >= 51.68 && t <= 52.28) ? (t - 51.68) / 0.60 : -1,
    doorKnock:   -1,
  };
  for (const kt of [104.00, 104.68, 105.36]) {
    if (t >= kt && t <= kt + 0.35) fx.doorKnock = (t - kt) / 0.35;
  }

  return {
    t,
    shot,
    camPos,
    camLook,
    fov,
    camRoll,
    impactPulse,
    skyHex,
    sunInt,
    ambInt,
    storeLightInt,
    fridgeOn,
    cardTint,
    shaftOpacity,
    deadboltU,
    shutterWinU,
    shutterDoorU,
    flashlightOn,
    flashLevel,
    radioGlowLevel,
    radioStaticLevel,
    skyDomeTint,
    windowsLit,
    emergInt,
    backDoorRattle,
    backDoorOpenAngle,
    ugMaintDoorAngle,
    ugDoorCloseU,
    radioCrackling,
    radioOff,
    tunnelEyesVisible,
    tunnelFig,
    introOverlay,
    trafficCarVis,
    trafficCarPos,
    trafficCarRot,
    abandonedCarPos,
    abandonedCarRot,
    swerveCarVis,
    swerveCarPos,
    swerveCarRot,
    // Blood pool decal under the hit-and-run man (grows 27.35 -> 29.6, gone by the store cut)
    bloodPool: (t >= 27.35 && t < 31.00 && shot.zone === 'street')
      ? { x: 3.05, z: 17.00, s: 0.55 + 0.55 * clamp01((t - 27.35) / 2.2), a: clamp01((t - 27.35) / 0.5) }
      : null,
    // V6.5 ORIGINS states
    cageDoorU: easeOut(t, 1.86, 2.16),
    alarmInt: (t >= 1.80 && t < 2.42) ? (0.55 + 0.45 * Math.sin(t * 17.0)) : ((t >= 1.24 && t < 1.80) ? 0.30 : 0.0),
    introFire: shot.id === 205,
    patrolCarVis,
    patrolCarPos,
    patrolCarRot,
    sunriseDamageVis: t >= 145.9,
    packVis: t >= 169.5 && t < 173.6,
    phoneState,
    chars,
    fx,
  };
}
