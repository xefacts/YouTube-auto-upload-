// scenes/shots/06_ch6.js — Chapter 6 Climax (s036..s042): Control Room & "That's Not My Dad" (618.43s .. 767.92s)
import { E, registerShot, layer, backdrop, veil, ease, prog, clamp, lerp, shake, seg, circle, rr, poly, glow, alpha, text, FONTS } from '/engine/core.js';
import { drawFigure, POSES, breathe, bigFace } from '/engine/rig2d.js';
import * as UI from '/engine/ui2d.js';
import { box, GY, controlRoomSet } from '../sets/outbreak_world.js';
import { YOU, CONTROL_MAN, BOY, SAFE } from '../cast.js';

// s036 — Maintenance Control Room: flashlight beam, desk, radio & man asking "How many followed you?" (618.43..643.32s)
registerShot('s036', {
  draw(g, t, info) {
    const cam = { z: 1.04 + 0.06 * (t / info.dur), x: 0, y: 0 };
    controlRoomSet(g, cam, t, { lightsOut: false, radioOn: false });

    layer(g, cam, 1.0, (g) => {
      // Man holding flashlight near entrance (right side of SAFE: x = 1095)
      drawFigure(g, {
        x: 1095, y: GY + 10, s: 1.48, facing: -1, outfit: CONTROL_MAN,
        pose: breathe(POSES.holdFront, t), expr: 'serious',
        rim: { color: '#ffd089', dir: [-1, -0.5], w: 4 }
      });
      poly(g, [[1045, GY - 195], [815, GY - 250], [815, GY - 90]], alpha('#fff2cc', 0.11));

      // YOU + small silent shadow beside your jacket (left side of SAFE: x = 825)
      drawFigure(g, {
        x: 825, y: GY + 14, s: 1.48, facing: 1, outfit: YOU,
        pose: breathe(POSES.stand, t), rim: { color: '#c9dcff', dir: [1, -0.5], w: 4 }
      });
      if (t > 13.5 && t < 18.5) {
        text(g, '"How many followed you?"', SAFE.CX, 175, { size: 21, color: '#ffd089', font: FONTS.serif, style: 'italic', weight: 900 });
      }
    });
  }
});

// s037 — Evacuation Wall Map Close-Up: EVACUATED / SEALED / NO ACCESS — and YOUR station marked (643.32..669.57s)
registerShot('s037', {
  draw(g, t, info) {
    UI.blueprint(g);
    const cx = SAFE.CX, w = 524, x = cx - w / 2, y = 145, h = 770;
    box(g, x, y, w, h, 16, '#0b1524', '#3b5f8f', 3);
    text(g, 'MUNICIPAL EVACUATION NETWORK', cx, y + 44, { size: 18, color: '#9ec5ff', font: FONTS.ui, weight: 900 });

    // Underground line network
    seg(g, [[cx - 170, y + 210], [cx - 40, y + 320], [cx + 95, y + 445], [cx - 20, y + 595]], 5, '#466f9e');

    const stations = [
      [cx - 165, y + 210, 'NORTH STA. — EVACUATED', '#ff5c6c', 2.0],
      [cx - 40,  y + 320, 'CENTRAL — SEALED',       '#ff5c6c', 5.0],
      [cx + 95,  y + 445, 'WEST LINE — NO ACCESS',  '#ff5c6c', 7.5],
      [cx - 20,  y + 595, 'THIS STATION — [ ? ]',   '#ffbf47', 11.0],
    ];
    for (const [sx, sy, lbl, col, ts] of stations) {
      const a = ease.out(prog(t, ts, ts + 0.8));
      g.save(); g.globalAlpha = a;
      g.strokeStyle = col; g.lineWidth = 4;
      g.beginPath(); g.arc(sx, sy, 22, 0, Math.PI * 2); g.stroke();
      box(g, cx - 210, sy + 28, 420, 40, 6, '#0f1d33', alpha(col, 0.5), 2);
      text(g, lbl, cx, sy + 48, { size: 15, color: col, font: FONTS.ui, weight: 900 });
      g.restore();
    }
  }
});

