// scenes/sets/outbreak_world.js — Reusable Hybrid 16:9 + Center 9:16 Safe Horror Sets
import { E, S, mood, shade, alpha, backdrop, linGrad, rr, glow, circle, seg, poly, layer, text, FONTS } from '/engine/core.js';
import * as FX from '/engine/fx2d.js';
import { SAFE } from '../cast.js';

export const GY = E.H * 0.80;

export function box(g, x, y, w, h, r, fill, stroke = null, lw = 2) {
  rr(g, x, y, w, h, r);
  if (fill) { g.fillStyle = fill; g.fill(); }
  if (stroke) { g.strokeStyle = stroke; g.lineWidth = lw; g.stroke(); }
}


export function flicker(t, speed = 7.3, minA = 0.72) {
  const v = Math.sin(t * speed) * Math.sin(t * speed * 2.17 + 1.3);
  return v > 0.78 ? minA : 1.0;
}

function groundPlane(g, y, topCol, botCol) {
  g.fillStyle = linGrad(g, 0, y, 0, E.H, [topCol, botCol]);
  g.fillRect(-E.W, y, E.W * 3, E.H - y + 200);
  g.fillStyle = alpha('#c9dcff', 0.08);
  g.fillRect(-E.W, y, E.W * 3, 3);
}

// First-person POV Smartphone HUD centered inside SAFE 9:16 column
export function drawPOVPhone(g, x, y, t, opts = {}) {
  const { vibrate = false, mode = 'alert', zoom = 1 } = opts;
  const vx = vibrate ? Math.sin(t * 58) * 5 : 0;
  const vy = vibrate ? Math.cos(t * 47) * 3 : 0;
  const w = 250 * zoom, h = 430 * zoom;
  const px = x - w / 2 + vx, py = y - h / 2 + vy;

  if (mode === 'alert') glow(g, x + vx, y + vy, 230 * zoom, '#ff3b4e', 0.34);
  else glow(g, x + vx, y + vy, 190 * zoom, '#5aa9ff', 0.24);

  // POV thumb/hand gripping phone (you = audience immersion!)
  box(g, px - 22, py + h * 0.48, 34, h * 0.38, 16, '#141b29');
  box(g, px + w - 12, py + h * 0.52, 28, h * 0.30, 14, '#141b29');

  // Phone bezel & screen
  box(g, px, py, w, h, 26 * zoom, '#0d121c', '#3c4d66', 4);
  box(g, px + 12, py + 24, w - 24, h - 48, 16 * zoom, mode === 'alert' ? '#1c0b12' : '#0b1626');

  if (mode === 'alert') {
    box(g, px + 22, py + 48, w - 44, 46 * zoom, 8, '#d92b3a');
    text(g, 'EMERGENCY ALERT', x + vx, py + 71 * zoom, { size: 17 * zoom, color: '#fff', font: FONTS.ui, weight: 900 });
    text(g, 'BIOLOGICAL', x + vx, py + 132 * zoom, { size: 22 * zoom, color: '#ff6b78', font: FONTS.ui, weight: 900 });
    text(g, 'OUTBREAK', x + vx, py + 160 * zoom, { size: 22 * zoom, color: '#ff6b78', font: FONTS.ui, weight: 900 });
    text(g, 'AVOID ALL CONTACT', x + vx, py + 215 * zoom, { size: 14 * zoom, color: '#e8eef7', font: FONTS.ui, weight: 800 });
    text(g, 'SEEK SHELTER NOW', x + vx, py + 242 * zoom, { size: 14 * zoom, color: '#ffd27d', font: FONTS.ui, weight: 800 });
    text(g, 'LOCK DOORS & WINDOWS', x + vx, py + 269 * zoom, { size: 13 * zoom, color: '#aebbd1', font: FONTS.ui, weight: 800 });
  } else if (mode === 'nocall') {
    text(g, 'NO SERVICE', x + vx, py + 115 * zoom, { size: 20 * zoom, color: '#ff6b78', font: FONTS.ui, weight: 900 });
    text(g, 'CALL FAILED', x + vx, py + 175 * zoom, { size: 18 * zoom, color: '#cbd5e6', font: FONTS.ui, weight: 800 });
    circle(g, x + vx, py + 280 * zoom, 28 * zoom, '#c92a3a');
  } else if (mode === 'map') {
    // Offline municipal transit map
    g.strokeStyle = alpha('#4b7bb5', 0.45); g.lineWidth = 2;
    for (let k = 1; k < 5; k++) {
      g.beginPath(); g.moveTo(px + 20, py + 40 + k * 65 * zoom); g.lineTo(px + w - 20, py + 40 + k * 65 * zoom); g.stroke();
      g.beginPath(); g.moveTo(px + k * 46 * zoom, py + 40); g.lineTo(px + k * 46 * zoom, py + h - 40); g.stroke();
    }
    seg(g, [[x - 55 * zoom, py + h - 95 * zoom], [x, py + 190 * zoom], [x + 48 * zoom, py + 135 * zoom]], 5, '#4de69b');
    circle(g, x - 55 * zoom, py + h - 95 * zoom, 8 * zoom, '#ffd27d');
    circle(g, x + 48 * zoom, py + 135 * zoom, 11 * zoom, '#4de69b');
    text(g, 'TRANSIT STATION', x + vx, py + 76 * zoom, { size: 16 * zoom, color: '#7ff5b8', font: FONTS.ui, weight: 900 });
    text(g, '2 BLOCKS EAST', x + vx, py + 102 * zoom, { size: 13 * zoom, color: '#d8e6fa', font: FONTS.ui, weight: 800 });
  }
}

