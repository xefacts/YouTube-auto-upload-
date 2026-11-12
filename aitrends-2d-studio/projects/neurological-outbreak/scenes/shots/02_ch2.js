// scenes/shots/02_ch2.js — Chapter 2 (s008..s014): Half Stock & Woman at the Glass (114.44s .. 228.40s)
import { E, registerShot, layer, veil, ease, prog, clamp, lerp, seg, circle, rr, glow, alpha, shade, text, FONTS } from '/engine/core.js';
import { drawFigure, POSES, breathe, bigFace } from '/engine/rig2d.js';
import * as FX from '/engine/fx2d.js';
import * as UI from '/engine/ui2d.js';
import { box, GY, storeInteriorSet, storeFrontEntranceSet, drawPOVPhone } from '../sets/outbreak_world.js';
import { YOU, WOMAN_GLASS, INFECTED_A, TWITCH_POSE, SAFE } from '../cast.js';

// s008 — 10 Minutes Later: No service, call fails, fewer people running outside (114.44..128.32s)
registerShot('s008', {
  draw(g, t, info) {
    const lookWindow = t > 7.8;
    const cam = { z: 1.04 + 0.05 * (t / info.dur), x: 0, y: 0 };
    if (!lookWindow) {
      storeInteriorSet(g, cam, t, { dim: 0.2 });
      layer(g, cam, 1.0, (g) => {
        veil(g, '#060a14', 0.35);
        drawPOVPhone(g, SAFE.CX, E.H * 0.52, t, { mode: 'nocall', zoom: 1.15 });
      });
    } else {
      storeFrontEntranceSet(g, cam, t, { shutterAmt: 0.35, chaos: false });
      layer(g, cam, 1.0, (g) => {
        drawFigure(g, { x: SAFE.CX - 95, y: GY + 24, s: 1.5, facing: 1, outfit: YOU, pose: breathe(POSES.stand, t), rim: { color: '#c9dcff', dir: [-0.7, -1], w: 4 } });
        text(g, 'STREETS GOING QUIET...', SAFE.CX, 175, { size: 19, color: '#9ab4d9', font: FONTS.ui, weight: 800 });
      });
    }
  }
});

// s009 — Checkout counter survey: 4 aisles, 2 fridges, 1 office, 1 storage room (128.32..142.71s)
registerShot('s009', {
  draw(g, t, info) {
    const cam = { z: 1.0 + 0.05 * (t / info.dur), x: Math.sin(t * 0.3) * 14, y: 0 };
    storeInteriorSet(g, cam, t, { dim: 0.15 });

    layer(g, cam, 1.0, (g) => {
      // Checkout counter inside SAFE column (x = 700..1220)
      box(g, 710, GY - 150, 500, 150, 6, '#1f2c40', '#0d131d', 4);
      box(g, 790, GY - 215, 95, 65, 6, '#141c29', '#3b4e6b', 2); // cash register

      drawFigure(g, { x: SAFE.CX + 70, y: GY, s: 1.48, facing: -1, outfit: YOU, pose: breathe(POSES.think, t), rim: { color: '#c9dcff', dir: [0.6, -1], w: 4 } });

      // Crisp HUD callout tags popping in inside SAFE column as narrator lists them!
      const tags = [
        [2.2, '4 AISLES', 795, 255],
        [4.0, '2 REFRIGERATORS', 1115, 255],
        [5.8, '1 SMALL OFFICE', 795, 320],
        [7.4, '1 STORAGE ROOM', 1115, 320],
      ];
      for (const [ts, lbl, tx, ty] of tags) {
        if (t > ts) {
          const a = ease.out(prog(t, ts, ts + 0.45));
          g.save(); g.globalAlpha = a;
          box(g, tx - 108, ty - 22, 216, 42, 8, '#111b2e', '#4c73a8', 2);
          text(g, lbl, tx, ty, { size: 16, color: '#dce9ff', font: FONTS.ui, weight: 900 });
          g.restore();
        }
      }
    });
  }
});

