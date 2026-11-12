// V3 Studio Master Cast & Biomechanics Upgrade:
// - True 2-Bone Anatomical Sprint/Walk Kinematics (Far-Limb Behind Torso, Near-Limb In Front,
//   Full -36°..+50° Thigh Stride, 82° Heel-Kick Recovery Knee Fold, Ground-Locked Foot Strike!)
// - 12 Situation-Accurate Rick Clips Human Facial Expressions (Zero sleepy half-lids during panic!)
// - Nightmare Horror Zombies (Necrotic Veins, Sunken Bruised Sockets, Glowing Pinprick Eyes, Bloody Fangs!)
// - Full V3 5-Act Cast: YOU, Police Officer, Woman (Plead -> Uncanny Twist), Infected Road Runner,
//   Fleeing Civilians, 3 Nightmare Zombies, Underground Older Survivor Man (Shush -> Pale Horror) & Young Boy!
// Appended to toonbase.js -> toon.js

const RICK_HEAD = "#f7f3ea";
const PALE_HEAD = "#dfe5e3";
const INF_HEAD  = "#9eb0a6";

export const ROLES = {
  you:       { jacket: "#2c5b7c", jacket2: "#1d3e56", trim: "#dce7ef", pants: "#262e3a", hair: "#3a271d", skin: RICK_HEAD, hoodie: true, seed: 11 },
  police:    { jacket: "#1c2d45", jacket2: "#121e30", badge: "#f2c64b", belt: "#181a1f", pants: "#182436", cap: "#19283e", hair: "#2b1e17", skin: RICK_HEAD, seed: 23 },
  woman:     { jacket: "#8c384a", jacket2: "#662635", trim: "#f2e5dd", pants: "#322c38", hair: "#2b1b20", longHair: true, skin: RICK_HEAD, seed: 37 },
  carMan:    { jacket: "#b83e32", jacket2: "#872b22", trim: "#e6dec8", pants: "#2b323b", hair: "#3d2a20", skin: "#d9dad4", seed: 41 },
  runnerA:   { jacket: "#d49c38", jacket2: "#a87926", trim: "#2d3b48", pants: "#2e343d", hair: "#261c18", skin: RICK_HEAD, seed: 53 },
  runnerB:   { jacket: "#4b754e", jacket2: "#365739", trim: "#e8dfc8", pants: "#2b3238", cap: "#3a5a3d", hair: "#5a3c28", skin: RICK_HEAD, seed: 61 },
  survMan:   { jacket: "#4b5747", jacket2: "#333d30", trim: "#c8c2b2", pants: "#2c302d", hair: "#4a4642", stubble: true, skin: "#efe8dc", seed: 71 },
  survBoy:   { jacket: "#d9862b", jacket2: "#a86219", trim: "#f5ebd6", pants: "#2d3644", hair: "#473022", hoodie: true, skin: RICK_HEAD, seed: 79 },
  infectedA: { jacket: "#364045", jacket2: "#22292d", pants: "#1f2427", hair: "#181b1d", skin: INF_HEAD, infected: true, jawOpen: 0.90, seed: 83 },
  infectedB: { jacket: "#474037", jacket2: "#2e2923", pants: "#23201c", hair: "#211b18", skin: "#94a69d", infected: true, jawOpen: 0.78, seed: 89 },
  infectedC: { jacket: "#2f3744", jacket2: "#1d232c", pants: "#1a1e25", hair: "#15171b", skin: "#a8b8b0", infected: true, jawOpen: 0.96, seed: 97 },
  // V6.5 ORIGINS: hidden evil scientist (full gas mask — identity NEVER revealed) + news anchor
  scientist: { jacket: "#dfe2df", jacket2: "#b6bab6", trim: "#39413c", pants: "#262b31", hair: "#20242a", skin: "#3a4038", gasMask: true, labGloves: true, seed: 101 },
  anchor:    { jacket: "#242a36", jacket2: "#171c26", trim: "#b8342c", pants: "#1d222b", hair: "#221c16", skin: RICK_HEAD, seed: 107 },
};

function drawModernHairFront(p, R, H, cx, hc, u, ow, thick, light) {
  if (R.cap) {
    const capCol = R.cap, capDark = mul(capCol, [0.72, 0.72, 0.78]);
    const dome = ellPts(cx, hc - H.b * 0.28, H.a * 1.04, H.b * 0.78, 180, 360, 0, 36);
    p.shadedFill(dome, capCol, capDark, light, H.a, 0.35);
    p.inkRing(dome, ow * 0.9, thick);
    const brim = [
      [cx - H.a * 0.76, hc - H.b * 0.30],
      [cx + H.a * 1.18, hc - H.b * 0.23],
      [cx + H.a * 1.12, hc - H.b * 0.09],
      [cx - H.a * 0.70, hc - H.b * 0.16],
    ];
    p.poly(brim, "#141920", ow * 0.82);
    // Gold police shield emblem or cap patch
    const patchCol = R.badge ? "#f2c64b" : "#f5efe0";
    p.poly(rrect(cx - 13 * u, hc - H.b * 0.68, cx + 13 * u, hc - H.b * 0.44, 4 * u), patchCol, ow * 0.48);
    return;
  }
  const hCol = R.hair || "#3b2920", hDark = mul(hCol, [0.70, 0.68, 0.74]), hHi = mix(hCol, "#ffffff", 0.16);
  const topArc = ellPts(cx, hc - H.b * 0.06, H.a * 1.04, H.b * 1.01, 174, 366, 0, 36);
  const bangs = R.infected
    ? [
        [cx + H.a * 0.96, hc - H.b * 0.14],
        [cx + H.a * 0.60, hc - H.b * 0.44],
        [cx + H.a * 0.26, hc + H.b * 0.05],
        [cx - H.a * 0.16, hc - H.b * 0.45],
        [cx - H.a * 0.56, hc + H.b * 0.02],
        [cx - H.a * 0.98, hc - H.b * 0.22],
      ]
    : [
        [cx + H.a * 0.98, hc - H.b * 0.20],
        [cx + H.a * 0.48, hc - H.b * 0.35],
        [cx + H.a * 0.08, hc - H.b * 0.24],
        [cx - H.a * 0.36, hc - H.b * 0.36],
        [cx - H.a * 0.98, hc - H.b * 0.20],
      ];
  const hairPoly = [...topArc, ...bangs];
  p.shadedFill(hairPoly, hCol, hDark, light, H.a, 0.35);
  if (!R.infected) {
    p.clip(hairPoly, () => {
      p.stroke(ellPts(cx - 18 * u, hc - H.b * 0.56, H.a * 0.44, H.b * 0.20, 200, 325, 0, 18), 5 * u, hHi);
    });
  }
  p.inkRing(hairPoly, ow * 0.88, thick);
}

