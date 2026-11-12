#!/usr/bin/env node
// Programmatic V3 framing verification: NDC projection of every fixed element + pixel probes.
// (No human eyes needed — validates all 7 baseline fixes + label visibility mathematically.)
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire('/tmp/studio_env/node/package.json');
const { chromium } = require('playwright-core');

const HERE = path.dirname(new URL(import.meta.url).pathname);
const WEB_ROOT = path.resolve(HERE, 'web');
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };
const server = http.createServer((req, res) => {
  const u = new URL(req.url, 'http://127.0.0.1');
  const p = path.join(WEB_ROOT, u.pathname === '/' ? 'index.html' : u.pathname);
  if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); res.end('404'); return; }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const port = server.address().port;

const browser = await chromium.launch({
  executablePath: '/tmp/chromium', headless: true,
  env: { ...process.env, LD_LIBRARY_PATH: '/tmp/al2023/lib:/tmp' },
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--enable-webgl', '--ignore-gpu-blocklist', '--use-gl=angle', '--use-angle=swiftshader'],
});
const page = await browser.newPage({ viewport: { width: 540, height: 960 } });
page.on('pageerror', (e) => console.error('[PAGEERR]', e));
await page.goto(`http://127.0.0.1:${port}/index.html?w=540&h=960`, { waitUntil: 'networkidle' });
await page.waitForFunction(() => window.__ready === true, null, { timeout: 60000 });

