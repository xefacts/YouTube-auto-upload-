// scenes/sets/bedroom.js — two night modes: 'bed' (moonlit bedroom) and 'hall' (Mia's bedroom doorway in warm hallway).
import { E, V, mood, layer, rr, seg, circle, linGrad, glow, alpha, shade } from '/engine/core.js';
import * as FX from '/engine/fx2d.js';

export const bedroomGround = () => E.H * V(0.82, 0.68);

export function nightBedroom(g, t, cam, o = {}) {
  const M = mood(o.mood || 'night'), GY = bedroomGround(), CX = E.W / 2;
  const wall = shade(M.wall, -0.25), wallDark = shade(M.wall, -0.55);

  layer(g, cam, 0.22, (g) => {
    g.fillStyle = linGrad(g, 0, -E.H, 0, GY, [wallDark, wall]);
    g.fillRect(-E.W * 2, -E.H, E.W * 5, GY + E.H);

    const wx = CX + V(180, 60), wy = GY - V(590, 780), ww = V(420, 340), wh = V(400, 440);
    FX.windowFrame(g, { x: wx, y: wy, w: ww, h: wh, cols: 2, rows: 2, frame: shade(wallDark, -0.4), bar: 9 }, (g, x, y, w, h) => {
      g.fillStyle = linGrad(g, 0, y, 0, y + h, M.sky); g.fillRect(x, y, w, h);
      FX.stars(g, t, { area: [x, y, w, h * 0.75], count: 55, seed: 42 });
      FX.moon(g, x + w * 0.68, y + h * 0.28, 34, M.key);
      FX.skyline(g, { x, y: y + h, w, minH: 40, maxH: h * 0.45, color: shade(wallDark, -0.35), windowColor: alpha(M.practical, 0.55), lit: 0.14, seed: 17 });
    });
    FX.godRays(g, wx + ww * 0.65, wy + wh * 0.3, { count: 6, angle: Math.PI * 0.72, spread: 0.55, len: 1100, color: M.key, a: 0.08, t });
    FX.clock(g, CX - V(460, 280), GY - V(500, 700), 36, 3 * 3600 + 12 * 60 + t, { face: '#dfe6f6', speed: o.clockSpeed ?? 1 });
  });

  layer(g, cam, 0.85, (g) => {
    g.fillStyle = linGrad(g, 0, GY, 0, GY + 600, [shade(M.floor, -0.1), shade(M.dark, -0.35)]);
    g.fillRect(-E.W * 2, GY, E.W * 5, E.H * 2);
    FX.floorLines(g, GY, GY + 600, 'rgba(0,0,0,.25)', 0.08);
    FX.pool(g, CX - V(140, 40), GY + 20, 480, 70, M.key, 0.18);
    if (o.bed !== false) {
      FX.bed(g, { x: CX - V(440, 260), y: GY, w: V(460, 420), color: shade(M.key, -0.45), frame: shade(wallDark, -0.3), pillow: '#dde4f8' });
    }
  });

  return { GY, CX, M, bedX: CX - V(440, 260) };
}

export function miaHallway(g, t, cam, o = {}) {
  const M = mood(o.mood || 'interiorWarm'), GY = bedroomGround(), CX = E.W / 2;
  const wall = shade(M.wall, -0.34), wallDark = shade(M.wall, -0.62);
  const doorX = CX + V(40, 20), doorW = 190, doorH = 380, openAmt = o.open ?? 0.42;

  layer(g, cam, 0.45, (g) => {
    g.fillStyle = linGrad(g, 0, -E.H, 0, GY, [wallDark, wall]);
    g.fillRect(-E.W * 2, -E.H, E.W * 5, GY + E.H);
    // Wainscoting trim
    g.fillStyle = shade(wallDark, -0.2); g.fillRect(-E.W * 2, GY - 150, E.W * 5, 8);

    // Warm wall sconce on left
    const sx = CX - V(380, 260), sy = GY - 330;
    rr(g, sx - 10, sy, 20, 32, 5); g.fillStyle = '#fff0d2'; g.fill();
    glow(g, sx, sy + 14, 180, M.practical, 0.38);

    // Mia's bedroom doorway with warm interior glow + little star nameplate
    FX.door(g, { x: doorX, y: GY, w: doorW, h: doorH, color: shade(M.wall, -0.18), open: openAmt, light: M.practical });
    // Doorframe molding
    g.strokeStyle = shade(wallDark, -0.35); g.lineWidth = 12;
    g.strokeRect(doorX - 6, GY - doorH - 6, doorW + 12, doorH + 6);
    // Little star sign on Mia's door
    if (openAmt < 0.75) {
      const signX = doorX + doorW * openAmt + (doorW * (1 - openAmt)) * 0.5;
      circle(g, signX, GY - doorH * 0.66, 14, '#f29ac0');
    }
  });

  layer(g, cam, 0.88, (g) => {
    g.fillStyle = linGrad(g, 0, GY, 0, GY + 600, [shade(M.floor, -0.1), shade(M.dark, -0.32)]);
    g.fillRect(-E.W * 2, GY, E.W * 5, E.H * 2);
    FX.floorLines(g, GY, GY + 600, 'rgba(0,0,0,.24)', 0.08);
    if (openAmt > 0) FX.pool(g, doorX + (doorW * openAmt) / 2, GY + 24, 260 * openAmt + 80, 52, M.practical, 0.32);
  });

  return { GY, CX, M, doorX, doorW, doorH, frameLeft: doorX - 6 };
}