/** V6.5 Gas-Mask Face for the hidden evil scientist — no skin, no eyes, NO identity. */
function drawGasMaskFace(p, cx, hc, H, u, ow, facing, light, grin = 0) {
  const fx = cx + facing * 12 * u;
  // Rubber hood shading wash
  p.ell(fx, hc - 6 * u, H.a * 0.98, H.b * 0.94, "rgba(21,26,23,0.30)", 0);
  // Forehead reinforcement ridge + strap
  p.band([[fx - H.a * 0.78, hc - H.b * 0.52], [fx + H.a * 0.78, hc - H.b * 0.56]], "#20261f", 7.5 * u, ow * 0.5, "round");
  // Twin circular lenses — dark glass with a cold glint
  const lensY = hc - 2 * u;
  for (const side of [-1, 1]) {
    const lx = fx + side * H.a * 0.46;
    const lr = H.a * 0.30;
    p.ell(lx, lensY, lr * 1.14, lr * 1.14, "#1a2118", ow * 0.9);          // rubber seat
    p.ell(lx, lensY, lr, lr, "#0d1420", 0);                                // glass
    const glintAng = light + 0.6;
    p.stroke([[lx + Math.cos(glintAng) * lr * 0.55, lensY + Math.sin(glintAng) * lr * 0.55],
              [lx + Math.cos(glintAng + 0.5) * lr * 0.28, lensY + Math.sin(glintAng + 0.5) * lr * 0.28]],
             4.2 * u, "rgba(168,214,255,0.85)", "round");
    p.ell(lx - lr * 0.34, lensY - lr * 0.34, lr * 0.16, lr * 0.10, "rgba(190,230,255,0.5)", 0);
  }
  // Bridge plate between lenses
  p.poly([[fx - H.a * 0.16, lensY - 6 * u], [fx + H.a * 0.16, lensY - 6 * u], [fx + H.a * 0.20, lensY + 7 * u], [fx - H.a * 0.20, lensY + 7 * u]], "#242a22", ow * 0.5);
  // Voice-filter cylinder at the mouth with ridged rings
  const fy = hc + H.b * 0.42;
  p.poly([[fx - 13 * u, fy - 11 * u], [fx + 13 * u, fy - 11 * u], [fx + 15 * u, fy + 12 * u], [fx - 15 * u, fy + 12 * u]], "#3d453b", ow * 0.62);
  for (const ry of [-4, 2, 8]) {
    p.band([[fx - 14 * u, fy + ry * u], [fx + 14 * u, fy + ry * u]], "#2a3026", 2.6 * u, 0, "round");
  }
  p.ell(fx, fy + 12 * u, 13 * u, 4.2 * u, "#171c15", ow * 0.4);
  // Side hose curling from the right cheek down out of frame
  p.stroke([[fx + H.a * 0.88, lensY + 8 * u], [fx + H.a * 1.04, lensY + 26 * u], [fx + H.a * 0.80, lensY + 44 * u]], 7.5 * u, "#2b322a", "round");
  if (grin > 0) {
    // V7 THE EVIL LAUGH: a slow, wrong smile curling out from under the voice-filter.
    // The mask hides the face — but the mouth area tightens, twists, rises. Genuinely wrong.
    const gy = fy + 1.5 * u;
    // shadowed smile crease rising asymmetrically around the filter cylinder
    p.stroke([[fx - 26 * u, gy + 7 * u], [fx - 15 * u, gy + 1 * u], [fx - 6 * u, gy - 1.5 * u]],
             3.4 * u, "rgba(6,8,6,0.78)", "round");
    p.stroke([[fx + 26 * u, gy + 4 * u], [fx + 15 * u, gy - 1 * u], [fx + 6 * u, gy - 1.5 * u]],
             3.4 * u, "rgba(6,8,6,0.78)", "round");
    // upper lip pressure bulge over the filter — he is pressing the smile OUT
    p.ell(fx, fy - 7.5 * u, 16 * u, 5.0 * u, "rgba(10,13,10,0.55)", 0);
    // cheek-hitch folds driving the asymmetry upward on his left
    p.stroke([[fx - 20 * u, fy - 12 * u], [fx - 24 * u, fy - 20 * u]], 2.6 * u, "rgba(8,10,8,0.60)", "round");
    p.stroke([[fx + 19 * u, fy - 11 * u], [fx + 23 * u, fy - 18 * u]], 2.2 * u, "rgba(8,10,8,0.50)", "round");
    // twin catchlights in the lenses flick brighter as the laugh builds (cold joy)
    const glr = H.a * 0.30, gly = hc - 2 * u;
    for (const side of [-1, 1]) {
      const glx = fx + side * H.a * 0.46;
      p.ell(glx - glr * 0.30, gly - glr * 0.30, glr * 0.20, glr * 0.13, "rgba(220,245,255,0.85)", 0);
    }
  }
}

/** Upgraded Nightmare Horror Zombie Face: Necrotic Veins, Torn Scar, Sunken Sockets, Glowing Eyes & Bloody Fangs */
function drawHorrorInfectedFace(p, cx, hc, H, u, ow, facing, jawAnim = 0.85, seed = 83) {
  const fx = cx + facing * 15 * u;
  // Upper skull necrotic shadow wash
  p.ell(fx, hc - 8 * u, 42 * u, 24 * u, "rgba(28, 36, 32, 0.34)", 0);

  // Branching dark crimson-violet necrotic veins across temples, cheeks & jaw
  const veinCol = "rgba(64, 14, 28, 0.74)";
  const veinSub = "rgba(88, 18, 32, 0.52)";
  p.stroke([[fx - 38 * u, hc - 28 * u], [fx - 24 * u, hc - 10 * u], [fx - 31 * u, hc + 12 * u]], 2.5 * u, veinCol);
  p.stroke([[fx - 24 * u, hc - 10 * u], [fx - 12 * u, hc - 1 * u]], 1.7 * u, veinSub);
  p.stroke([[fx + 36 * u, hc - 24 * u], [fx + 22 * u, hc + 2 * u], [fx + 29 * u, hc + 24 * u]], 2.5 * u, veinCol);
  p.stroke([[fx + 22 * u, hc + 2 * u], [fx + 10 * u, hc + 12 * u]], 1.7 * u, veinSub);
  p.stroke([[fx - 18 * u, hc + 26 * u], [fx - 24 * u, hc + 42 * u]], 2.0 * u, veinCol);

  // Torn cheek gash on right side
  p.stroke([[fx + 18 * u, hc + 10 * u], [fx + 32 * u, hc + 18 * u]], 3.4 * u, "#4f0c14");

  // Deep bruised sunken eye sockets
  const exL = fx - 18.5 * u, exR = fx + 18.5 * u, ey = hc - 2 * u;
  p.ell(exL, ey, 15.8 * u, 13.5 * u, "rgba(24, 12, 20, 0.72)", 0);
  p.ell(exR, ey - 1.5 * u, 14.5 * u, 12.5 * u, "rgba(24, 12, 20, 0.72)", 0);

  // Bloodshot dark-crimson sclera + piercing glowing amber-white pinprick horror pupils!
  p.ell(exL, ey, 12.0 * u, 10.0 * u, "#320d14", ow * 0.58);
  p.ell(exR, ey - 1.5 * u, 10.6 * u, 9.0 * u, "#320d14", ow * 0.58);
  p.dot(exL + 1.5 * u, ey, 4.8 * u, "#ffd24c");
  p.dot(exL + 1.5 * u, ey, 2.2 * u, "#ffffff");
  p.dot(exR + 1.0 * u, ey - 1.5 * u, 4.2 * u, "#ffd24c");
  p.dot(exR + 1.0 * u, ey - 1.5 * u, 2.0 * u, "#ffffff");

  // Contorted snarling brows
  p.stroke([[exL - 13 * u, ey - 14 * u], [exL + 11 * u, ey - 6 * u]], 4.6 * u, "#180f12");
  p.stroke([[exR - 11 * u, ey - 6 * u], [exR + 13 * u, ey - 15 * u]], 4.6 * u, "#180f12");

  // Snapping gaping horror jaw with jagged stained teeth & dripping dark crimson blood!
  const mw = 23 * u, mh = (10 + 14 * jawAnim) * u, my = hc + 26 * u;
  p.ell(fx + 1 * u, my + mh * 0.72, mw * 0.92, mh * 0.62, "rgba(108, 12, 20, 0.65)", 0);
  // Blood drips down chin
  p.stroke([[fx - 6 * u, my + mh * 0.8], [fx - 7 * u, my + mh + 9 * u]], 3.2 * u, "#6e0b14");
  p.stroke([[fx + 8 * u, my + mh * 0.7], [fx + 9 * u, my + mh + 6 * u]], 2.6 * u, "#6e0b14");

  const mPoly = ellPts(fx, my, mw, mh, 0, 360, 0, 24);
  p.poly(mPoly, "#1f060a", ow * 0.66);
  p.clip(mPoly, () => {
    for (let k = -3; k <= 3; k++) {
      const tx = fx + k * 5.6 * u;
      p.poly([[tx - 2.6 * u, my - mh], [tx + 2.6 * u, my - mh], [tx, my - mh + 8.5 * u]], "#e3dac6", 0);
      p.poly([[tx - 2.4 * u, my + mh], [tx + 2.4 * u, my + mh], [tx, my + mh - 8.0 * u]], "#d1c5b0", 0);
    }
  });
}

