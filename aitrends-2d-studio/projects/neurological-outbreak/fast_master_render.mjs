// fast_master_render.mjs — High-speed parallel renderer for Neurological Outbreak (16:9 Master + 6 Vertical 9:16 Shorts)
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { spawn, execFileSync } from 'node:child_process';
import { chromium } from 'playwright';

const ROOT = '/home/user/YouTube-auto-upload-/aitrends-2d-studio';
const PROJECT = path.join(ROOT, 'projects/neurological-outbreak');
const OUT_DIR = '/home/user/YouTube-auto-upload-/deliverables/neurological_outbreak';
const PARTS_DIR = '/tmp/neuro_render_parts';
fs.mkdirSync(OUT_DIR, { recursive: true });
fs.rmSync(PARTS_DIR, { recursive: true, force: true });
fs.mkdirSync(PARTS_DIR, { recursive: true });

const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.woff2': 'font/woff2', '.png': 'image/png', '.jpg': 'image/jpeg' };
function listScenes(dir, base) {
  let out = [];
  if (!fs.existsSync(dir)) return out;
  for (const f of fs.readdirSync(dir).sort()) {
    const p = path.join(dir, f);
    if (fs.statSync(p).isDirectory()) out = out.concat(listScenes(p, `${base}/${f}`));
    else if (f.endsWith('.js') && !f.startsWith('_')) out.push(`${base}/${f}`);
  }
  return out;
}

const workerPipes = new Map();
const server = http.createServer((req, res) => {
  if (req.method === 'POST' && req.url.startsWith('/__frame/')) {
    const wid = req.url.slice(9);
    const ff = workerPipes.get(wid);
    const chunks = [];
    req.on('data', c => chunks.push(c));
    req.on('end', () => {
      const buf = Buffer.concat(chunks);
      if (!ff.stdin.write(buf)) ff.stdin.once('drain', () => res.end('ok'));
      else res.end('ok');
    });
    return;
  }
  const url = decodeURIComponent(req.url.split('?')[0]);
  if (url === '/__manifest') {
    res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
    return res.end(JSON.stringify(listScenes(path.join(PROJECT, 'scenes'), '/project/scenes')));
  }
  const p = url.startsWith('/project/') ? path.join(PROJECT, url.slice(9)) : path.join(ROOT, url);
  if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
}).listen(0);

const PORT = server.address().port;

// Exact Midnight Blue LUT curves matching engine/player.js applyGrade()
function buildFFmpegCurves(gr) {
  const clamp = v => Math.max(0, Math.min(1, v));
  const xs = [0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0];
  const ch = [0, 1, 2].map(c => xs.map(x0 => {
    let x = clamp((x0 - 0.5) * gr.contrast + 0.5);
    x = clamp(gr.gain[c] * (x + gr.lift[c] * (1 - x)));
    x = clamp(Math.pow(x, 1 / gr.gamma[c]));
    return `${x0.toFixed(3)}/${x.toFixed(3)}`;
  }).join(' '));
  return `scale=1920:1080:flags=lanczos,curves=r='${ch[0]}':g='${ch[1]}':b='${ch[2]}',eq=saturation=${gr.sat}`;
}

const MIDNIGHT_GRADE = {
  contrast: 1.06,
  sat: 0.80,
  lift: [0, 0.025, 0.09],
  gamma: [0.92, 0.98, 1.08],
  gain: [0.84, 0.95, 1.15]
};
const VF = buildFFmpegCurves(MIDNIGHT_GRADE);

const chapters = JSON.parse(fs.readFileSync(path.join(PROJECT, 'timeline/chapters.json'), 'utf8'));
const totalDur = chapters.duration;
const RENDER_FPS = 12; // Classic 2D animation-on-twos -> output at smooth 24fps
const ENGINE_FPS = 24;
const totalSteps = Math.ceil(totalDur * RENDER_FPS);
const WORKERS = 2;
const chunkSteps = Math.ceil(totalSteps / WORKERS);

console.log(`Rendering ${totalDur.toFixed(2)}s (${totalSteps} unique drawings -> ${totalSteps * 2} frames @ 24fps 1080p) across ${WORKERS} workers...`);
const tStart = Date.now();