// 1. CONVENIENCE STORE AISLE & CHECKOUT SET
export function storeInteriorSet(g, cam, t, opts = {}) {
  const { dim = 0, powerFlicker = false, night = false } = opts;
  const M = mood('night');
  const fl = powerFlicker ? flicker(t, 9.5, 0.35) : 1.0;

  backdrop(g, [shade(M.dark, -0.38), shade(M.wall, -0.30 - dim * 0.25)]);

  layer(g, cam, 0.25, (g) => {
    FX.windowFrame(g, { x: 260, y: 150, w: 1400, h: 360, cols: 5, frame: shade(M.dark, -0.45), bar: 10 }, (g, x, y, w, h) => {
      g.fillStyle = linGrad(g, 0, y, 0, y + h, night ? ['#050811', '#101b30'] : M.sky);
      g.fillRect(x, y, w, h);
      FX.skyline(g, { x, y: y + h, w, minH: 55, maxH: 205, color: shade(M.dark, -0.35), windowColor: alpha(M.practical, 0.52), lit: 0.24, seed: 31 });
    });
  });

  // Left & Right 16:9 wing shelving + flickering refrigerators
  layer(g, cam, 0.6, (g) => {
    box(g, 90, 210, 460, GY - 210, 8, shade(M.wall, -0.42), shade(M.dark, -0.5), 3);
    for (let i = 0; i < 2; i++) {
      const rx = 115 + i * 215;
      box(g, rx, 235, 195, GY - 265, 6, alpha('#7fc8ff', 0.09 * fl), shade(M.dark, -0.3), 2);
      glow(g, rx + 97, 420, 170, '#7fc8ff', 0.11 * fl * (1 - dim));
      for (let sh = 0; sh < 4; sh++) {
        g.fillStyle = shade(M.dark, -0.35);
        g.fillRect(rx + 8, 310 + sh * 115, 179, 6);
      }
    }
    box(g, 1350, 240, 470, GY - 240, 6, shade(M.wall, -0.44), shade(M.dark, -0.5), 3);
    for (let sh = 0; sh < 4; sh++) {
      const sy = 320 + sh * 125;
      g.fillStyle = shade(M.wall, -0.18);
      g.fillRect(1365, sy, 440, 8);
      for (let c = 0; c < 5; c++) {
        if ((c + sh) % 2 === 0) box(g, 1385 + c * 82, sy - 38, 32, 38, 4, c % 2 ? '#7a353c' : '#3a5875');
      }
    }
  });

  layer(g, cam, 1.0, (g) => {
    groundPlane(g, GY, shade(M.floor, -0.32), shade(M.dark, -0.55));
    for (const lx of [360, SAFE.CX, 1560]) {
      box(g, lx - 140, 52, 280, 14, 4, alpha('#e8f2ff', 0.78 * fl * (1 - dim * 0.7)));
      glow(g, lx, 80, 320, M.practical, 0.19 * fl * (1 - dim * 0.65));
    }
  });
}

