// scenes/shots/01_zombie_storyboard.js — All 12 Storyboard Shots (s001 .. s012) for Zombie Apocalypse 4-Minute Countdown
import { E, V, S, registerShot, mood, layer, blurLayer, backdrop, veil, ease, prog, clamp, lerp, shake, seg, circle, ring, rr, poly, glow, linGrad, alpha, shade, mix, text, FONTS } from '/engine/core.js';
import { drawFigure, POSES, breathe, walkPose, bigFace } from '/engine/rig2d.js';
import * as FX from '/engine/fx2d.js';
import * as UI from '/engine/ui2d.js';
import { apartmentSet, rooftopSet, countdownHUD, aptGround } from '../sets/outbreak_sets.js';
import { YOU, SAM, ZOMBIE_A, ZOMBIE_B, ZOMBIE_POSE, CAST } from '../cast.js';

function zombieFig(g, x, y, s, facing, outfit, rimCol, phase = 0) {
  const sway = Math.sin(phase) * 6;
  const p = { ...ZOMBIE_POSE, head: [17 + sway * 0.4, -195 + Math.abs(sway) * 0.4], hF: [70, -158 + sway], hB: [60, -148 - sway] };
  drawFigure(g, {
    x, y, s, facing, outfit, pose: p, expr: 'angry',
    face: { eyes: 'wide', mouth: 'oBig' }, color: '#b8ffcf',
    rim: { color: rimCol, dir: [-facing * 0.8, -0.5], w: 4 }
  });
}

// s001 — [04:00] COLD OPEN EMERGENCY ALERT
registerShot('s001', {
  draw(g, t, info) {
    const p = ease.inOut(t / info.dur);
    const cam = { z: 1.02 + 0.06 * p, x: -20 * p };
    const { GY, CX, M, alertCol } = apartmentSet(g, t, cam, { mood: 'dusk' });
    layer(g, cam, 1, (g) => {
      drawFigure(g, {
        x: CX - 210, y: GY, s: 1.52, facing: 1, outfit: YOU,
        pose: breathe(POSES.phone, t), prop: { type: 'phone', glow: alertCol },
        expr: 'shocked', rim: { color: M.rim, dir: [-0.4, -1], w: 4.5 }
      });
      drawFigure(g, {
        x: CX + 70, y: GY, s: 1.52, facing: 1, outfit: SAM,
        pose: breathe(POSES.handsOnHead, t, 1, 2),
        expr: 'scared', rim: { color: alertCol, dir: [1, -0.3], w: 4.5 }
      });
    });
    FX.dust(g, t, { count: 40, color: M.practical, a: 0.36 });
    countdownHUD(g, '04:00', 'MINUTE 1 BEGINS', true);
  }
});

// s002 — [03:45] GIANT BIGFACE REACTION
registerShot('s002', {
  draw(g, t, info) {
    const M = mood('dusk'), ui = S().ui;
    blurLayer(g, 14, (g) => apartmentSet(g, t, { z: 1.6, x: 140, y: -110 }, { mood: 'dusk' }));
    veil(g, M.dark, 0.38);
    const r = 315 * (1 + 0.03 * (t / info.dur));
    glow(g, E.W * 0.62, E.H * 0.62, 360, ui.accent, 0.25);
    bigFace(g, E.W / 2, E.H * 0.58, r, {
      outfit: YOU, expr: 'determined', look: [0.25, -0.1],
      rimColor: ui.accent, rimSide: 1
    });
    FX.rings(g, E.W / 2, E.H * 0.56, t, { count: 3, r0: r * 1.05, r1: r * 1.55, speed: 0.8, color: ui.accent, a: 0.35 });
    countdownHUD(g, '03:45', 'DECIDE FAST', true);
  }
});

