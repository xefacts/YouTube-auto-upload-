// scenes/sets/yard.js — golden-hour park / backyard soccer pitch with low sun, god rays, trees, goal post and turf lines.
import { E, V, mood, layer, backdrop, seg, circle, linGrad, glow, alpha, shade, mix } from '/engine/core.js';
import * as FX from '/engine/fx2d.js';

export const yardGround = () => E.H * V(0.8, 0.68);

export function yard(g, t, cam, o = {}) {
  const M = mood(o.mood || 'golden'), GY = yardGround(), CX = E.W / 2;
  const treeCol = shade(M.dark, -0.15);

  layer(g, cam, 0.14, (g) => {
    backdrop(g, M.sky);
    const sx = CX + V(460, 220), sy = GY - V(410, 620);
    FX.sun(g, sx, sy, 78, '#fff7e2', M.key, 5.2);
    FX.godRays(g, sx, sy, { count: 11, angle: Math.PI * 0.68, spread: 1.15, len: 1700, color: M.key, a: 0.09, t });
    FX.clouds(g, { y: GY - V(720, 1180), h: 160, color: '#ffe8c8', a: 0.14, seed: 19 });
  });

  layer(g, cam, 0.36, (g) => {
    FX.hills(g, { y: GY - 90, amp: 95, color: mix(M.sky[1] || M.wall, M.dark, 0.62), seed: 12 });
    FX.skyline(g, { x: -E.W, y: GY - 70, w: E.W * 3, minH: 40, maxH: 150, color: mix(M.sky[1] || M.wall, M.dark, 0.78), windowColor: alpha(M.practical, 0.45), lit: 0.16, seed: 23 });
  });

  layer(g, cam, 0.62, (g) => {
    for (const tx of [-880, -640, -360, 520, 790, 1080]) FX.tree(g, CX + tx, GY - 18, 1.15 + ((Math.abs(tx) % 3) * 0.15), treeCol);
    // Goalpost silhouette on the left
    const gx = CX - V(680, 420);
    seg(g, [[gx, GY - 10], [gx, GY - 230], [gx + 130, GY - 230], [gx + 130, GY - 10]], 8, alpha('#f6efe4', 0.65));
    // Fence slats along back
    g.fillStyle = shade(M.dark, -0.1);
    g.fillRect(-E.W * 2, GY - 48, E.W * 5, 8);
    g.fillRect(-E.W * 2, GY - 22, E.W * 5, 8);
  });

  layer(g, cam, 0.9, (g) => {
    g.fillStyle = linGrad(g, 0, GY - 16, 0, GY + 600, [shade(M.grass, 0.06), shade(M.grass, -0.35), shade(M.dark, -0.3)]);
    g.fillRect(-E.W * 2, GY - 16, E.W * 5, E.H * 2);
    // Pitch chalk line
    seg(g, [[-E.W, GY + 24], [E.W * 2, GY + 24]], 4, 'rgba(255,250,235,.22)');
    FX.pool(g, CX + V(220, 80), GY + 16, 620, 75, M.key, 0.22);
  });

  return { GY, CX, M };
}