// 2. STORE FRONT GLASS ENTRANCE & SECURITY SHUTTERS (Centered at SAFE.CX = 960)
export function storeFrontEntranceSet(g, cam, t, opts = {}) {
  const { shutterAmt = 0, night = false, chaos = false, barricade = false } = opts;
  const M = mood('night');

  backdrop(g, [shade(M.dark, -0.42), shade(M.wall, -0.36)]);

  layer(g, cam, 0.35, (g) => {
    const skyCols = night ? ['#050811', '#0e182b'] : M.sky;
    g.fillStyle = linGrad(g, 0, 110, 0, GY, skyCols);
    g.fillRect(180, 110, 1560, GY - 110);
    FX.skyline(g, { x: 180, y: GY - 80, w: 1560, minH: 90, maxH: 310, color: shade(M.dark, -0.32), windowColor: alpha(M.practical, night ? 0.22 : 0.55), lit: night ? 0.14 : 0.28, seed: 19 });
    g.fillStyle = shade(M.road, -0.3);
    g.fillRect(180, GY - 85, 1560, 95);
    if (chaos) {
      glow(g, SAFE.CX + 110, GY - 130, 260, '#ff4d4d', 0.32);
      glow(g, SAFE.CX - 140, GY - 110, 200, '#ff944d', 0.24);
    }
  });

  layer(g, cam, 1.0, (g) => {
    g.fillStyle = shade(M.dark, -0.48);
    g.fillRect(-100, 0, E.W + 200, 120);
    g.fillRect(-100, 110, 290, GY - 110);
    g.fillRect(1730, 110, 290, GY - 110);
    g.fillRect(715, 110, 22, GY - 110);
    g.fillRect(1183, 110, 22, GY - 110);
    g.fillRect(SAFE.CX - 7, 110, 14, GY - 110);

    g.fillStyle = alpha('#9ec5ff', 0.06);
    g.fillRect(737, 120, 446, GY - 120);

    // Heavy metal deadbolt
    box(g, SAFE.CX - 28, 515, 56, 30, 5, '#7e8c9f', '#202836', 2);

    if (shutterAmt > 0.01) {
      const shH = (GY - 120) * Math.min(1, shutterAmt);
      g.fillStyle = '#252e3d';
      g.fillRect(190, 120, 1540, shH);
      g.strokeStyle = alpha('#0b0f18', 0.65);
      g.lineWidth = 2;
      for (let sy = 136; sy < 120 + shH; sy += 22) {
        g.beginPath(); g.moveTo(190, sy); g.lineTo(1730, sy); g.stroke();
      }
    }

    groundPlane(g, GY, shade(M.floor, -0.35), shade(M.dark, -0.58));

    if (barricade) {
      for (const bx of [760, 1005]) {
        box(g, bx, 350, 165, GY - 350, 5, shade('#2d394b', -0.15), '#131924', 3);
        for (let r = 0; r < 4; r++) {
          g.fillStyle = '#43536b';
          g.fillRect(bx + 6, 410 + r * 105, 153, 8);
        }
      }
      box(g, 855, GY - 155, 115, 155, 6, '#59412e', '#261b12', 3);
      box(g, 978, GY - 120, 105, 120, 6, '#4a3627', '#261b12', 3);
    }
  });
}