async function runWorker(wIdx) {
  const s0 = wIdx * chunkSteps;
  const s1 = Math.min(totalSteps, s0 + chunkSteps);
  const wid = String(wIdx);
  const outPart = path.join(PARTS_DIR, `part_${wid}.mp4`);

  const ff = spawn('ffmpeg', [
    '-y', '-v', 'error',
    '-f', 'image2pipe', '-framerate', String(RENDER_FPS), '-i', '-',
    '-vf', VF,
    '-r', String(ENGINE_FPS),
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p',
    outPart
  ], { stdio: ['pipe', 'inherit', 'inherit'] });
  workerPipes.set(wid, ff);

  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH,
    args: [
      '--no-sandbox', '--disable-setuid-sandbox',
      '--disable-accelerated-2d-canvas',
      '--ignore-gpu-blocklist', '--enable-unsafe-swiftshader',
      '--use-gl=angle', '--use-angle=swiftshader',
      '--disable-dev-shm-usage'
    ]
  });

  // Render at crisp 0.75x (1440x810) and lanczos-upscale + C-LUT grade to 1920x1080 in FFmpeg
  const page = await browser.newPage({ viewport: { width: 1440, height: 810 } });
  page.on('pageerror', e => console.error(`[W${wid} pageerror]`, e.message));
  await page.goto(`http://localhost:${PORT}/player.html?style=midnight&scale=0.75`);
  await page.waitForFunction('window.READY === true', null, { timeout: 90000 });

  await page.evaluate(async () => {
    const { STYLES } = await import('/engine/styles.js');
    STYLES.midnight.grade.grain = 0;
    const ctx = document.getElementById('main').getContext('2d');
    ctx.getImageData = () => ({ data: new Uint8ClampedArray(0) });
    ctx.putImageData = () => {};
  });

  const batchSize = 240; // log progress every 20s of video
  for (let cur = s0; cur < s1; cur += batchSize) {
    const end = Math.min(s1, cur + batchSize);
    await page.evaluate(async ({ a, b, wid }) => {
      const c = document.getElementById('main');
      for (let step = a; step < b; step++) {
        window.renderFrame(step * 2);
        const blob = await new Promise(r => c.toBlob(r, 'image/jpeg', 0.91));
        await fetch(`/__frame/${wid}`, { method: 'POST', body: blob });
      }
    }, { a: cur, b: end, wid });
    const el = ((Date.now() - tStart) / 1000).toFixed(1);
    console.log(`  [Worker ${wid}] ${end - s0}/${s1 - s0} steps (${((end - s0) / (s1 - s0) * 100).toFixed(0)}%) | elapsed ${el}s`);
  }

  const errs = await page.evaluate('window.ERRORS');
  if (errs.length) console.error(`[Worker ${wid}] Shot errors:`, errs);

  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  return outPart;
}

const partFiles = await Promise.all([0, 1].map(runWorker));
server.close();

const concatList = path.join(PARTS_DIR, 'list.txt');
fs.writeFileSync(concatList, partFiles.map(p => `file '${p}'`).join('\n'));

const silentMaster = path.join(PARTS_DIR, 'silent_master.mp4');
execFileSync('ffmpeg', ['-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', concatList, '-c', 'copy', silentMaster]);

const audioMaster = path.join(PROJECT, 'input/voiceover_master.mp3');
const fullMoviePath = path.join(OUT_DIR, 'Neurological_Outbreak_Full_Movie_16x9_1080p.mp4');

console.log('Muxing 16:9 1080p Master Movie with Emotional Horror Audio & Foley...');
execFileSync('ffmpeg', [
  '-y', '-v', 'error',
  '-i', silentMaster, '-i', audioMaster,
  '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
  '-shortest', '-movflags', '+faststart',
  fullMoviePath
]);

// Slice all 6 Vertical 9:16 Shorts (1080x1920) cleanly from center-safe 9:16 column (crop=608:1080:656:0)
const shortSlugs = [
  'Short_Ep01_Aisle_Four_Alert_9x16.mp4',
  'Short_Ep02_Woman_At_The_Glass_9x16.mp4',
  'Short_Ep03_Storage_Room_Window_9x16.mp4',
  'Short_Ep04_Midnight_Ringing_Phone_9x16.mp4',
  'Short_Ep05_Dead_Street_Chase_9x16.mp4',
  'Short_Ep06_Thats_Not_My_Dad_9x16.mp4',
];

console.log('Extracting 6 Standalone Vertical 9:16 Shorts (1080x1920)...');
for (let i = 0; i < chapters.chapters.length; i++) {
  const ch = chapters.chapters[i];
  const outShort = path.join(OUT_DIR, shortSlugs[i]);
  const dur = ch.duration;
  const fadeOutSt = Math.max(0, dur - 0.7).toFixed(2);
  execFileSync('ffmpeg', [
    '-y', '-v', 'error',
    '-ss', String(ch.start), '-t', String(dur),
    '-i', fullMoviePath,
    '-vf', `crop=608:1080:656:0,scale=1080:1920:flags=lanczos,fade=t=in:st=0:d=0.45,fade=t=out:st=${fadeOutSt}:d=0.65`,
    '-af', `afade=t=in:st=0:d=0.35,afade=t=out:st=${fadeOutSt}:d=0.65`,
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart',
    outShort
  ]);
  console.log(`  Wrote ${shortSlugs[i]} (${ch.start}s..${ch.end}s, ${dur.toFixed(1)}s)`);
}

fs.rmSync(PARTS_DIR, { recursive: true, force: true });
console.log(`ALL DONE in ${((Date.now() - tStart) / 1000).toFixed(1)}s!`);
