import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire('/tmp/studio_env/node/package.json');
const { chromium } = require('playwright-core');

const WEB_ROOT = path.resolve('projects/rick-outbreak-3d/web');
const OUT_DIR  = '/tmp/rick_study/qa_stills';
fs.mkdirSync(OUT_DIR, { recursive: true });

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg' };
const server = http.createServer((req, res) => {
  const u = new URL(req.url, 'http://127.0.0.1');
  const p = path.join(WEB_ROOT, u.pathname === '/' ? 'index.html' : u.pathname);
  if (!fs.existsSync(p)) { res.writeHead(404); res.end('404'); return; }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const port = server.address().port;

const browser = await chromium.launch({
  executablePath: '/tmp/chromium',
  headless: true,
  env: { ...process.env, LD_LIBRARY_PATH: '/tmp/al2023/lib:/tmp' },
  args: [
    '--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
    '--enable-webgl', '--ignore-gpu-blocklist',
    '--use-gl=angle', '--use-angle=swiftshader',
  ],
});

const page = await browser.newPage({ viewport: { width: 720, height: 1280 } });
page.on('pageerror', (err) => console.error('PAGE ERROR:', err));
page.on('console', (msg) => { if (msg.type() === 'error') console.error('CONSOLE ERR:', msg.text()); });

await page.goto(`http://127.0.0.1:${port}/index.html?w=720&h=1280`, { waitUntil: 'networkidle' });
await page.waitForFunction(() => window.__ready === true, null, { timeout: 20000 });

const shots = await page.evaluate(() => window.__SHOTS);
console.log(`Loaded ${shots.length} shots. Rendering QA stills...`);

const tStart = Date.now();
for (const s of shots) {
  const tMid = +((s.t0 + s.t1) * 0.5).toFixed(2);
  const b64 = await page.evaluate((t) => {
    window.__renderAt(t);
    return window.__outCanvas.toDataURL('image/jpeg', 0.92).split(',')[1];
  }, tMid);
  const fname = `S${String(s.id).padStart(2, '0')}_t${tMid.toFixed(1)}s.jpg`;
  fs.writeFileSync(path.join(OUT_DIR, fname), Buffer.from(b64, 'base64'));
}
const elapsed = Date.now() - tStart;
console.log(`Rendered ${shots.length} stills in ${elapsed} ms (${(elapsed / shots.length).toFixed(1)} ms/still incl shadow rebake!).`);

// Also benchmark sequential 30fps speed across 60 consecutive frames (2 seconds)
const tSeq = Date.now();
for (let f = 0; f < 60; f++) {
  await page.evaluate((t) => {
    window.__renderAt(t);
    return window.__outCanvas.toDataURL('image/jpeg', 0.93).length;
  }, 34.0 + f / 30);
}
const seqMs = Date.now() - tSeq;
console.log(`Sequential 30fps benchmark: ${(seqMs / 60).toFixed(1)} ms/frame!`);

await browser.close();
server.close();