// s003 — [03:30] TITLE CARD OVER BURNING SKYLINE
registerShot('s003', {
  draw(g, t, info) {
    const M = mood('dusk'), cam = { z: 1.05 - 0.04 * (t / info.dur), y: -12 * (t / info.dur) };
    layer(g, cam, 0.2, (g) => {
      backdrop(g, M.sky);
      FX.sun(g, E.W / 2, E.H * 0.64, 88, '#fff2da', M.key, 5.2);
      FX.godRays(g, E.W / 2, E.H * 0.64, { count: 13, angle: -Math.PI / 2, spread: Math.PI * 1.5, len: 1800, color: M.key, a: 0.08, t });
    });
    layer(g, cam, 0.5, (g) => {
      FX.skyline(g, { x: -200, y: E.H * 0.76, w: E.W + 400, minH: 80, maxH: 320, color: shade(M.wall, -0.35), windowColor: alpha(M.practical, 0.8), lit: 0.28, seed: 21 });
      for (const sx of [420, 1380]) {
        glow(g, sx, E.H * 0.72, 200, S().ui.accent, 0.35);
        for (let k = 0; k < 5; k++) circle(g, sx + k * 16, E.H * 0.62 - k * 44, 30 + k * 10, alpha(M.dark, 0.45 - k * 0.06));
      }
    });
    layer(g, cam, 0.8, (g) => {
      g.fillStyle = shade(M.dark, -0.25); g.fillRect(-E.W, E.H * 0.76, E.W * 3, E.H);
      FX.skyline(g, { x: -200, y: E.H * 0.84, w: E.W + 400, minH: 50, maxH: 170, color: shade(M.dark, -0.45), windowColor: alpha(M.practical, 0.9), lit: 0.2, seed: 7 });
    });
    FX.dust(g, t, { count: 45, color: S().ui.gold, a: 0.42 });
    UI.titleCard(g, 2.0, { lines: ['WHAT IF ZOMBIES STARTED', 'AND YOU HAD 4 MINUTES?'], sub: '240 SECONDS TO SURVIVE', dur: 4.0, y: E.H * 0.34 });
  }
});

// s004 — [03:10] 3D THREE.JS STREET OUTBREAK ORBIT
registerShot('s004', {
  kind: '3d',
  init(T) {
    const M = mood('dusk');
    const st = T.stage({ mood: 'dusk', fov: 42, fog: [16, 48], keyPos: [-6, 14, 10], keyIntensity: 2.8, ambient: 1.55 });
    st.add(T.ground(80, 80, M.road, T.tiles(M.road, 14, [12, 12])));
    // Apartment blocks lining LEFT (x=-6.2) and RIGHT (x=+6.2) sides of the avenue
    for (let i = -3; i <= 1; i++) {
      const zPos = i * 5.2 - 2.0;
      const hL = 8.5 + (Math.abs(i) % 3) * 2.8;
      const bL = T.building(4.4, hL, 4.4, { color: M.wall, win: M.practical, lit: 0.55, seed: 10 + i });
      bL.position.set(-6.2, hL / 2, zPos); st.add(bL);
      const hR = 8.0 + ((i + 4) % 3) * 2.6;
      const bR = T.building(4.4, hR, 4.4, { color: M.wall, win: M.practical, lit: 0.5, seed: 30 + i });
      bR.position.set(6.2, hR / 2, zPos); st.add(bR);
    }
    // Streetlamps + warm volumetric cones along both curbs
    for (const zPos of [-10, -4, 2]) {
      for (const side of [-3.4, 3.4]) {
        st.add(T.cyl(0.06, 0.08, 4.2, M.dark, side, 2.1, zPos));
        const sh = T.shaft(2.2, 4.2, M.practical, 0.14); sh.position.set(side, 2.0, zPos); st.add(sh);
      }
    }
    // Abandoned gridlocked cars + red hazard glow
    st.add(T.box(1.5, 0.72, 2.5, '#6e2b35', -1.9, 0.42, -5.0), T.box(1.3, 0.52, 1.3, '#3b1922', -1.9, 0.95, -5.1));
    st.add(T.box(1.5, 0.72, 2.5, '#354966', 2.1, 0.42, -2.2), T.box(1.3, 0.52, 1.3, '#202c40', 2.1, 0.95, -2.3));
    // Shambling zombie horde advancing down the center avenue toward camera
    const zCoords = [[-1.6, -1.2], [-0.4, -0.4], [0.9, -0.9], [1.9, 0.4], [-1.1, 1.1], [0.2, 1.5], [-2.3, -3.2], [0.8, -3.6], [-0.5, -5.2]];
    const zombies = zCoords.map(([x, z], idx) => {
      const f = T.figure3D(idx % 2 ? ZOMBIE_A : ZOMBIE_B, { rim: M.key, pose: ZOMBIE_POSE });
      f.position.set(x, 0, z); st.add(f); return f;
    });
    return { stage: st, zombies };
  },
  draw(s, t, info) {
    const u = Math.min(1, t / Math.max(0.01, info.dur));
    s.stage.camera.position.set(-1.8 + u * 3.6, 3.4 - u * 0.6, 7.6 - u * 1.1);
    s.stage.camera.lookAt(0, 1.5, -3.5);
  },
  overlay(g) {
    countdownHUD(g, '03:10', 'STREETS GRIDLOCKED', true);
  }
});