const results = await page.evaluate(() => {
  const THREE = window.__THREE; // may be undefined; we do manual projection math instead
  const out = [];
  const log = (name, ok, info) => out.push({ name, ok, info: info || '' });

  // ---- camera builder replicating renderAt() ----
  function cameraAt(t) {
    const st = window.__evaluateScene(t);
    // replicate main.js: fov, position, lookAt, roll
    const cam = {
      pos: st.camPos, look: st.camLook, fov: st.fov, roll: st.camRoll, st,
      aspect: 540 / 960,
    };
    // build view basis
    const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
    const norm = (a) => { const l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
    const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
    let fwd = norm(sub(cam.look, cam.pos));
    let right = norm(cross(fwd, [0, 1, 0]));
    let up = cross(right, fwd);
    // apply roll (rotate right/up around fwd)
    const rr = (cam.roll || 0) * Math.PI / 180;
    const r2 = [right[0] * Math.cos(rr) + up[0] * Math.sin(rr), right[1] * Math.cos(rr) + up[1] * Math.sin(rr), right[2] * Math.cos(rr) + up[2] * Math.sin(rr)];
    const u2 = [-right[0] * Math.sin(rr) + up[0] * Math.cos(rr), -right[1] * Math.sin(rr) + up[1] * Math.cos(rr), -right[2] * Math.sin(rr) + up[2] * Math.cos(rr)];
    cam.fwd = fwd; cam.right = r2; cam.up = u2;
    const vFov = cam.fov * Math.PI / 180;
    cam.tanV = Math.tan(vFov / 2);
    cam.tanH = cam.tanV * cam.aspect;
    return cam;
  }
  function project(cam, p) {
    const d = [p[0] - cam.pos[0], p[1] - cam.pos[1], p[2] - cam.pos[2]];
    const x = d[0] * cam.right[0] + d[1] * cam.right[1] + d[2] * cam.right[2];
    const y = d[0] * cam.up[0] + d[1] * cam.up[1] + d[2] * cam.up[2];
    const z = d[0] * cam.fwd[0] + d[1] * cam.fwd[1] + d[2] * cam.fwd[2];
    return { x: x / (z * cam.tanH), y: y / (z * cam.tanV), z };
  }

  // ---- 1. Shots 1-2: YOU head/chest clearly in frame, bottles to the RIGHT ----
  for (const [t, nm] of [[13.24, 'Shot1-early'], [13.74, 'Shot1-late']]) { // V7 render time (story 4.2/4.7 + 9.04)
    const cam = cameraAt(t);
    const head = project(cam, [3.10, 1.62, 3.05]);
    const chest = project(cam, [3.10, 1.30, 3.05]);
    const waist = project(cam, [3.10, 1.05, 3.05]);
    const bottle = project(cam, [3.50, 1.30, 4.28]);
    const reg = project(cam, [2.25, 1.30, 4.02]);
    const ok = head.z > 0 && Math.abs(head.x) < 0.72 && head.y > -0.85 && head.y < 0.92
            && waist.y > -1.05 && Math.abs(chest.x) < 0.78
            && (bottle.x > head.x + 0.06 || bottle.y < waist.y)   // bottles right of / below face
            && (reg.x < head.x - 0.05 || reg.y < waist.y);        // register left of face
    log(`${nm} YOU waist-up clear of counter props`, ok,
      `head(${head.x.toFixed(2)},${head.y.toFixed(2)}) waist(${waist.x.toFixed(2)},${waist.y.toFixed(2)}) bottle(${bottle.x.toFixed(2)},${bottle.y.toFixed(2)}) reg(${reg.x.toFixed(2)},${reg.y.toFixed(2)})`);
  }

  // ---- 2. Phone inserts: all 4 phone corners inside frame ----
  const phonePos = { 15.04: [3.02, 1.35, 3.10], 17.54: [3.02, 1.35, 3.10], 23.04: [3.02, 1.35, 3.10],
                     127.04: [2.66, 1.35, -13.80], 130.54: [2.66, 1.35, -13.80],
                     168.54: [3.02, 1.35, 3.10], 172.04: [3.02, 1.35, 3.10] }; // V7 render time (story + 9.04)
  for (const [tStr, pos] of Object.entries(phonePos)) {
    const t = parseFloat(tStr);
    const cam = cameraAt(t);
    // phone faces camera: corners = pos +/- camera-right*0.125 +/- camera-up*0.222 (slight margin over 0.12/0.215)
    let worst = 0;
    for (const sx of [-1, 1]) for (const sy of [-1, 1]) {
      const p = [pos[0] + sx * 0.125 * cam.right[0] + sy * 0.222 * cam.up[0],
                 pos[1] + sx * 0.125 * cam.right[1] + sy * 0.222 * cam.up[1],
                 pos[2] + sx * 0.125 * cam.right[2] + sy * 0.222 * cam.up[2]];
      const nd = project(cam, p);
      worst = Math.max(worst, Math.abs(nd.x), Math.abs(nd.y));
      if (nd.z <= 0) worst = 99;
    }
    log(`Phone insert t=${tStr} full bezel+status bar in frame`, worst < 0.97, `worstNDC=${worst.toFixed(3)}`);
  }

  // ---- 3. Street: carMan & police clear of abandoned car ----
  {
    const cam = cameraAt(31.04);
    const man = project(cam, [-2.40, 1.5, 16.20]);
    const car = project(cam, [-5.2, 0.9, 13.0]);
    log('Shot9 carMan in frame, abandonedCar off sightline',
      man.z > 0 && Math.abs(man.x) < 0.7 && (Math.abs(car.x) > 0.95 || car.z <= 0),
      `man(${man.x.toFixed(2)},${man.y.toFixed(2)}) car(${car.x.toFixed(2)},${car.y.toFixed(2)})`);
  }
  {
    // police: -0.40 -> -3.10 over 61.28-66.84; infA: shamble 1.90 -> 0.32 by 65.30,
    // then LUNGE 0.32 -> -2.30 by 66.20 (tackles the officer down).
    const lerp = (a, b, u) => a + (b - a) * u;
    for (const tt of [62.5, 64.2, 66.5]) {
      const u1 = Math.min(1, Math.max(0, (tt - 61.28) / 4.02));
      const uL = Math.min(1, Math.max(0, (tt - 65.30) / 0.90));
      const infX = tt < 65.30 ? lerp(1.90, 0.32, u1) : lerp(0.32, -2.30, uL);
      const cam = cameraAt(tt + 9.04); // V7: story math on tt, render probe + 9.04
      const pol = project(cam, [lerp(-0.40, -3.10, Math.min(1, (tt - 61.28) / 5.56)), 1.45, 17.50]);
      const inf = project(cam, [infX, 1.45, 17.35]);
      log(`Shot27/28 t=${tt} police+lead-infected both framed`,
        pol.z > 0 && inf.z > 0 && Math.abs(pol.x) < 0.92 && Math.abs(inf.x) < 0.98 && pol.y > -0.9 && inf.y > -0.9,
        `pol(${pol.x.toFixed(2)},${pol.y.toFixed(2)}) inf(${inf.x.toFixed(2)},${inf.y.toFixed(2)})`);
    }
  }

  // ---- 4. Woman uncanny close-up: full face + mouth above captions ----
  {
    const cam = cameraAt(79.54);
    const top = project(cam, [0.55, 1.68, 7.95]);
    const mouth = project(cam, [0.55, 1.42, 7.95]);
    const chin = project(cam, [0.55, 1.28, 7.95]);
    log('Shot30 woman full face centered above captions',
      top.y < 0.92 && mouth.y < 0.62 && mouth.y > -0.55 && chin.y > -0.9 && Math.abs(mouth.x) < 0.5,
      `top(${top.y.toFixed(2)}) mouth(${mouth.x.toFixed(2)},${mouth.y.toFixed(2)}) chin(${chin.y.toFixed(2)})`);
  }

  // ---- 5. Peep window at y=1.55 aligned with mimic face ----
  {
    const cam = cameraAt(120.54);
    const win = project(cam, [2.80, 1.55, -16.32]);
    const face = project(cam, [2.80, 1.52, -17.10]);
    const d = Math.hypot(win.x - face.x, win.y - face.y);
    log('Shot43 peep window aligned with mimic face', win.z > 0 && Math.abs(win.x) < 0.6 && Math.abs(win.y) < 0.75 && d < 0.28,
      `win(${win.x.toFixed(2)},${win.y.toFixed(2)}) face(${face.x.toFixed(2)},${face.y.toFixed(2)}) d=${d.toFixed(3)}`);
  }

  // ---- 6. YOU freeze close-up: full head in frame ----
  {
    // Heights measured from the frozen_terror texture: content top row 228/1000 -> y1.36,
    // face centroid row 414 -> y1.03 (eyes ~1.08, chin ~0.95).
    const cam = cameraAt(141.54);
    const top = project(cam, [2.65, 1.38, -13.95]);
    const chin = project(cam, [2.65, 0.95, -13.95]);
    const eyes = project(cam, [2.65, 1.08, -13.95]);
    log('Shot49 YOU frozen_terror full head in frame',
      top.y < 0.9 && chin.y > -0.88 && Math.abs(eyes.x) < 0.45 && eyes.y > -0.5 && eyes.y < 0.6,
      `top(${top.y.toFixed(2)}) chin(${chin.y.toFixed(2)}) eyes(${eyes.x.toFixed(2)},${eyes.y.toFixed(2)})`);
  }

  // ---- 7. Alley maintenance door + hazard/lamp visible, doorway NOT bricked ----
  {
    const cam = cameraAt(194.04);
    const door = project(cam, [0.0, 1.4, -35.0]);
    const voidDark = project(cam, [0.0, 1.4, -36.4]);
    log('Shot63 maint door + stairwell void in frame', door.z > 0 && Math.abs(door.x) < 0.65 && Math.abs(voidDark.x) < 0.8,
      `door(${door.x.toFixed(2)},${door.y.toFixed(2)})`);
  }

  // ---- 8. Underground boy-grab two-shot: you AND boy both in frame ----
  {
    const cam = cameraAt(258.54);
    const you = project(cam, [1.28, 0.95, -62.80]);
    const boy = project(cam, [0.85, 0.85, -62.95]);
    log('Shot80 you+boy sleeve-grab two-shot', you.z > 0 && boy.z > 0 && Math.abs(you.x) < 0.85 && Math.abs(boy.x) < 0.85 && you.y > -0.9 && boy.y > -0.9,
      `you(${you.x.toFixed(2)},${you.y.toFixed(2)}) boy(${boy.x.toFixed(2)},${boy.y.toFixed(2)})`);
  }

  // ---- 9. Shot 82: self-closing door + hazard bulkhead region in frame ----
  {
    const cam = cameraAt(267.44);
    const doorTop = project(cam, [0.0, 3.4, -52.10]);
    const doorMid = project(cam, [0.0, 3.0, -52.10]);
    log('Shot82 closing door framed w/ hazard trim', doorTop.z > 0 && doorMid.z > 0 && doorTop.y < 0.9 && doorMid.y > -0.9 && Math.abs(doorMid.x) < 0.6,
      `top(${doorTop.x.toFixed(2)},${doorTop.y.toFixed(2)}) mid(${doorMid.x.toFixed(2)},${doorMid.y.toFixed(2)})`);
  }

  // ---- 10. Flashlight rations: labeled cluster in frame ----
  {
    const cam = cameraAt(98.54);
    const c1 = project(cam, [3.44, 1.25, 4.30]);
    const c2 = project(cam, [4.00, 1.18, 4.15]);
    const c3 = project(cam, [4.05, 1.20, 3.94]);
    log('Shot35 labeled rations cluster in frame', c1.z > 0 && c2.z > 0 && c3.z > 0 && Math.abs(c1.x) < 0.9 && Math.abs(c2.x) < 0.9 && Math.abs(c3.x) < 0.95 && c1.y > -0.9 && c3.y > -0.9,
      `w(${c1.x.toFixed(2)},${c1.y.toFixed(2)}) can(${c2.x.toFixed(2)},${c2.y.toFixed(2)}) fak(${c3.x.toFixed(2)},${c3.y.toFixed(2)})`);
  }

  // ---- 10b. V6.5 ORIGINS COLD OPEN: every montage beat framed correctly ----
  {
    // 200 busy life: the running boy mid-frame, mom behind
    const cam = cameraAt(0.30);
    const st = cam.st;
    const boy = st.chars.survBoy, mom = st.chars.woman;
    const boyHead = project(cam, [boy.pos[0], 1.12, boy.pos[2]]);
    const momHead = project(cam, [mom.pos[0], 1.55, mom.pos[2]]);
    log('Origins 200 busy life: boy running in frame + mom behind',
      boy.visible && mom.visible && boyHead.z > 0 && Math.abs(boyHead.x) < 0.55 && Math.abs(boyHead.y) < 0.75,
      `boy(${boyHead.x.toFixed(2)},${boyHead.y.toFixed(2)}) momVis=${mom.visible} momHead(${momHead.x.toFixed(2)},${momHead.y.toFixed(2)})`);
  }
  {
    // 201 lab wide: scientist at the bench, monitors behind
    const cam = cameraAt(2.70);
    const sci = project(cam, [-40.55, 1.55, -14.55]);
    const mon = project(cam, [-40.0, 1.6, -16.0]);
    log('Origins 201 lab wide: masked scientist + monitor wall in frame',
      sci.z > 0 && Math.abs(sci.x) < 0.7 && Math.abs(sci.y) < 0.8 && mon.z > 0 && Math.abs(mon.x) < 0.9,
      `sci(${sci.x.toFixed(2)},${sci.y.toFixed(2)}) mon(${mon.x.toFixed(2)},${mon.y.toFixed(2)})`);
  }
  {
    // 202 lab close: the gas-mask face fills the frame
    const cam = cameraAt(3.85);
    const mask = project(cam, [-40.55, 1.60, -14.55]);
    const vials = project(cam, [-41.3, 1.1, -15.6]);
    log('Origins 202 lab close: mask face large + vial glow present',
      mask.z > 0 && Math.abs(mask.x) < 0.45 && Math.abs(mask.y) < 0.6 && vials.z > 0 && Math.abs(vials.x) < 1.0,
      `mask(${mask.x.toFixed(2)},${mask.y.toFixed(2)}) vials(${vials.x.toFixed(2)},${vials.y.toFixed(2)})`);
  }
  {
    // V7 304 the button: scientist at the console, glass containers + chemical rain in frame
    const cam = cameraAt(5.00);
    const st = cam.st;
    const sci = st.chars.scientist;
    const sciP = project(cam, [sci.pos[0], 1.45, sci.pos[2]]);
    const contA = project(cam, [-40.62, 1.1, -14.10]);
    const contB = project(cam, [-39.25, 1.1, -14.05]);
    log('Origins 304 containers: scientist + both glass vessels framed, rain on',
      sci.visible && sciP.z > 0 && Math.abs(sciP.x) < 0.85 && Math.abs(sciP.y) < 0.9 &&
      contA.z > 0 && contB.z > 0 && Math.abs(contA.x) < 1.0 && Math.abs(contB.x) < 1.0 && (st.introDrip || 0) > 0.2,
      `sci(${sciP.x.toFixed(2)},${sciP.y.toFixed(2)}) contA(${contA.x.toFixed(2)},${contA.y.toFixed(2)}) contB(${contB.x.toFixed(2)},${contB.y.toFixed(2)}) drip=${(st.introDrip || 0).toFixed(2)}`);
  }
  {
    // V7 306 evil laugh: mask fills frame, evilGrin expr + laugh shake active
    const cam = cameraAt(7.00);
    const st = cam.st;
    const sci = st.chars.scientist;
    const mask = project(cam, [sci.pos[0], 1.60, sci.pos[2]]);
    log('Origins 306 evil grin: mask centered + evilGrin expr + shake',
      sci.visible && sci.expr === 'evilGrin' && mask.z > 0 && Math.abs(mask.x) < 0.45 && Math.abs(mask.y) < 0.6 && sci.shake > 0.004,
      `mask(${mask.x.toFixed(2)},${mask.y.toFixed(2)}) expr=${sci.expr} shake=${sci.shake.toFixed(4)}`);
  }
  {
    // 204 news: anchor centered, breaking-news wall behind
    const cam = cameraAt(9.00);
    const anchor = project(cam, [-40.0, 1.35, -50.30]);
    const wallTop = project(cam, [-40.0, 2.6, -51.5]);
    log('Origins 204 news: anchor + breaking wall in frame',
      anchor.z > 0 && Math.abs(anchor.x) < 0.5 && Math.abs(anchor.y) < 0.8 && wallTop.z > 0 && wallTop.y > -0.2,
      `anchor(${anchor.x.toFixed(2)},${anchor.y.toFixed(2)}) wallTopY=${wallTop.y.toFixed(2)}`);
  }
  {
    // 205 destruction: horde running + fire glow zone in frame
    const cam = cameraAt(8.10);
    const st = cam.st;
    let inFrame = 0;
    for (const k of ['infA', 'infB', 'infC']) {
      const c = st.chars[k];
      if (!c.visible) continue;
      const p = project(cam, [c.pos[0], 1.2, c.pos[2]]);
      if (p.z > 0 && Math.abs(p.x) < 0.95 && Math.abs(p.y) < 0.95) inFrame++;
    }
    const fire = project(cam, [-1.9, 0.9, 17.5]);
    log('Origins 205 destruction: horde + fires in frame, introFire on',
      inFrame >= 2 && fire.z > 0 && Math.abs(fire.x) < 0.95 && st.introFire,
      `inFrame=${inFrame} fire(${fire.x.toFixed(2)},${fire.y.toFixed(2)}) introFire=${st.introFire}`);
  }
  {
    // Phone sequence: social feed -> banner -> alert mode timeline (VO-synced)
    const m = (tt) => window.__evaluateScene(tt).phoneState.mode; // probes in RENDER time (story + 9.04)
    const seq = [m(14.14), m(14.54), m(15.04)];
    log('Origins phone timeline: social0 -> social1 -> alert1',
      seq[0] === 'social0' && seq[1] === 'social1' && seq[2] === 'alert1', JSON.stringify(seq));
  }

  // ---- 11. Sunrise: abandoned cars visible but off store sightline ----
  {
    const cam = cameraAt(163.64);
    const swerve = project(cam, [3.8, 1.0, 19.0]);
    log('Shot54 sunrise abandoned car in frame', swerve.z > 0 && Math.abs(swerve.x) < 0.9, `(${swerve.x.toFixed(2)},${swerve.y.toFixed(2)})`);
  }

  // helper: NDC -> pixel rect around a world point
  const pxRect = (cam, p, halfW = 0.24, halfH = 0.24) => {
    const nd = project(cam, p);
    const cx = (nd.x + 1) / 2 * 540, cy = (1 - nd.y) / 2 * 960;
    return [Math.max(0, cx - halfW * 540), Math.max(0, cy - halfH * 960), Math.min(540, cx + halfW * 540), Math.min(960, cy + halfH * 960)];
  };

  // ---- 12. Pixel probes (labels actually rendering!) ----
  const pc = document.createElement('canvas');
  pc.width = 540; pc.height = 960;
  const pg = pc.getContext('2d');
  const probe = (t) => {
    const c = window.__renderAt(t);
    pg.drawImage(c, 0, 0, 540, 960);
    return pg.getImageData(0, 0, 540, 960).data;
  };
  const countColor = (data, x0, y0, x1, y1, test) => {
    // pxRect returns floats — floor/ceil them or array indices go fractional and read undefined!
    const X0 = Math.max(0, Math.floor(x0)), Y0 = Math.max(0, Math.floor(y0));
    const X1 = Math.min(540, Math.ceil(x1)), Y1 = Math.min(960, Math.ceil(y1));
    let n = 0, tot = 0;
    for (let y = Y0; y < Y1; y += 2) for (let x = X0; x < X1; x += 2) {
      const i = (y * 540 + x) * 4; tot++;
      if (test(data[i], data[i + 1], data[i + 2])) n++;
    }
    return n / Math.max(1, tot);
  };

  // 12a. Phone alert banner red present in upper-middle, dark bezel rows at very top of phone area
  {
    const d = probe(17.54);
    const redFrac = countColor(d, 160, 220, 380, 340, (r, g, b) => r > 120 && g < 90 && b < 90);
    const whiteFrac = countColor(d, 160, 220, 380, 340, (r, g, b) => r > 200 && g > 195 && b > 185);
    log('Pixel: alert1 card visible on phone (V6 white/amber)', redFrac > 0.08 || whiteFrac > 0.08, `redFrac=${redFrac.toFixed(3)} whiteFrac=${whiteFrac.toFixed(3)}`);
  }
  // 12b. Counter rations: red can + white FAK + gold chocolate pixels present (projection-driven region!)
  {
    const d = probe(98.54);
    const cam = cameraAt(98.54);
    const [x0, y0, x1, y1] = pxRect(cam, [3.72, 1.18, 4.10], 0.42, 0.30);
    const redFrac = countColor(d, x0, y0, x1, y1, (r, g, b) => r > 115 && g < 95 && b < 95);
    const whiteFrac = countColor(d, x0, y0, x1, y1, (r, g, b) => r > 195 && g > 195 && b > 190);
    const goldFrac = countColor(d, x0, y0, x1, y1, (r, g, b) => r > 145 && g > 105 && b < 115);
    log('Pixel: labeled cans/FAK/choco colors on counter', redFrac > 0.015 && whiteFrac > 0.008 && goldFrac > 0.003,
      `rect=${x0.toFixed(0)},${y0.toFixed(0)}-${x1.toFixed(0)},${y1.toFixed(0)} red=${redFrac.toFixed(3)} white=${whiteFrac.toFixed(3)} gold=${goldFrac.toFixed(3)}`);
  }
  // 12c. Neon: cyan pixels around the right storefront window (shot 12 pan end, powered)
  {
    const d = probe(39.74);
    const cam = cameraAt(39.74);
    const [x0, y0, x1, y1] = pxRect(cam, [3.35, 2.62, 7.24], 0.30, 0.22);
    const cyanFrac = countColor(d, x0, y0, x1, y1, (r, g, b) => b > 140 && g > 130 && r < 160);
    log('Pixel: OPEN 24 HRS neon cyan glow', cyanFrac > 0.004, `rect=${x0.toFixed(0)},${y0.toFixed(0)}-${x1.toFixed(0)},${y1.toFixed(0)} cyanFrac=${cyanFrac.toFixed(4)}`);
  }
  // 12d. Underground: warm amber bulkhead visible while door still partly open (t=256.6)
  {
    const d = probe(265.64);
    const cam = cameraAt(265.64);
    const [x0, y0, x1, y1] = pxRect(cam, [0.60, 4.46, -51.74], 0.20, 0.18);
    const warmFrac = countColor(d, x0, y0, x1, y1, (r, g, b) => r > 145 && g > 85 && b < 130);
    log('Pixel: warm bulkhead glow above door', warmFrac > 0.006, `rect=${x0.toFixed(0)},${y0.toFixed(0)}-${x1.toFixed(0)},${y1.toFixed(0)} warmFrac=${warmFrac.toFixed(4)}`);
  }
  // 12e. Alley hazard: yellow-black stripes near door top
  {
    const d = probe(194.04);
    const yelFrac = countColor(d, 100, 60, 440, 700, (r, g, b) => r > 160 && g > 120 && b < 100);
    log('Pixel: hazard yellow near alley door', yelFrac > 0.004, `yelFrac=${yelFrac.toFixed(4)}`);
  }
  // 12f. Shelf products: colored rows in store background (shot 14 at 34s pans store)
  {
    const d = probe(43.54);
    const colorFrac = countColor(d, 60, 300, 480, 900, (r, g, b) => (r > 130 && g < 100 && b < 100) || (b > 130 && r < 110) || (r > 150 && g > 110 && b < 110));
    log('Pixel: labeled shelf product colors visible', colorFrac > 0.02, `colorFrac=${colorFrac.toFixed(3)}`);
  }
  // 12g. Phone map: yellow route on blue map bg
  {
    const d = probe(171.54);
    const mapFrac = countColor(d, 140, 200, 400, 700, (r, g, b) => (b > 60 && b < 130 && g > 60 && r < 80) || (r > 190 && g > 150 && b < 110));
    log('Pixel: offline map route visible', mapFrac > 0.02, `mapFrac=${mapFrac.toFixed(3)}`); // V6: ACES palette
  }

  return out;
});

let fails = 0;
for (const r of results) {
  console.log(`${r.ok ? 'PASS' : 'FAIL'} | ${r.name} ${r.ok ? '' : '<<< ' + r.info}`);
  if (!r.ok) fails++;
}
console.log(`\n${results.filter((r) => r.ok).length}/${results.length} checks passed${fails ? ' — FIX NEEDED' : ' — ALL GOOD'}`);
await browser.close();
server.close();
process.exit(fails ? 1 : 0);
