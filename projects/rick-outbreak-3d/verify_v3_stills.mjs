#!/usr/bin/env node
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';

const require = createRequire('/tmp/studio_env/node/package.json');
const { chromium } = require('playwright-core');

const WEB_ROOT = path.resolve('projects/rick-outbreak-3d/web');
const OUT_DIR  = '/tmp/rick_study/v3/qa_stills';
fs.mkdirSync(OUT_DIR, { recursive: true });

const BEATS = [
  [0.40,   '00a_ColdOpen_InfectionMap'],
  [1.10,   '00b_ColdOpen_Maul'],
  [2.00,   '00c_ColdOpen_HordeStrobes'],
  [2.90,   '00d_ColdOpen_TitleSmash'],
  [3.70,   '00e_PeaceAerial_Day1'],
  [4.40,   '01_CalmWork_417PM'],
  [6.00,   '02_Startled_PhoneBuzz'],
  [8.50,   '03_Alert1_StayIndoors'],
  [22.00,  '04_ManStaring_Road'],
  [25.60,  '05_SprintAtCar_RunFix'],
  [29.50,  '06_PanickedRunners_RunFix'],
  [43.40,  '07_LockFrontDoor'],
  [45.70,  '08_ShutterClosed_100Pct'],
  [54.50,  '09_WomanPleading_Glass'],
  [64.20,  '10_PoliceVsHorrorZombies'],
  [70.50,  '11_WomanExpressionChange'],
  [80.20,  '12_AllShutters_100PctClosed'],
  [89.50,  '13_Flashlight_Supplies'],
  [111.50, '14_PeepWindow_MimicShape'],
  [118.50, '15_Alert2_MimicSpeech'],
  [132.50, '16_YouFreeze_TerrorExpr'],
  [152.80, '17_Sunrise_BrokenWindows'],
  [162.50, '18_Phone_1Bar_OfflineMap'],
  [181.40, '19_AlleySprint_RunFix'],
  [185.00, '20_MaintDoor_HangingOpen'],
  [205.50, '21_Underground_ManShush'],
  [226.50, '22_ManGoesPale_Horror'],
  [249.50, '23_BoyGrabsSleeve_Panic'],
  [258.40, '24_MaintDoor_ClosingItself'],
  [247.50, '23_TunnelFig_DadVoice'],
  [254.90, '24_TunnelLUNGE'],
  [260.10, '25_ToBeContinued'],
];

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
  executablePath: '/tmp/chromium',
  headless: true,
  env: { ...process.env, LD_LIBRARY_PATH: '/tmp/al2023/lib:/tmp' },
  args: [
    '--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
    '--enable-webgl', '--ignore-gpu-blocklist', '--use-gl=angle', '--use-angle=swiftshader',
  ],
});
const page = await browser.newPage({ viewport: { width: 540, height: 960 } });
page.on('pageerror', (e) => console.error('[PAGEERR]', e));
page.on('console', (m) => { if (m.type() === 'error') console.error('[CONSOLEERR]', m.text()); });

await page.goto(`http://127.0.0.1:${port}/index.html?w=540&h=960`, { waitUntil: 'networkidle' });
await page.waitForFunction(() => window.__ready === true, null, { timeout: 30000 });

for (const [t, name] of BEATS) {
  const b64 = await page.evaluate((ts) => {
    const c = window.__renderAt(ts);
    return c.toDataURL('image/jpeg', 0.94).split(',')[1];
  }, t);
  fs.writeFileSync(path.join(OUT_DIR, `${name}.jpg`), Buffer.from(b64, 'base64'));
}

await browser.close();
server.close();
console.log(`Rendered ${BEATS.length} QA keyframes -> ${OUT_DIR}`);
