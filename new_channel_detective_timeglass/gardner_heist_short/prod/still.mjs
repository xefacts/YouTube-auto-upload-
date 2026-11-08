// render specific frames: node still.mjs <outdir> <sc> f1 f2 f3 ...
import { chromium as pw } from 'playwright';
import chromiumPkg from '@sparticuz/chromium';
import http from 'http'; import fs from 'fs'; import path from 'path';
const [,, outdir, scArg = '0.6', ...fs_] = process.argv;
const SC = +scArg, FR = fs_.map(Number);
fs.mkdirSync(outdir, { recursive: true });
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
pg.on('pageerror', e => console.log('ERR', e.message, '\n', e.stack));
pg.on('console', m => console.log('CONSOLE', m.text().slice(0, 300)));
await pg.goto(`http://localhost:${srv.address().port}/index.html?sc=${SC}&ms=0&sm=512${process.env.QS||''}`);
await pg.waitForFunction(() => window.ready || window.err, null, { timeout: 240000 });
await pg.evaluate(([OW, OH]) => {
  window.__c = document.createElement('canvas'); window.__c.width = OW; window.__c.height = OH;
  window.__x = window.__c.getContext('2d'); window.__c3 = document.getElementById('c'); window.__cap = document.getElementById('caption');
  window.__one = (f, q) => { window.renderFrame(f);
    const x = window.__x, c = window.__c; x.clearRect(0, 0, c.width, c.height);
    x.drawImage(window.__c3, 0, 0, c.width, c.height); x.drawImage(window.__cap, 0, 0, c.width, c.height);
    const fa = window.fadeAmt ? window.fadeAmt(f) : 1;
    if (fa < 1) { x.save(); x.globalAlpha = 1 - fa; x.fillStyle = '#000'; x.fillRect(0, 0, c.width, c.height); x.restore(); }
    return c.toDataURL('image/jpeg', q); };
}, [Math.round(720 * SC), Math.round(1280 * SC)]);
for (const f of FR) {
  const t0 = Date.now();
  const d = await pg.evaluate(([f]) => window.__one(f, 0.92), [f]);
  fs.writeFileSync(path.join(outdir, `f${String(f).padStart(5, '0')}.jpg`), Buffer.from(d.split(',')[1], 'base64'));
  console.log(f, Date.now() - t0, 'ms');
}
await b.close(); srv.close();
