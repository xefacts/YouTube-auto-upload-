// scenes/sets/outbreak_sets.js — reusable sets for Zombie Apocalypse 4-Minute Storyboard (all colours from mood()/S()).
import { E, V, S, mood, layer, backdrop, rr, seg, circle, poly, linGrad, glow, alpha, shade, mix, text, FONTS } from '/engine/core.js';
import * as FX from '/engine/fx2d.js';

export const aptGround = () => E.H * V(0.82, 0.68);

export function countdownHUD(g, timeStr, sub = null, urgent = false) {
  const ui = S().ui, col = urgent ? ui.accent : ui.gold;
  const x = E.W - 76, y = 104;
  rr(g, x - 210, y - 34, 224, sub ? 78 : 58, 12);
  g.fillStyle = 'rgba(10,12,20,.78)'; g.fill();
  g.strokeStyle = alpha(col, 0.65); g.lineWidth = 2.5; g.stroke();
  text(g, timeStr, x - 98, y - 4, { size: 42, color: col, font: FONTS.ui, weight: 900, glow: 16, glowColor: alpha(col, 0.65), spacing: 2 });
  if (sub) text(g, sub, x - 98, y + 28, { size: 17, color: ui.cream, font: FONTS.ui, weight: 800, spacing: 1.5 });
}

export function apartmentSet(g, t, cam, o = {}) {
  const M = mood(o.mood || 'dusk'), GY = aptGround(), CX = E.W / 2;
  const wall = shade(M.wall, -0.3), wallDark = shade(M.wall, -0.58);
  const alertCol = S().ui.accent;

  layer(g, cam, 0.16, (g) => {
    backdrop(g, M.sky);
    FX.sun(g, CX - 180, GY - 480, 62, '#fff2dc', M.key, 4.5);
    FX.skyline(g, { x: -E.W, y: GY - 190, w: E.W * 3, minH: 70, maxH: 260, color: mix(M.sky[1] || M.wall, wallDark, 0.72), windowColor: alpha(M.practical, 0.7), lit: 0.28, seed: 11 });
    // Distant smoke plumes rising over city
    for (const sx of [CX - 310, CX + 90]) {
      for (let k = 0; k < 5; k++) {
        circle(g, sx + k * 18 + Math.sin(t + k) * 6, GY - 340 - k * 42, 26 + k * 9, alpha(M.dark, 0.42 - k * 0.06));
      }
    }
  });

  layer(g, cam, 0.52, (g) => {
    const wx = CX - 520, wy = GY - 600, ww = 640, wh = 380;
    g.fillStyle = linGrad(g, 0, -E.H, 0, GY, [wallDark, wall]);
    g.fillRect(-E.W * 2, -E.H, E.W * 5, wy + E.H);
    g.fillRect(-E.W * 2, wy, wx + E.W * 2, GY - wy + 20);
    g.fillRect(wx + ww, wy, E.W * 3, GY - wy + 20);
    g.fillRect(wx, wy + wh, ww, GY - (wy + wh) + 20);

    const fc = shade(wallDark, -0.35);
    g.fillStyle = fc; g.fillRect(wx + ww / 2 - 5, wy, 10, wh); g.fillRect(wx, wy + wh * 0.65, ww, 8);
    g.strokeStyle = fc; g.lineWidth = 13; g.strokeRect(wx, wy, ww, wh);

    // Big wall TV flashing Emergency Alert
    const tx = CX + 290, ty = GY - 480, tw = 340, th = 200;
    FX.screen(g, { x: tx, y: ty, w: tw, h: th, glowC: alertCol, a: 0.42 }, (g, x, y, w, h) => {
      g.fillStyle = linGrad(g, x, y, x, y + h, ['#2b0b12', '#4a101a']); g.fillRect(x, y, w, h);
      g.fillStyle = alertCol; g.fillRect(x, y + 18, w, 42);
      text(g, 'EMERGENCY ALERT', x + w / 2, y + 40, { size: 24, color: '#fff', font: FONTS.ui, weight: 900, spacing: 2 });
      text(g, 'STAY INDOORS', x + w / 2, y + 108, { size: 32, color: S().ui.gold, font: FONTS.ui, weight: 900, spacing: 1.5 });
      text(g, 'BIO-CONTAINMENT BREACH', x + w / 2, y + 152, { size: 18, color: '#ffd8d8', font: FONTS.ui, weight: 800 });
    });
    FX.lightCone(g, tx + tw / 2, ty + th / 2, { angle: Math.PI, spread: 0.68, len: 680, color: alertCol, a: 0.16 });
  });

  layer(g, cam, 0.86, (g) => {
    g.fillStyle = linGrad(g, 0, GY, 0, GY + 600, [shade(M.floor, -0.08), shade(M.dark, -0.35)]);
    g.fillRect(-E.W * 2, GY, E.W * 5, E.H * 2);
    FX.floorLines(g, GY, GY + 600, 'rgba(0,0,0,.25)', 0.08);
    FX.pool(g, CX - 200, GY + 20, 440, 62, M.key, 0.2);
    FX.pool(g, CX + 350, GY + 24, 320, 50, alertCol, 0.18);
  });

  return { GY, CX, M, alertCol };
}

export function rooftopSet(g, t, cam, o = {}) {
  const M = mood(o.mood || 'dusk'), GY = E.H * 0.78, CX = E.W / 2;
  const dark = shade(M.dark, -0.2);

  layer(g, cam, 0.14, (g) => {
    backdrop(g, M.sky);
    FX.sun(g, CX + 340, GY - 340, 74, '#fff4de', M.key, 5);
    // Searchlight beams sweeping across dusk sky
    FX.godRays(g, CX - 420, GY + 80, { count: 4, angle: -Math.PI * 0.38, spread: 0.45, len: 1600, color: M.rim, a: 0.12, t });
    FX.godRays(g, CX + 380, GY + 80, { count: 3, angle: -Math.PI * 0.64, spread: 0.35, len: 1500, color: S().ui.accent, a: 0.1, t });
  });

  layer(g, cam, 0.42, (g) => {
    FX.skyline(g, { x: -E.W, y: GY + 30, w: E.W * 3, minH: 90, maxH: 360, color: mix(M.wall, dark, 0.65), windowColor: alpha(M.practical, 0.75), lit: 0.26, seed: 29 });
    // Rising smoke & embers
    for (const sx of [CX - 520, CX + 140, CX + 620]) {
      glow(g, sx, GY - 20, 180, S().ui.accent, 0.28);
      for (let k = 0; k < 5; k++) circle(g, sx + k * 14, GY - 70 - k * 48, 28 + k * 10, alpha(dark, 0.45 - k * 0.06));
    }
  });

  layer(g, cam, 0.88, (g) => {
    // Concrete roof parapet + steel access hatch
    g.fillStyle = shade(M.floor, -0.15); g.fillRect(-E.W * 2, GY - 48, E.W * 5, 52);
    g.fillStyle = linGrad(g, 0, GY, 0, GY + 500, [shade(M.floor, -0.05), dark]);
    g.fillRect(-E.W * 2, GY, E.W * 5, E.H);
    // Steel roof hatch locked shut
    rr(g, CX - 260, GY - 26, 220, 28, 6); g.fillStyle = '#384052'; g.fill();
    g.strokeStyle = M.rim; g.lineWidth = 3; g.stroke();
    FX.pool(g, CX + 80, GY + 16, 520, 64, M.key, 0.22);
  });

  return { GY, CX, M };
}