// s005 — [02:45] EXPONENTIAL OUTBREAK DATA CARD (BLUEPRINT)
registerShot('s005', {
  draw(g, t) {
    UI.blueprint(g);
    UI.dataCard(g, 2.2, {
      w: 1140,
      title: 'INFECTION CASCADE',
      subtitle: '20-SECOND INCUBATION · EXPONENTIAL SPREAD',
      from: 1, to: 4096, decimals: 0, unit: ' CASES',
      start: 0.2, dur: 2.0, shape: 2.4,
      labels: [[0.15, '1 MIN: 8'], [0.55, '2.5 MIN: 256'], [1.0, '4 MIN: 4,096']]
    });
    countdownHUD(g, '02:45', 'EXPONENTIAL SPREAD', false);
  }
});

// s006 — [02:15] MINUTE 2: FILL WATER FIRST (MACRO KITCHEN INSERT)
registerShot('s006', {
  draw(g, t) {
    const M = mood('interiorWarm'), GY = E.H * 0.78, CX = E.W / 2;
    backdrop(g, [shade(M.dark, -0.2), shade(M.wall, -0.25)]);
    FX.windowFrame(g, { x: CX - 420, y: 90, w: 840, h: 360, cols: 3, frame: shade(M.dark, -0.35), bar: 10 }, (g, x, y, w, h) => {
      g.fillStyle = linGrad(g, 0, y, 0, y + h, M.sky); g.fillRect(x, y, w, h);
      FX.skyline(g, { x, y: y + h, w, minH: 40, maxH: 180, color: shade(M.wall, -0.45), windowColor: alpha(M.practical, 0.7), seed: 14 });
    });
    // Counter + chrome faucet blasting water into big pot + bottles
    g.fillStyle = shade(M.wall, -0.42); g.fillRect(-100, GY - 110, E.W + 200, 400);
    g.fillStyle = shade(M.wall, 0.05); g.fillRect(-100, GY - 122, E.W + 200, 14);
    const fx = CX + 40, fy = GY - 122;
    seg(g, [[fx + 70, fy], [fx + 70, fy - 130]], 14, '#8d99ae');
    g.strokeStyle = '#d8e2f0'; g.lineWidth = 13; g.beginPath(); g.arc(fx + 25, fy - 130, 45, 0, Math.PI, true); g.stroke();
    // Blasting water stream + splash rings
    g.fillStyle = '#7fe4ff'; g.fillRect(fx - 26, fy - 125, 14, 115);
    glow(g, fx - 19, fy - 55, 120, '#7fe4ff', 0.45);
    // Steel pot + water jugs
    rr(g, fx - 95, fy - 92, 150, 92, 10); g.fillStyle = '#3c4658'; g.fill();
    g.fillStyle = '#7fe4ff'; g.fillRect(fx - 87, fy - 76, 134, 12);
    for (const bx of [CX + 230, CX + 310, CX + 385]) {
      rr(g, bx, fy - 96, 54, 96, 12); g.fillStyle = 'rgba(130,225,255,.65)'; g.fill();
      rr(g, bx + 15, fy - 112, 24, 18, 4); g.fillStyle = '#d64a33'; g.fill();
    }
    // YOU moving with fast speed afterimages on left
    drawFigure(g, {
      x: CX - 230, y: GY + 165, s: 1.85, facing: 1, outfit: YOU,
      pose: POSES.holdFront, expr: 'determined',
      trail: { count: 4, dx: -38, a: 0.25 },
      rim: { color: M.rim, dir: [0.5, -1], w: 5 }
    });
    UI.callout(g, 1.2, { at: [fx - 20, fy - 92], to: [fx - 210, fy - 210], str: 'RULE #1: FILL EVERY CONTAINER', color: S().ui.gold, start: 0 });
    countdownHUD(g, '02:15', 'PRESSURE DROPPING', false);
  }
});

