#!/usr/bin/env node
// Quick QA stills: captures key story beats to /tmp/town_story/qa for review.
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { createRequire } from 'node:module';

const require = createRequire('/tmp/studio_env/node/package.json');
const { chromium } = require('playwright-core');
const HERE = path.dirname(new URL(import.meta.url).pathname);
const WEB_ROOT = path.resolve(HERE, 'web');
const OUT_DIR = '/tmp/town_story/qa';

const BEATS = [
  [1.5, 'a01_aerial_title'],
  [4.5, 'a02_street_life'],
  [8.0, 'a03_arrival_box'],
  [11.8, 'a04_finch_warns'],
  [14.8, 'a05_kid_dismissive'],
  [17.5, 'a06_dusk_run'],
  [20.0, 'a07_door_slam'],
  [23.5, 'a08_lamps_flicker'],
  [26.5, 'a09_kid_peek'],
  [29.8, 'a10_empty_street'],
  [33.0, 'a11_count_begins'],
  [37.0, 'a12_finch_stumble'],
  [41.0, 'a13_lamps_turn'],
  [44.5, 'a14_kid_shocked'],
  [48.0, 'a15_four_three'],
  [51.0, 'a16_creepy_smile'],
  [53.0, 'a17_flash'],
  [55.0, 'a18_aftermath_hat'],
  [59.0, 'a19_finds_hat'],
  [63.5, 'a20_tracking_plates'],
  [67.2, 'a21_turns_corner'],
  [70.0, 'a22_plate_149'],
  [74.0, 'a23_aerial_reveal'],
  [78.0, 'a24_end_card'],
];

const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript' };
const server = http.createServer((req, res) => {
  const u = new URL(req.url, 'http://127.0.0.1');
  const p = path.join(WEB_ROOT, u.pathname === '/' ? 'index.html' : u.pathname);
  if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); res.end('404'); return; }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const port = server.address().port;

fs.mkdirSync(OUT_DIR, { recursive: true });
const browser = await chromium.launch({
  executablePath: '/tmp/chromium', headless: true,
  env: { ...process.env, LD_LIBRARY_PATH: '/tmp/al2023/lib:/tmp' },
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
    '--enable-webgl', '--ignore-gpu-blocklist', '--use-gl=angle', '--use-angle=swiftshader'],
});
const page = await browser.newPage({ viewport: { width: 540, height: 960 } });
page.on('pageerror', (e) => console.error('[PAGE EXC]', e.message));
await page.goto(`http://127.0.0.1:${port}/index.html?w=540&h=960`, { waitUntil: 'networkidle' });
await page.waitForFunction(() => window.__ready === true, null, { timeout: 120000 });

for (const [t, name] of BEATS) {
  const b64 = await page.evaluate((tt) => {
    const c = window.__captureBatch(Math.round(tt * 30), 1, 30)[0];
    return c;
  }, t);
  fs.writeFileSync(path.join(OUT_DIR, `${name}_t${t.toFixed(1)}.jpg`), Buffer.from(b64, 'base64'));
  console.log(`captured ${name} @ t=${t}`);
}
await browser.close();
server.close();
console.log(`DONE -> ${OUT_DIR}`);