// s010 — Checking empty shelves, torn rice bag & flickering refrigerators (142.71..159.81s)
registerShot('s010', {
  draw(g, t, info) {
    const cam = { z: 1.06 + 0.05 * (t / info.dur), x: 0, y: 0 };
    storeInteriorSet(g, cam, t, { dim: 0.22, powerFlicker: true });

    layer(g, cam, 1.0, (g) => {
      // Center-safe sparse shelf rack showing mostly bare metal shelves
      box(g, 715, 215, 490, GY - 215, 6, '#151e2d', '#0b1018', 4);
      for (let r = 0; r < 4; r++) {
        const sy = 315 + r * 125;
        g.fillStyle = '#2b3b52'; g.fillRect(727, sy, 466, 9);
      }
      // Just 2 dented cans + 1 torn rice bag on Aisle 2
      box(g, 790, 402, 34, 38, 4, '#7d4147');
      box(g, 842, 405, 34, 35, 4, '#456b58');
      box(g, 1020, 515, 78, 50, 8, '#d9cdb8', '#362f25', 2);
      text(g, 'RICE', 1059, 540, { size: 13, color: '#2b241c', font: FONTS.ui, weight: 900 });

      drawFigure(g, {
        x: SAFE.CX - 40, y: GY + 16, s: 1.5, facing: 1, outfit: YOU,
        pose: breathe(POSES.holdFront, t), rim: { color: '#9ec5ff', dir: [-0.8, -1], w: 4 }
      });
    });
  }
});

// s011 — Office Inventory Computer: 2 missing deliveries, actual stock < 50% (159.81..175.89s)
registerShot('s011', {
  draw(g, t, info) {
    UI.blueprint(g);
    // Center-safe 9:16 Inventory Terminal Card (width 520px inside 656..1264!)
    const cx = SAFE.CX, w = 520, x = cx - w / 2, y = 175, h = 710;
    box(g, x, y, w, h, 16, '#0d1626', '#3d6191', 3);
    box(g, x + 20, y + 22, w - 40, 56, 8, '#172640');
    text(g, 'STORE INVENTORY TERMINAL', cx, y + 50, { size: 20, color: '#9ec5ff', font: FONTS.ui, weight: 900 });

    const rows = [
      ['DELIVERY #1 (TUE)', 'MISSING', '#ff5c6c', 1.5],
      ['DELIVERY #2 (THU)', 'MISSING', '#ff5c6c', 3.5],
      ['RECORDED UNITS', '420 PCS', '#cbd9ed', 6.0],
      ['ACTUAL SHELF STOCK', '< 42%', '#ffb85c', 8.5],
    ];
    rows.forEach(([k, v, col, ts], i) => {
      const a = ease.out(prog(t, ts, ts + 0.6));
      const ry = y + 125 + i * 92;
      g.save(); g.globalAlpha = a;
      box(g, x + 28, ry, w - 56, 72, 8, '#121f36', alpha(col, 0.45), 2);
      text(g, k, x + 48, ry + 36, { size: 16, color: '#b5c6e0', font: FONTS.ui, weight: 800, align: 'left' });
      text(g, v, x + w - 48, ry + 36, { size: 20, color: col, font: FONTS.ui, weight: 900, align: 'right' });
      g.restore();
    });

    // Depletion bar at bottom of card
    const barP = ease.inOut(prog(t, 8.0, 12.0));
    box(g, x + 36, y + 540, w - 72, 34, 8, '#09101c', '#2a3d59', 2);
    box(g, x + 40, y + 544, (w - 80) * lerp(0.95, 0.38, barP), 26, 6, '#ff5c6c');
    text(g, 'SUPPLY DEFICIT WARNING', cx, y + 625, { size: 18, color: '#ff7b86', font: FONTS.ui, weight: 900 });
  }
});

// s012 — Rationing count on counter + sitting down disappointed (175.89..197.04s)
registerShot('s012', {
  draw(g, t, info) {
    const sitDown = t > 11.2;
    const cam = { z: 1.05, x: 0, y: 0 };
    storeInteriorSet(g, cam, t, { dim: 0.25, powerFlicker: true });

    layer(g, cam, 1.0, (g) => {
      // Counter table with exact supplies inside SAFE column (x = 710..1210)
      box(g, 705, GY - 135, 510, 135, 6, '#1e2b3d', '#0c121b', 4);

      // 4 water bottles (appear t > 0.6)
      if (t > 0.4) for (let i = 0; i < 4; i++) box(g, 735 + i * 32, GY - 205, 24, 70, 6, '#5aa9e6', '#dceeff', 2);
      // 3 protein bars (t > 2.2)
      if (t > 2.0) for (let i = 0; i < 3; i++) box(g, 882, GY - 152 - i * 16, 54, 13, 3, '#c97b3a');
      // Half jar of peanut butter (t > 3.8)
      if (t > 3.6) {
        box(g, 958, GY - 190, 42, 55, 6, '#4a3a2c', '#d9a45b', 2);
        box(g, 961, GY - 162, 36, 25, 3, '#b87d3b');
      }
      // 2 bruised apples + cans (t > 5.5)
      if (t > 5.4) {
        circle(g, 1032, GY - 150, 15, '#7a3138');
        circle(g, 1066, GY - 150, 15, '#6e2c32');
        box(g, 1105, GY - 185, 36, 50, 4, '#4c6682');
        box(g, 1148, GY - 185, 36, 50, 4, '#5e7355');
      }

      drawFigure(g, {
        x: SAFE.CX, y: sitDown ? GY + 36 : GY + 8, s: 1.48, facing: 1, outfit: YOU,
        pose: sitDown ? breathe(POSES.sit, t) : breathe(POSES.sad, t),
        expr: 'sad', rim: { color: '#c9dcff', dir: [0, -1], w: 4 }
      });
    });
  }
});

