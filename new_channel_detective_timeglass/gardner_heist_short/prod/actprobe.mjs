import { chromium as pw } from 'playwright';
import chromiumPkg from '@sparticuz/chromium';
import http from 'http'; import fs from 'fs'; import path from 'path';
const root = path.resolve('web');
const srv = http.createServer((q, s) => {
  let u; try { u = decodeURIComponent(q.url.split('?')[0]); } catch { s.writeHead(400); return s.end(); }
  if (u === '/') u = '/index.html';
  const p = path.resolve(root, `.${u}`);
  if (!fs.existsSync(p) || !fs.statSync(p).isFile()) { s.writeHead(404); return s.end(); }
  s.writeHead(200, { 'Content-Type': p.endsWith('.js') ? 'text/javascript' : 'text/html' });
  fs.createReadStream(p).pipe(s);
}).listen(0);
await new Promise(r => srv.on('listening', r));
const drop = /^--(in-process-gpu|single-process|no-zygote|use-gl|use-angle|enable-unsafe-swiftshader|enable-features|disable-features|ignore-gpu-blocklist|disable-dev-shm-usage)$/;
const b = await pw.launch({ executablePath: await chromiumPkg.executablePath(), headless: true,
  args: [...chromiumPkg.args.filter(a => !drop.test(a)), '--use-gl=swiftshader', '--enable-unsafe-swiftshader'] });
const pg = await b.newPage({ viewport: { width: 720, height: 1280 } });
pg.on('pageerror', e => console.log('ERR', e.message));
await pg.goto(`http://localhost:${srv.address().port}/index.html?sc=0.35&ms=0&sm=256`);
await pg.waitForFunction(() => window.ready || window.err, null, { timeout: 240000 });
for (const f of [3600, 3900, 5200, 6000]) {
  const r = await pg.evaluate(async (f) => {
    const m = await import('./story.js');
    const a = m.actorsAt(f, await import('./toon.js'));
    return { f, n: a.length, keys: a.map(x => `${x.key}@${x.x.toFixed(1)},${x.z.toFixed(1)} s${x.s}`) };
  }, f);
  console.log(JSON.stringify(r));
}
await b.close(); srv.close();
