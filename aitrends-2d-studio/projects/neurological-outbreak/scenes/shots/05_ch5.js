// scenes/shots/05_ch5.js — Chapter 5 (s029..s035): Dead Street & "Are You Alone?" (450.08s .. 618.43s)
import { E, registerShot, mood, layer, backdrop, veil, ease, prog, clamp, lerp, shake, seg, circle, rr, glow, alpha, shade, text, FONTS } from '/engine/core.js';
import { drawFigure, POSES, breathe, walkPose } from '/engine/rig2d.js';
import * as FX from '/engine/fx2d.js';
import { box, GY, storeInteriorSet, storeFrontEntranceSet, storageDoorSet, stationStairsSet } from '../sets/outbreak_world.js';
import { YOU, INFECTED_A, INFECTED_B, CONTROL_MAN, TWITCH_POSE, SAFE } from '../cast.js';

// s029 — Cold Dawn Decision: packing water, protein bars, medkit & flashlight into backpack (450.08..468.94s)
registerShot('s029', {
  draw(g, t, info) {
    const cam = { z: 1.06 + 0.05 * (t / info.dur), x: 0, y: 0 };
    storeInteriorSet(g, cam, t, { dim: 0.18, night: false });

    layer(g, cam, 1.0, (g) => {
      box(g, 705, GY - 140, 510, 140, 6, '#1e2c40', '#0c131d', 4);
      // Backpack centered on counter (x = SAFE.CX)
      box(g, SAFE.CX - 55, GY - 255, 110, 115, 22, '#3b5249', '#16211d', 4);
      box(g, SAFE.CX - 36, GY - 210, 72, 52, 10, '#2c3e37');
      // First-aid kit red cross + flashlight beside bag
      box(g, SAFE.CX + 85, GY - 190, 58, 46, 6, '#d9dce3', '#8c2b35', 2);
      seg(g, [[SAFE.CX + 114, GY - 178], [SAFE.CX + 114, GY - 156]], 6, '#d92b3a');
      seg(g, [[SAFE.CX + 103, GY - 167], [SAFE.CX + 125, GY - 167]], 6, '#d92b3a');

      drawFigure(g, {
        x: SAFE.CX - 115, y: GY + 12, s: 1.5, facing: 1, outfit: YOU,
        pose: breathe(POSES.holdFront, t), rim: { color: '#c9dcff', dir: [-0.6, -1], w: 4 }
      });
    });
  }
});

// s030 — Rear door horror: cargo strap hanging loose, hand truck fallen — something is inside! (468.94..480.46s)
registerShot('s030', {
  draw(g, t, info) {
    const cam = { z: 1.15 + 0.10 * (t / info.dur), x: 0, y: -15 };
    storageDoorSet(g, cam, t, { broken: true, handTruck: false, truckFallen: true, emergencyFlicker: true });

    layer(g, cam, 1.0, (g) => {
      // Door slightly ajar with pitch-black shadow inside storage room
      box(g, 838, 230, 38, GY - 230, 0, '#03050a');
      text(g, 'BREACHED — SOMETHING IS INSIDE', SAFE.CX, 175, { size: 19, color: '#ff6b78', font: FONTS.ui, weight: 900 });
    });
  }
});

// s031 — Returning to front entrance: removing shelves, crates & unlocking deadbolt into silence (480.46..497.88s)
registerShot('s031', {
  draw(g, t, info) {
    const cleared = t > 6.5;
    const cam = { z: 1.06 + 0.06 * (t / info.dur), x: 0, y: 0 };
    storeFrontEntranceSet(g, cam, t, { shutterAmt: cleared ? 0.0 : 0.45, night: false, barricade: !cleared });

    layer(g, cam, 1.0, (g) => {
      drawFigure(g, {
        x: SAFE.CX - 35, y: GY + 18, s: 1.5, facing: 1, outfit: YOU,
        pose: cleared ? POSES.stand : POSES.reach,
        rim: { color: '#c9dcff', dir: [0, -1], w: 4.5 }
      });
      if (t > 9.0) text(g, 'COMPLETE SILENCE OUTSIDE', SAFE.CX, 185, { size: 19, color: '#a8c6ed', font: FONTS.ui, weight: 800 });
    });
  }
});

