#!/usr/bin/env node
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';

const require = createRequire('/tmp/studio_env/node/package.json');
const { chromium } = require('playwright-core');

const HERE = path.dirname(new URL(import.meta.url).pathname);
const WEB_ROOT = path.resolve(HERE, 'web');
const OUT_DIR  = '/tmp/rick_study/v3/qa_stills';
fs.mkdirSync(OUT_DIR, { recursive: true });

const V7 = 9.04; // V7 intro retime: render = story + 9.04 (from story 3.36 onward)
const BEATS = [
  [0.30,      '00a_Origins_BusyLife'],
  [1.95,      '00b_Origins_OfficeElder'],
  [2.70,      '00c_Origins_LabWide'],
  [3.85,      '00d_Origins_LabClose_Mask'],
  [5.00,      '00e_Origins_Containers_Button'],
  [6.10,      '00f_Origins_Transformation'],
  [7.00,      '00g_Origins_EvilGrin_Laugh'],
  [8.10,      '00h_Origins_CityChaos'],
  [9.00,      '00i_Origins_NewsScreens'],
  [11.00,     '00j_Origins_BlackScreen'],
  [3.70 + V7, '00k_PeaceAerial_Day1'],
  [4.40 + V7, '01_CalmWork_417PM'],
  [6.00 + V7, '02_Startled_PhoneBuzz'],
  [8.50 + V7, '03_Alert1_StayIndoors'],
  [22.00 + V7, '04_ManStaring_Road'],
  [25.60 + V7, '05_SprintAtCar_RunFix'],
  [29.50 + V7, '06_PanickedRunners_RunFix'],
  [43.40 + V7, '07_LockFrontDoor'],
  [45.70 + V7, '08_ShutterClosed_100Pct'],
  [54.50 + V7, '09_WomanPleading_Glass'],
  [64.20 + V7, '10_PoliceVsHorrorZombies'],
  [70.50 + V7, '11_WomanExpressionChange'],
  [80.20 + V7, '12_AllShutters_100PctClosed'],
  [89.50 + V7, '13_Flashlight_Supplies'],
  [111.50 + V7, '14_PeepWindow_MimicShape'],
  [118.50 + V7, '15_Alert2_MimicSpeech'],
  [132.50 + V7, '16_YouFreeze_TerrorExpr'],
  [152.80 + V7, '17_Sunrise_BrokenWindows'],
  [162.50 + V7, '18_Phone_1Bar_OfflineMap'],
  [181.40 + V7, '19_AlleySprint_RunFix'],
  [185.00 + V7, '20_MaintDoor_HangingOpen'],
  [205.50 + V7, '21_Underground_ManShush'],
  [226.50 + V7, '22_ManGoesPale_Horror'],
  [249.50 + V7, '23_BoyGrabsSleeve_Panic'],
  [258.40 + V7, '24_MaintDoor_ClosingItself'],
  [247.50 + V7, '25_TunnelFig_DadVoice'],
  [254.90 + V7, '26_TunnelLUNGE'],
  [260.10 + V7, '27_ToBeContinued'],
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
