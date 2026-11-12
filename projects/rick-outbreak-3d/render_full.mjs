import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { spawn, execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';

const require = createRequire('/tmp/studio_env/node/package.json');
const { chromium } = require('playwright-core');

const FFMPEG   = '/tmp/studio_env/bin/ffmpeg';
const WEB_ROOT = path.resolve('projects/rick-outbreak-3d/web');
const OUT_DIR  = '/tmp/rick_study/out';
fs.mkdirSync(OUT_DIR, { recursive: true });

const TOTAL_FRAMES = 10032; // 334.40s * 30.0 fps
const FPS          = 30;
const RW           = 480;   // flat-shaded toon upscales razor-sharp with lanczos+cas=0.45 -> 1080x1920
const RH           = 854;
const BATCH        = 24;

const MIME = {
  '.html': 'text/html',
  '.js':   'text/javascript',
  '.json': 'application/json',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
};

const server = http.createServer((req, res) => {
  const u = new URL(req.url, 'http://127.0.0.1');
  const p = path.join(WEB_ROOT, u.pathname === '/' ? 'index.html' : u.pathname);
  if (!fs.existsSync(p)) { res.writeHead(404); res.end('404'); return; }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const port = server.address().port;
console.log(`[Render] Local scene server listening on 127.0.0.1:${port}`);

async function renderSegment(workerId, fStart, fEnd, outMkv) {
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
  page.on('pageerror', (e) => console.error(`[W${workerId} ERR]`, e));
  await page.goto(`http://127.0.0.1:${port}/index.html?w=${RW}&h=${RH}`, { waitUntil: 'networkidle' });
  await page.waitForFunction(() => window.__ready === true, null, { timeout: 30000 });

  // Zero-CPU stream copy during WebGL render so 100% of CPU goes to SwiftShader!
  const ff = spawn(FFMPEG, [
    '-y',
    '-f', 'image2pipe',
    '-vcodec', 'mjpeg',
    '-framerate', String(FPS),
    '-i', '-',
    '-c:v', 'copy',
    outMkv,
  ], { stdio: ['pipe', 'ignore', 'pipe'] });

  let ffErr = '';
  ff.stderr.on('data', (d) => { ffErr = (ffErr + d.toString()).slice(-1500); });

  const totalSeg = fEnd - fStart;
  const t0 = Date.now();

  for (let f = fStart; f < fEnd; f += BATCH) {
    const cnt = Math.min(BATCH, fEnd - f);
    const b64List = await page.evaluate(
      ([sf, c, fps]) => window.__captureBatch(sf, c, fps),
      [f, cnt, FPS]
    );
    for (let i = 0; i < b64List.length; i++) {
      const buf = Buffer.from(b64List[i], 'base64');
      if (!ff.stdin.write(buf)) {
        await new Promise((res) => ff.stdin.once('drain', res));
      }
    }
    const done = (f + cnt) - fStart;
    if (done % 480 < BATCH || done === totalSeg) {
      const el = (Date.now() - t0) / 1000;
      const fpsRate = done / Math.max(0.1, el);
      const etaMin = ((totalSeg - done) / Math.max(0.01, fpsRate)) / 60;
      console.log(`[W${workerId}] ${done}/${totalSeg} frames (${((done / totalSeg) * 100).toFixed(1)}%) | ${fpsRate.toFixed(2)} fps | ETA ${etaMin.toFixed(1)}m`);
    }
  }

  ff.stdin.end();
  const exitCode = await new Promise((res) => ff.on('close', res));
  await browser.close();
  if (exitCode !== 0) {
    throw new Error(`Worker ${workerId} ffmpeg exited ${exitCode}: ${ffErr}`);
  }
  console.log(`[W${workerId}] Raw MJPEG segment complete -> ${outMkv}`);
}

const mid = Math.floor(TOTAL_FRAMES / 2); // 5016
const raw0 = path.join(OUT_DIR, 'raw_part0.mkv');
const raw1 = path.join(OUT_DIR, 'raw_part1.mkv');

const tAll = Date.now();
await Promise.all([
  renderSegment(0, 0, mid, raw0),
  renderSegment(1, mid, TOTAL_FRAMES, raw1),
]);

server.close();
console.log(`[Render] All ${TOTAL_FRAMES} frames rendered in ${((Date.now() - tAll) / 60000).toFixed(2)} min! Encoding 1080x1920 Clean Master...`);

const concatTxt = path.join(OUT_DIR, 'concat_raw.txt');
fs.writeFileSync(concatTxt, `file '${raw0}'\nfile '${raw1}'\n`);

const cleanMaster = path.join(OUT_DIR, 'Outbreak_RickClips_3D_Full_Clean_1080x1920.mp4');
execFileSync(FFMPEG, [
  '-y',
  '-f', 'concat', '-safe', '0', '-i', concatTxt,
  '-i', path.join(OUT_DIR, 'master_audio.wav'),
  '-vf', 'scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p',
  '-c:v', 'libx264', '-preset', 'veryfast', '-tune', 'animation',
  '-crf', '23', '-maxrate', '2050k', '-bufsize', '4100k', '-r', String(FPS),
  '-c:a', 'aac', '-b:a', '192k',
  '-shortest',
  '-movflags', '+faststart',
  cleanMaster,
], { stdio: 'inherit' });

fs.unlinkSync(raw0);
fs.unlinkSync(raw1);
console.log(`[Render] FULL 334.40s CLEAN MASTER COMPLETE -> ${cleanMaster}`);
