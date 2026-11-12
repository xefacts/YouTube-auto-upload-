// scenes/shots/01_ch1.js — Chapter 1 (s001..s007): Aisle Four & Biological Emergency (0.00s .. 114.44s)
import { E, S, registerShot, mood, layer, backdrop, veil, ease, prog, clamp, lerp, shake, seg, circle, rr, poly, glow, alpha, shade, text, FONTS } from '/engine/core.js';
import { drawFigure, POSES, breathe, walkPose } from '/engine/rig2d.js';
import * as FX from '/engine/fx2d.js';
import { box, GY, storeInteriorSet, storeFrontEntranceSet, drawPOVPhone } from '../sets/outbreak_world.js';
import { YOU, DRIVER, INFECTED_A, INFECTED_B, TWITCH_POSE, SAFE } from '../cast.js';

// s001 — Aisle 4 POV: comparing two cans of soup when your phone suddenly vibrates (0.00..9.59s)
registerShot('s001', {
  draw(g, t, info) {
    const vib = t > 6.6;
    const sh = vib ? shake(t, 3.5) : { x: 0, y: 0 };
    const cam = { z: 1.02 + 0.05 * (t / info.dur), x: sh.x, y: sh.y };
    storeInteriorSet(g, cam, t, { dim: 0.05 });

    // Center-safe Aisle 4 shelf rack + POV hands comparing two soup cans!
    layer(g, cam, 1.0, (g) => {
      box(g, 710, 220, 500, 490, 8, '#172131', '#0b1019', 4);
      for (let r = 0; r < 3; r++) {
        const sy = 335 + r * 135;
        g.fillStyle = '#2c3c54'; g.fillRect(722, sy, 476, 10);
        for (let c = 0; c < 6; c++) {
          box(g, 742 + c * 74, sy - 52, 42, 52, 5, c % 2 ? '#8f343d' : '#3a6289', '#101622', 2);
        }
      }

      // First-person POV hands holding 2 soup cans in lower center SAFE column
      const bob = Math.sin(t * 2.2) * 5;
      // Left hand + red soup can
      box(g, 775, 695 + bob, 92, 126, 10, '#a63842', '#1d0d11', 3);
      box(g, 783, 725 + bob, 76, 48, 4, '#f2e5d5');
      text(g, 'TOMATO', 821, 749 + bob, { size: 13, color: '#8f2933', font: FONTS.ui, weight: 900 });
      box(g, 748, 760 + bob, 42, 160, 18, '#141c2b');

      // Right hand + blue soup can (drops slightly when phone vibrates!)
      const drop = vib ? ease.out(prog(t, 6.6, 7.3)) * 55 : 0;
      box(g, 1045, 695 - bob + drop, 92, 126, 10, '#366596', '#0e1b2b', 3);
      box(g, 1053, 725 - bob + drop, 76, 48, 4, '#e6eef7');
      text(g, 'BROTH', 1091, 749 - bob + drop, { size: 13, color: '#244970', font: FONTS.ui, weight: 900 });
      box(g, 1122, 760 - bob + drop, 42, 160, 18, '#141c2b');

      // Vibrating phone rising at bottom center at t=6.6s!
      if (vib) {
        const rise = ease.out(prog(t, 6.6, 7.6));
        const vx = Math.sin(t * 62) * 6;
        glow(g, SAFE.CX + vx, 930 - rise * 130, 180, '#ff3b4e', 0.42);
        box(g, SAFE.CX - 75 + vx, 850 - rise * 120, 150, 240, 20, '#121826', '#ff4d5e', 3);
        // Vibration wave rings
        for (const sgn of [-1, 1]) {
          seg(g, [[SAFE.CX + sgn * 96 + vx, 780], [SAFE.CX + sgn * 108 + vx, 825], [SAFE.CX + sgn * 96 + vx, 870]], 4, '#ff6b78');
        }
      }
    });
    FX.dust(g, t, { count: 28, color: '#9ec5ff', a: 0.22 });
  }
});

