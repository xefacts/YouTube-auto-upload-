// scenes/shots/01_cold_open.js — Act 1 Cold Open (s001 .. s009)
import { E, V, S, registerShot, mood, layer, blurLayer, veil, ease, prog, clamp, lerp, shake, wordTime, seg, circle, rr, glow, alpha } from '/engine/core.js';
import { drawFigure, POSES, posesAt, breathe, bigFace, soccerBall } from '/engine/rig2d.js';
import * as FX from '/engine/fx2d.js';
import * as UI from '/engine/ui2d.js';
import { kitchen, teaCup } from '../sets/kitchen.js';
import { yard } from '../sets/yard.js';
import { YOU, LEO } from '../cast.js';

function drawFly(g, x, y, t, s = 1) {
  for (let i = 1; i <= 6; i++) {
    circle(g, x + i * 10 * s, y + Math.sin((t - i * 0.03) * 24) * 6 * s, 1.8 * s, 'rgba(20,16,26,.34)');
  }
  circle(g, x, y, 5.2 * s, '#120e18');
  const wf = Math.abs(Math.sin(t * 92));
  g.fillStyle = 'rgba(235,244,255,.58)';
  g.beginPath(); g.ellipse(x - 2 * s, y - 6 * s, 3.2 * s, 7.5 * s * wf + 1.2, -0.42, 0, Math.PI * 2); g.fill();
  g.beginPath(); g.ellipse(x + 3 * s, y - 6 * s, 3.2 * s, 7.5 * s * wf + 1.2, 0.42, 0, Math.PI * 2); g.fill();
}

function drawHandArm(g, hx, hy, fromX, fromY, s, closed, sleeveCol, rimCol) {
  const ink = S().ink;
  const drawPass = (colArm, colSleeve) => {
    seg(g, [[hx, hy], [fromX, fromY]], 58 * s, colArm);
    seg(g, [[lerp(hx, fromX, 0.22), lerp(hy, fromY, 0.22)], [fromX, fromY]], 84 * s, colSleeve);
    if (closed) {
      circle(g, hx, hy, 40 * s, colArm);
      for (let i = 0; i < 4; i++) circle(g, hx + (i - 1.5) * 14 * s, hy - 26 * s, 13 * s, colArm);
    } else {
      circle(g, hx, hy + 6 * s, 36 * s, colArm);
      for (let i = 0; i < 4; i++) {
        const a = -1.9 + i * 0.34;
        seg(g, [[hx, hy], [hx + Math.cos(a) * 76 * s, hy + Math.sin(a) * 76 * s]], 14 * s, colArm);
      }
    }
  };
  g.save(); g.translate(-4, -5); drawPass(rimCol, rimCol); g.restore();
  drawPass(ink, sleeveCol);
}

// s001 — "A fly buzzes past your ear."
registerShot('s001', {
  draw(g, t, info) {
    const p = ease.inOut(t / info.dur);
    const cam = { z: 1.02 + 0.08 * p, x: -28 * p, y: -12 * p };
    const { GY, CX, M } = kitchen(g, t, cam, { mood: 'dusk', teaHot: true });
    const youX = CX - V(40, 20), sc = V(1.55, 1.65);
    const fx = lerp(CX + 560, CX - 520, ease.linear(t / info.dur));
    const fy = GY - 208 * sc + Math.sin(t * 11) * 16;
    layer(g, cam, 1, (g) => {
      drawFigure(g, {
        x: youX, y: GY, s: sc, facing: 1, outfit: YOU,
        pose: breathe(POSES.relaxed, t), expr: 'neutral',
        rim: { color: M.rim, dir: [0, -1], w: 4.5 }, blink: (t % 3.1) > 2.98
      });
      drawFly(g, fx, fy, t, 1.45);
    });
    blurLayer(g, 11, (g) => {
      rr(g, 90, GY - 210, 110, 260, 26); g.fillStyle = alpha(M.practical, 0.28); g.fill();
    }, cam, 1.65);
    FX.dust(g, t, { count: 42, color: M.practical, a: 0.38 });
  }
});

