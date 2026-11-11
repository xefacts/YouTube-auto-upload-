// scenes/shots/04_ch4.js — Chapter 4 (s022..s028): Midnight Map & The Ringing Phone (354.78s .. 450.08s)
import { E, registerShot, layer, veil, ease, prog, clamp, lerp, seg, circle, rr, glow, alpha, text, FONTS } from '/engine/core.js';
import { drawFigure, POSES, breathe } from '/engine/rig2d.js';
import * as UI from '/engine/ui2d.js';
import { box, GY, storeInteriorSet, storeFrontEntranceSet, drawPOVPhone } from '../sets/outbreak_world.js';
import { YOU, INFECTED_A, INFECTED_B, TWITCH_POSE, SAFE } from '../cast.js';

// s022 — Exhausted behind checkout counter: shaking hands, supplies & clock at 11:58 PM (354.78..378.29s)
registerShot('s022', {
  draw(g, t, info) {
    const cam = { z: 1.06 + 0.05 * (t / info.dur), x: 0, y: 0 };
    storeInteriorSet(g, cam, t, { dim: 0.45, night: true, powerFlicker: true });

    layer(g, cam, 1.0, (g) => {
      // Wall digital/analog store clock inside SAFE column showing 11:58 PM ("almost midnight")
      box(g, SAFE.CX - 85, 155, 170, 56, 10, '#0c1320', '#395275', 3);
      text(g, '11:58 PM', SAFE.CX, 183, { size: 22, color: '#ff6b78', font: FONTS.ui, weight: 900 });

      // Counter + crouched exhausted YOU behind it
      box(g, 705, GY - 150, 510, 150, 6, '#172233', '#090e17', 4);
      const tremor = Math.sin(t * 36) * 2.5;
      drawFigure(g, {
        x: SAFE.CX + tremor, y: GY + 34, s: 1.48, facing: 1, outfit: YOU,
        pose: POSES.sit, expr: 'sad',
        rim: { color: '#9ec5ff', dir: [0, -1], w: 4 }
      });
    });
  }
});

// s023 — Counter Emergency Radio: sweeping frequencies -> pure STATIC (378.29..384.11s)
registerShot('s023', {
  draw(g, t, info) {
    const cam = { z: 1.25, x: 0, y: 20 };
    storeInteriorSet(g, cam, t, { dim: 0.55, night: true });

    layer(g, cam, 1.0, (g) => {
      veil(g, '#040710', 0.48);
      // Close-up emergency desktop radio centered in SAFE
      box(g, SAFE.CX - 180, 430, 360, 190, 14, '#141c29', '#3b4f6e', 4);
      seg(g, [[SAFE.CX + 120, 430], [SAFE.CX + 145, 280]], 5, '#8ea4c2');
      // Frequency dial sweeping + static waveform jagged line
      box(g, SAFE.CX - 145, 465, 290, 58, 8, '#09111c', '#2b405e', 2);
      const dialX = lerp(SAFE.CX - 125, SAFE.CX + 115, (Math.sin(t * 2.4) + 1) * 0.5);
      seg(g, [[dialX, 470], [dialX, 518]], 4, '#ff5c6c');

      g.strokeStyle = '#7fb3ff'; g.lineWidth = 2;
      g.beginPath();
      for (let i = 0; i <= 36; i++) {
        const sx = SAFE.CX - 135 + i * 7.5;
        const sy = 568 + Math.sin(t * 48 + i * 1.9) * 14;
        if (i === 0) g.moveTo(sx, sy); else g.lineTo(sx, sy);
      }
      g.stroke();
      text(g, 'STATIC — NO SIGNAL', SAFE.CX, 385, { size: 20, color: '#ff7b86', font: FONTS.ui, weight: 900 });
    });
  }
});

