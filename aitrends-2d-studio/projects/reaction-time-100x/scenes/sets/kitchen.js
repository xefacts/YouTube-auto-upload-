// scenes/sets/kitchen.js — sunlit / dusk apartment kitchen with wide city window, sink + faucet, pendant lamp, steaming tea mug.
import { E, V, mood, layer, backdrop, rr, seg, circle, poly, linGrad, glow, alpha, shade, mix } from '/engine/core.js';
import * as FX from '/engine/fx2d.js';

export const kitchenGround = () => E.H * V(0.82, 0.68);

export function teaCup(g, x, y, t = 0, o = {}) {
  const { s = 1, hot = true, body = '#f4efe6', tea = '#b8642a', rot = 0 } = o;
  g.save(); g.translate(x, y); g.rotate(rot); g.scale(s, s);
  // saucer + mug
  g.fillStyle = 'rgba(0,0,0,.25)'; g.beginPath(); g.ellipse(0, 2, 24, 5, 0, 0, Math.PI * 2); g.fill();
  rr(g, -22, -4, 44, 6, 3); g.fillStyle = shade(body, -0.12); g.fill();
  rr(g, -15, -34, 30, 31, 6); g.fillStyle = body; g.fill();
  seg(g, [[15, -27], [24, -21], [24, -13], [15, -9]], 4, body);
  g.fillStyle = tea; g.fillRect(-12, -32, 24, 4);
  g.fillStyle = 'rgba(0,0,0,.14)'; g.fillRect(4, -30, 10, 26);
  if (hot) {
    g.strokeStyle = 'rgba(255,245,230,.48)'; g.lineWidth = 2.4; g.lineCap = 'round';
    for (let k = -1; k <= 1; k++) {
      g.beginPath();
      for (let j = 0; j <= 10; j++) {
        const u = j / 10, sy = -38 - u * 36;
        const sx = k * 7 + Math.sin(u * 4.5 - t * 2.8 + k * 1.7) * (4 + u * 4);
        j ? g.lineTo(sx, sy) : g.moveTo(sx, sy);
      }
      g.stroke();
    }
  }
  g.restore();
}

export function sinkUnit(g, x, counterTopY, M, o = {}) {
  const w = o.w || 210, rimCol = '#cfd6e2', darkMetal = '#6d7586';
  // recessed basin lip + water shimmer
  rr(g, x - w / 2, counterTopY - 8, w, 14, 4); g.fillStyle = rimCol; g.fill();
  rr(g, x - w / 2 + 10, counterTopY - 4, w - 20, 8, 2); g.fillStyle = '#5fa8d3'; g.fill();
  glow(g, x, counterTopY, 90, '#9fe0ff', 0.16);
  // gooseneck faucet
  const fx = x + w * 0.28;
  seg(g, [[fx, counterTopY - 8], [fx, counterTopY - 66]], 7, darkMetal);
  g.strokeStyle = rimCol; g.lineWidth = 6.5; g.lineCap = 'round';
  g.beginPath(); g.arc(fx - 22, counterTopY - 66, 22, 0, Math.PI, true); g.stroke();
  // handles
  seg(g, [[fx + 22, counterTopY - 8], [fx + 28, counterTopY - 22]], 4.5, rimCol);
}