// s002 — "You don't look. You just... know."
registerShot('s002', {
  draw(g, t, info) {
    const M = mood('dusk');
    blurLayer(g, 14, (g) => kitchen(g, t, { z: 1.55, x: -80, y: -130 }, { mood: 'dusk' }));
    veil(g, M.dark, 0.36);
    const knowT = (wordTime('know', info.shot.start) ?? (info.shot.start + 1.8)) - info.shot.start;
    const r = V(305, 330) * (1 + 0.03 * ease.inOut(t / info.dur));
    const cx = E.W / 2, cy = E.H * V(0.58, 0.54);
    if (t > knowT - 0.1) {
      FX.rings(g, cx, cy - 30, t - (knowT - 0.1), { count: 3, r0: r * 1.02, r1: r * 1.75, speed: 0.9, color: S().ui.gold, a: 0.55 });
      glow(g, cx, cy, r * 1.5, S().ui.gold, 0.18 * ease.out(prog(t, knowT - 0.1, knowT + 0.4)));
    }
    bigFace(g, cx, cy, r, {
      outfit: YOU, expr: t > knowT ? 'smirk' : 'determined',
      look: [0, 0], rimColor: M.rim, rimSide: -1, blink: (t % 3.4) > 3.28
    });
    const fx = lerp(E.W * 0.88, E.W * 0.12, t / info.dur);
    blurLayer(g, 5, (g) => drawFly(g, fx, E.H * 0.38 + Math.sin(t * 14) * 18, t, 3.4));
  }
});

// s003 — "Leo fumbles his phone over the sink,"
registerShot('s003', {
  draw(g, t, info) {
    const p = ease.inOut(t / info.dur);
    const cam = { z: 1.06 + 0.08 * p, x: -30 + 25 * p, y: -18 * p };
    const { GY, M, topY, sinkX } = kitchen(g, t, cam, { mood: 'dusk', teaHot: true });
    const sc = V(1.52, 1.62);
    const fumble = prog(t, 0.35, 1.85);
    const phoneX = sinkX + Math.sin(t * 16) * 18 * (1 - fumble * 0.5);
    const phoneY = lerp(topY - 125, topY - 38, ease.in(fumble));
    const phoneRot = t * 5.2;
    layer(g, cam, 1, (g) => {
      // YOU on left, already alert and shifting weight forward
      drawFigure(g, {
        x: sinkX - V(230, 180), y: GY, s: sc, facing: 1, outfit: YOU,
        pose: breathe(posesAt(t, [[0, 'stand'], [0.65, 'ready']], 0.35), t),
        expr: t > 0.6 ? 'determined' : 'neutral',
        look: [0.6, 0.2], rim: { color: M.rim, dir: [0, -1], w: 4.5 }
      });
      // LEO on right of sink fumbling frantically
      const leoPose = {
        ...POSES.reach,
        eF: [28, -155 + Math.sin(t * 22) * 14], hF: [54, -140 + Math.cos(t * 22) * 18],
        eB: [18, -148 - Math.sin(t * 22) * 12], hB: [44, -132 - Math.cos(t * 22) * 16]
      };
      drawFigure(g, {
        x: sinkX + V(155, 130), y: GY, s: sc, facing: -1, outfit: LEO,
        pose: leoPose, expr: t > 0.4 ? 'shocked' : 'scared',
        look: [-0.6, 0.5], rim: { color: M.rim, dir: [0, -1], w: 4.5 }
      });
      // Tumbling glowing smartphone above sink
      g.save(); g.translate(phoneX, phoneY); g.rotate(phoneRot);
      rr(g, -11, -21, 22, 42, 4); g.fillStyle = '#0c0e16'; g.fill();
      rr(g, -8, -17, 16, 34, 2); g.fillStyle = '#7fe4ff'; g.fill();
      glow(g, 0, 0, 52, '#7fe4ff', 0.45);
      g.restore();
      FX.rings(g, phoneX, phoneY, t, { count: 2, r0: 18, r1: 68, speed: 2.2, color: '#ffffff', a: 0.35 });
    });
    FX.dust(g, t, { count: 38, color: M.practical, a: 0.35 });
  }
});