// s002 — POV Phone Screen: BIOLOGICAL EMERGENCY national broadcast + scream outside (9.59..34.14s)
registerShot('s002', {
  draw(g, t, info) {
    const scream = t > 21.5; // "Then someone screams outside" (~31.7s global -> lt ~22.1s)
    const sh = scream ? shake(t, 4.5) : { x: 0, y: 0 };
    const cam = { z: 1.05 + 0.08 * (t / info.dur), x: sh.x, y: sh.y };
    storeInteriorSet(g, cam, t, { dim: 0.35 });

    layer(g, cam, 1.0, (g) => {
      veil(g, '#050812', 0.45);
      drawPOVPhone(g, SAFE.CX, E.H * 0.52, t, { vibrate: t < 4.0, mode: 'alert', zoom: 1.24 });
      if (scream) {
        // Sudden crimson flash from front windows when someone screams outside!
        const pulse = Math.abs(Math.sin(t * 7));
        glow(g, SAFE.CX, 210, 420, '#ff3b4e', 0.25 + 0.2 * pulse);
        text(g, '! SCREAM OUTSIDE !', SAFE.CX, 145, { size: 22, color: '#ff7b86', font: FONTS.ui, weight: 900 });
      }
    });
  }
});

// s003 — 3D Street Outbreak: abandoned car, man running & chased by 3 figures, falls (34.14..58.72s)
registerShot('s003', {
  kind: '3d',
  init(T) {
    const M = mood('night');
    const st = T.stage({ mood: 'night', fov: 40, fog: [14, 48], keyPos: [-5, 13, 9], keyIntensity: 2.6, ambient: 1.45 });
    st.add(T.ground(80, 80, M.road, T.tiles(M.road, 14, [12, 12])));
    for (let i = -3; i <= 1; i++) {
      const zP = i * 5.4 - 2.5;
      const bL = T.building(4.4, 9.5, 4.4, { color: M.wall, win: M.practical, lit: 0.42, seed: 11 + i });
      bL.position.set(-6.4, 4.75, zP); st.add(bL);
      const bR = T.building(4.4, 9.0, 4.4, { color: M.wall, win: M.practical, lit: 0.38, seed: 41 + i });
      bR.position.set(6.4, 4.5, zP); st.add(bR);
    }
    // Abandoned car angled in middle of road (center-safe!)
    const car = T.box(1.55, 0.75, 2.7, '#4c617d', -0.9, 0.42, -5.5);
    const cab = T.box(1.35, 0.55, 1.35, '#253245', -0.9, 0.98, -5.6);
    st.add(car, cab);

    // Fleeing man + 3 chasers kept right near x = -0.8 .. +0.9 (center 9:16 column!)
    const runner = T.figure3D({ top: 'tshirt', color: '#d48c46', head: 'short' }, { rim: M.rim, pose: POSES.ready });
    const chasers = [0, 1, 2].map(k => T.figure3D(k % 2 ? INFECTED_A : INFECTED_B, { rim: '#ff6b78', pose: TWITCH_POSE }));
    st.add(runner, ...chasers);
    return { stage: st, runner, chasers };
  },
  draw(s, t, info) {
    // lt 0..17.8s running; lt >= 17.8s ("Then the man falls. The three people reach him.")
    const fallT = 17.8;
    const runProg = clamp(t / fallT);
    const rz = -4.2 + runProg * 4.4;
    s.runner.position.set(0.15, t >= fallT ? 0.18 : 0, rz);
    s.runner.rotation.z = t >= fallT ? Math.PI * 0.46 : 0;

    const catchProg = t >= fallT ? clamp((t - fallT) / 3.2) : 0;
    const offsets = [[-0.45, -1.9], [0.35, -2.3], [-0.05, -2.8]];
    s.chasers.forEach((c, idx) => {
      const [ox, oz] = offsets[idx];
      const cz = lerp(rz + oz, rz - 0.35 + idx * 0.22, catchProg);
      c.position.set(ox, 0, cz);
    });

    s.stage.camera.position.set(Math.sin(t * 0.25) * 0.5, 2.7, 6.8 - (t / info.dur) * 1.1);
    s.stage.camera.lookAt(0, 1.1, -1.5);
  },
  overlay(g) {
    // Store window mullions framing the center 9:16 view so viewer feels inside the store!
    g.fillStyle = '#070b13';
    g.fillRect(0, 0, 140, E.H); g.fillRect(E.W - 140, 0, 140, E.H);
    g.fillRect(0, 0, E.W, 64);
  }
});

