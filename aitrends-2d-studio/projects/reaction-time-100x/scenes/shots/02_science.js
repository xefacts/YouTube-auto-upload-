// scenes/shots/02_science.js — Act 2 The Science & The Core Rule (s010 .. s016)
import { E, V, S, registerShot, mood, layer, blurLayer, ease, prog, clamp, lerp, wordTime, seg, circle, ring, rr, glow, alpha, text, FONTS } from '/engine/core.js';
import { drawFigure, POSES, posesAt, breathe } from '/engine/rig2d.js';
import * as FX from '/engine/fx2d.js';
import * as UI from '/engine/ui2d.js';
import { kitchen } from '../sets/kitchen.js';
import { YOU } from '../cast.js';

function eyeIcon(g, r, c) {
  g.strokeStyle = c; g.lineWidth = 5;
  g.beginPath(); g.ellipse(0, 0, r, r * 0.56, 0, 0, Math.PI * 2); g.stroke();
  circle(g, 0, 0, r * 0.28, c);
}
function brainIcon(g, r, c) {
  g.strokeStyle = c; g.lineWidth = 5;
  for (const dx of [-0.32, 0.32]) { g.beginPath(); g.ellipse(dx * r, 0, r * 0.42, r * 0.62, 0, 0, Math.PI * 2); g.stroke(); }
  seg(g, [[-r * 0.5, -r * 0.1], [-r * 0.18, r * 0.15]], 4, c);
  seg(g, [[r * 0.5, -r * 0.1], [r * 0.18, r * 0.15]], 4, c);
}
function handIcon(g, r, c) {
  g.strokeStyle = c; g.lineWidth = 5.5; g.lineCap = 'round';
  rr(g, -r * 0.36, -r * 0.1, r * 0.72, r * 0.68, r * 0.18); g.stroke();
  for (let i = -1.5; i <= 1.5; i++) seg(g, [[i * r * 0.2, -r * 0.1], [i * r * 0.22, -r * 0.62]], 5, c);
}

function drawComparisonBoard(g, t, showYou, tYou = 0, showMs = false) {
  UI.blueprint(g);
  const ui = S().ui, bpc = UI.bpStroke();
  const x0 = V(470, 130), x1 = E.W - V(260, 140), maxMs = 300;
  const rowY = [E.H * V(0.38, 0.38), E.H * V(0.66, 0.6)];

  // Axis ticks 0 .. 300 ms
  seg(g, [[x0, rowY[1] + 115], [x1, rowY[1] + 115]], 2, alpha(bpc, 0.55));
  for (let ms = 0; ms <= 300; ms += 50) {
    const x = x0 + (ms / maxMs) * (x1 - x0);
    seg(g, [[x, rowY[1] + 105], [x, rowY[1] + 125]], 2, alpha(bpc, 0.6));
    text(g, `${ms} ms`, x, rowY[1] + 152, { size: 26, color: alpha(bpc, 0.8), font: FONTS.ui, weight: 800 });
  }

  const drawRow = (y, label, valStr, msVal, color, pose, alphaRow = 1) => {
    g.save(); g.globalAlpha *= alphaRow;
    if (!E.vertical) UI.lineFigure(g, { x: 260, y: y + 105, s: 1.0, pose, color: alpha(color, 0.9) });
    text(g, label, x0, y - 58, { size: 38, color, font: FONTS.ui, weight: 900, align: 'left', spacing: 2 });
    rr(g, x0, y - 26, x1 - x0, 52, 26); g.fillStyle = alpha(color, 0.12); g.fill();
    const w = Math.max(18, ((x1 - x0) * msVal) / maxMs);
    rr(g, x0, y - 26, w, 52, 26); g.fillStyle = color; g.fill();
    glow(g, x0 + w, y, 70, color, 0.55);
    text(g, valStr, x0 + w + 28, y + 2, { size: 54, color, font: FONTS.ui, weight: 900, align: 'left', glow: 14, glowColor: alpha(color, 0.6) });
    g.restore();
  };

  const pNorm = showYou ? 1 : ease.inOut(prog(t, 0.35, 2.1));
  const normVal = showYou || showMs ? `${Math.round(250 * pNorm)} ms` : `${(0.25 * pNorm).toFixed(2)} s`;
  drawRow(rowY[0], 'AVERAGE HUMAN', normVal, 250 * pNorm, bpc, POSES.stand);

  if (showYou) {
    const pYou = ease.out(prog(t, tYou, tYou + 0.25));
    drawRow(rowY[1], 'YOU (100X)', '2.5 ms', 2.5 * pYou, ui.gold, POSES.ready, clamp(pYou * 4));
  }
}

// s010 — "Most people react in about a quarter of a second. Two hundred and fifty milliseconds."
registerShot('s010', {
  draw(g, t, info) {
    const msT = (wordTime('two', info.shot.start) ?? (info.shot.start + 2.6)) - info.shot.start;
    drawComparisonBoard(g, t, false, 0, t >= msT - 0.1);
    if (t >= msT - 0.1) {
      UI.readout(g, { label: '0.25 SECONDS =', value: '250 ms', x: E.W / 2, y: E.H * 0.64, align: 'center', a: ease.out(prog(t, msT - 0.1, msT + 0.3)) });
    }
  }
});