/**
 * Custom High-Readability Rick-Clips Situation-Accurate Human Face Renderer!
 * Eliminates sleepy half-closed eyelids during tense/horror beats; every emotion reads unmistakably!
 */
function drawSituationHumanFace(p, roleKey, R, cx, hc, H, u, ow, expr, facing, blink, speakOpen) {
  const fx = cx + facing * 15 * u;
  const ey = hc - 1 * u;
  const exL = fx - 18.5 * u;
  const exR = fx + 18.5 * u;

  // Special Case: Woman's Spine-Chilling Uncanny Twist ("Her expression changes: 'Please, open the door'")
  if (expr === "woman_uncanny") {
    p.ell(fx, ey - 8 * u, 40 * u, 20 * u, "rgba(32, 26, 42, 0.24)", 0);
    // Creeping dark veins on cheeks
    p.stroke([[exL - 12 * u, ey + 10 * u], [exL - 4 * u, ey + 22 * u]], 1.8 * u, "rgba(72, 24, 44, 0.52)");
    p.stroke([[exR + 12 * u, ey + 8 * u], [exR + 5 * u, ey + 21 * u]], 1.8 * u, "rgba(72, 24, 44, 0.52)");
    // Unblinking asymmetric bloodshot pale eyes with pinprick black-amber dots!
    p.ell(exL, ey, 12.2 * u, 11.4 * u, "#f0dcd8", ow * 0.62);
    p.ell(exR, ey - 1.2 * u, 10.6 * u, 9.8 * u, "#f0dcd8", ow * 0.62);
    p.dot(exL + facing * 2 * u, ey, 3.6 * u, "#8f241e");
    p.dot(exL + facing * 2 * u, ey, 1.8 * u, "#12080a");
    p.dot(exR + facing * 2 * u, ey - 1.2 * u, 3.2 * u, "#8f241e");
    p.dot(exR + facing * 2 * u, ey - 1.2 * u, 1.6 * u, "#12080a");
    // Eerie flat/crooked brows
    p.stroke([[exL - 12 * u, ey - 14 * u], [exL + 11 * u, ey - 12 * u]], 3.8 * u, "#241726");
    p.stroke([[exR - 11 * u, ey - 13 * u], [exR + 12 * u, ey - 16 * u]], 3.8 * u, "#241726");
    // Uncanny crooked mouth (speaking "Please, open the door" with zero human warmth)
    const my = hc + 25 * u;
    if (speakOpen > 0.05) {
      p.ell(fx, my, (8 + 5 * speakOpen) * u, (4 + 7 * speakOpen) * u, "#280e14", ow * 0.58);
    } else {
      p.stroke([[fx - 13 * u, my + 2 * u], [fx, my + 4 * u], [fx + 14 * u, my - 4 * u]], 3.6 * u, "#241726");
    }
    return;
  }

  // Optional stubble on Older Survivor Man
  if (R.stubble) {
    p.ell(fx, hc + 24 * u, 32 * u, 18 * u, "rgba(68, 66, 62, 0.16)", 0);
  }

  // Map legacy expression names cleanly to V3 situation states
  const mode = ({
    neutral: "calm_work",
    alert: "startled_shock",
    panic: "extreme_panic",
    tense: "dread_reading",
    plead: "plead_terror",
    exhausted: "exhausted_hush",
     road_trance: "road_trance",
  })[expr] || expr;

  // Forehead dread shadow on intense terror states
  if (mode === "extreme_panic" || mode === "frozen_terror" || mode === "pale_horror") {
    p.ell(fx, hc - 18 * u, 42 * u, 16 * u, "rgba(30, 38, 56, 0.18)", 0);
  }

  // Dark under-eye exhaustion circles for underground survivors or frozen terror
  if (mode === "exhausted_hush" || mode === "pale_horror" || mode === "frozen_terror" || mode === "extreme_panic") {
    p.arc(exL, ey + 4 * u, 10 * u, 8 * u, 25, 155, 2.2 * u, "rgba(62, 46, 58, 0.42)");
    p.arc(exR, ey + 4 * u, 10 * u, 8 * u, 25, 155, 2.2 * u, "rgba(62, 46, 58, 0.42)");
  }

  // Eye geometry per emotional situation (NEVER sleepy during shock/panic!)
  const canBlink = !(mode === "extreme_panic" || mode === "frozen_terror" || mode === "startled_shock" || mode === "pale_horror" || mode === "road_trance");
  const isBlinking = canBlink && blink > 0.65;

  let eyeRx = 10.2 * u, eyeRy = 10.8 * u, pupR = 4.6 * u, lookX = facing * 3.2 * u, lookY = 0;
  if (mode === "extreme_panic" || mode === "frozen_terror" || mode === "pale_horror") {
    eyeRx = 12.6 * u; eyeRy = 13.8 * u; pupR = 3.1 * u; // Wide whites + tiny contracted panic pupils!
  } else if (mode === "startled_shock" || mode === "boy_hope") {
    eyeRx = 11.8 * u; eyeRy = 12.6 * u; pupR = 3.8 * u;
  } else if (mode === "dread_reading") {
    eyeRx = 10.6 * u; eyeRy = 10.4 * u; pupR = 4.2 * u; lookY = 2.8 * u; // Looking down at phone!
  } else if (mode === "straining_effort") {
    eyeRx = 10.8 * u; eyeRy = 8.8 * u; pupR = 4.2 * u; // Intense focused squint!
  } else if (mode === "plead_terror" || mode === "hesitant_conflict") {
    eyeRx = 11.6 * u; eyeRy = 12.2 * u; pupR = 4.8 * u;
  } else if (mode === "exhausted_hush") {
    eyeRx = 10.2 * u; eyeRy = 8.6 * u; pupR = 4.4 * u;
  } else if (mode === "road_trance") {
    eyeRx = 11.4 * u; eyeRy = 11.8 * u; pupR = 2.6 * u; lookY = -3.2 * u; // Staring blankly upward at nothing!
  }

  if (isBlinking) {
    p.stroke([[exL - 10 * u, ey], [exL + 10 * u, ey]], 3.8 * u, "#241726");
    p.stroke([[exR - 10 * u, ey], [exR + 10 * u, ey]], 3.8 * u, "#241726");
  } else {
    p.ell(exL, ey, eyeRx, eyeRy, "#ffffff", ow * 0.62);
    p.ell(exR, ey, eyeRx, eyeRy, "#ffffff", ow * 0.62);
    p.dot(exL + lookX, ey + lookY, pupR, "#18141c");
    p.dot(exR + lookX, ey + lookY, pupR, "#18141c");
    // Crisp eye catchlight for life & emotion!
    if (mode !== "road_trance") {
      p.dot(exL + lookX - 1.6 * u, ey + lookY - 1.8 * u, 1.5 * u, "#ffffff");
      p.dot(exR + lookX - 1.6 * u, ey + lookY - 1.8 * u, 1.5 * u, "#ffffff");
    }
    // Upper weary lid line ONLY for exhausted_hush
    if (mode === "exhausted_hush") {
      p.stroke([[exL - eyeRx, ey - eyeRy * 0.45], [exL + eyeRx, ey - eyeRy * 0.35]], 3.2 * u, "#241726");
      p.stroke([[exR - eyeRx, ey - eyeRy * 0.35], [exR + eyeRx, ey - eyeRy * 0.45]], 3.2 * u, "#241726");
    }
  }

  // Glistening tear droplets on pleading terror faces
  if (mode === "plead_terror") {
    p.dot(exL - 5 * u, ey + eyeRy + 2.5 * u, 3.3 * u, "#8fd8ff");
    p.dot(exR + 5 * u, ey + eyeRy + 2.5 * u, 3.3 * u, "#8fd8ff");
  }

  // Expressive Eyebrows per situation
  const bw = 4.2 * u;
  if (mode === "extreme_panic" || mode === "plead_terror" || mode === "hesitant_conflict" || mode === "pale_horror") {
    // Steep worried/terrified upturned inner brows (/  \)
    p.stroke([[exL - 12 * u, ey - eyeRy - 3 * u], [exL + 11 * u, ey - eyeRy - 11 * u]], bw, "#241726");
    p.stroke([[exR - 11 * u, ey - eyeRy - 11 * u], [exR + 12 * u, ey - eyeRy - 3 * u]], bw, "#241726");
  } else if (mode === "dread_reading" || mode === "straining_effort") {
    // Tense angled furrowed brows (\  /)
    p.stroke([[exL - 12 * u, ey - eyeRy - 9 * u], [exL + 11 * u, ey - eyeRy - 3 * u]], bw, "#241726");
    p.stroke([[exR - 11 * u, ey - eyeRy - 3 * u], [exR + 12 * u, ey - eyeRy - 9 * u]], bw, "#241726");
  } else if (mode === "startled_shock" || mode === "frozen_terror" || mode === "boy_hope") {
    // High raised shock arches
    p.stroke([[exL - 12 * u, ey - eyeRy - 8 * u], [exL, ey - eyeRy - 13 * u], [exL + 11 * u, ey - eyeRy - 8 * u]], bw, "#241726");
    p.stroke([[exR - 11 * u, ey - eyeRy - 8 * u], [exR, ey - eyeRy - 13 * u], [exR + 12 * u, ey - eyeRy - 8 * u]], bw, "#241726");
  } else {
    // Calm / neutral / trance brows
    p.stroke([[exL - 11 * u, ey - eyeRy - 6 * u], [exL + 10 * u, ey - eyeRy - 6 * u]], 3.8 * u, "#241726");
    p.stroke([[exR - 10 * u, ey - eyeRy - 6 * u], [exR + 11 * u, ey - eyeRy - 6 * u]], 3.8 * u, "#241726");
  }

  // Subtle nose bridge line
  p.stroke([[fx + facing * 3 * u, ey + 3 * u], [fx + facing * 5 * u, ey + 13 * u], [fx + facing * 1 * u, ey + 15 * u]], 2.6 * u, "rgba(36,23,38,0.65)");

  // Mouth per situation + active lip-sync override
  const my = hc + 25.5 * u;
  if (speakOpen > 0.05) {
    const mw = (7.0 + 6.5 * speakOpen) * u;
    const mh = (3.5 + 8.5 * speakOpen) * u;
    p.ell(fx, my, mw, mh, "#38151e", ow * 0.56);
    if (speakOpen > 0.22) {
      p.poly(rrect(fx - mw * 0.65, my - mh * 0.82, fx + mw * 0.65, my - mh * 0.30, 1.5 * u), "#f7f3ea", 0);
    }
  } else if (mode === "extreme_panic") {
    // Wide open trembling horror mouth with clenched upper & lower teeth!
    const mw = 14.5 * u, mh = 9.2 * u;
    const mp = ellPts(fx, my, mw, mh, 0, 360, 0, 20);
    p.poly(mp, "#331119", ow * 0.58);
    p.clip(mp, () => {
      p.poly(rrect(fx - mw, my - mh, fx + mw, my - mh + 4.2 * u, 1 * u), "#f7f3ea", 0);
      p.poly(rrect(fx - mw, my + mh - 3.6 * u, fx + mw, my + mh, 1 * u), "#ece5d8", 0);
    });
  } else if (mode === "startled_shock" || mode === "pale_horror") {
    p.ell(fx, my, 8.8 * u, 9.6 * u, "#331119", ow * 0.58);
  } else if (mode === "straining_effort") {
    // Gritted clenched teeth grimace
    const mp = rrect(fx - 13 * u, my - 5 * u, fx + 13 * u, my + 5 * u, 4 * u);
    p.poly(mp, "#f7f3ea", ow * 0.56);
    p.stroke([[fx - 11 * u, my], [fx + 11 * u, my]], 2.2 * u, "#241726");
  } else if (mode === "frozen_terror" || mode === "dread_reading" || mode === "plead_terror" || mode === "hesitant_conflict") {
    // Quivering downturn / tense horror frown
    p.stroke([[fx - 11 * u, my + 3.5 * u], [fx, my - 1.5 * u], [fx + 11 * u, my + 3.5 * u]], 3.6 * u, "#241726");
  } else if (mode === "boy_hope") {
    p.arc(fx, my - 2 * u, 9 * u, 5 * u, 20, 160, 3.4 * u, "#241726");
  } else {
    // Calm neutral slight line
    p.stroke([[fx - 9 * u, my + 1 * u], [fx + 9 * u, my + 1 * u]], 3.4 * u, "#241726");
  }
}

