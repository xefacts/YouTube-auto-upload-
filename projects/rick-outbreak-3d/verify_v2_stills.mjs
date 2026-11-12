import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire('/tmp/studio_env/node/package.json');
const { chromium } = require('playwright-core');

const WEB_ROOT = path.resolve('projects/rick-outbreak-3d/web');
const OUT_DIR  = '/tmp/rick_study/v2/qa_stills';
fs.mkdirSync(OUT_DIR, { recursive: true });

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png' };
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
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--enable-webgl', '--ignore-gpu-blocklist', '--use-gl=angle', '--use-angle=swiftshader'],
});

const page = await browser.newPage({ viewport: { width: 540, height: 960 } });
page.on('console', (m) => { if (m.type() === 'error') console.error('[PAGE ERR]', m.text()); });
page.on('pageerror', (e) => console.error('[EXC]', e));

await page.goto(`http://127.0.0.1:${port}/index.html?w=540&h=960`, { waitUntil: 'networkidle' });
await page.waitForFunction(() => window.__ready === true, null, { timeout: 30000 });

const probes = [
  [1.8,   '01_soup_cans'],
  [4.6,   '02_hand_phone_buzz'],
  [9.5,   '03_alert_screen_grip'],
  [24.0,  '04_sprint_to_window'],
  [29.5,  '05_street_zombie_chase'],
  [35.1,  '06_man_forward_trip'],
  [36.6,  '07_man_fallen_ABOVE_road'],
  [39.6,  '08_car_crash_bloom'],
  [42.5,  '09_runners_proper_dir'],
  [55.5,  '10_driver_palms_on_glass'],
  [61.5,  '11_zombie_behind_driver'],
  [65.2,  '12_driver_sprint_LEFT'],
  [80.0,  '13_call_failed_grip'],
  [106.5, '14_fridges_unobstructed'],
  [114.5, '15_office_pc_screen'],
  [125.5, '16_you_crouchSit_floor'],
  [142.5, '17_woman_palm_press'],
  [147.4, '18_woman_help_me_lips'],
  [151.8, '19_zombie_behind_woman'],
  [161.5, '20_you_pushing_shelves'],
  [180.5, '21_handtruck_brace'],
  [208.5, '22_veined_claw_arm'],
  [231.8, '23_zombie_faces_window'],
  [235.2, '24_sprint_back_corridor'],
];

const t0 = Date.now();
for (const [ts, name] of probes) {
  const b64 = await page.evaluate((t) => {
    const c = window.__renderAt(t);
    return c.toDataURL('image/jpeg', 0.92).split(',')[1];
  }, ts);
  fs.writeFileSync(path.join(OUT_DIR, `${name}.jpg`), Buffer.from(b64, 'base64'));
}
console.log(`Rendered ${probes.length} V2 stills in ${((Date.now() - t0)/1000).toFixed(2)}s (${(probes.length / ((Date.now() - t0)/1000)).toFixed(1)} fps @ 540x960)!`);

await browser.close();
server.close();
