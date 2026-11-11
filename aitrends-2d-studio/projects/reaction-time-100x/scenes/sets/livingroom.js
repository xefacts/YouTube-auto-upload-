// scenes/sets/livingroom.js — evening apartment living room with glowing 60Hz TV, sofa, coffee table, and city window.
import { E, V, mood, layer, rr, seg, circle, poly, linGrad, glow, alpha, shade, mix } from '/engine/core.js';
import * as FX from '/engine/fx2d.js';

export const livingGround = () => E.H * V(0.82, 0.68);

export function controllerProp(g, x, y, rot = 0, s = 1, col = '#1b1d28') {
  g.save(); g.translate(x, y); g.rotate(rot); g.scale(s, s);
  rr(g, -24, -12, 48, 22, 9); g.fillStyle = col; g.fill();
  poly(g, [[-22, 2], [-30, 18], [-14, 12]], col);
  poly(g, [[22, 2], [30, 18], [14, 12]], col);
  circle(g, -10, -2, 3.5, '#6fe8ff');
  circle(g, 11, -4, 2.5, '#ff6f61'); circle(g, 16, 0, 2.5, '#ffd47e');
  g.restore();
}

export function sofa(g, x, GY, w = 520, color = '#34283c') {
  const dark = shade(color, -0.32), hi = shade(color, 0.14);
  // legs
  for (const dx of [-w * 0.44, w * 0.44]) seg(g, [[x + dx, GY - 22], [x + dx, GY]], 9, '#1a131f');
  // backrest
  rr(g, x - w / 2, GY - 175, w, 125, 22); g.fillStyle = dark; g.fill();
  // seat cushion
  rr(g, x - w / 2 + 12, GY - 82, w - 24, 62, 16); g.fillStyle = color; g.fill();
  g.fillStyle = alpha(hi, 0.35); g.fillRect(x - w / 2 + 28, GY - 82, w - 56, 6);
  // armrests
  rr(g, x - w / 2 - 18, GY - 126, 44, 106, 16); g.fillStyle = shade(color, -0.15); g.fill();
  rr(g, x + w / 2 - 26, GY - 126, 44, 106, 16); g.fill();
}

export function livingroom(g, t, cam, o = {}) {
  const M = mood(o.mood || 'interiorCool'), GY = livingGround(), CX = E.W / 2;
  const wall = shade(M.wall, -0.25), wallDark = shade(M.wall, -0.55);
  const tvGlow = o.tvGlow || '#6fd8ff';

  layer(g, cam, 0.25, (g) => {
    g.fillStyle = linGrad(g, 0, -E.H, 0, GY, [wallDark, wall]);
    g.fillRect(-E.W * 2, -E.H, E.W * 5, GY + E.H);

    // Tall twilight/night window on left
    const wx = CX - V(690, 440), wy = GY - V(590, 780), ww = V(380, 320), wh = V(390, 440);
    FX.windowFrame(g, { x: wx, y: wy, w: ww, h: wh, cols: 2, rows: 2, frame: shade(wallDark, -0.4), bar: 9 }, (g, x, y, w, h) => {
      g.fillStyle = linGrad(g, 0, y, 0, y + h, M.sky); g.fillRect(x, y, w, h);
      FX.stars(g, t, { area: [x, y, w, h * 0.65], count: 35, seed: 31 });
      FX.skyline(g, { x, y: y + h, w, minH: 50, maxH: h * 0.62, color: shade(wallDark, -0.2), windowColor: alpha(M.practical, 0.8), lit: 0.32, seed: 9 });
      if (o.rainOutside) FX.rain(g, t, { area: [x - 20, y - 20, w + 40, h + 40], count: 70, speed: 900, a: 0.35 });
    });

    // Bookshelf + warm floor lamp on right
    const lx = CX + V(580, 380);
    FX.lampPost(g, lx, GY, 340, { color: shade(wallDark, -0.35), light: M.practical, on: o.lampOn !== false, a: 0.16 });
    FX.clock(g, CX + V(360, 220), GY - V(520, 720), 32, 21 * 3600 + 10 * 60 + t * (o.clockSpeed ?? 1), { face: '#eae4f2' });
  });

  layer(g, cam, 0.82, (g) => {
    g.fillStyle = linGrad(g, 0, GY, 0, GY + 600, [shade(M.floor, -0.08), shade(M.dark, -0.3)]);
    g.fillRect(-E.W * 2, GY, E.W * 5, E.H * 2);
    FX.floorLines(g, GY, GY + 600, 'rgba(0,0,0,.22)', 0.08);
    // Rug under sofa
    rr(g, CX - 420, GY + 12, 840, 56, 24); g.fillStyle = alpha(M.practical, 0.1); g.fill();

    if (o.sofa !== false) sofa(g, CX - V(70, 0), GY, V(540, 480), mix(M.wall, '#2a1f38', 0.5));

    if (o.tv !== false) {
      const tx = CX + V(420, 290), ty = GY - 290, tw = 250, th = 155;
      // TV console stand
      rr(g, tx - 30, GY - 110, tw + 60, 110, 8); g.fillStyle = shade(wallDark, -0.35); g.fill();
      FX.screen(g, { x: tx, y: ty, w: tw, h: th, glowC: tvGlow, a: 0.34 }, (g, x, y, w, h) => {
        g.fillStyle = linGrad(g, x, y, x + w, y + h, ['#0d2238', '#164668']); g.fillRect(x, y, w, h);
        // Animated arcade/action bars on TV
        const p = (t * 2.4) % 1;
        circle(g, x + w * (0.25 + 0.5 * Math.sin(t * 4)), y + h * 0.55, 16, '#ffd47e');
        g.fillStyle = 'rgba(127,232,255,.35)'; g.fillRect(x, y + h * p, w, 4);
      });
      FX.lightCone(g, tx, ty + th / 2, { angle: Math.PI, spread: 0.65, len: 680, color: tvGlow, a: 0.14 });
    }
  });

  return { GY, CX, M, sofaX: CX - V(70, 0) };
}
