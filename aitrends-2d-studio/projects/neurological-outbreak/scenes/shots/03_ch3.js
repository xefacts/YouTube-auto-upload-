// scenes/shots/03_ch3.js — Chapter 3 (s015..s021): The Storage Room Window (228.40s .. 354.78s)
import { E, registerShot, layer, backdrop, veil, ease, prog, clamp, lerp, shake, seg, circle, rr, poly, glow, alpha, text, FONTS } from '/engine/core.js';
import { drawFigure, POSES, breathe, walkPose } from '/engine/rig2d.js';
import * as FX from '/engine/fx2d.js';
import { box, GY, storeInteriorSet, storeFrontEntranceSet, storageDoorSet } from '../sets/outbreak_world.js';
import { YOU, INFECTED_A, INFECTED_B, TWITCH_POSE, SAFE } from '../cast.js';

// s015 — Sun disappears, automatic lights switch on, dragging metal shelves to barricade front (228.40..249.72s)
registerShot('s015', {
  draw(g, t, info) {
    const lightsOn = t > 2.6;
    const barDone = t > 10.5;
    const cam = { z: 1.03 + 0.05 * (t / info.dur), x: 0, y: 0 };
    storeFrontEntranceSet(g, cam, t, { shutterAmt: 0.85, night: true, barricade: barDone });

    layer(g, cam, 1.0, (g) => {
      if (!lightsOn) veil(g, '#040710', 0.58);
      else glow(g, SAFE.CX, 95, 420, '#ffd089', 0.22);

      if (!barDone) {
        const pushX = lerp(SAFE.CX - 180, SAFE.CX - 45, ease.inOut(prog(t, 5.0, 10.4)));
        box(g, pushX + 55, 360, 160, GY - 360, 5, '#2d394b', '#131924', 3);
        drawFigure(g, {
          x: pushX, y: GY + 10, s: 1.48, facing: 1, outfit: YOU,
          pose: walkPose(t * 4.5), rim: { color: '#ffd089', dir: [0, -1], w: 4 }
        });
      } else {
        // "Then you remember something..."
        drawFigure(g, {
          x: SAFE.CX, y: GY + 18, s: 1.5, facing: -1, outfit: YOU,
          pose: breathe(POSES.think, t), expr: 'scared', rim: { color: '#c9dcff', dir: [0, -1], w: 4.5 }
        });
        if (t > 17.5) text(g, 'THE BACK DELIVERY DOOR...', SAFE.CX, 205, { size: 20, color: '#ff8578', font: FONTS.ui, weight: 900 });
      }
    });
  }
});

// s016 — Flashlight sweep onto weak wooden back door & wire-mesh window (249.72..264.35s)
registerShot('s016', {
  draw(g, t, info) {
    const cam = { z: 1.06 + 0.07 * (t / info.dur), x: 0, y: 0 };
    storageDoorSet(g, cam, t, { broken: false, handTruck: false, emergencyFlicker: true });

    layer(g, cam, 1.0, (g) => {
      veil(g, '#03050a', 0.55);
      // First-person POV Flashlight Cone sweeping across wooden frame, padlock & wire-mesh window!
      const aimX = SAFE.CX + Math.sin(t * 1.3) * 75;
      const aimY = 410 + Math.cos(t * 0.9) * 85;
      poly(g, [[SAFE.CX - 140, E.H + 20], [aimX - 135, aimY - 90], [aimX + 135, aimY + 90]], alpha('#fff2cc', 0.16));
      glow(g, aimX, aimY, 185, '#ffeab3', 0.34);
    });
  }
});

// s017 — Bracing heavy hand truck & tightening yellow cargo strap to steel beam (264.35..273.96s)
registerShot('s017', {
  draw(g, t, info) {
    const strapped = t > 3.2;
    const cam = { z: 1.12, x: 0, y: 0 };
    storageDoorSet(g, cam, t, { broken: false, handTruck: true, strapLoose: !strapped });

    layer(g, cam, 1.0, (g) => {
      drawFigure(g, {
        x: strapped ? SAFE.CX + 130 : SAFE.CX - 110, y: GY + 16, s: 1.48,
        facing: strapped ? -1 : 1, outfit: YOU,
        pose: strapped ? breathe(POSES.holdFront, t) : POSES.reach,
        rim: { color: '#ff8566', dir: [0, -1], w: 4 }
      });
    });
  }
});

// s018 — Quiet hour at counter -> metallic CLATTER -> flashlight OFF -> creeping down corridor (273.96..298.63s)
registerShot('s018', {
  draw(g, t, info) {
    // Clatter occurs at ~283.65s global -> lt ~ 9.7s! Flashlight off at lt ~ 13.5s!
    const clatter = t > 9.6;
    const lightOff = t > 13.5;
    const sh = (t > 9.6 && t < 10.6) ? shake(t, 5.5) : { x: 0, y: 0 };
    const cam = { z: 1.04 + 0.08 * (t / info.dur), x: sh.x, y: sh.y };

    if (t < 16.5) {
      storeInteriorSet(g, cam, t, { dim: lightOff ? 0.72 : 0.3, night: true, powerFlicker: clatter });
      layer(g, cam, 1.0, (g) => {
        box(g, 710, GY - 145, 500, 145, 6, '#1a2536', '#0a0f18', 3);
        drawFigure(g, {
          x: SAFE.CX, y: GY + 18, s: 1.5, facing: clatter ? 1 : -1, outfit: YOU,
          pose: clatter ? POSES.ready : breathe(POSES.sit, t),
          expr: clatter ? 'scared' : 'neutral',
          rim: { color: clatter ? '#ff6b78' : '#c9dcff', dir: [0, -1], w: 4 }
        });
        if (t > 9.6 && t < 12.2) {
          text(g, '* CLATTER! *', SAFE.CX + 95, 290, { size: 26, color: '#ff6b78', font: FONTS.ui, weight: 900 });
        }
      });
    } else {
      // Creeping toward back doorway under flickering red emergency light
      storageDoorSet(g, cam, t, { broken: true, handTruck: true, emergencyFlicker: true });
      layer(g, cam, 1.0, (g) => {
        veil(g, '#03050a', 0.45);
        drawFigure(g, {
          x: lerp(SAFE.CX - 210, SAFE.CX - 130, prog(t, 16.5, 24.0)), y: GY + 24, s: 1.52,
          facing: 1, outfit: YOU, pose: walkPose(t * 2.4),
          rim: { color: '#ff6b52', dir: [1, -0.5], w: 4 }
        });
      });
    }
  }
});