export function kitchen(g, t, cam, o = {}) {
  const M = mood(o.mood || 'dusk'), GY = kitchenGround(), CX = E.W / 2;
  const wall = shade(M.wall, -0.28), wallDark = shade(M.wall, -0.56);
  const counterY = GY, counterH = 148, topY = counterY - counterH;
  const sinkX = CX - V(160, 110), mugX = CX + V(210, 150);

  // Sky + city view outside the wide kitchen window
  layer(g, cam, 0.18, (g) => {
    backdrop(g, M.sky);
    FX.sun(g, CX + V(80, 40), topY - V(180, 220), 68, '#fff5e0', M.key, 4.8);
    FX.godRays(g, CX + V(80, 40), topY - V(180, 220), { count: 9, angle: Math.PI * 0.55, spread: 1.0, len: 1300, color: M.key, a: 0.08, t });
    FX.skyline(g, { x: -E.W, y: topY - 10, w: E.W * 3, minH: 50, maxH: V(210, 280), color: mix(M.sky[1] || M.wall, wallDark, 0.72), windowColor: alpha(M.practical, 0.7), lit: 0.28, seed: 14 });
  });

  // Back wall + wide mullioned window + upper cabinets + pendant lamp
  layer(g, cam, 0.55, (g) => {
    const wx = CX - V(430, 360), wy = GY - V(620, 760), ww = V(860, 720), wh = V(360, 420);
    // Wall panels around the window cutout so the real parallax sky shines through
    g.fillStyle = linGrad(g, 0, -E.H, 0, GY, [wallDark, wall]);
    g.fillRect(-E.W * 2, -E.H, E.W * 5, wy + E.H);
    g.fillRect(-E.W * 2, wy, wx + E.W * 2, GY - wy + 20);
    g.fillRect(wx + ww, wy, E.W * 3, GY - wy + 20);
    g.fillRect(wx, wy + wh, ww, GY - (wy + wh) + 20);

    // Window mullions + frame
    const frameC = shade(wallDark, -0.35);
    g.fillStyle = frameC;
    for (let i = 1; i < 4; i++) g.fillRect(wx + (ww * i) / 4 - 5, wy, 10, wh);
    g.fillRect(wx, wy + wh * 0.68, ww, 8);
    g.strokeStyle = frameC; g.lineWidth = 14; g.strokeRect(wx, wy, ww, wh);
    // Warm window sill spill
    g.fillStyle = alpha(M.key, 0.35); g.fillRect(wx - 8, wy + wh, ww + 16, 7);

    // Upper cabinets flanking window
    for (const cx of [wx - 340, wx + ww + 40]) {
      rr(g, cx, wy + 10, 300, 190, 8); g.fillStyle = shade(wall, -0.32); g.fill();
      g.strokeStyle = shade(wallDark, -0.4); g.lineWidth = 2.5; g.strokeRect(cx + 10, wy + 20, 135, 170); g.strokeRect(cx + 155, wy + 20, 135, 170);
    }
    // Wall clock on right
    FX.clock(g, wx + ww + 190, wy + 275, 32, 7 * 3600 + 15 * 60 + t, { face: '#f2ece2' });

    // Warm pendant lamp above counter
    const px = CX + V(190, 130), py = wy - 10;
    seg(g, [[px, -E.H], [px, py + 70]], 3, shade(wallDark, -0.5));
    poly(g, [[px - 44, py + 95], [px + 44, py + 95], [px + 18, py + 66], [px - 18, py + 66]], shade(wallDark, -0.4));
    circle(g, px, py + 97, 10, '#fff6df');
    glow(g, px, py + 104, 180, M.practical, 0.42);
    FX.lightCone(g, px, py + 95, { angle: Math.PI / 2, spread: 0.72, len: 520, color: M.practical, a: 0.13 });
  });

  // Floor + main kitchen counter + sink + optional tea mug
  layer(g, cam, 0.85, (g) => {
    g.fillStyle = linGrad(g, 0, GY, 0, GY + 600, [shade(M.floor, -0.05), shade(M.dark, -0.25)]);
    g.fillRect(-E.W * 2, GY, E.W * 5, E.H * 2);
    FX.floorLines(g, GY, GY + 600, 'rgba(0,0,0,.24)', 0.075);
    FX.pool(g, CX, GY + 18, 520, 68, M.key, 0.22);

    if (o.counter !== false) {
      FX.counter(g, { x: CX - V(580, 460), y: counterY, w: V(1160, 920), h: counterH, color: shade(wall, -0.42), top: shade(M.wall, 0.05), doors: 8 });
      sinkUnit(g, sinkX, topY - 8, M);
      if (o.tea !== false) teaCup(g, mugX, topY - 8, t, { s: 1.15, hot: o.teaHot !== false });
    }
  });

  return { GY, CX, M, topY: topY - 8, sinkX, mugX };
}