// s024 — Blueprint Offline City Map: Municipal Transit Station 2 blocks east + storm drains (384.11..413.34s)
registerShot('s024', {
  draw(g, t, info) {
    UI.blueprint(g);
    const zoom = 1 + 0.14 * ease.inOut(prog(t, 6.0, 15.0));
    const cx = SAFE.CX, w = 520, x = cx - w / 2, y = 150, h = 760;

    box(g, x, y, w, h, 20, '#0a1424', '#3d689e', 3);
    text(g, 'OFFLINE CITY TRANSIT MAP', cx, y + 46, { size: 19, color: '#9ec5ff', font: FONTS.ui, weight: 900 });

    // Street grid inside card
    g.strokeStyle = alpha('#4a78b0', 0.32); g.lineWidth = 2;
    for (let i = 1; i <= 6; i++) {
      g.beginPath(); g.moveTo(x + 28, y + 80 + i * 88); g.lineTo(x + w - 28, y + 80 + i * 88); g.stroke();
      g.beginPath(); g.moveTo(x + i * 74, y + 95); g.lineTo(x + i * 74, y + h - 95); g.stroke();
    }

    // Store marker (bottom-left of safe map) -> dashed route -> Transit Station (top-right of safe map)
    const sx = cx - 135, sy = y + 545;
    const tx = cx + 115, ty = y + 255;
    const routeP = ease.inOut(prog(t, 2.5, 11.0));
    seg(g, [[sx, sy], [lerp(sx, cx, routeP), sy], [lerp(sx, tx, routeP), lerp(sy, ty, routeP)]], 6, '#4de69b');

    circle(g, sx, sy, 12, '#ffd27d');
    text(g, 'YOU (STORE)', sx + 12, sy + 32, { size: 14, color: '#ffd27d', font: FONTS.ui, weight: 900 });

    glow(g, tx, ty, 85 * zoom, '#4de69b', 0.35);
    box(g, tx - 58, ty - 34, 116, 68, 8, '#112b24', '#4de69b', 3);
    text(g, 'TRANSIT STA.', tx, ty - 8, { size: 13, color: '#8affc1', font: FONTS.ui, weight: 900 });
    text(g, 'EAST ACCESS', tx, ty + 14, { size: 12, color: '#d4f7e4', font: FONTS.ui, weight: 800 });

    // Storm drainage network sub-callout at t > 13s
    if (t > 12.5) {
      const a = ease.out(prog(t, 12.5, 14.0));
      g.save(); g.globalAlpha = a;
      box(g, x + 32, y + h - 125, w - 64, 86, 10, '#102036', '#4de69b', 2);
      text(g, 'REINFORCED WALLS · GENERATORS', cx, y + h - 94, { size: 15, color: '#8affc1', font: FONTS.ui, weight: 900 });
      text(g, '+ STORM DRAINAGE TUNNEL NETWORK', cx, y + h - 66, { size: 14, color: '#cde2ff', font: FONTS.ui, weight: 800 });
      g.restore();
    }
  }
});

// s025 — Putting phone away -> eerie sound from front entrance: A PHONE RINGING (413.34..422.20s)
registerShot('s025', {
  draw(g, t, info) {
    const ring = t > 4.8;
    const cam = { z: 1.08 + 0.06 * (t / info.dur), x: 0, y: 0 };
    storeFrontEntranceSet(g, cam, t, { shutterAmt: 0.72, night: true, barricade: true });

    layer(g, cam, 1.0, (g) => {
      veil(g, '#040710', 0.42);
      if (ring) {
        const r = ((t * 110) % 140) + 25;
        g.strokeStyle = alpha('#7fb8ff', 1 - r / 170); g.lineWidth = 3;
        g.beginPath(); g.arc(SAFE.CX, 470, r, 0, Math.PI * 2); g.stroke();
        glow(g, SAFE.CX, 470, 150, '#5aa9ff', 0.28);
        text(g, '♪ RINGING OUTSIDE... ♪', SAFE.CX, 240, { size: 20, color: '#9ec5ff', font: FONTS.ui, weight: 900 });
      }
    });
  }
});