// s019 — HORROR CLOSE-UP: Broken wire-mesh window, reaching infected arm & searching fingers + clicking (298.63..323.58s)
registerShot('s019', {
  draw(g, t, info) {
    const cam = { z: 1.38 + 0.10 * (t / info.dur), x: 0, y: -95 };
    storageDoorSet(g, cam, t, { broken: true, handTruck: true, emergencyFlicker: true });

    layer(g, cam, 1.0, (g) => {
      // Reaching grey-green infected arm thrust through the broken wire-mesh opening (900..1020, y=350)!
      const reach = ease.out(prog(t, 1.5, 5.5));
      const wriggle = Math.sin(t * 5.2) * 10;
      const elbowX = 955 - reach * 35, elbowY = 362 + wriggle * 0.4;
      const handX = 955 - reach * 92, handY = 378 + wriggle;

      seg(g, [[978, 352], [elbowX, elbowY], [handX, handY]], 16, '#2b3832');
      // 4 searching fingers repeatedly opening & closing!
      const spread = 0.5 + 0.5 * Math.sin(t * 6.8);
      for (let f = -2; f <= 1; f++) {
        const ang = Math.PI + f * (0.16 + 0.24 * spread);
        seg(g, [[handX, handY], [handX + Math.cos(ang) * 26, handY + Math.sin(ang) * 26]], 5, '#3b4d44');
      }

      // Eerie clicking sound visual ripples when t > 13.5s ("A low clicking noise")
      if (t > 13.2 && t < 19.5) {
        const r = ((t * 90) % 75) + 18;
        g.strokeStyle = alpha('#ff6b78', 1 - r / 95); g.lineWidth = 2.5;
        g.beginPath(); g.arc(965, 345, r, 0, Math.PI * 2); g.stroke();
      }

      // Cargo strap vibrating taut at t > 19.5s ("It's already stretched tight")
      if (t > 19.5) {
        const vibY = Math.sin(t * 65) * 3.5;
        seg(g, [[920, 520 + vibY], [1175, 530 - vibY]], 7, '#ffbf47');
      }
    });
  }
});

// s020 — Desperate struggle: leaning all weight into hand truck against reaching arm (323.58..334.48s)
registerShot('s020', {
  draw(g, t, info) {
    const sh = shake(t, 3.8);
    const cam = { z: 1.18, x: sh.x, y: sh.y };
    storageDoorSet(g, cam, t, { broken: true, handTruck: true, emergencyFlicker: true });

    layer(g, cam, 1.0, (g) => {
      // Infected arm pushing farther in
      seg(g, [[975, 352], [905, 368], [848 + Math.sin(t * 9) * 8, 385]], 16, '#2f3d36');
      // YOU braced hard against the hand truck inside SAFE!
      drawFigure(g, {
        x: 832, y: GY + 8, s: 1.5, facing: 1, outfit: YOU,
        pose: POSES.ready, expr: 'angry',
        rim: { color: '#ff6b52', dir: [1, -0.4], w: 4.5 }
      });
    });
  }
});

// s021 — Second heavy impact + multiple shapes behind broken glass -> sprinting back! (334.48..354.78s)
registerShot('s021', {
  draw(g, t, info) {
    const flee = t > 10.2;
    const sh = t < 3.0 ? shake(t, 7.0) : shake(t, 2.5);
    const cam = { z: 1.14, x: sh.x, y: sh.y };
    storageDoorSet(g, cam, t, { broken: true, handTruck: true, emergencyFlicker: true });

    layer(g, cam, 1.0, (g) => {
      // Multiple glowing eyes / silhouettes swarming behind the broken mesh window!
      for (const [ex, ey] of [[922, 332], [960, 322], [995, 342]]) {
        circle(g, ex + Math.sin(t * 4 + ex) * 4, ey, 18, '#0c1210');
        circle(g, ex - 5, ey - 2, 3, '#ff5c6c');
        circle(g, ex + 5, ey - 2, 3, '#ff5c6c');
      }

      const youX = flee ? lerp(835, 685, clamp((t - 10.2) / 3.5)) : 835;
      drawFigure(g, {
        x: youX, y: GY + 12, s: 1.5, facing: flee ? -1 : 1, outfit: YOU,
        pose: flee ? walkPose(t * 10, { run: true }) : POSES.ready,
        expr: 'scared', rim: { color: '#ff6b52', dir: [1, -0.5], w: 4.5 }
      });
      veil(g, '#040710', 0.32 * prog(t, 16.5, 20.0));
    });
  }
});