// 3. BACK STORAGE ROOM & WIRE-MESH DELIVERY DOOR (Centered at SAFE.CX = 960)
export function storageDoorSet(g, cam, t, opts = {}) {
  const { broken = false, handTruck = true, strapLoose = false, truckFallen = false, emergencyFlicker = true } = opts;
  const fl = emergencyFlicker ? flicker(t, 11.2, 0.28) : 1.0;

  backdrop(g, ['#060910', '#0f1624']);

  layer(g, cam, 0.7, (g) => {
    for (const sx of [140, 1460]) {
      box(g, sx, 220, 320, GY - 220, 4, '#151d2b', '#0a0e17', 3);
      for (let r = 0; r < 3; r++) {
        g.fillStyle = '#263244';
        g.fillRect(sx + 8, 330 + r * 165, 304, 8);
        box(g, sx + 35, 265 + r * 165, 95, 65, 4, '#3d2e24');
        box(g, sx + 165, 275 + r * 165, 85, 55, 4, '#2d3a4b');
      }
    }
    g.fillStyle = '#2b3648';
    g.fillRect(1168, 80, 28, GY - 80);
  });

  layer(g, cam, 1.0, (g) => {
    box(g, 822, 215, 276, GY - 215, 4, '#3a281e', '#17100c', 5);
    box(g, 838, 230, 244, GY - 230, 2, '#2b1f18', '#140e0a', 3);

    box(g, 898, 285, 124, 130, 3, broken ? '#05070d' : '#1b2738', '#4a372b', 4);
    g.strokeStyle = alpha('#8fa4bf', broken ? 0.35 : 0.55);
    g.lineWidth = 1.5;
    for (let i = 0; i < 6; i++) {
      if (broken && i > 1 && i < 5) continue;
      g.beginPath(); g.moveTo(902 + i * 22, 289); g.lineTo(902 + i * 22, 411); g.stroke();
      g.beginPath(); g.moveTo(902, 293 + i * 22); g.lineTo(1018, 293 + i * 22); g.stroke();
    }
    if (broken) {
      g.fillStyle = '#9db7d6';
      for (const [gx, gy, gw, gh] of [[904, 288, 16, 18], [998, 290, 18, 22], [906, 396, 20, 16], [992, 392, 22, 19]]) {
        g.fillRect(gx, gy, gw, gh);
      }
    }

    box(g, 1052, 535, 22, 28, 4, '#6e4730', '#24160e', 2);
    groundPlane(g, GY, '#111722', '#070a10');

    if (broken) {
      g.fillStyle = alpha('#b8d4f5', 0.65);
      for (let k = 0; k < 14; k++) g.fillRect(865 + (k * 17) % 190, GY + 8 + (k * 7) % 24, 9, 5);
    }

    if (handTruck && !truckFallen) {
      seg(g, [[895, GY], [925, 485]], 12, '#b04b3e');
      seg(g, [[860, GY - 6], [955, GY - 6]], 10, '#7c8b9e');
      circle(g, 892, GY - 14, 18, '#262e3a');
      if (!strapLoose) seg(g, [[920, 520], [1175, 530]], 6, '#d99b38');
    } else if (truckFallen) {
      seg(g, [[760, GY + 8], [935, GY - 8]], 11, '#b04b3e');
      circle(g, 765, GY + 4, 17, '#262e3a');
      seg(g, [[1175, 530], [1158, 695]], 6, '#d99b38');
    }

    box(g, SAFE.CX - 36, 92, 72, 22, 6, alpha('#ff6b4a', 0.85 * fl));
    glow(g, SAFE.CX, 112, 290, '#ff5c3b', 0.22 * fl);
  });
}

// 4. DEAD STREET & TRANSIT STATION ENTRANCE STAIRS (Part 5)
export function stationStairsSet(g, cam, t, opts = {}) {
  const { doorOpen = false } = opts;
  const M = mood('night');
  backdrop(g, ['#0a111d', '#152236']);

  layer(g, cam, 0.5, (g) => {
    FX.skyline(g, { x: -100, y: 380, w: E.W + 200, minH: 90, maxH: 260, color: '#0d1524', windowColor: alpha(M.practical, 0.2), lit: 0.12, seed: 44 });
    // Concrete stairwell walls descending into station
    poly(g, [[120, 380], [670, 380], [670, GY], [120, GY]], '#121b2b');
    poly(g, [[1250, 380], [1800, 380], [1800, GY], [1250, GY]], '#121b2b');
  });

  layer(g, cam, 1.0, (g) => {
    groundPlane(g, GY, '#0e1522', '#060a11');
    // Locked main metal shutter (left-center of SAFE: x = 695..955)
    box(g, 695, 310, 255, GY - 310, 4, '#222c3b', '#0d121a', 4);
    for (let sy = 330; sy < GY; sy += 22) {
      g.fillStyle = '#151c27'; g.fillRect(701, sy, 243, 3);
    }
    text(g, 'STATION CLOSED', 822, 285, { size: 17, color: '#ff6b78', font: FONTS.ui, weight: 900 });

    // Narrow Maintenance Door + Card Reader (right-center of SAFE: x = 1005..1195)
    box(g, 1005, 330, 185, GY - 330, 4, doorOpen ? '#080e17' : '#2b394d', '#101722', 4);
    if (doorOpen) {
      glow(g, 1095, 520, 190, '#ffd089', 0.28);
      poly(g, [[1005, 330], [1075, 348], [1075, GY - 12], [1005, GY]], '#243142');
    }
    // Electronic Card Reader beside door
    box(g, 972, 495, 24, 38, 4, '#18202c', '#3b4b63', 2);
    circle(g, 984, 507, 4, doorOpen ? '#4de68a' : '#ff4d5e');
    glow(g, 984, 507, 45, doorOpen ? '#4de68a' : '#ff4d5e', 0.45);
  });
}

