// framing probe: node probe.mjs '<json>'  -> [{f, ndc:[...]}]
import { chromium as pw } from 'playwright';
import chromiumPkg from '@sparticuz/chromium';
import http from 'http'; import fs from 'fs'; import path from 'path';
const JOB = JSON.parse(process.argv[2]);
const root = path.resolve('web');
const srv = http.createServer((q, s) => {
  let u; try { u = decodeURIComponent(q.url.split('?')[0]); } catch { s.writeHead(400); return s.end(); }
  if (u === '/') u = '/index.html';
  const p = path.resolve(root, `.${u}`);
  if (!p.startsWith(root + path.sep) || !fs.existsSync(p) || !fs.statSync(p).isFile()) { s.writeHead(404); return s.end(); }
  s.writeHead(200, { 'Content-Type': p.endsWith('.js') ? 'text/javascript' : p.endsWith('.html') ? 'text/html' : 'application/octet-stream' });
  fs.createReadStream(p).pipe(s);
}).listen(0);
await new Promise(r => srv.on('listening', r));
const drop = /^--(in-process-gpu|single-process|no-zygote|use-gl|use-angle|enable-unsafe-swiftshader|enable-features|disable-features|ignore-gpu-blocklist|disable-dev-shm-usage)$/;
const b = await pw.launch({ executablePath: await chromiumPkg.executablePath(), headless: true,
  args: [...chromiumPkg.args.filter(a => !drop.test(a)), '--use-gl=swiftshader', '--enable-unsafe-swiftshader'] });
const pg = await b.newPage({ viewport: { width: 720, height: 1280 } });
pg.on('pageerror', e => console.log('ERR', e.message));
await pg.goto(`http://localhost:${srv.address().port}/index.html?sc=0.4&ms=0&sm=256`);
await pg.waitForFunction(() => window.ready || window.err, null, { timeout: 240000 });
for (const job of JOB) {
  const r = await pg.evaluate(([f, pts]) => { window.renderFrame(f); return window.__proj(pts); }, [job.f, job.pts]);
  console.log(job.f, job.labels ? job.labels.map((l, i) => `${l}:${r[i][0]},${r[i][1]}`).join('  ') : JSON.stringify(r));
}
await b.close(); srv.close();