// s004 — "and before it has dropped ten centimeters," (TIME-STOP #1)
registerShot('s004', {
  draw(g, t, info) {
    const cam = { z: 1.0 + 0.05 * (t / info.dur), r: -0.025 + 0.015 * (t / info.dur) };
    blurLayer(g, 13, (g) => kitchen(g, 0, { z: 1.95, x: -160, y: -150 }, { mood: 'dusk' }));
    veil(g, '#0d1024', 0.42);
    const px = E.W * 0.46, py0 = E.H * 0.33, py = py0 + 36 * ease.out(t / info.dur);
    layer(g, cam, 1, (g) => {
      FX.drops(g, t, { count: 65, color: '#cfe4ff', rMin: 3, rMax: 13, drift: 2.5 });
      FX.rings(g, px, py, t, { count: 3, r0: 90, r1: 440, speed: 0.32, color: '#cfe4ff', a: 0.34 });
      // Giant smartphone frozen mid-tumble
      g.save(); g.translate(px, py); g.rotate(-0.52 + 0.06 * t);
      rr(g, -42, -82, 84, 164, 14); g.fillStyle = '#0c0e18'; g.fill();
      g.strokeStyle = '#b8d4ff'; g.lineWidth = 3.5; g.stroke();
      rr(g, -34, -68, 68, 136, 8); g.fillStyle = '#7fe0ff'; g.fill();
      glow(g, 0, 0, 170, '#7fe0ff', 0.35);
      g.restore();
      // Sink water surface shimmer at bottom
      g.fillStyle = 'rgba(95,180,235,.26)'; g.fillRect(0, E.H * 0.78, E.W, E.H * 0.25);
    });
    g.save(); g.globalCompositeOperation = 'soft-light'; g.fillStyle = 'rgba(75,120,255,.38)'; g.fillRect(0, 0, E.W, E.H); g.restore();
    UI.dimension(g, t, { x1: px + 115, y1: py0 - 50, x2: px + 115, y2: py + 65, str: '10 cm', color: S().ui.gold, start: 0.2 });
    UI.badge(g, { str: '100x', a: ease.out(prog(t, 0.15, 0.55)) });
  }
});

// s005 — "your hand is already there."
registerShot('s005', {
  draw(g, t, info) {
    const M = mood('dusk');
    blurLayer(g, 15, (g) => kitchen(g, t, { z: 1.85, x: -160, y: -120 }, { mood: 'dusk' }));
    veil(g, M.dark, 0.35);
    const snap = 0.42, caught = t >= snap;
    const k = ease.out(prog(t, 0, snap));
    const tx = E.W * 0.52, ty = E.H * 0.52;
    const [sx, sy] = caught ? shake(t, 11 * (1 - prog(t, snap, snap + 0.45)), 28) : [0, 0];
    g.save(); g.translate(sx, sy);
    // Phone
    g.save(); g.translate(tx, ty + (caught ? 0 : -18 * (1 - k))); g.rotate(caught ? -0.18 : -0.5);
    rr(g, -32, -62, 64, 124, 11); g.fillStyle = '#0c0e18'; g.fill();
    rr(g, -26, -52, 52, 104, 6); g.fillStyle = '#7fe0ff'; g.fill();
    g.restore();
    // Streaking hero hand from left
    const hx = lerp(-120, tx - 8, k), hy = lerp(E.H * 0.72, ty + 8, k);
    drawHandArm(g, hx, hy, -380, E.H * 0.88, V(1.35, 1.2), caught, YOU.color, M.rim);
    g.restore();
    if (caught) {
      FX.rings(g, tx, ty, t - snap, { count: 3, r0: 50, r1: 380, speed: 1.5, color: S().ui.gold, a: 0.6 * (1 - prog(t, snap, snap + 1.1)) });
      FX.speedLines(g, t, { cx: tx, cy: ty, count: 44, a: 0.34 * (1 - prog(t, snap, snap + 0.55)) });
      UI.readout(g, { label: 'CAUGHT AT:', value: '2.5 ms', x: V(150, 90), y: E.H - V(155, 420), a: ease.out(prog(t, 0.55, 0.9)) });
    }
  }
});