// s026 — Peering through gap in shelves: motionless person with glowing ringing phone in pocket (422.20..435.79s)
registerShot('s026', {
  draw(g, t, info) {
    const cam = { z: 1.22 + 0.08 * (t / info.dur), x: 0, y: -15 };
    storeFrontEntranceSet(g, cam, t, { shutterAmt: 0.35, night: true });

    layer(g, cam, 1.0, (g) => {
      // Motionless infected standing outside glass with glowing pocket phone!
      drawFigure(g, {
        x: SAFE.CX - 20, y: GY - 10, s: 1.48, facing: -1, outfit: INFECTED_B,
        pose: POSES.stand, expr: 'neutral',
        rim: { color: '#8ab8ff', dir: [0, -1], w: 4 }
      });
      const pulse = 0.5 + 0.5 * Math.sin(t * 12);
      glow(g, SAFE.CX - 12, GY - 145, 75, '#6bb5ff', 0.45 * pulse);
      circle(g, SAFE.CX - 12, GY - 145, 7, '#bfe0ff');

      // Foreground shelf slats framing YOUR secret POV gap (left/right edges of SAFE!)
      g.fillStyle = '#070b13';
      g.fillRect(0, 0, 725, E.H);
      g.fillRect(1195, 0, E.W - 1195, E.H);
      g.fillStyle = '#182233';
      g.fillRect(715, 0, 16, E.H);
      g.fillRect(1189, 0, 16, E.H);
    });
  }
});

// s027 — Second infected approaches & BOTH turn toward the glass! (435.79..444.81s)
registerShot('s027', {
  draw(g, t, info) {
    const arrive = ease.out(prog(t, 0.4, 4.2));
    const snapTurn = t > 5.0;
    const cam = { z: 1.26 + 0.06 * (t / info.dur), x: 0, y: -18 };
    storeFrontEntranceSet(g, cam, t, { shutterAmt: 0.35, night: true });

    layer(g, cam, 1.0, (g) => {
      drawFigure(g, {
        x: SAFE.CX - 48, y: GY - 10, s: 1.46, facing: -1, outfit: INFECTED_B,
        pose: snapTurn ? TWITCH_POSE : POSES.stand, expr: 'angry',
        rim: { color: '#8ab8ff', dir: [0, -1], w: 4 }
      });
      drawFigure(g, {
        x: lerp(SAFE.CX + 165, SAFE.CX + 58, arrive), y: GY - 14, s: 1.44, facing: -1,
        outfit: INFECTED_A, pose: TWITCH_POSE, expr: 'angry',
        rim: { color: '#ff5c6c', dir: [0.6, -1], w: 4 }
      });
      if (snapTurn) {
        for (const ex of [SAFE.CX - 52, SAFE.CX + 52]) {
          circle(g, ex - 5, GY - 305, 3.5, '#ff6b78');
          circle(g, ex + 5, GY - 305, 3.5, '#ff6b78');
        }
      }
      g.fillStyle = '#070b13';
      g.fillRect(0, 0, 715, E.H); g.fillRect(1205, 0, E.W - 1205, E.H);
    });
  }
});

// s028 — Cliffhanger Part 4: Slowly backing away — the store is attracting attention (444.81..450.08s)
registerShot('s028', {
  draw(g, t, info) {
    const p = t / info.dur;
    const cam = { z: 1.16 - 0.14 * p, x: 0, y: 0 };
    storeFrontEntranceSet(g, cam, t, { shutterAmt: 0.75, night: true, barricade: true });

    layer(g, cam, 1.0, (g) => {
      veil(g, '#03060e', 0.35 + 0.35 * p);
      drawFigure(g, {
        x: SAFE.CX, y: GY + 28, s: 1.5, facing: 1, outfit: YOU,
        pose: POSES.stand, rim: { color: '#ff5c6c', dir: [0, -1], w: 4.5 }
      });
      text(g, 'ATTRACTING ATTENTION...', SAFE.CX, 225, { size: 21, color: '#ff7b86', font: FONTS.ui, weight: 900 });
    });
  }
});