/** Ground-Clamped Fallen Pose */
function drawFallenChar(p, R, opts, u, ow, thick, light) {
  const skin = R.skin || RICK_HEAD;
  const sole = 964;
  const cx = 300;
  p.band([[cx - 175, sole - 22], [cx - 95, sole - 34], [cx - 20, sole - 26]], R.pants || "#2f3640", 26, ow * 0.72, "round");
  p.band([[cx - 155, sole - 8], [cx - 78, sole - 16], [cx - 10, sole - 18]], R.pants || "#2f3640", 26, ow * 0.72, "round");
  p.ell(cx - 185, sole - 18, 18, 11, "#2a2226", ow * 0.68);
  p.ell(cx - 166, sole - 5, 18, 11, "#2a2226", ow * 0.68);
  const tPoly = rrect(cx - 32, sole - 76, cx + 112, sole - 12, 28);
  p.gradFill(tPoly, R.jacket, R.jacket2, light, 0.28);
  p.inkRing(tPoly, ow * 0.95, thick);
  p.band([[cx + 88, sole - 42], [cx + 152, sole - 24], [cx + 205, sole - 14]], R.jacket, 22, ow * 0.68, "round");
  p.ell(cx + 214, sole - 13, 13, 9, skin, ow * 0.62);
  const H = headBlob(R.seed, 98, 0.25);
  const hx = cx + 148, hy = sole - 68;
  const hp = blobPts(hx, hy, H);
  p.shadedFill(hp, skin, "#d8d0c4", light, H.a, 0.42);
  p.inkRing(hp, ow * 0.95, thick);
  drawSituationHumanFace(p, "carMan", R, hx, hy + 4, H, (2 * H.a) / 100, ow * 0.9, "extreme_panic", 0.25, 0, 0);
  drawModernHairFront(p, R, H, hx, hy, (2 * H.a) / 100, ow * 0.9, thick, light);
}

