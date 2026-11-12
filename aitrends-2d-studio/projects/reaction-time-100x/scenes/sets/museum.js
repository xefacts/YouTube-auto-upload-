// scenes/sets/museum.js — grand museum hall with arched skylight/windows, mezzanine metal rail, dark stairs, overhead lamp & thin red emergency lights.
import { E, V, mood, layer, rr, seg, circle, poly, linGrad, glow, alpha, shade } from '/engine/core.js';
import * as FX from '/engine/fx2d.js';

export const museumGround = () => E.H * V(0.83, 0.68);

export function metalRail(g, x0, x1, y, posts = 7, color = '#6c768e', hi = '#b8c6e0') {
  seg(g, [[x0, y - 92], [x1, y - 92]], 8, hi);
  seg(g, [[x0, y - 48], [x1, y - 48]], 5, color);
  for (let i = 0; i <= posts; i++) {
    const px = x0 + ((x1 - x0) * i) / posts;
    seg(g, [[px, y], [px, y - 92]], 6, color);
  }
}

export function heavyBarrier(g, x, y, rot = 0, s = 1, redLight = false) {
  g.save(); g.translate(x, y); g.rotate(rot); g.scale(s, s);
  // Steel crowd/exhibit barrier on heavy base rollers (40 kg)
  rr(g, -95, -130, 190, 108, 8); g.fillStyle = '#252a38'; g.fill();
  g.strokeStyle = redLight ? '#ff6a6a' : '#8e9ab4'; g.lineWidth = 6; g.stroke();
  // Hazard chevrons across center band
  g.save(); g.beginPath(); g.rect(-88, -94, 176, 32); g.clip();
  g.fillStyle = '#e0a82e'; g.fillRect(-88, -94, 176, 32);
  g.fillStyle = '#1b1e28';
  for (let k = -6; k <= 6; k++) poly(g, [[k * 32, -94], [k * 32 + 16, -94], [k * 32 - 4, -62], [k * 32 - 20, -62]], '#1b1e28');
  g.restore();
  // Heavy base + wheels
  rr(g, -104, -22, 208, 12, 4); g.fillStyle = '#485066'; g.fill();
  circle(g, -78, -6, 9, '#141720'); circle(g, 78, -6, 9, '#141720');
  g.restore();
}

export function fallingScreen(g, x, y, rot = 0, s = 1, broken = false) {
  g.save(); g.translate(x, y); g.rotate(rot); g.scale(s, s);
  // Snapped steel cables above
  seg(g, [[-75, -60], [-82, -110]], 3, '#8892a8');
  seg(g, [[75, -60], [88, -95]], 3, '#8892a8');
  rr(g, -115, -60, 230, 120, 8); g.fillStyle = '#111520'; g.fill();
  g.strokeStyle = '#606a82'; g.lineWidth = 5; g.stroke();
  g.fillStyle = broken ? '#1c1018' : '#20324a'; g.fillRect(-105, -50, 210, 100);
  if (broken) {
    seg(g, [[-20, 40], [0, -10], [45, -35]], 2.5, '#ff8a8a');
    seg(g, [[0, -10], [-55, -30]], 2, '#ff8a8a');
  } else {
    glow(g, 0, 0, 130, '#ff4d4d', 0.22);
  }
  g.restore();
}