// s032 — 3D Silent Dead Morning Street: abandoned bus, changing traffic light, motionless infected facing station (497.88..520.27s)
registerShot('s032', {
  kind: '3d',
  init(T) {
    const M = mood('night');
    const st = T.stage({ mood: 'night', fov: 40, fog: [12, 44], keyPos: [6, 14, 8], keyIntensity: 2.3, ambient: 1.5 });
    st.add(T.ground(80, 80, M.road, T.tiles(M.road, 14, [12, 12])));
    for (let i = -3; i <= 1; i++) {
      const zP = i * 5.5 - 3.0;
      const bL = T.building(4.5, 9.2, 4.5, { color: M.wall, win: M.practical, lit: 0.12, seed: 60 + i });
      bL.position.set(-6.5, 4.6, zP); st.add(bL);
      const bR = T.building(4.5, 8.8, 4.5, { color: M.wall, win: M.practical, lit: 0.12, seed: 80 + i });
      bR.position.set(6.5, 4.4, zP); st.add(bR);
    }
    // Abandoned city bus angled across middle of road (center-safe!)
    st.add(T.box(4.4, 1.85, 1.55, '#3b5470', 0.2, 1.02, -6.2));
    st.add(T.box(4.2, 0.65, 1.60, '#182433', 0.2, 1.35, -6.2));

    // Motionless infected standing near bus, ALL facing -Z (toward underground station!)
    const coords = [[-1.1, -3.2], [-0.3, -2.6], [0.6, -3.0], [1.2, -3.8], [0.0, -4.1]];
    coords.forEach(([x, z], idx) => {
      const f = T.figure3D(idx % 2 ? INFECTED_A : INFECTED_B, { rim: '#9ec5ff', pose: POSES.stand });
      f.position.set(x, 0, z);
      f.rotation.y = Math.PI; // facing away toward the underground station!
      st.add(f);
    });
    return { stage: st };
  },
  draw(s, t, info) {
    const u = t / info.dur;
    s.stage.camera.position.set(-0.9 + u * 1.8, 2.5, 6.2 - u * 1.2);
    s.stage.camera.lookAt(0, 1.2, -4.5);
  },
  overlay(g, t) {
    // Changing traffic light overhead inside SAFE column!
    const phase = Math.floor(t / 3.2) % 3;
    box(g, SAFE.CX + 140, 110, 42, 108, 8, '#141b26', '#2c394d', 2);
    circle(g, SAFE.CX + 161, 132, 10, phase === 0 ? '#ff4d5e' : '#33181c');
    circle(g, SAFE.CX + 161, 164, 10, phase === 1 ? '#ffbf47' : '#332916');
    circle(g, SAFE.CX + 161, 196, 10, phase === 2 ? '#4de68a' : '#142e20');
  }
});

// s033 — Stepping into cold street -> Child's backpack, fallen bicycle & family photo (520.27..551.32s)
registerShot('s033', {
  draw(g, t, info) {
    const photoZoom = t > 18.0; // "There's a small photograph attached to it. A family. Two parents and a little boy."
    const cam = { z: photoZoom ? 1.22 : 1.04 + 0.06 * (t / info.dur), x: 0, y: photoZoom ? 40 : 0 };
    const M = mood('night');
    backdrop(g, ['#0d1726', '#1a2b42']);

    layer(g, cam, 0.5, (g) => {
      FX.skyline(g, { x: -100, y: GY - 90, w: E.W + 200, minH: 90, maxH: 290, color: '#101a2b', windowColor: alpha(M.practical, 0.16), lit: 0.1, seed: 52 });
      g.fillStyle = '#121a26'; g.fillRect(-100, GY - 90, E.W + 200, E.H);
    });

    layer(g, cam, 1.0, (g) => {
      // Fallen child's bicycle + small red backpack on asphalt inside SAFE!
      circle(g, SAFE.CX + 45, GY - 18, 28, '#1b2433');
      circle(g, SAFE.CX + 125, GY - 14, 28, '#1b2433');
      seg(g, [[SAFE.CX + 45, GY - 18], [SAFE.CX + 85, GY - 32], [SAFE.CX + 125, GY - 14]], 5, '#6384ab');
      box(g, SAFE.CX - 35, GY - 48, 52, 44, 12, '#9e4638', '#24110e', 2);

      if (!photoZoom) {
        const walkX = lerp(SAFE.CX - 190, SAFE.CX - 85, clamp(t / 15.0));
        drawFigure(g, {
          x: walkX, y: GY - 6, s: 1.44, facing: 1, outfit: YOU,
          pose: t < 15 ? walkPose(t * 3.2) : POSES.kneel,
          rim: { color: '#c9dcff', dir: [-0.5, -1], w: 4 }
        });
      } else {
        // Tactile POV Polaroid photograph of two parents + little boy in brown hoodie!
        veil(g, '#050912', 0.48);
        box(g, SAFE.CX - 150, 290, 300, 355, 8, '#e8e4da', '#2b3442', 3);
        box(g, SAFE.CX - 128, 314, 256, 255, 4, '#1b2a40');
        // 2 parents + little boy silhouettes inside photo!
        circle(g, SAFE.CX - 55, 415, 22, '#2d3f59'); box(g, SAFE.CX - 80, 440, 50, 125, 10, '#3a5475');
        circle(g, SAFE.CX + 55, 422, 20, '#2d3f59'); box(g, SAFE.CX + 32, 445, 46, 120, 10, '#594769');
        circle(g, SAFE.CX, 468, 16, '#1c2433'); box(g, SAFE.CX - 20, 486, 40, 82, 8, '#874c3a'); // same brown hoodie as BOY in Ch6!
        text(g, 'FAMILY PHOTO', SAFE.CX, 610, { size: 16, color: '#2b3340', font: FONTS.ui, weight: 900 });
      }
    });
    FX.dust(g, t, { count: 32, color: '#b8d4ff', a: 0.25 });
  }
});