export function rickChar(p, roleKey = "you", opts = {}) {
  const R = ROLES[roleKey] || ROLES.you;
  const {
    expr = R.infected ? "infected" : "calm_work",
    blink = 0,
    facing = 0,
    L = "hang",
    R: Rarm = "hang",
    tilt = 0,
    headTilt = 0,
    bob = 0,
    step = 0,            // 0..1 continuous velocity-locked gait phase
    isRunning = false,   // true -> full athletic sprint stride, 82° knee recovery, 20° forward lean, pumping arms!
    reverseWalk = false, // true -> cautious backward step while facing threat (Police Officer / YOU stepping back)
    crouchSit = false,   // true -> seated/crouched bent knees at y=0
    hasBackpack = false, // true -> survival backpack straps on YOU (Act IV & V)
    fallU = 0,
    breath = 0,
    sweat = false,
    speakOpen = 0,
    phoneBuzz = 0,
    shakeAmt = 0,
    jawAnim = R.infected ? 0.85 : 0,
    light = rad(-125),
  } = opts;

  const seed = opts.seed ?? R.seed;
  const H = headBlob(seed, 120, facing);
  const W = 2 * H.a, HH = 2 * H.b, u = W / 100;
  const thick = thickAngle(light);
  const ow = 4.5 * u;

  if (fallU >= 0.55) {
    drawFallenChar(p, R, opts, u, ow, thick, light);
    return;
  }

  // Dynamic skin pallor when Older Man goes pale or Woman turns uncanny!
  const skin = (expr === "pale_horror" || expr === "woman_uncanny")
    ? PALE_HEAD
    : (R.skin || RICK_HEAD);
  const handCol = R.labGloves ? "#23282b" : skin;

  const sole = 968;
  const moveDir = facing < -0.05 ? -1 : 1;
  const gaitSign = reverseWalk ? -1 : 1;

  // Athletic vertical sprint bounce (peaks twice per full stride during flight phase!)
  const hasGait = step > 0.0001;
  const runBounce = (hasGait && isRunning)
    ? Math.abs(Math.sin(Math.PI * 2 * step)) * 0.105
    : (hasGait ? Math.abs(Math.sin(Math.PI * 2 * step)) * 0.038 : 0);

  const sitDrop  = crouchSit ? 0.42 : 0;
  const tripDrop = fallU > 0 ? fallU * 0.65 : 0;
  const legsL = 1.24 - sitDrop - tripDrop;
  const torsoL = 1.03;
  const breathLift = breath * 0.022;

  const torsoBot = sole - legsL * HH - (bob + runBounce) * HH;
  const hipY = torsoBot - 0.06 * HH;
  const chin = torsoBot - (torsoL + breathLift) * HH;
  const hc = chin - H.b * 0.90;

  // Pelvis shifts slightly forward during sprint so center-of-gravity leads the push-off foot!
  const cx = 300 + (isRunning ? moveDir * 14 * u : 0);
  const pantsCol = R.pants || "#2b3340";
  const pantsFar = mul(pantsCol, [0.78, 0.78, 0.84]);

  // Natural forward torso lean during sprint (19° human sprint, 25° zombie lunge!)
  const autoLean = (fallU > 0 ? fallU * 48 : 0)
    + (isRunning ? (R.infected ? 25 : 19) * moveDir : 0)
    + (R.infected && !isRunning ? 11 * moveDir : 0)
    + (reverseWalk ? -6 * moveDir : 0)
    + tilt;

  p.rot = null;

  // Subtle cartoon sprint speed lines behind fast human sprinters!
  if (isRunning && !R.infected && Math.abs(facing) > 0.25) {
    const backX = cx - moveDir * 115 * u;
    p.stroke([[backX, hipY - 45 * u], [backX - moveDir * 52 * u, hipY - 45 * u]], 3.0 * u, "rgba(255,255,255,0.34)");
    p.stroke([[backX + moveDir * 12 * u, hipY + 25 * u], [backX - moveDir * 44 * u, hipY + 25 * u]], 2.6 * u, "rgba(255,255,255,0.28)");
  }

  // Long hair back layer (for Woman)
  if (R.longHair) {
    const hCol = R.hair || "#2b1b20";
    const backHair = rrect(cx - H.a * 1.04, hc - H.b * 0.16, cx + H.a * 1.04, chin + 0.30 * HH, 24 * u);
    p.shadedFill(backHair, mul(hCol, [0.82, 0.80, 0.85]), mul(hCol, [0.58, 0.56, 0.62]), light, H.a);
    p.inkRing(backHair, ow * 0.82, thick);
  }

  // ---- TRUE 2-BONE ANATOMICAL LEG SOLVER (Far leg draws BEHIND torso; Near leg draws IN FRONT!) ----
  const isProfile = Math.abs(facing) > 0.22;
  const computeLeg = (side) => {
    const isNear = isProfile ? (side * moveDir > 0) : (side > 0);
    const hipX = cx + (isProfile ? side * 6 * u : side * 15 * u);
    const col = isNear ? pantsCol : pantsFar;

    if (crouchSit) {
      const kneeX = hipX + (isProfile ? moveDir * 36 * u : side * 24 * u);
      const kneeY = hipY + (sole - hipY) * 0.48;
      const fx = hipX + (isProfile ? moveDir * 24 * u : side * 18 * u);
      const fy = sole - 7 * u;
      return { hipX, kneeX, kneeY, fx, fy, shoeAng: 0, col, isNear };
    }

    if (hasGait) {
      // Phase u_ang in [0..2π); side > 0 is 180° out of phase with side < 0
      const ph = ((step * gaitSign + (side > 0 ? 0.5 : 0.0)) % 1 + 1) % 1;
      const ang = ph * Math.PI * 2;
      const s = Math.sin(ang);
      const c = Math.cos(ang);

      const L1 = 0.53 * (sole - hipY); // Thigh bone length
      const L2 = 0.52 * (sole - hipY); // Shin bone length

      if (isRunning) {
        // FULL ATHLETIC SPRINT BIOMECHANICS:
        // Thigh swings wide from -37° (rear push-off) to +51° (high forward knee drive)!
        const thighAng = (0.12 + 0.77 * s) * moveDir;
        // Knee folds anatomically BACKWARD (-moveDir) up to 84° during forward recovery (c > 0),
        // and straightens cleanly on rear push-off & front foot strike!
        const recovery = Math.max(0, Math.cos(ang - 0.32));
        const kneeFold = (0.12 + 1.32 * Math.pow(recovery, 1.45)) * moveDir;
        const shinAng  = thighAng - kneeFold;

        const kneeX = hipX + Math.sin(thighAng) * L1;
        const kneeY = hipY + Math.cos(thighAng) * L1;
        let fx = kneeX + Math.sin(shinAng) * L2;
        let fy = Math.min(sole - 6 * u, kneeY + Math.cos(shinAng) * L2);
        // Natural plantarflexion on rear push-off & dorsiflexion on front strike!
        const shoeAng = (-0.34 * s + 0.25 * recovery) * moveDir;
        return { hipX, kneeX, kneeY, fx, fy, shoeAng, col, isNear };
      } else {
        // NATURAL GROUNDED WALK / BACKING-AWAY BIOMECHANICS:
        const thighAng = (0.04 + 0.44 * s) * moveDir;
        const recovery = Math.max(0, Math.cos(ang - 0.25));
        const kneeFold = (0.06 + 0.68 * Math.pow(recovery, 1.5)) * moveDir;
        const shinAng  = thighAng - kneeFold;

        const kneeX = hipX + Math.sin(thighAng) * L1 * 0.96;
        const kneeY = hipY + Math.cos(thighAng) * L1 * 0.96;
        let fx = kneeX + Math.sin(shinAng) * L2 * 0.96;
        let fy = Math.min(sole - 6 * u, kneeY + Math.cos(shinAng) * L2 * 0.96);
        const shoeAng = (-0.18 * s) * moveDir;
        return { hipX, kneeX, kneeY, fx, fy, shoeAng, col, isNear };
      }
    }

    // Standing idle / zombie wide stance
    const fx = hipX + side * (R.infected ? 10 : 4) * u;
    const fy = sole - 6 * u;
    const kneeX = (hipX + fx) * 0.5 + (R.infected ? moveDir * 9 * u : 0);
    const kneeY = (hipY + fy) * 0.5;
    return { hipX, kneeX, kneeY, fx, fy, shoeAng: 0, col, isNear };
  };

  const drawOneLeg = (lg) => {
    p.band([[lg.hipX, hipY], [lg.kneeX, lg.kneeY], [lg.fx, lg.fy]], lg.col, 14.2 * u, ow * 0.60, "round");
    const shX = lg.fx + moveDir * 7.5 * u;
    const shY = lg.fy + 2 * u;
    p.rot = lg.shoeAng ? [lg.shoeAng, lg.fx, lg.fy] : null;
    p.ell(shX, shY, 15.2 * u, 7.6 * u, "#231c20", ow * 0.72);
    // Crisp sneaker/boot sole accent so foot movement reads with razor clarity!
    p.stroke([[shX - 11 * u, shY + 4.5 * u], [shX + 11 * u, shY + 4.5 * u]], 2.4 * u, "#d8d3c8");
    p.rot = null;
  };

  const legs = [computeLeg(-1), computeLeg(1)];
  // Draw FAR leg behind torso first!
  for (const lg of legs) if (!lg.isNear) drawOneLeg(lg);

  // ---- Breathing Pill/Bean Torso + Survival Backpack ----
  const jx = shakeAmt ? Math.sin(seed * 13 + shakeAmt * 38) * 3.5 * u : 0;
  p.rot = autoLean ? [rad(autoLean), cx, hipY] : null;

  const breathW = 1.0 + breath * 0.036;
  const T = {
    a: 0.40 * W * breathW,
    b: 0.53 * (torsoBot - (chin - 0.15 * HH)),
    nTop: 2.35,
    nBot: 2.35,
    egg: 0.08,
    asym: 0.03 * facing,
    rot: 0,
    noise: 0.005,
    seed: seed + 7,
  };
  const tcx = cx + 3.5 * u * facing + jx;
  const tcy = torsoBot - T.b + 0.05 * HH;
  const tp = blobPts(tcx, tcy, T);

  // Survival Backpack behind back when `hasBackpack` is active (Act IV & V)
  if (hasBackpack) {
    const bpSide = facing >= 0 ? -1 : 1;
    const bpPoly = rrect(tcx + bpSide * T.a * 0.45 - 18 * u, tcy - T.b * 0.65, tcx + bpSide * T.a * 0.45 + 18 * u, tcy + T.b * 0.58, 12 * u);
    p.poly(bpPoly, "#2d3530", ow * 0.72);
  }

  const shY = chin + (0.16 - breath * 0.025) * HH;
  const shoulder = (side) => [
    tcx + (isProfile ? side * 0.32 * T.a : side * 0.80 * T.a),
    shY
  ];

  // ---- Articulated Sleeved Arms & Connected Hands ----
  const makeArm = (side, pose) => {
    const s = shoulder(side);
    const X = (k) => tcx + side * (T.a * 0.88 + k * u);
    const isNearArm = isProfile ? (side * moveDir > 0) : (side > 0);

    // Full biomechanical opposite-phase arm pumping when walking or sprinting!
    if ((pose === "hang" || pose === "run") && hasGait) {
      const ph = ((step * gaitSign + (side > 0 ? 0.0 : 0.5)) % 1 + 1) % 1;
      const sw = Math.sin(ph * Math.PI * 2); // opposes same-side leg!
      if (isRunning) {
        // 90°-bent athletic sprint arms pumping vigorously from hip to chin!
        const shAng = (0.15 + 0.92 * sw) * moveDir;
        const L_up = 0.34 * HH, L_fore = 0.32 * HH;
        const elbX = s[0] + Math.sin(shAng) * L_up;
        const elbY = s[1] + Math.cos(shAng) * L_up;
        // Forearm bent ~85° FORWARD (+moveDir) relative to upper arm!
        const foreAng = shAng + 1.38 * moveDir;
        const hndX = elbX + Math.sin(foreAng) * L_fore;
        const hndY = elbY + Math.cos(foreAng) * L_fore;
        return { pts: [s, [elbX, elbY], [hndX, hndY]], front: isNearArm, fist: true, farDim: !isNearArm };
      } else {
        const elbX = s[0] + sw * 16 * u * moveDir + side * 4 * u;
        const elbY = s[1] + 0.35 * HH;
        const hndX = elbX + (sw * 22 + 5) * u * moveDir;
        const hndY = elbY + 0.30 * HH - Math.abs(sw) * 4 * u;
        return { pts: [s, [elbX, elbY], [hndX, hndY]], front: isNearArm, fist: true, farDim: !isNearArm };
      }
    }

    switch (pose) {
      case "phoneBuzz": {
        const vb = Math.sin(phoneBuzz * 52) * 3.5 * u;
        return { pts: [s, [X(18), s[1] + 0.24 * HH], [tcx + side * 0.44 * T.a + vb, s[1] + 0.06 * HH]], front: true, overHead: true, prop: "phoneBuzz" };
      }
      case "flashlight":
        return { pts: [s, [X(18), s[1] + 0.16 * HH], [tcx + moveDir * 48 * u, s[1] + 0.02 * HH]], front: true, prop: "flashlight" };
      case "pullShutter":
        // Reaching high overhead to yank down the heavy metal shutter handle!
        return { pts: [s, [X(16), s[1] - 0.22 * HH], [tcx + side * 18 * u, s[1] - 0.56 * HH]], front: true, overHead: true, fist: true };
      case "lockDoor":
        return { pts: [s, [X(18), s[1] + 0.12 * HH], [tcx + moveDir * 44 * u, s[1] + 0.04 * HH]], front: true, fist: true };
      case "wave":
        // Warm goodbye wave — arm up beside the head, hand swinging (mom sending the boy off)
        return { pts: [s, [X(20), s[1] + 0.02 * HH], [X(30), s[1] - 0.42 * HH]], front: true, overHead: true, palmSpread: true };
      case "plead":
        return { pts: [s, [X(22), s[1] + 0.04 * HH], [X(26), s[1] - 0.34 * HH]], front: true, overHead: true, palmSpread: true };
      case "slam":
        return { pts: [s, [X(22), s[1] - 0.04 * HH], [X(28), s[1] - 0.38 * HH]], front: true, overHead: true, palmSpread: true };
      case "shush": {
        // Older Man raising 1 index finger directly to his lips ("Don't make a sound")!
        const fxLip = cx + facing * 15 * u;
        return { pts: [s, [X(16), s[1] + 0.18 * HH], [fxLip + 4 * u, hc + 34 * u]], front: true, overHead: true, shushFinger: true };
      }
      case "grabSleeve":
        // Young Boy reaching across in panic to grab YOU's jacket sleeve!
        return { pts: [s, [s[0] + moveDir * 24 * u, s[1] + 0.08 * HH], [s[0] + moveDir * 56 * u, s[1] - 0.02 * HH]], front: true, overHead: true, fist: true };
      case "shake": {
        const sh = Math.sin(shakeAmt * 48 + side * 2) * 4 * u;
        return { pts: [s, [X(14), s[1] + 0.28 * HH], [tcx + side * 0.34 * T.a + sh, s[1] + 0.12 * HH]], front: true, fist: true };
      }
      case "labWork":
        // Scientist leaning into the bench, hands forward at working height
        return { pts: [s, [X(22), s[1] - 0.02 * HH], [X(38), s[1] - 0.26 * HH]], front: isNearArm, holdVial: isNearArm };
      case "zombieReach": {
        const tw = Math.sin(seed * 5 + step * Math.PI * 4 + side) * 7 * u;
        const reachF = isRunning ? 58 : 46;
        return {
          pts: [
            s,
            [s[0] + moveDir * 26 * u + side * 6 * u, s[1] + 0.02 * HH],
            [s[0] + moveDir * reachF * u + side * 8 * u, s[1] - 0.12 * HH + tw]
          ],
          front: isNearArm,
          claw: true,
          farDim: !isNearArm,
        };
      }
      default:
        return { pts: [s, [X(8), s[1] + 0.38 * HH], [X(6), s[1] + 0.72 * HH]], front: false, fist: true };
    }
  };

  const arms = [makeArm(-1, L), makeArm(1, Rarm)];

  const drawOneArm = (a) => {
    const slvCol = a.farDim ? R.jacket2 : R.jacket;
    p.band(a.pts, slvCol, 13.0 * u, ow * 0.58, "round");
    const [hx, hy] = a.pts[2];

    if (a.palmSpread) {
      p.ell(hx, hy, 8.8 * u, 9.8 * u, handCol, ow * 0.62);
      for (let f = -2; f <= 2; f++) {
        const ang = rad(f * 18 - 90);
        p.band([[hx + Math.cos(ang) * 5 * u, hy + Math.sin(ang) * 5 * u],
                [hx + Math.cos(ang) * 13 * u, hy + Math.sin(ang) * 14 * u]], handCol, 3.8 * u, ow * 0.35, "round");
      }
    } else if (a.shushFinger) {
      p.ell(hx, hy, 7.2 * u, 6.8 * u, handCol, ow * 0.58);
      p.band([[hx, hy - 3 * u], [hx, hy - 19 * u]], handCol, 4.2 * u, ow * 0.42, "round");
    } else if (a.claw) {
      p.ell(hx, hy, 7.8 * u, 7.0 * u, handCol, ow * 0.58);
      for (const f of [-1.5, -0.5, 0.5, 1.5]) {
        p.stroke([[hx + f * 3.2 * u, hy], [hx + (f * 4.5 + moveDir * 8) * u, hy + 5 * u], [hx + (f * 5 + moveDir * 12) * u, hy + 12 * u]], 2.8 * u, "#240d12");
      }
    } else {
      p.ell(hx, hy, 7.4 * u, 7.0 * u, handCol, ow * 0.58);
    }
    if (a.holdVial) {
      p.ell(hx, hy - 13 * u, 5.4 * u, 9.5 * u, "#cdeedd", ow * 0.5);
      p.ell(hx, hy - 19 * u, 3.4 * u, 4.4 * u, "#8effc0", 0);
      p.stroke([[hx - 5.4 * u, hy - 8.5 * u], [hx + 5.4 * u, hy - 8.5 * u]], 2.2 * u, "#39413c", "round");
    }

    if (a.prop === "phoneBuzz") {
      p.poly(rrect(hx - 11 * u, hy - 26 * u, hx + 11 * u, hy + 6 * u, 4 * u), "#1a1d24", ow * 0.68);
      p.poly(rrect(hx - 8.5 * u, hy - 22 * u, hx + 8.5 * u, hy + 2 * u, 2 * u), "#ff3328", 0);
      p.poly(rrect(hx - 6.5 * u, hy - 18 * u, hx + 6.5 * u, hy - 12 * u, 1 * u), "#ffffff", 0);
      p.ell(hx - 9.5 * u, hy - 5 * u, 4.2 * u, 3.2 * u, handCol, ow * 0.45);
      if (phoneBuzz > 0) {
        const pulse = (phoneBuzz * 6) % 1;
        for (const sgn of [-1, 1]) {
          const rx = hx + sgn * (15 + pulse * 7) * u;
          p.stroke([[rx, hy - 20 * u], [rx + sgn * 3 * u, hy - 10 * u], [rx, hy]], 2.6 * u, "#ff6247");
          const rx2 = hx + sgn * (21 + pulse * 9) * u;
          p.stroke([[rx2, hy - 17 * u], [rx2 + sgn * 3 * u, hy - 10 * u], [rx2, hy - 3 * u]], 2.0 * u, "#ffcf48");
        }
      }
    } else if (a.prop === "flashlight") {
      p.poly(rrect(hx - 6 * u, hy - 6.5 * u, hx + 20 * u, hy + 6.5 * u, 3 * u), "#323840", ow * 0.62);
      p.poly(rrect(hx + 16 * u, hy - 8.5 * u, hx + 24 * u, hy + 8.5 * u, 2 * u), "#ffd452", ow * 0.52);
    }
  };

  // Draw FAR arm behind torso!
  for (let i = 0; i < 2; i++) if (!arms[i].front) drawOneArm(arms[i]);

  // Torso fill + clothing details
  p.gradFill(tp, R.jacket, R.jacket2, light, 0.26);
  p.clip(tp, () => {
    if (R.badge) {
      // Police Officer uniform details: center placket + gold shield badge + utility belt!
      p.stroke([[tcx, tcy - T.b * 0.85], [tcx, tcy + T.b * 0.85]], 2.8 * u, R.jacket2);
      p.poly([
        [tcx + 14 * u, tcy - T.b * 0.42],
        [tcx + 23 * u, tcy - T.b * 0.36],
        [tcx + 20 * u, tcy - T.b * 0.16],
        [tcx + 14 * u, tcy - T.b * 0.10],
        [tcx + 8 * u,  tcy - T.b * 0.16],
        [tcx + 5 * u,  tcy - T.b * 0.36],
      ], R.badge, ow * 0.38);
      p.poly(rrect(tcx - T.a, tcy + T.b * 0.62, tcx + T.a, tcy + T.b * 0.86, 2 * u), R.belt, 0);
    } else if (R.hoodie) {
      p.stroke([[tcx, tcy - T.b * 0.82], [tcx, tcy + T.b * 0.88]], 2.8 * u, R.jacket2);
      p.poly(rrect(tcx - T.a * 0.58, tcy + T.b * 0.18, tcx + T.a * 0.58, tcy + T.b * 0.68, 6 * u), R.jacket2, ow * 0.45);
      p.stroke([[tcx - 9 * u, tcy - T.b * 0.72], [tcx - 10 * u, tcy - T.b * 0.28]], 2.4 * u, R.trim);
      p.stroke([[tcx + 9 * u, tcy - T.b * 0.72], [tcx + 10 * u, tcy - T.b * 0.28]], 2.4 * u, R.trim);
    } else if (R.trim) {
      p.poly([[tcx - 15 * u, tcy - T.b * 0.88], [tcx, tcy - T.b * 0.42], [tcx + 15 * u, tcy - T.b * 0.88]], R.trim, ow * 0.5);
    }
    if (hasBackpack) {
      p.stroke([[tcx - T.a * 0.46, tcy - T.b * 0.80], [tcx - T.a * 0.52, tcy + T.b * 0.55]], 5.5 * u, "#232926");
      p.stroke([[tcx + T.a * 0.46, tcy - T.b * 0.80], [tcx + T.a * 0.52, tcy + T.b * 0.55]], 5.5 * u, "#232926");
    }
    if (R.infected) {
      // Heavy crimson blood splatters & ragged tears on horror zombie clothing!
      p.ell(tcx - 6 * u, tcy - T.b * 0.52, 26 * u, 20 * u, "rgba(104, 10, 18, 0.68)", 0);
      p.ell(tcx + 12 * u, tcy + 8 * u, 18 * u, 26 * u, "rgba(86, 12, 18, 0.52)", 0);
      p.stroke([[tcx - 26 * u, tcy + 2 * u], [tcx + 14 * u, tcy + 28 * u]], 4.8 * u, "#170e10");
      p.stroke([[tcx - 14 * u, tcy - 18 * u], [tcx + 20 * u, tcy - 4 * u]], 3.8 * u, "#170e10");
    }
  });
  p.inkRing(tp, ow, thick);

  if (R.hoodie) {
    const hoodCollar = ellPts(tcx, chin + 0.06 * HH, T.a * 0.64, 12 * u, 0, 180, 0, 20);
    p.poly(hoodCollar, R.jacket2, ow * 0.70);
  }

  p.rot = null;
  // Draw NEAR leg in front of hip seam for crisp side-run depth!
  for (const lg of legs) if (lg.isNear) drawOneLeg(lg);

  p.rot = autoLean ? [rad(autoLean), cx, hipY] : null;
  // Draw NEAR arm in front of torso!
  for (let i = 0; i < 2; i++) if (arms[i].front && !arms[i].overHead) drawOneArm(arms[i]);

  // ---- Head ----
  const infTwitch = R.infected ? (4 + Math.sin(step * Math.PI * 3 + seed) * 4) : 0; // V7: neck stays straight, only a faint unsteady sway
  const totHeadRot = rad(autoLean * 0.45 + headTilt + infTwitch);
  p.rot = totHeadRot ? [totHeadRot, cx + jx, chin] : null;
  const hp = blobPts(cx + jx, hc, H);
  const skinShadow = R.infected ? "#72827b" : (skin === PALE_HEAD ? "#bfc8c5" : "#d9d1c4");
  p.shadedFill(hp, skin, skinShadow, light, H.a, 0.42);
  p.inkRing(hp, ow * 1.04, thick);

  if (R.gasMask) {
    drawGasMaskFace(p, cx + jx, hc + 4 * u, H, u, ow, facing, light, expr === 'evilGrin' ? 1 : 0);
  } else if (R.infected) {
    drawHorrorInfectedFace(p, cx + jx, hc + 4 * u, H, u, ow, facing, jawAnim, seed);
  } else {
    drawSituationHumanFace(p, roleKey, R, cx + jx, hc + 4 * u, H, u, ow, expr, facing, blink, speakOpen);
  }

  const showSweat = sweat || expr === "extreme_panic" || expr === "frozen_terror" || expr === "pale_horror";
  if (showSweat && !R.infected) {
    const sx = cx + jx + H.a * 0.66, sy = hc - H.b * 0.04;
    p.poly([[sx, sy - 11 * u], [sx + 6 * u, sy + 3 * u], [sx, sy + 8 * u], [sx - 6 * u, sy + 3 * u]], "#8ad4ff", ow * 0.45);
  }

  if (!R.gasMask) drawModernHairFront(p, R, H, cx + jx, hc, u, ow, thick, light);
  p.rot = null;

  // Draw foreground raised hands/props (phoneBuzz, Woman's palm, Shutter pull, Man's shush finger, Boy's sleeve grab) IN FRONT of head!
  for (let i = 0; i < 2; i++) if (arms[i].overHead) drawOneArm(arms[i]);
}