// s007 — [01:45] BARRICADE THE FRONT DOOR
registerShot('s007', {
  draw(g, t) {
    const M = mood('interiorWarm'), GY = aptGround(), CX = E.W / 2;
    const [sx, sy] = shake(t, 6, 18);
    const cam = { z: 1.08, x: sx, y: sy };
    layer(g, cam, 0.4, (g) => {
      g.fillStyle = linGrad(g, 0, -E.H, 0, GY, [shade(M.wall, -0.62), shade(M.wall, -0.32)]);
      g.fillRect(-E.W, -E.H, E.W * 3, GY + E.H);
      // Rattling apartment door on right with red hallway crack light
      const dx = CX + 330;
      FX.door(g, { x: dx, y: GY, w: 185, h: 410, color: shade(M.wall, -0.18), open: 0.06, light: S().ui.accent });
      FX.rings(g, dx + 10, GY - 220, t, { count: 3, r0: 25, r1: 190, speed: 1.8, color: S().ui.accent, a: 0.55 });
    });
    layer(g, cam, 0.9, (g) => {
      g.fillStyle = shade(M.floor, -0.2); g.fillRect(-E.W, GY, E.W * 3, E.H);
      FX.floorLines(g, GY, GY + 500, 'rgba(0,0,0,.28)', 0.08);
      // Heavy sofa shoved against door
      rr(g, CX + 40, GY - 155, 310, 155, 20); g.fillStyle = shade(M.wall, -0.1); g.fill();
      // YOU and SAM leaning hard into the sofa
      drawFigure(g, {
        x: CX - 30, y: GY, s: 1.55, facing: 1, outfit: YOU,
        pose: POSES.ready, rot: 0.16, expr: 'determined',
        rim: { color: M.rim, dir: [1, -0.4], w: 4.5 }
      });
      drawFigure(g, {
        x: CX - 190, y: GY, s: 1.5, facing: 1, outfit: SAM,
        pose: POSES.ready, rot: 0.14, expr: 'scared',
        rim: { color: M.rim, dir: [1, -0.4], w: 4.5 }
      });
    });
    FX.dust(g, t, { count: 55, color: M.practical, a: 0.45 });
    countdownHUD(g, '01:45', 'BARRICADE ENTRY', true);
  }
});