// s011 — "Eye, to brain, to hand."
registerShot('s011', {
  draw(g, t, info) {
    UI.blueprint(g);
    const c = UI.bpStroke(), gold = S().ui.gold, g0 = info.shot.start;
    const T = ['eye', 'brain', 'hand'].map((w, i) => (wordTime(w, g0) ?? (g0 + 0.15 + i * 0.62)) - g0);
    const pts = [[E.W * 0.22, E.H * 0.48], [E.W * 0.5, E.H * 0.48], [E.W * 0.78, E.H * 0.48]];
    const icons = [eyeIcon, brainIcon, handIcon], labels = ['EYE', 'BRAIN', 'HAND'], R = 92;

    for (let i = 0; i < 2; i++) {
      const [ax, ay] = pts[i], [bx, by] = pts[i + 1];
      g.setLineDash([10, 12]);
      seg(g, [[ax + R + 16, ay], [bx - R - 16, by]], 3.5, alpha(c, 0.4));
      g.setLineDash([]);
      const k = ease.inOut(prog(t, T[i] + 0.05, T[i + 1]));
      if (k > 0 && k < 1) {
        const px = lerp(ax + R + 16, bx - R - 16, k);
        glow(g, px, ay, 55, gold, 0.9); circle(g, px, ay, 10, '#fff9e6');
      }
    }
    pts.forEach(([x, y], i) => {
      const on = ease.outBack(prog(t, T[i] - 0.08, T[i] + 0.26));
      const active = t >= T[i] - 0.05;
      const col = active ? gold : alpha(c, 0.5);
      g.save(); g.translate(x, y); g.scale(0.65 + 0.35 * on, 0.65 + 0.35 * on);
      ring(g, 0, 0, R, 4.5, col);
      if (active) glow(g, 0, 0, R * 1.5, gold, 0.28);
      icons[i](g, R * 0.52, col);
      g.restore();
      text(g, labels[i], x, y + R + 58, { size: 42, color: col, font: FONTS.ui, weight: 900, spacing: 3 });
    });
  }
});

// s012 — "You? Two and a half milliseconds."
registerShot('s012', {
  draw(g, t, info) {
    const tYou = (wordTime('two', info.shot.start) ?? (info.shot.start + 0.8)) - info.shot.start;
    drawComparisonBoard(g, t, true, tYou, true);
    UI.badge(g, { str: '100x FASTER', a: ease.out(prog(t, tYou + 0.25, tYou + 0.65)), size: 44 });
  }
});

// s013 — "Here's the rule that runs the whole story."
registerShot('s013', {
  draw(g, t, info) {
    const p = ease.inOut(t / info.dur);
    const cam = { z: 1.05 + 0.1 * p, x: -20 * p, y: -15 * p };
    const { GY, CX, M } = kitchen(g, t, cam, { mood: 'dusk', tea: false });
    layer(g, cam, 1, (g) => {
      drawFigure(g, {
        x: CX, y: GY, s: V(1.62, 1.72), facing: 1, outfit: YOU,
        pose: breathe(posesAt(t, [[0, 'stand'], [0.35, 'pointUp']], 0.35), t),
        expr: 'determined', rim: { color: M.rim, dir: [0, -1], w: 5 }
      });
    });
    FX.dust(g, t, { count: 45, color: M.practical, a: 0.4 });
  }
});

// s014 — "Your brain got faster. Nothing else did."
registerShot('s014', {
  draw(g, t, info) {
    UI.blueprint(g);
    const bpc = UI.bpStroke(), gold = S().ui.gold;
    const cx = E.W / 2, gy = E.H * 0.82;
    const nothingT = (wordTime('nothing', info.shot.start) ?? (info.shot.start + 1.65)) - info.shot.start;

    UI.lineFigure(g, { x: cx, y: gy, s: 2.35, pose: POSES.stand, color: bpc });
    const headY = gy - 208 * 2.35;
    // Blazing gold brain node
    const pulse = 1 + 0.08 * Math.sin(t * 9);
    glow(g, cx + 6, headY, 130 * pulse, gold, 0.65);
    circle(g, cx + 6, headY, 26 * pulse, gold);
    FX.rings(g, cx + 6, headY, t, { count: 3, r0: 36, r1: 135, speed: 1.3, color: gold, a: 0.5 });

    UI.callout(g, t, { at: [cx + 38, headY - 12], to: [cx + 250, headY - 70], str: 'BRAIN: 100x SPEED', color: gold, start: 0.15 });
    UI.callout(g, t, { at: [cx - 30, gy - 320], to: [cx - 280, gy - 350], str: 'HEART & LUNGS: 1.0x', color: bpc, start: nothingT });
    UI.callout(g, t, { at: [cx + 28, gy - 140], to: [cx + 260, gy - 160], str: 'MUSCLES: 1.0x', color: bpc, start: nothingT + 0.15 });
  }
});