// s004 — Street chaos & YOU rush to front doors and lock heavy metal deadbolt (58.72..78.67s)
registerShot('s004', {
  draw(g, t, info) {
    const lockPhase = t > 14.2; // "grab the heavy metal deadbolt, and lock both doors" (~73s global)
    const sh = shake(t, lockPhase ? 4.0 : 2.2);
    const cam = { z: lockPhase ? 1.24 : 1.04 + 0.06 * (t / info.dur), x: sh.x, y: lockPhase ? 30 + sh.y : sh.y };
    storeFrontEntranceSet(g, cam, t, { chaos: true });

    layer(g, cam, 1.0, (g) => {
      if (!lockPhase) {
        // Outside silhouettes sprinting past the glass inside SAFE 740..1180
        for (let k = 0; k < 3; k++) {
          const rx = 740 + ((t * (145 + k * 35) + k * 160) % 430);
          drawFigure(g, { x: rx, y: GY - 82, s: 0.92, facing: k % 2 ? 1 : -1, outfit: k % 2 ? INFECTED_A : DRIVER, pose: walkPose(t * 9 + k, { run: true }), expr: 'scared' });
        }
        // YOU backing away then rushing forward inside center SAFE column
        const rush = prog(t, 10.5, 14.0);
        drawFigure(g, {
          x: lerp(SAFE.CX - 90, SAFE.CX - 35, rush), y: GY + 25, s: 1.48, facing: 1,
          outfit: YOU, pose: rush > 0.1 ? walkPose(t * 8, { run: true }) : breathe(POSES.ready, t),
          rim: { color: '#c9dcff', dir: [-0.6, -1], w: 4 }
        });
      } else {
        // Extreme tactile POV insert: YOUR hand slamming heavy steel deadbolt LOCKED!
        const slide = ease.out(prog(t, 14.5, 16.2));
        box(g, SAFE.CX - 220, 390, 440, 250, 14, '#141c2b', '#2f3f57', 5);
        box(g, SAFE.CX - 170, 475, 340, 74, 8, '#2b374a', '#0d121c', 3);
        const boltX = lerp(SAFE.CX - 145, SAFE.CX + 10, slide);
        box(g, boltX, 491, 135, 42, 6, '#9fb2cc', '#1c2533', 3);
        // POV hand gripping deadbolt knob
        circle(g, boltX + 45, 512, 26, '#cfdcf0');
        box(g, boltX + 20, 530, 54, 190, 22, '#111827');
        if (slide > 0.85) {
          glow(g, SAFE.CX + 75, 512, 110, '#4de68a', 0.35);
          text(g, 'DEADBOLT LOCKED', SAFE.CX, 435, { size: 22, color: '#7ff5b2', font: FONTS.ui, weight: 900 });
        }
      }
    });
  }
});

