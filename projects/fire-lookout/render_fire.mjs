#!/usr/bin/env node
// "THE FIRE LOOKOUT" — full renderer + caption encoder
// Renders 4,395 frames (146.5s @ 30fps) via 3 SwiftShader Chromium workers,
// then upscales + burns 1-word captions + muxes the normalized master audio.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { spawn, execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';

const require = createRequire('/tmp/studio_env/node/package.json');
const { chromium } = require('playwright-core');

const FFMPEG    = '/tmp/studio_env/bin/ffmpeg';
const HERE      = path.dirname(new URL(import.meta.url).pathname);
const ROOT      = path.resolve(HERE);                 // project root (img/ lives here)
const ASS_PATH  = path.resolve(HERE, 'data/captions.ass');
const FONT_DIR  = path.resolve(HERE, 'web/fonts');
const AUDIO_WAV = '/tmp/fire_lookout/master_audio_norm.wav';
const OUT_DIR   = '/tmp/fire_lookout/render_chunks';
const FINAL_MP4 = '/tmp/fire_lookout/Fire_Lookout_FINAL_1080x1920.mp4';

const TOTAL_FRAMES = 4395; // 146.5s @ 30fps
const FPS = 30;
const RW = 540, RH = 960;
const BATCH = 24;

fs.mkdirSync(OUT_DIR, { recursive: true });
if (!fs.existsSync(path.join(ROOT, 'web/index.html'))) {
  console.error('[FATAL] web/index.html missing'); process.exit(1);
}
try { execFileSync('pkill', ['-f', '/tmp/chromium'], { stdio: 'ignore' }); console.log('[T] Swept orphaned chromium'); } catch {}
await new Promise((r) => setTimeout(r, 1000));

const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.png': 'image/png', '.ttf': 'font/ttf' };
const server = http.createServer((req, res) => {
  const u = new URL(req.url, 'http://127.0.0.1');
  const p = path.join(ROOT, decodeURIComponent(u.pathname));
  if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); res.end('404'); return; }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const port = server.address().port;
console.log(`[T] Scene server ready on 127.0.0.1:${port}`);

const RANGES = [
  { id: 0, start: 0,    end: 1465 },
  { id: 1, start: 1465, end: 2930 },
  { id: 2, start: 2930, end: TOTAL_FRAMES },
];

const tGlobal = Date.now();
let completedFrames = 0;

async function runWorker({ id, start, end }) {
  const chunkPath = path.join(OUT_DIR, `chunk_${id}.mkv`);
  if (fs.existsSync(chunkPath)) fs.unlinkSync(chunkPath);
  const ff = spawn(FFMPEG, [
    '-y', '-hide_banner', '-loglevel', 'error',
    '-f', 'image2pipe', '-vcodec', 'mjpeg', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'copy', chunkPath,
  ], { stdio: ['pipe', 'inherit', 'inherit'] });
  const browser = await chromium.launch({
    executablePath: '/tmp/chromium', headless: true,
    env: { ...process.env, LD_LIBRARY_PATH: '/tmp/al2023/lib:/tmp' },
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
      '--enable-webgl', '--ignore-gpu-blocklist', '--use-gl=angle', '--use-angle=swiftshader'],
  });
  try {
    const page = await browser.newPage({ viewport: { width: RW, height: RH } });
    page.on('pageerror', (e) => console.error(`[W${id} EXC]`, e));
    await page.goto(`http://127.0.0.1:${port}/web/index.html?w=${RW}&h=${RH}`, { waitUntil: 'networkidle' });
    await page.waitForFunction(() => window.__ready === true, null, { timeout: 180000 });
    console.log(`[W${id}] ready — rendering frames [${start}..${end - 1}] (${end - start} frames)`);
    let cur = start, lastLog = Date.now();
    while (cur < end) {
      const cnt = Math.min(BATCH, end - cur);
      const b64Arr = await page.evaluate(([s, c, fps]) => window.__captureBatch(s, c, fps), [cur, cnt, FPS]);
      if (!Array.isArray(b64Arr) || b64Arr.length !== cnt) throw new Error(`batch size mismatch at ${cur}`);
      for (let i = 0; i < b64Arr.length; i++) {
        const buf = Buffer.from(b64Arr[i].split(',')[1] || b64Arr[i], 'base64');
        if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
      }
      cur += cnt; completedFrames += cnt;
      if (Date.now() - lastLog > 15000 || cur >= end) {
        const elapsed = (Date.now() - tGlobal) / 1000;
        const totFps = completedFrames / Math.max(0.1, elapsed);
        const eta = (TOTAL_FRAMES - completedFrames) / Math.max(0.1, totFps);
        console.log(`[PROGRESS] ${completedFrames}/${TOTAL_FRAMES} (${((completedFrames / TOTAL_FRAMES) * 100).toFixed(1)}%) | W${id}: ${cur - start}/${end - start} | ${totFps.toFixed(2)} fps | ETA ${eta.toFixed(0)}s`);
        lastLog = Date.now();
      }
    }
    ff.stdin.end();
    await new Promise((res, rej) => ff.on('close', (code) => (code === 0 ? res() : rej(new Error(`W${id} ffmpeg ${code}`)))));
    console.log(`[W${id}] chunk done -> ${chunkPath}`);
    return chunkPath;
  } catch (err) {
    console.error(`[W${id}] FAILED:`, err && err.message || err);
    try { ff.stdin.destroy(); } catch {}
    try { ff.kill('SIGKILL'); } catch {}
    throw err;
  } finally { try { await browser.close(); } catch {} }
}

const chunkPromises = [];
for (const r of RANGES) { chunkPromises.push(runWorker(r)); await new Promise((rr) => setTimeout(rr, 2500)); }
const chunkFiles = await Promise.all(chunkPromises);
server.close();

const concatTxt = path.join(OUT_DIR, 'concat.txt');
fs.writeFileSync(concatTxt, chunkFiles.map((f) => `file '${f}'`).join('\n') + '\n');

console.log(`[ENCODE] Upscale 540x960 -> 1080x1920 + captions + audio...`);
const vf = `scale=1080:1920:flags=lanczos,unsharp=5:5:0.42:5:5:0.0,ass=${ASS_PATH.replace(/:/g, '\\\\:')}:fontsdir=${FONT_DIR.replace(/:/g, '\\\\:')}`;
execFileSync(FFMPEG, [
  '-y', '-hide_banner', '-stats',
  '-f', 'concat', '-safe', '0', '-i', concatTxt,
  '-i', AUDIO_WAV,
  '-vf', vf, '-r', '30',
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
  '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart',
  FINAL_MP4,
], { stdio: 'inherit' });

const szMB = (fs.statSync(FINAL_MP4).size / (1024 * 1024)).toFixed(2);
console.log(`[DONE] ${FINAL_MP4} (${szMB} MB) in ${(((Date.now() - tGlobal) / 1000) / 60).toFixed(1)}min`);