// s008 — [01:15] MINUTE 3: SILENCE & BLACKOUT DIAGRAM
registerShot('s008', {
  draw(g, t) {
    UI.blueprint(g);
    const ui = S().ui, bpc = UI.bpStroke(), CX = E.W / 2;
    // Left vs Right comparison: LIT WINDOW (DANGER) vs DARK + SILENT (SAFE)
    const drawAptBox = (cx, title, col, lit, safe) => {
      rr(g, cx - 340, 190, 680, 650, 22);
      g.fillStyle = alpha(col, 0.08); g.fill();
      g.strokeStyle = alpha(col, 0.65); g.lineWidth = 3; g.stroke();
      text(g, title, cx, 255, { size: 36, color: col, font: FONTS.ui, weight: 900, spacing: 2 });
      // Building silhouette inside panel
      rr(g, cx - 160, 340, 320, 380, 8); g.fillStyle = '#070c18'; g.fill(); g.strokeStyle = alpha(bpc, 0.45); g.stroke();
      if (lit) {
        rr(g, cx - 90, 410, 180, 120, 6); g.fillStyle = ui.gold; g.fill();
        glow(g, cx, 470, 210, ui.gold, 0.55);
        FX.rings(g, cx, 470, t, { count: 3, r0: 80, r1: 260, speed: 1.2, color: ui.accent, a: 0.6 });
        text(g, 'ATTRACTS HORDE', cx, 780, { size: 30, color: ui.accent, font: FONTS.ui, weight: 900 });
      } else {
        rr(g, cx - 90, 410, 180, 120, 6); g.fillStyle = '#101a2e'; g.fill();
        UI.lineFigure(g, { x: cx, y: 690, s: 0.95, pose: POSES.crouch, color: ui.good });
        text(g, 'INVISIBLE · BREAKER OFF', cx, 780, { size: 30, color: ui.good, font: FONTS.ui, weight: 900 });
      }
    };
    drawAptBox(CX - 410, 'LIGHTS & SOUND ON', ui.accent, true, false);
    drawAptBox(CX + 410, 'TOTAL BLACKOUT', ui.good, false, true);
    countdownHUD(g, '01:15', 'KILL ALL POWER', false);
  }
});

// s009 — [00:45] STAIRWELL CUTAWAY: NEVER GO DOWN — CLIMB UP
registerShot('s009', {
  draw(g, t) {
    const M = mood('storm'), CX = E.W / 2;
    backdrop(g, [shade(M.dark, -0.35), shade(M.wall, -0.35)]);
    // Vertical building shaft cutaway
    const sx = CX - 380, sw = 760;
    g.fillStyle = shade(M.wall, -0.52); g.fillRect(sx, 60, sw, E.H - 120);
    g.strokeStyle = shade(M.wall, -0.15); g.lineWidth = 10; g.strokeRect(sx, 60, sw, E.H - 120);
    // Mid-floor divider
    g.fillStyle = shade(M.wall, -0.2); g.fillRect(sx, E.H * 0.53, sw, 18);

    // Bottom half: red-lit ground stairwell swarming with zombies (TRAP)
    glow(g, CX, E.H * 0.78, 380, S().ui.accent, 0.32);
    for (const [zx, f] of [[CX - 220, 1], [CX - 70, 1], [CX + 90, -1], [CX + 230, -1]]) {
      zombieFig(g, zx, E.H * 0.9, 1.05, f, ZOMBIE_A, S().ui.accent, zx * 0.1 + t * 4);
    }
    UI.callout(g, 1.2, { at: [CX + 180, E.H * 0.74], to: [CX + 460, E.H * 0.72], str: 'LOBBY STAIRS = TRAP', color: S().ui.accent, start: 0 });

    // Top half: cool rim-lit roof ladder where YOU & SAM climb UP to hatch
    const lx = CX - 60;
    seg(g, [[lx - 28, 90], [lx - 28, E.H * 0.53]], 7, M.rim);
    seg(g, [[lx + 28, 90], [lx + 28, E.H * 0.53]], 7, M.rim);
    for (let ry = 130; ry < E.H * 0.52; ry += 38) seg(g, [[lx - 28, ry], [lx + 28, ry]], 5, M.rim);
    glow(g, lx, 90, 200, M.key, 0.5);
    drawFigure(g, { x: lx, y: 340, s: 1.08, facing: 1, outfit: YOU, pose: POSES.reach, expr: 'determined', rim: { color: M.rim, dir: [0, -1], w: 4 } });
    drawFigure(g, { x: lx + 140, y: E.H * 0.53, s: 1.08, facing: -1, outfit: SAM, pose: POSES.pointUp, expr: 'surprised', rim: { color: M.rim, dir: [0, -1], w: 4 } });
    UI.callout(g, 1.2, { at: [lx + 35, 190], to: [CX + 460, 190], str: 'CLIMB TO ROOF HATCH', color: S().ui.gold, start: 0 });
    countdownHUD(g, '00:45', 'GO UP, NOT DOWN', false);
  }
});