// 5. UNDERGROUND MAINTENANCE CONTROL ROOM & GREEN CORRIDOR (Part 6 Climax)
export function controlRoomSet(g, cam, t, opts = {}) {
  const { lightsOut = false, radioOn = false } = opts;
  const M = mood('night');
  const fl = lightsOut ? 0 : flicker(t, 6.2, 0.86);

  backdrop(g, lightsOut ? ['#020408', '#040810'] : ['#09101c', '#131f33']);

  layer(g, cam, 0.8, (g) => {
    g.strokeStyle = '#1d2a3d'; g.lineWidth = 14;
    g.beginPath(); g.moveTo(120, 180); g.lineTo(580, 180); g.lineTo(580, GY); g.stroke();
    g.beginPath(); g.moveTo(1340, 210); g.lineTo(1800, 210); g.lineTo(1800, GY); g.stroke();

    // Wall Evacuation Map inside SAFE zone (x = 700..935, y = 215..430)
    box(g, 700, 215, 235, 215, 6, lightsOut ? '#080e17' : '#18263b', '#2e415e', 3);
    g.strokeStyle = alpha('#5c85b8', lightsOut ? 0.15 : 0.7); g.lineWidth = 3;
    g.beginPath(); g.moveTo(725, 385); g.lineTo(795, 315); g.lineTo(865, 305); g.lineTo(910, 255); g.stroke();
    for (const [mx, my, special] of [[745, 365, false], [795, 315, false], [865, 305, true], [905, 260, false]]) {
      g.strokeStyle = special ? '#ffbd4a' : '#ff4d5e';
      g.lineWidth = special ? 3.5 : 2.5;
      g.beginPath(); g.arc(mx, my, special ? 14 : 10, 0, Math.PI * 2); g.stroke();
    }

    // Second Door leading to narrow Maintenance Corridor (x = 1010..1215)
    box(g, 1010, 225, 205, GY - 225, 4, lightsOut ? '#0a1018' : '#1b2636', '#0b1019', 4);
    box(g, 1068, 285, 88, 125, 4, '#040b08', '#26354a', 3);
    glow(g, 1112, 348, lightsOut ? 175 : 95, '#3dff8b', lightsOut ? 0.38 : 0.24);
    circle(g, 1112, 338, 7, '#6bffa8');
  });

  layer(g, cam, 1.0, (g) => {
    groundPlane(g, GY, lightsOut ? '#04070d' : '#0f1724', '#04060b');

    box(g, 715, GY - 155, 250, 155, 5, lightsOut ? '#0d131e' : '#223044', '#0c121c', 3);
    box(g, 785, GY - 208, 105, 53, 6, '#1b222e', '#39485e', 2);
    seg(g, [[872, GY - 208], [882, GY - 268]], 3, '#7e90a8');
    const radCol = radioOn ? '#ff5252' : '#35465c';
    circle(g, 808, GY - 182, 6, radCol);
    if (radioOn) glow(g, 808, GY - 182, 105, '#ff4d4d', 0.45);

    if (!lightsOut) glow(g, SAFE.CX, 105, 340, M.practical, 0.17 * fl);
  });
}