// s006 — "Then the soccer ball leaves his foot."
registerShot('s006', {
  draw(g, t, info) {
    const kickT = 0.48, p = ease.inOut(t / info.dur);
    const [sx, sy] = t > kickT ? shake(t, 7 * (1 - prog(t, kickT, kickT + 0.35)), 25) : [0, 0];
    const cam = { z: 1.02 + 0.07 * p, x: 35 * p + sx, y: -10 * p + sy };
    const { GY, CX, M } = yard(g, t, cam, { mood: 'golden' });
    const sc = V(1.4, 1.5), leoX = CX - V(360, 230), youX = CX + V(360, 230);
    const flight = ease.out(prog(t, kickT, info.dur));
    const bx = lerp(leoX + 68 * sc, youX - 80 * sc, flight);
    const by = lerp(GY - 34, GY - 220, Math.sin(flight * Math.PI * 0.72));
    layer(g, cam, 1, (g) => {
      drawFigure(g, {
        x: leoX, y: GY, s: sc, facing: 1, outfit: LEO,
        pose: posesAt(t, [[0, 'ready'], [kickT - 0.12, 'kick']], 0.18),
        expr: 'determined', rim: { color: M.rim, dir: [0.6, -0.8], w: 4.5 }
      });
      drawFigure(g, {
        x: youX, y: GY, s: sc, facing: -1, outfit: YOU,
        pose: breathe(POSES.relaxed, t), expr: 'neutral',
        look: [-0.8, -0.2], rim: { color: M.rim, dir: [0.6, -0.8], w: 4.5 }
      });
      soccerBall(g, bx, by, 26, t * 9);
      if (t > kickT && t < kickT + 0.55) {
        FX.rings(g, leoX + 68 * sc, GY - 34, t - kickT, { count: 2, r0: 15, r1: 120, speed: 2.4, color: '#fff3dc', a: 0.65 });
      }
    });
    FX.dust(g, t, { count: 45, color: '#ffe5b8', a: 0.4 });
  }
});

// s007 — "You watch it... all the way." (SLOW-MO BALL TRACKING)
registerShot('s007', {
  draw(g, t, info) {
    const M = mood('golden');
    blurLayer(g, 12, (g) => yard(g, t * 0.08, { z: 1.65, x: 90, y: -90 }, { mood: 'golden' }));
    veil(g, '#1c1210', 0.28);
    FX.drops(g, t, { count: 55, color: '#ffe6b8', rMin: 2.5, rMax: 9, drift: 2 });
    const bx = lerp(E.W * 0.24, E.W * 0.68, ease.linear(t / info.dur));
    const by = E.H * 0.47 - Math.sin((t / info.dur) * Math.PI) * 34;
    // Dotted predicted trajectory arc
    g.save(); g.setLineDash([8, 12]);
    seg(g, [[E.W * 0.12, E.H * 0.54], [bx, by], [E.W * 0.88, E.H * 0.52]], 3, alpha(S().ui.gold, 0.55));
    g.setLineDash([]); g.restore();
    glow(g, bx, by, 160, M.key, 0.35);
    soccerBall(g, bx, by, V(74, 68), t * 0.85);
    // Blurred OTS silhouette of YOU watching on right
    blurLayer(g, 7, (g) => {
      bigFace(g, E.W * 0.88, E.H * 0.78, 210, { outfit: YOU, expr: 'determined', look: [-0.8, -0.3], rimColor: M.rim, rimSide: -1 });
    });
    UI.callout(g, t, { at: [bx, by - 76], to: [bx + 110, by - 165], str: 'SPIN: 0.04 rad/ms', color: S().ui.gold, start: 0.25 });
  }
});