/** Authentic Rick-Clips Over-the-Shoulder / Running Away Back Card */
export function rickBackPOV(p, roleKey = "you", opts = {}) {
  const R = ROLES[roleKey] || ROLES.you;
  const { headTilt = 0, bob = 0, step = 0, isRunning = false, breath = 0, fullBody = false, hasBackpack = false, light = rad(-125) } = opts;

  if (fullBody) {
    const H = headBlob(R.seed, 120, 0);
    const W = 2 * H.a, HH = 2 * H.b, u = W / 100;
    const ow = 4.5 * u, thick = thickAngle(light);
    const sole = 968, cx = 300;
    const bounce = step > 0 ? Math.abs(Math.sin(Math.PI * 2 * step)) * (isRunning ? 0.095 : 0.035) : 0;
    const torsoBot = sole - 1.24 * HH - (bob + bounce) * HH;
    const chin = torsoBot - (1.03 + breath * 0.02) * HH;
    const hc = chin - H.b * 0.90;
    const hipY = torsoBot - 0.06 * HH;

    for (const side of [-1, 1]) {
      const ph = step > 0 ? Math.sin(Math.PI * 2 * (step + (side > 0 ? 0.5 : 0))) : 0;
      const lift = Math.max(0, ph) * (isRunning ? 68 : 28) * u;
      const hx = cx + side * 16 * u;
      const fy = sole - 6 * u - lift;
      p.band([[hx, hipY], [hx + side * 4 * u, (hipY + fy) * 0.5], [hx, fy]], R.pants || "#2b3340", 14.2 * u, ow * 0.58, "round");
      p.ell(hx, fy + 2 * u, 12 * u, 8.5 * u, "#231c20", ow * 0.70);
      if (lift > 16 * u) {
        // Shoe sole visible when heel kicks up while running away!
        p.ell(hx, fy + 1 * u, 9.5 * u, 12 * u, "#3b3538", ow * 0.55);
      }
    }
    for (const side of [-1, 1]) {
      const ph = step > 0 ? Math.sin(Math.PI * 2 * (step + (side > 0 ? 0 : 0.5))) : 0;
      const sx = cx + side * 0.36 * W, sy = chin + 0.16 * HH;
      const ex = sx + side * 18 * u, ey = sy + (0.32 - ph * 0.12) * HH;
      const hx = ex + side * 4 * u, hy = ey + (isRunning ? -0.12 : 0.28) * HH;
      p.band([[sx, sy], [ex, ey], [hx, hy]], R.jacket, 12.8 * u, ow * 0.58, "round");
      p.ell(hx, hy, 7 * u, 7 * u, R.skin, ow * 0.55);
    }
    const tp = rrect(cx - 0.40 * W, chin + 0.05 * HH, cx + 0.40 * W, torsoBot, 38 * u);
    p.gradFill(tp, R.jacket, R.jacket2, light, 0.25);
    p.inkRing(tp, ow, thick);
    if (hasBackpack) {
      const bp = rrect(cx - 0.27 * W, chin + 0.22 * HH, cx + 0.27 * W, torsoBot - 16 * u, 18 * u);
      p.poly(bp, "#2d3530", ow * 0.75);
    } else if (R.hoodie) {
      p.poly(ellPts(cx, chin + 0.22 * HH, 0.28 * W, 22 * u, 0, 180, 0, 20), R.jacket2, ow * 0.75);
    }
    const hp = blobPts(cx, hc, H);
    p.shadedFill(hp, R.hair || "#3a271d", mul(R.hair || "#3a271d", [0.7, 0.68, 0.74]), light, H.a, 0.35);
    p.inkRing(hp, ow, thick);
    return;
  }

  const H = headBlob(R.seed, 146, 0);
  const W = 2 * H.a, u = W / 100;
  const cx = 300, hc = 545 - (bob + breath * 0.08) * 38;
  const ow = 5.0 * u, thick = thickAngle(light);

  const shPts = rrect(cx - 195 * (1 + breath * 0.02), hc + H.b * 0.78, cx + 195 * (1 + breath * 0.02), 995, 68);
  p.gradFill(shPts, R.jacket, R.jacket2, light, 0.25);
  p.inkRing(shPts, ow, thick);
  const hoodPts = ellPts(cx, hc + H.b * 0.92, 118, 48, 0, 180, 0, 24);
  p.poly(hoodPts, R.jacket2, ow * 0.85);

  p.rot = headTilt ? [rad(headTilt), cx, hc + H.b] : null;
  const hp = blobPts(cx, hc, H);
  p.shadedFill(hp, R.skin, "#d8d1c5", light, H.a, 0.4);
  const hairBack = ellPts(cx, hc - H.b * 0.06, H.a * 1.02, H.b * 0.96, 155, 385, 0, 40);
  hairBack.push([cx + H.a * 0.92, hc + H.b * 0.42], [cx, hc + H.b * 0.52], [cx - H.a * 0.92, hc + H.b * 0.42]);
  const hCol = R.hair || "#3a271d";
  p.shadedFill(hairBack, hCol, mul(hCol, [0.7, 0.68, 0.74]), light, H.a, 0.35);
  p.inkRing(hp, ow * 1.05, thick);
  p.inkRing(hairBack, ow * 0.9, thick);
  p.rot = null;
}