// s013 — Motionless woman outside glass raises hand & mouths "Help me." (197.04..220.99s)
registerShot('s013', {
  draw(g, t, info) {
    const raiseHand = prog(t, 9.5, 13.5);
    const helpMe = t > 18.5; // "Help me." at ~219.15s global -> lt ~ 22.1s, mouth moves at lt ~ 16s
    const cam = { z: 1.12 + 0.12 * (t / info.dur), x: 0, y: -18 * (t / info.dur) };
    storeFrontEntranceSet(g, cam, t, { shutterAmt: 0.22, night: true });

    layer(g, cam, 1.0, (g) => {
      // Motionless woman standing dead-center outside the glass (x = SAFE.CX)
      drawFigure(g, {
        x: SAFE.CX, y: GY - 8, s: 1.52, facing: -1, outfit: WOMAN_GLASS,
        pose: raiseHand > 0.05 ? POSES.reach : POSES.stand,
        expr: 'sad', rim: { color: '#a8c6ff', dir: [0, -1], w: 4.5 }
      });
      // Pale palm pressed flat against window glass + condensation halo
      if (raiseHand > 0.5) {
        const a = (raiseHand - 0.5) * 2;
        glow(g, SAFE.CX - 38, 455, 75, '#dceaff', 0.25 * a);
        box(g, SAFE.CX - 50, 438, 24, 34, 8, alpha('#cfdcf0', 0.85 * a));
      }
      // Silent lip-read subtitle ghosted right on the glass inside SAFE!
      if (helpMe) {
        const p = ease.out(prog(t, 18.5, 20.5));
        g.save(); g.globalAlpha = p * 0.9;
        text(g, '"Help me..."', SAFE.CX, 335, { size: 28, color: '#e6f0ff', font: FONTS.serif, style: 'italic', weight: 900 });
        g.restore();
      }
    });
  }
});

// s014 — Cliffhanger Part 2: You don't move — crooked figure appears behind her! (220.99..228.40s)
registerShot('s014', {
  draw(g, t, info) {
    const emerge = ease.out(prog(t, 1.4, 5.2));
    const cam = { z: 1.24 + 0.06 * (t / info.dur), x: 0, y: -22 };
    storeFrontEntranceSet(g, cam, t, { shutterAmt: 0.22, night: true });

    layer(g, cam, 1.0, (g) => {
      // Unnatural crooked figure lurching out of the fog right behind her inside SAFE!
      if (emerge > 0.02) {
        const wob = Math.sin(t * 9.5) * 7;
        g.save(); g.globalAlpha = emerge;
        drawFigure(g, {
          x: lerp(SAFE.CX + 145, SAFE.CX + 82, emerge) + wob * 0.4,
          y: GY - 28, s: 1.38, facing: -1, outfit: INFECTED_A,
          pose: TWITCH_POSE, expr: 'angry',
          rim: { color: '#ff4d5e', dir: [0.8, -0.6], w: 4.5 }
        });
        // Eerie pale eye pinpoints
        circle(g, lerp(SAFE.CX + 145, SAFE.CX + 82, emerge) - 8, GY - 295, 3.5, '#ff6b78');
        g.restore();
      }

      drawFigure(g, {
        x: SAFE.CX - 22, y: GY - 8, s: 1.52, facing: -1, outfit: WOMAN_GLASS,
        pose: POSES.reach, expr: 'scared', rim: { color: '#a8c6ff', dir: [-0.5, -1], w: 4 }
      });
      veil(g, '#050812', 0.25 * prog(t, 5.5, 7.2));
    });
  }
});