// s034 — Footsteps behind you: infected turns head, second emerges -> BREAK INTO A RUN! (551.32..568.31s)
registerShot('s034', {
  draw(g, t, info) {
    const sprint = t > 11.5;
    const sh = sprint ? shake(t, 4.8) : { x: 0, y: 0 };
    const cam = { z: 1.12 + 0.08 * (t / info.dur), x: sh.x, y: sh.y };
    backdrop(g, ['#0b1320', '#162438']);

    layer(g, cam, 1.0, (g) => {
      g.fillStyle = '#101722'; g.fillRect(-100, GY - 40, E.W + 200, 300);
      // Infected #1 turning head + Infected #2 emerging from car shadow
      drawFigure(g, {
        x: SAFE.CX - 120, y: GY - 12, s: 1.35, facing: 1, outfit: INFECTED_A,
        pose: sprint ? walkPose(t * 9, { run: true }) : TWITCH_POSE,
        expr: 'angry', rim: { color: '#ff5c6c', dir: [-1, -0.5], w: 4 }
      });
      if (t > 7.5) {
        drawFigure(g, {
          x: SAFE.CX + 110, y: GY - 18, s: 1.32, facing: -1, outfit: INFECTED_B,
          pose: sprint ? walkPose(t * 9.5, { run: true }) : TWITCH_POSE,
          expr: 'angry', rim: { color: '#ff5c6c', dir: [1, -0.5], w: 4 }
        });
      }
      if (sprint) {
        FX.speedLines(g, SAFE.CX, E.H * 0.5, t, { count: 36, color: '#c9dcff', r0: 220, r1: 950, a: 0.35 });
      }
    });
  }
});

// s035 — Station stairs: locked shutter -> card reader -> "Are you alone?" -> "No." -> Door opens & pulled inside! (568.31..618.43s)
registerShot('s035', {
  draw(g, t, info) {
    // Voice asks "Are you alone?" at ~599s global -> lt ~ 30.7s! Lock clicks & opens at ~612.5s -> lt ~ 44.2s!
    const voiceCue = t > 29.5;
    const doorOpen = t > 44.0;
    const sh = t < 8.0 ? shake(t, 3.8) : { x: 0, y: 0 };
    const cam = { z: 1.08 + 0.10 * (t / info.dur), x: sh.x, y: sh.y };
    stationStairsSet(g, cam, t, { doorOpen });

    layer(g, cam, 1.0, (g) => {
      // Approaching infected shadows at top of stairs when t > 33s!
      if (t > 33.0 && !doorOpen) {
        drawFigure(g, { x: 745, y: 380, s: 0.72, facing: 1, outfit: INFECTED_A, pose: TWITCH_POSE });
        drawFigure(g, { x: 805, y: 380, s: 0.70, facing: 1, outfit: INFECTED_B, pose: TWITCH_POSE });
      }

      const youX = doorOpen ? lerp(955, 1085, clamp((t - 44.0) / 2.2)) : (t < 14.0 ? 830 : 955);
      drawFigure(g, {
        x: youX, y: GY + 8, s: 1.46, facing: 1, outfit: YOU,
        pose: t < 14.0 ? POSES.reach : breathe(POSES.ready, t),
        expr: 'scared', rim: { color: doorOpen ? '#4de68a' : '#c9dcff', dir: [0, -1], w: 4.5 }
      });

      if (voiceCue && t < 36.0) {
        text(g, '"Are you alone?"', 1095, 290, { size: 22, color: '#dceaff', font: FONTS.serif, style: 'italic', weight: 900 });
      }
      if (t > 40.5 && t < 43.8) {
        // Remember: YOU answered "No." — foreshadowing the silent boy from the street!
        text(g, '"No."', 935, 420, { size: 24, color: '#ffd27d', font: FONTS.serif, style: 'italic', weight: 900 });
      }
      if (doorOpen) {
        // Control man's arm pulling YOU inside!
        drawFigure(g, { x: 1135, y: GY + 6, s: 1.46, facing: -1, outfit: CONTROL_MAN, pose: POSES.reach });
      }
    });
  }
});