// s038 — Pointing toward second steel door & narrow corridor with dim GREEN emergency light (669.57..690.01s)
registerShot('s038', {
  draw(g, t, info) {
    const cam = { z: 1.14 + 0.08 * (t / info.dur), x: 35 * (t / info.dur), y: -15 };
    controlRoomSet(g, cam, t, { lightsOut: false, radioOn: false });

    layer(g, cam, 1.0, (g) => {
      drawFigure(g, {
        x: 925, y: GY + 10, s: 1.48, facing: 1, outfit: CONTROL_MAN,
        pose: POSES.point, rim: { color: '#4de68a', dir: [1, -0.4], w: 4 }
      });
      glow(g, 1112, 348, 160, '#3dff8b', 0.34);
      if (t > 16.0) text(g, 'STORM DRAINAGE CORRIDOR', SAFE.CX, 175, { size: 18, color: '#7ff5b2', font: FONTS.ui, weight: 800 });
    });
  }
});

// s039 — Radio static erupts: "Control room, do you copy?" -> Child interrupts: "Please don't open the door." (690.01..713.88s)
registerShot('s039', {
  draw(g, t, info) {
    // Radio turns on immediately; Child speaks at ~704.36s global -> lt ~ 14.35s!
    const childVoice = t > 14.1 && t < 16.5;
    const cam = { z: 1.18 + 0.08 * (t / info.dur), x: -20, y: 12 };
    controlRoomSet(g, cam, t, { lightsOut: false, radioOn: true });

    layer(g, cam, 1.0, (g) => {
      // Man reaching toward radio, then freezing & slowly lowering hand after child voice!
      const reached = t > 6.5 && t < 15.5;
      drawFigure(g, {
        x: 965, y: GY + 10, s: 1.48, facing: -1, outfit: CONTROL_MAN,
        pose: reached ? POSES.reach : POSES.stand,
        expr: t > 14.2 ? 'scared' : 'serious',
        rim: { color: '#ff5c6c', dir: [-1, -0.4], w: 4 }
      });

      // Glowing radio static rings rising from desk radio (x=835, y=GY-185)
      const r = ((t * 95) % 110) + 18;
      g.strokeStyle = alpha(childVoice ? '#7ff5b2' : '#ff5c6c', 1 - r / 135);
      g.lineWidth = 3;
      g.beginPath(); g.arc(835, GY - 185, r, 0, Math.PI * 2); g.stroke();

      if (childVoice) {
        text(g, '"Please don\'t open the door."', SAFE.CX, 210, { size: 25, color: '#9effc8', font: FONTS.serif, style: 'italic', weight: 900 });
      }
    });
  }
});

// s040 — THREE KNOCKS from the other side of the second door — "Whatever you do, don't answer it." (713.88..726.82s)
registerShot('s040', {
  draw(g, t, info) {
    // Knocks hit right after "Then you hear three knocks" (~715.6s global -> lt ~ 1.75s, 2.28s, 2.82s)!
    const kPulse = Math.max(
      t > 1.70 && t < 2.15 ? 1 - (t - 1.70) / 0.45 : 0,
      t > 2.23 && t < 2.68 ? 1 - (t - 2.23) / 0.45 : 0,
      t > 2.77 && t < 3.30 ? 1 - (t - 2.77) / 0.53 : 0
    );
    const sh = kPulse > 0 ? shake(t, 7.5 * kPulse) : { x: 0, y: 0 };
    const cam = { z: 1.22 + 0.06 * (t / info.dur), x: 25 + sh.x, y: -15 + sh.y };
    controlRoomSet(g, cam, t, { lightsOut: false, radioOn: true });

    layer(g, cam, 1.0, (g) => {
      if (kPulse > 0.02) {
        glow(g, 1112, 460, 210, '#ff4d5e', 0.55 * kPulse);
        g.strokeStyle = alpha('#ff6b78', kPulse); g.lineWidth = 4;
        g.beginPath(); g.arc(1112, 460, 45 + (1 - kPulse) * 95, 0, Math.PI * 2); g.stroke();
      }
      drawFigure(g, {
        x: 910, y: GY + 12, s: 1.5, facing: -1, outfit: CONTROL_MAN,
        pose: POSES.stand, expr: 'scared',
        rim: { color: '#ff5c6c', dir: [1, -0.5], w: 4.5 }
      });
      if (t > 8.8) {
        text(g, '"Whatever you do, don\'t answer it."', SAFE.CX, 195, { size: 22, color: '#ff858f', font: FONTS.serif, style: 'italic', weight: 900 });
      }
    });
  }
});