// s005 — Delivery driver slams against the glass, shouting frantically (78.67..90.60s)
registerShot('s005', {
  draw(g, t, info) {
    const impact = t < 1.2 ? (1.2 - t) * 7 : 1.2;
    const sh = shake(t, impact);
    const cam = { z: 1.14 + 0.06 * (t / info.dur), x: sh.x, y: sh.y };
    storeFrontEntranceSet(g, cam, t, { chaos: true });

    layer(g, cam, 1.0, (g) => {
      // Delivery driver pressed right against the center glass door (x = SAFE.CX + 35)
      drawFigure(g, {
        x: SAFE.CX + 38, y: GY - 12, s: 1.46, facing: -1, outfit: DRIVER,
        pose: breathe(POSES.handsOnHead, t * 2.2, 1.6), expr: 'scared',
        rim: { color: '#ff7b6b', dir: [0.8, -0.5], w: 4.5 }
      });
      // Impact shock ring on glass
      if (t < 2.2) {
        glow(g, SAFE.CX + 12, 460, 160, '#dceaff', (1 - t / 2.2) * 0.32);
      }
      // YOU moving closer on the inside (x = SAFE.CX - 135)
      const stepIn = ease.inOut(prog(t, 7.5, 11.0));
      drawFigure(g, {
        x: lerp(SAFE.CX - 165, SAFE.CX - 115, stepIn), y: GY + 30, s: 1.54, facing: 1,
        outfit: YOU, pose: breathe(POSES.stand, t),
        rim: { color: '#c9dcff', dir: [-1, -0.4], w: 4 }
      });
    });
  }
});

// s006 — Another figure approaches behind driver; driver turns & sprints away (90.60..103.30s)
registerShot('s006', {
  draw(g, t, info) {
    const turnT = 4.2, fleeT = 6.8;
    const cam = { z: 1.15, x: 0, y: 0 };
    storeFrontEntranceSet(g, cam, t, { chaos: true });

    layer(g, cam, 1.0, (g) => {
      // Creeping infected figure approaching from behind inside SAFE zone!
      const infX = lerp(SAFE.CX + 185, SAFE.CX + 95, clamp(t / 9.0));
      drawFigure(g, {
        x: infX, y: GY - 34, s: 1.24, facing: -1, outfit: INFECTED_A,
        pose: breathe(TWITCH_POSE, t * 1.6, 1.4), expr: 'angry',
        rim: { color: '#ff5263', dir: [1, -0.4], w: 4 }
      });

      // Delivery driver: faces store -> turns around -> sprints away from store!
      const fleeing = t > fleeT;
      const drvX = fleeing ? lerp(SAFE.CX + 20, SAFE.CX - 220, clamp((t - fleeT) / 4.2)) : SAFE.CX + 20;
      drawFigure(g, {
        x: drvX, y: GY - 12, s: 1.44, facing: t < turnT ? -1 : (fleeing ? -1 : 1),
        outfit: DRIVER,
        pose: fleeing ? walkPose(t * 10, { run: true }) : POSES.ready,
        expr: 'scared', rim: { color: '#ffd089', dir: [-0.6, -0.8], w: 4 }
      });

      // YOU watching through glass
      drawFigure(g, {
        x: SAFE.CX - 140, y: GY + 34, s: 1.52, facing: 1, outfit: YOU,
        pose: POSES.stand, rim: { color: '#c9dcff', dir: [-1, -0.4], w: 4 }
      });
    });
  }
});

// s007 — Pulling heavy steel security shutters ALL the way down — Cliffhanger Part 1! (103.30..114.44s)
registerShot('s007', {
  draw(g, t, info) {
    const shut = ease.inOut(prog(t, 0.5, 6.2));
    const sh = t > 0.5 && t < 6.3 ? shake(t, 2.2) : { x: 0, y: 0 };
    const cam = { z: 1.04 + 0.08 * (t / info.dur), x: sh.x, y: sh.y };
    storeFrontEntranceSet(g, cam, t, { chaos: true, shutterAmt: shut });

    layer(g, cam, 1.0, (g) => {
      drawFigure(g, {
        x: SAFE.CX, y: GY + 24, s: 1.52, facing: 1, outfit: YOU,
        pose: shut < 0.92 ? POSES.reach : breathe(POSES.stand, t),
        rim: { color: '#c9dcff', dir: [0, -1], w: 4.5 }
      });
      if (shut >= 0.95) {
        veil(g, '#050914', 0.28 * prog(t, 6.2, 10.0));
        text(g, 'LOCKED INSIDE', SAFE.CX, 225, { size: 24, color: '#9ec5ff', font: FONTS.ui, weight: 900 });
      }
    });
  }
});