// s015 — "Muscles can't move quicker than muscle moves."
registerShot('s015', {
  draw(g, t, info) {
    UI.blueprint(g);
    const bpc = UI.bpStroke(), accent = S().ui.accent, gold = S().ui.gold;
    const sx = E.W * 0.34, sy = E.H * 0.58, L1 = 210, L2 = 200;
    const swing = ease.inOut(prog(t, 0.2, 1.5));
    const elbow = [sx + L1 * 0.85, sy + L1 * 0.2];
    const ang = lerp(0.55, -1.05, swing);
    const hand = [elbow[0] + Math.cos(ang) * L2, elbow[1] + Math.sin(ang) * L2];

    // Trajectory arc
    g.strokeStyle = alpha(accent, 0.55); g.lineWidth = 4; g.setLineDash([10, 10]);
    g.beginPath(); g.arc(elbow[0], elbow[1], L2, -1.05, 0.55); g.stroke(); g.setLineDash([]);

    // Arm bones + muscle fiber curve
    seg(g, [[sx, sy], elbow, hand], 16, bpc);
    circle(g, sx, sy, 18, gold); circle(g, elbow[0], elbow[1], 14, gold); circle(g, hand[0], hand[1], 20, accent);

    // Biological speed cap meter on right
    const mx = E.W * 0.62, my = E.H * 0.42, mw = 460;
    text(g, 'BIOLOGICAL MUSCLE LIMIT', mx, my - 48, { size: 34, color: S().ui.cream, font: FONTS.ui, weight: 900, align: 'left', spacing: 2 });
    rr(g, mx, my - 22, mw, 44, 22); g.fillStyle = alpha(bpc, 0.15); g.fill();
    rr(g, mx, my - 22, mw * 0.68 * swing, 44, 22); g.fillStyle = accent; g.fill();
    seg(g, [[mx + mw * 0.68, my - 42], [mx + mw * 0.68, my + 42]], 5, gold);
    text(g, 'MAX: 1.0x', mx + mw * 0.68, my + 74, { size: 36, color: gold, font: FONTS.ui, weight: 900 });
  }
});

// s016 — "The world didn't slow down. You just... started earlier."
registerShot('s016', {
  draw(g, t, info) {
    UI.blueprint(g);
    const bpc = UI.bpStroke(), gold = S().ui.gold, cream = S().ui.cream;
    const x0 = 320, x1 = E.W - 220, w = x1 - x0;
    const yNorm = E.H * 0.36, yYou = E.H * 0.62;
    const pTime = clamp(t / (info.dur * 0.82)); // 0 .. 1 represents 0 .. 450 ms

    // Shared ms timeline
    text(g, 'SAME MUSCLE SPEED — DIFFERENT START TIME', E.W / 2, E.H * 0.16, { size: 38, color: cream, font: FONTS.ui, weight: 900, spacing: 2.5 });

    // Row 1: NORMAL (waits 55% of timeline thinking, then moves)
    text(g, 'NORMAL', x0 - 36, yNorm, { size: 34, color: bpc, font: FONTS.ui, weight: 900, align: 'right' });
    rr(g, x0, yNorm - 22, w * 0.55, 44, 12); g.fillStyle = alpha(bpc, 0.16); g.fill();
    text(g, 'THINKING (250 ms)', x0 + w * 0.275, yNorm + 1, { size: 24, color: alpha(bpc, 0.85), font: FONTS.ui, weight: 800 });
    const normMove = clamp((pTime - 0.55) / 0.45);
    if (normMove > 0) {
      rr(g, x0 + w * 0.55, yNorm - 22, w * 0.45 * normMove, 44, 12); g.fillStyle = bpc; g.fill();
    }

    // Row 2: YOU (thinks 2.5ms = tiny sliver, immediately moves at exact same slope!)
    text(g, 'YOU', x0 - 36, yYou, { size: 34, color: gold, font: FONTS.ui, weight: 900, align: 'right' });
    rr(g, x0, yYou - 22, 14, 44, 7); g.fillStyle = '#ffffff'; g.fill();
    const youMove = clamp((pTime - 0.02) / 0.45);
    rr(g, x0 + 14, yYou - 22, Math.max(16, w * 0.45 * youMove), 44, 12); g.fillStyle = gold; g.fill();
    glow(g, x0 + 14 + w * 0.45 * youMove, yYou, 65, gold, 0.6);

    const earlyT = (wordTime('started', info.shot.start) ?? (info.shot.start + 2.1)) - info.shot.start;
    if (t >= earlyT - 0.1) {
      UI.dimension(g, t, { x1: x0 + 14, y1: yYou + 66, x2: x0 + w * 0.55, y2: yYou + 66, str: '247.5 ms HEAD START', color: gold, start: earlyT - 0.1 });
    }
  }
});
