#!/usr/bin/env node
// V3 Master Full-Length 3D Horror Renderer + 1080x1920 1-Word Captions Encoder
// Renders all 7,810 frames (260.320s @ 30fps) via 3 load-balanced SwiftShader Chromium workers,
// captures lossless MJPEG chunks, then upscales to 1080x1920 + burns 660 synced 1-word pop captions
// + muxes the unedited ElevenLabs v4 voiceover horror master (-14.2 LUFS) into final H.264 MP4 (< 100 MB).

import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { spawn, execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';

const require = createRequire('/tmp/studio_env/node/package.json');
const { chromium } = require('playwright-core');

const FFMPEG    = '/tmp/studio_env/bin/ffmpeg';
const WEB_ROOT  = path.resolve('projects/rick-outbreak-3d/web');
const ASS_PATH  = path.resolve('projects/rick-outbreak-3d/data/captions_v3.ass');
const AUDIO_WAV = '/tmp/rick_study/v3/master_audio_v3.wav';
const OUT_DIR   = '/tmp/rick_study/v3/render_chunks';
const FINAL_MP4 = '/tmp/rick_study/v3/Rick_Clips_Outbreak_V3_Final_1080x1920.mp4';

const TOTAL_FRAMES = 7810; // 260.320s @ 30fps
const FPS   = 30;
const RW    = 540;
const RH    = 960;
const BATCH = 24;

fs.mkdirSync(OUT_DIR, { recursive: true });

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js':   'text/javascript',
  '.json': 'application/json',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
};

const server = http.createServer((req, res) => {
  const u = new URL(req.url, 'http://127.0.0.1');
  const p = path.join(WEB_ROOT, u.pathname === '/' ? 'index.html' : u.pathname);
  if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) {
    res.writeHead(404); res.end('404'); return;
  }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});

await new Promise((r) => server.listen(0, '127.0.0.1', r));
const port = server.address().port;
console.log(`[V3] Local scene server ready on 127.0.0.1:${port}`);

// Cost-balanced 3-worker split across 7,810 frames
const RANGES = [
  { id: 0, start: 0,    end: 2260 }, // 2260 frames (street chase + store lock)
  { id: 1, start: 2260, end: 5060 }, // 2800 frames (power cut, flashlight, mimic, brother)
  { id: 2, start: 5060, end: TOTAL_FRAMES }, // 2750 frames (sunrise, platform, tunnel, door)
];

const tGlobal = Date.now();
let completedFrames = 0;

async function runWorker({ id, start, end }) {
  const chunkPath = path.join(OUT_DIR, `chunk_${id}.mkv`);
  if (fs.existsSync(chunkPath)) fs.unlinkSync(chunkPath);

  const ff = spawn(FFMPEG, [
    '-y', '-hide_banner', '-loglevel', 'error',
    '-f', 'image2pipe', '-vcodec', 'mjpeg', '-framerate', String(FPS),
    '-i', '-',
    '-c:v', 'copy',
    chunkPath,
  ], { stdio: ['pipe', 'inherit', 'inherit'] });

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

  const page = await browser.newPage({ viewport: { width: RW, height: RH } });
  page.on('pageerror', (e) => console.error(`[W${id} EXC]`, e));
  await page.goto(`http://127.0.0.1:${port}/index.html?w=${RW}&h=${RH}`, { waitUntil: 'networkidle' });
  await page.waitForFunction(() => window.__ready === true, null, { timeout: 30000 });
  console.log(`[W${id}] WebGL + PostProcessing ready — rendering frames [${start}..${end - 1}] (${end - start} frames)`);

  let cur = start;
  let lastLog = Date.now();
  while (cur < end) {
    const cnt = Math.min(BATCH, end - cur);
    const b64Arr = await page.evaluate(
      ([s, c, fps]) => window.__captureBatch(s, c, fps),
      [cur, cnt, FPS]
    );
    for (let i = 0; i < b64Arr.length; i++) {
      const buf = Buffer.from(b64Arr[i], 'base64');
      if (!ff.stdin.write(buf)) {
        await new Promise((r) => ff.stdin.once('drain', r));
      }
    }
    cur += cnt;
    completedFrames += cnt;

    if (Date.now() - lastLog > 12000 || cur >= end) {
      const elapsed = (Date.now() - tGlobal) / 1000;
      const totFps = completedFrames / Math.max(0.1, elapsed);
      const eta = (TOTAL_FRAMES - completedFrames) / Math.max(0.1, totFps);
      console.log(
        `[PROGRESS] ${completedFrames}/${TOTAL_FRAMES} (${((completedFrames / TOTAL_FRAMES) * 100).toFixed(1)}%) | ` +
        `W${id}: ${cur - start}/${end - start} | ${totFps.toFixed(2)} fps total | ETA ${eta.toFixed(0)}s`
      );
      lastLog = Date.now();
    }
  }

  ff.stdin.end();
  await new Promise((res, rej) => {
    ff.on('close', (code) => (code === 0 ? res() : rej(new Error(`W${id} ffmpeg exited ${code}`))));
  });
  await browser.close();
  console.log(`[W${id}] Completed lossless MJPEG chunk -> ${chunkPath}`);
  return chunkPath;
}

const chunkFiles = await Promise.all(RANGES.map(runWorker));
server.close();

const concatTxt = path.join(OUT_DIR, 'concat.txt');
fs.writeFileSync(concatTxt, chunkFiles.map((f) => `file '${f}'`).join('\n') + '\n');

console.log(`[ENCODE] Upscaling 540x960 -> 1080x1920 (Lanczos) + burning 660 1-word ASS captions + muxing master_audio_v3.wav...`);
// fontsdir: resolve Anton from the repo fonts/ dir - self-contained, no ~/.fonts dependency.
const FONT_DIR = path.resolve('projects/rick-outbreak-3d/fonts');
const vf = `scale=1080:1920:flags=lanczos,unsharp=5:5:0.42:5:5:0.0,ass=${ASS_PATH.replace(/:/g, '\\:')}:fontsdir=${FONT_DIR.replace(/:/g, '\\:')}`;

execFileSync(FFMPEG, [
  '-y', '-hide_banner', '-stats',
  '-f', 'concat', '-safe', '0', '-i', concatTxt,
  '-i', AUDIO_WAV,
  '-vf', vf,
  '-r', '30',
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
  '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
  '-shortest',
  '-movflags', '+faststart',
  FINAL_MP4,
], { stdio: 'inherit' });

const szMB = (fs.statSync(FINAL_MP4).size / (1024 * 1024)).toFixed(2);
const totalSec = ((Date.now() - tGlobal) / 1000) / 60;
console.log(`[DONE] Final V3 Master MP4 ready: ${FINAL_MP4} (${szMB} MB) in ${totalSec.toFixed(1)}min!`);