// s041 — Closer radio whisper "Dad?" -> Man turns pale -> Looking down at silent boy holding your jacket! (726.82..755.28s)
registerShot('s041', {
  draw(g, t, info) {
    // "Dad?" at ~732.33s -> lt ~ 5.51s! "You slowly look down" at ~744.5s -> lt ~ 17.7s!
    const dadCue = t > 5.3 && t < 7.6;
    const lookDown = t > 17.2;
    const cam = { z: lookDown ? 1.24 : 1.15, x: 0, y: lookDown ? 55 : 0 };
    controlRoomSet(g, cam, t, { lightsOut: false, radioOn: true });

    layer(g, cam, 1.0, (g) => {
      if (!lookDown) {
        // Man turning ghostly pale beside desk radio
        drawFigure(g, {
          x: SAFE.CX + 65, y: GY + 12, s: 1.54, facing: -1, outfit: CONTROL_MAN,
          pose: POSES.stand, expr: 'shocked',
          color: t > 7.8 ? '#dce6f5' : undefined,
          rim: { color: '#c9dcff', dir: [-1, -0.5], w: 4.5 }
        });
        if (dadCue) {
          text(g, '"Dad?"', 835, GY - 245, { size: 28, color: '#9effc8', font: FONTS.serif, style: 'italic', weight: 900 });
        }
      } else {
        // Looking down at YOUR slate jacket sleeve — the silent little boy in the brown hoodie is holding it!
        veil(g, '#040812', 0.38);
        drawFigure(g, {
          x: SAFE.CX - 85, y: GY + 24, s: 1.58, facing: 1, outfit: YOU,
          pose: POSES.stand, rim: { color: '#c9dcff', dir: [0, -1], w: 4 }
        });
        drawFigure(g, {
          x: SAFE.CX + 28, y: GY + 24, s: 1.02, facing: -1, outfit: BOY,
          pose: POSES.reach, expr: 'scared',
          rim: { color: '#ffd089', dir: [-1, -0.6], w: 4.5 }
        });
      }
    });
  }
});

// s042 — FINALE TWIST: "That's not my dad." -> TOTAL BLACKOUT -> Something running toward YOU! (755.28..767.92s)
registerShot('s042', {
  draw(g, t, info) {
    // 0.0..1.1s: "That's not my dad."
    // 2.85s (758.13s global): "The emergency lights go out." -> PITCH BLACKOUT!
    // 8.80s (764.07s global): "Something begins running toward you." -> rushing corridor terror!
    const blackout = t > 3.95;
    const sprint = t > 8.80;

    if (!blackout) {
      // Terrified giant close-up of the boy looking straight up at YOU whispering "That's not my dad."
      backdrop(g, ['#050912', '#0d1626']);
      bigFace(g, SAFE.CX, E.H * 0.56, 0.92, {
        outfit: BOY, expr: 'scared',
        face: { eyes: 'wide', mouth: t < 1.15 ? 'oSmall' : 'flat' },
        rim: '#ffd089'
      });
      text(g, '"That\'s not my dad."', SAFE.CX, 225, { size: 28, color: '#ffe0a3', font: FONTS.serif, style: 'italic', weight: 900 });
    } else {
      // TOTAL BLACKOUT — only the sickly green corridor light & something sprinting straight at YOU!
      const sh = sprint ? shake(t, 14.0 * clamp((t - 8.8) / 2.2), 9.5) : [0, 0];
      g.fillStyle = '#010204';
      g.fillRect(0, 0, E.W, E.H);

      const rushP = sprint ? ease.in(clamp((t - 8.8) / 2.6)) : 0;
      const cx = SAFE.CX + sh[0], cy = E.H * 0.48 + sh[1];

      // Eerie green emergency light at far end of narrow maintenance corridor
      glow(g, cx, cy - 40, 120 + rushP * 260, '#2dff7e', 0.28 + 0.25 * rushP);
      box(g, cx - (65 + rushP * 180), cy - (110 + rushP * 220), 130 + rushP * 360, 220 + rushP * 440, 4, alpha('#06170e', 0.65), alpha('#2dff7e', 0.22), 2);

      if (sprint && t < 11.6) {
        // Pale glowing eyes + twisted silhouette lunging down the corridor straight toward camera!
        const eyeSpread = 10 + rushP * 58;
        const eyeR = 3 + rushP * 14;
        glow(g, cx - eyeSpread, cy - 20, eyeR * 4.5, '#ff3b4e', 0.85);
        glow(g, cx + eyeSpread, cy - 20, eyeR * 4.5, '#ff3b4e', 0.85);
        circle(g, cx - eyeSpread, cy - 20, eyeR, '#ffd6db');
        circle(g, cx + eyeSpread, cy - 20, eyeR, '#ffd6db');
      }

      // Hard cut to pitch black on final 1.0s!
      if (t >= 11.6) {
        g.fillStyle = '#000000';
        g.fillRect(0, 0, E.W, E.H);
      }
    }
  }
});
