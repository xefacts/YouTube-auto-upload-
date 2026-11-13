#!/usr/bin/env node
// Preview animatic: captures 48 story keyframes for a fast slideshow preview.
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { createRequire } from 'node:module';
const require = createRequire('/tmp/studio_env/node/package.json');
const { chromium } = require('playwright-core');

const HERE = path.dirname(new URL(import.meta.url).pathname);
const WEB_ROOT = path.resolve(HERE, 'web');
const OUT_DIR = '/tmp/town_story/preview';
fs.mkdirSync(OUT_DIR, { recursive: true });

const N_FRAMES = 48;
const T_START = 0.8, T_STEP = 1.65; // covers 0.8 -> 78.7

const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript' };
const server = http.createServer((req, res) => {
  const u = new URL(req.url, 'http://127.0.0.1');
  const p = path.join(WEB_ROOT, u.pathname === '/' ? 'index.html' : u.pathname);
  if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const port = server.address().port;

const browser = await chromium.launch({
  executablePath: '/tmp/chromium', headless: true,
  env: { ...process.env, LD_LIBRARY_PATH: '/tmp/al2023/lib:/tmp' },
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--enable-webgl', '--use-gl=angle', '--use-angle=swiftshader'],
});
const page = await browser.newPage({ viewport: { width: 540, height: 960 } });
page.on('pageerror', (e) => console.error('[PAGE EXC]', e.message));
await page.goto(`http://127.0.0.1:${port}/index.html?w=540&h=960`, { waitUntil: 'networkidle' });
await page.waitForFunction(() => window.__ready === true, null, { timeout: 120000 });

for (let k = 0; k < N_FRAMES; k++) {
  const t = T_START + k * T_STEP;
  const b64 = await page.evaluate((tt) => window.__captureBatch(Math.round(tt * 30), 1, 30)[0], t);
  fs.writeFileSync(path.join(OUT_DIR, `f${String(k).padStart(3, '0')}.jpg`), Buffer.from(b64, 'base64'));
}
console.log(`captured ${N_FRAMES} frames -> ${OUT_DIR}`);
await browser.close();
server.close();