// s008 — "Like it's swimming through honey." (3D THREE.JS GOLDEN ORBIT #1)
registerShot('s008', {
  kind: '3d',
  init(T) {
    const M = mood('golden');
    const st = T.stage({ mood: 'golden', fov: V(36, 50), fog: [16, 52], keyPos: [9, 8, -6], keyIntensity: 2.7, ambient: 1.25 });
    st.add(T.ground(70, 70, M.grass, T.tiles(M.grass, 14, [8, 8])));
    const leo = T.figure3D(LEO, { rim: M.rim, pose: POSES.kick });
    leo.position.set(-2.2, 0, 0); st.add(leo);
    const you = T.figure3D(YOU, { rim: M.rim, pose: POSES.relaxed });
    you.position.set(2.2, 0, 0); you.rotation.y = Math.PI; st.add(you);
    // Mid-air golden-lit soccer ball
    const ball = T.sphere(0.22, T.mat('#f6efe4', { roughness: 0.4 }), 0.1, 1.35, 0);
    st.add(ball);
    // Floating amber honey-dust spheres in 3D space
    for (let i = 0; i < 24; i++) {
      const a = i * 1.37, d = 0.7 + (i % 5) * 0.55;
      const p = T.sphere(0.03 + (i % 3) * 0.015, T.basic(M.practical), Math.cos(a) * d, 0.7 + (i % 6) * 0.32, Math.sin(a) * d);
      st.add(p);
    }
    for (const [tx, tz] of [[-7, -6], [-3, -8], [4, -7], [8, -5], [-6, 6], [7, 6]]) {
      st.add(T.tree3D(tx, tz, 1.15, M.dark));
    }
    for (const sx of [-1.5, 0.5, 2.5]) {
      const sh = T.shaft(2.4, 7.5, M.key, 0.07);
      sh.position.set(sx, 3.2, -1.8); sh.rotation.z = 0.42; st.add(sh);
    }
    return { stage: st, ball };
  },
  draw(s, t, info, T) {
    s.ball.rotation.z = t * 0.6;
    s.ball.position.x = -0.15 + 0.35 * (t / info.dur);
    T.orbit(s.stage.camera, t, { target: [0, 1.2, 0], radius: V(5.4, 7.0), height: [2.1, 1.6], from: -0.65, to: 0.55, dur: info.dur });
  },
  overlay(g, t) {
    UI.badge(g, { str: '100x SLOW', a: ease.out(prog(t, 0.1, 0.5)) });
  }
});

// s009 — "And your tea, sitting on the counter? Still hot."
registerShot('s009', {
  draw(g, t, info) {
    const M = mood('dusk'), p = ease.inOut(t / info.dur);
    blurLayer(g, 12, (g) => kitchen(g, t, { z: 1.7, x: 180, y: -90 }, { mood: 'dusk', counter: false }));
    veil(g, M.dark, 0.25);
    const cy = E.H * V(0.74, 0.66), cx = E.W * 0.48 - 20 * p;
    // Crisp foreground counter surface
    g.fillStyle = shade(M.wall, -0.35); g.fillRect(-100, cy, E.W + 200, E.H);
    g.fillStyle = alpha(M.key, 0.28); g.fillRect(-100, cy, E.W + 200, 8);
    FX.pool(g, cx, cy + 12, 260, 36, M.practical, 0.32);
    teaCup(g, cx, cy, t, { s: V(3.1, 2.8), hot: true });
    FX.dust(g, t, { count: 35, color: M.practical, a: 0.42 });
    const hotT = (wordTime('still', info.shot.start) ?? (info.shot.start + 1.9)) - info.shot.start;
    UI.readout(g, { label: 'ELAPSED: 0.4 s  ·', value: 'STILL HOT', x: E.W / 2, y: E.H * V(0.87, 0.78), align: 'center', a: ease.out(prog(t, hotT - 0.1, hotT + 0.35)) });
  }
});