// s010 — [00:15] SIGNATURE TIME-STOP: DOOR SPLINTERS AS YOU REACH HATCH
registerShot('s010', {
  draw(g, t) {
    const M = mood('storm');
    blurLayer(g, 11, (g) => {
      backdrop(g, [M.dark, M.wall]);
      glow(g, E.W * 0.35, E.H * 0.65, 420, S().ui.accent, 0.45);
    });
    veil(g, '#0b1026', 0.35);
    FX.drops(g, t, { count: 75, color: '#cfe4ff', rMin: 3, rMax: 13, drift: 2 });
    // Frozen wood splinters radiating from lower-left breach
    const bx = E.W * 0.32, by = E.H * 0.62;
    FX.rings(g, bx, by, t, { count: 3, r0: 90, r1: 480, speed: 0.3, color: '#dce8ff', a: 0.4 });
    for (let i = 0; i < 14; i++) {
      const a = -0.9 + i * 0.16, d = 90 + (i % 4) * 65;
      const px = bx + Math.cos(a) * d, py = by + Math.sin(a) * d;
      g.save(); g.translate(px, py); g.rotate(a + 0.4);
      poly(g, [[-26, -6], [28, 0], [-20, 8]], shade(M.practical, -0.35));
      g.restore();
    }
    zombieFig(g, E.W * 0.24, E.H * 0.92, 1.65, 1, ZOMBIE_A, S().ui.accent, 1);
    // Hero pulling Sam upward on right
    drawFigure(g, {
      x: E.W * 0.72, y: E.H * 0.78, s: 1.68, facing: -1, outfit: YOU,
      pose: POSES.reach, expr: 'determined', rim: { color: M.rim, dir: [-1, -0.5], w: 5 }
    });
    g.save(); g.globalCompositeOperation = 'soft-light'; g.fillStyle = 'rgba(80,125,255,.36)'; g.fillRect(0, 0, E.W, E.H); g.restore();
    UI.badge(g, { str: 'TIME-STOP · 00:15', x: E.W - 80, y: 120, color: S().ui.gold, size: 40 });
  }
});

// s011 — [00:00] ZERO HOUR ON THE ROOFTOP
registerShot('s011', {
  draw(g, t, info) {
    const p = ease.inOut(t / info.dur);
    const cam = { z: 1.06 - 0.05 * p, y: -10 * p };
    const { GY, CX, M } = rooftopSet(g, t, cam, { mood: 'dusk' });
    layer(g, cam, 1, (g) => {
      drawFigure(g, {
        x: CX - 40, y: GY, s: 1.48, facing: 1, outfit: YOU,
        pose: breathe(POSES.stand, t), expr: 'determined',
        rim: { color: M.rim, dir: [0.6, -0.8], w: 4.5 }
      });
      drawFigure(g, {
        x: CX + 130, y: GY, s: 1.45, facing: -1, outfit: SAM,
        pose: breathe(POSES.relaxed, t, 1, 2), expr: 'smile',
        rim: { color: M.rim, dir: [0.6, -0.8], w: 4.5 }
      });
    });
    FX.dust(g, t, { count: 42, color: M.practical, a: 0.4 });
    countdownHUD(g, '00:00', 'SURVIVED MINUTE 4', false);
  }
});

// s012 — END SCREEN CTA
registerShot('s012', {
  draw(g, t) {
    const M = mood('dusk');
    UI.endScreen(g, 1.8, {
      question: 'What would YOU grab in 4 minutes?',
      cast: CAST,
      moodColors: M.sky.slice(0, 3),
      rim: M.rim
    });
  }
});