/** Seamless Horror Zombie Arm + Veins + Claws */
export function creepyArmCard(p, opts = {}) {
  const { openClose = 0.5, reach = 0.78, twitch = 0 } = opts;
  const skin = "#aeb9b3", sh = "#83918b", sleeve = "#2c3338";
  const ow = 9.5;
  const yMid = 505 + Math.sin(twitch * 17) * 12;
  const elbowX = 175 + reach * 88;
  const wristX = 335 + reach * 125;
  const wristY = yMid + Math.cos(twitch * 12) * 16;

  p.poly([[0, yMid - 64], [148, yMid - 46], [134, yMid - 8], [154, yMid + 22], [138, yMid + 50], [0, yMid + 64]], sleeve, ow * 0.85);
  p.band([[125, yMid + 2], [elbowX, yMid - 12], [wristX, wristY]], skin, 44, ow * 0.52, "round");
  p.stroke([[155, yMid - 6], [elbowX + 18, yMid - 16], [wristX - 24, wristY - 4]], 4.2, "rgba(74, 18, 28, 0.62)");
  p.stroke([[elbowX, yMid + 4], [wristX - 10, wristY + 10]], 3.2, "rgba(92, 16, 22, 0.55)");
  p.ell(wristX + 24, wristY, 34, 28, skin, ow * 0.80);

  const spread = 0.32 + 0.68 * openClose;
  const curl = 1.05 - 0.58 * openClose;
  const angles = [-58, -27, 0, 27, 55];
  angles.forEach((deg, idx) => {
    const a1 = rad(deg * spread);
    const a2 = a1 + rad((idx === 0 ? -30 : 38) * curl);
    const len1 = idx === 0 ? 36 : 46;
    const len2 = idx === 0 ? 28 : 38;
    const bx = wristX + 36 + Math.cos(a1) * 14;
    const by = wristY + Math.sin(a1) * 18;
    const kx = bx + Math.cos(a1) * len1;
    const ky = by + Math.sin(a1) * len1;
    const tx = kx + Math.cos(a2) * len2;
    const ty = ky + Math.sin(a2) * len2;
    p.band([[bx, by], [kx, ky], [tx, ty]], sh, 12.5, ow * 0.38, "round");
    p.poly([
      [tx, ty - 4],
      [tx + Math.cos(a2) * 13, ty + Math.sin(a2) * 13],
      [tx - 3, ty + 4],
    ], "#1e1216", 2);
  });
}