export function museum(g, t, cam, o = {}) {
  const emergency = o.emergency !== false;
  const M = mood(o.mood || 'interiorCool'), GY = museumGround(), CX = E.W / 2;
  const wall = shade(M.wall, emergency ? -0.48 : -0.22);
  const wallDark = shade(M.wall, emergency ? -0.72 : -0.5);
  const emRed = '#ff3b3b';

  layer(g, cam, 0.3, (g) => {
    g.fillStyle = linGrad(g, 0, -E.H, 0, GY, [wallDark, wall]);
    g.fillRect(-E.W * 2, -E.H, E.W * 5, GY + E.H);

    // Tall classical arched museum windows & columns
    for (const i of [-2, -1, 0, 1, 2]) {
      const wx = CX + i * 420 - 110, wy = GY - 620;
      FX.windowFrame(g, { x: wx, y: wy, w: 220, h: 430, cols: 2, rows: 2, arch: true, frame: shade(wallDark, -0.35), bar: 8 }, (g, x, y, w, h) => {
        g.fillStyle = linGrad(g, 0, y, 0, y + h, M.sky); g.fillRect(x, y, w, h);
        FX.stars(g, t, { area: [x, y, w, h * 0.6], count: 20, seed: 50 + i });
      });
      // Classical column between arches
      const colX = CX + i * 420 + 185;
      g.fillStyle = shade(wall, -0.15); g.fillRect(colX, GY - 680, 48, 680);
      g.fillStyle = shade(wallDark, -0.25); g.fillRect(colX - 8, GY - 685, 64, 18); g.fillRect(colX - 8, GY - 22, 64, 22);
    }

    // Dark staircase recess on the right
    if (o.stairs !== false) {
      const sx = CX + V(520, 300);
      g.fillStyle = shade(wallDark, -0.45); g.fillRect(sx, GY - 420, 320, 420);
      for (let step = 0; step < 9; step++) {
        g.fillStyle = shade(wall, -0.25 - step * 0.04);
        g.fillRect(sx + step * 30, GY - (step + 1) * 28, 320 - step * 30, 28);
      }
    }

    // Overhead main museum lamp vs thin red emergency wall beacons
    const lampY = GY - 660;
    seg(g, [[CX, -E.H], [CX, lampY]], 4, '#222636');
    rr(g, CX - 60, lampY, 120, 20, 6); g.fillStyle = '#2c3246'; g.fill();
    if (!emergency) {
      circle(g, CX, lampY + 22, 14, '#fff8e8');
      glow(g, CX, lampY + 26, 260, M.key, 0.5);
      FX.lightCone(g, CX, lampY + 20, { angle: Math.PI / 2, spread: 0.85, len: 720, color: M.key, a: 0.16 });
    } else {
      // Thin red emergency beacons along upper wall
      const pulse = 0.78 + 0.22 * Math.sin(t * 5.5);
      for (const ex of [-560, 0, 560]) {
        const bx = CX + ex, by = GY - 540;
        rr(g, bx - 26, by - 7, 52, 14, 5); g.fillStyle = '#381018'; g.fill();
        rr(g, bx - 20, by - 4, 40, 8, 3); g.fillStyle = emRed; g.fill();
        glow(g, bx, by, 170, emRed, 0.42 * pulse);
        FX.lightCone(g, bx, by + 4, { angle: Math.PI / 2, spread: 0.42, len: 620, color: emRed, a: 0.16 * pulse });
        FX.lensStreak(g, bx, by, 340, '#ff6b6b', 0.3 * pulse, 2.5);
      }
    }
  });

  layer(g, cam, 0.86, (g) => {
    g.fillStyle = linGrad(g, 0, GY, 0, GY + 600, [shade(M.floor, emergency ? -0.32 : -0.05), shade(M.dark, -0.45)]);
    g.fillRect(-E.W * 2, GY, E.W * 5, E.H * 2);
    FX.floorLines(g, GY, GY + 600, 'rgba(0,0,0,.28)', 0.075);
    if (emergency) {
      for (const ex of [-560, 0, 560]) FX.pool(g, CX + ex, GY + 18, 220, 42, emRed, 0.2);
    } else {
      FX.pool(g, CX, GY + 18, 520, 68, M.key, 0.22);
    }
    if (o.rail !== false) {
      metalRail(g, CX - V(760, 480), CX - V(260, 120), GY - 4);
    }
  });

  return { GY, CX, M, rimColor: emergency ? '#ff6b6b' : M.rim, railRight: CX - V(260, 120) };
}
