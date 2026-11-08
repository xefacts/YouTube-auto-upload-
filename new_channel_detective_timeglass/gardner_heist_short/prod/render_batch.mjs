// batched renderer: composites at csc*720 x csc*1280 in-page, writes JPEGs
// usage: node render_batch.mjs <outdir> <from> <to> [batch] [sc] [csc] [quality]
import { chromium as pw } from 'playwright';
import chromiumPkg from '@sparticuz/chromium';
import http from 'http'; import fs from 'fs'; import path from 'path';

const [,, outdir, fromArg, toArg, batchArg = '24', scArg = '0.85', cscArg = '1.5', qual = '0.93'] = process.argv;
const F0 = +fromArg, F1 = +toArg, BATCH = +batchArg, SC = +scArg, CSC = +cscArg, STEP = +(process.env.STEP || 1);
fs.mkdirSync(outdir, { recursive: true });
const root = path.resolve(process.env.WEB || 'web');
const srv = http.createServer((q, s) => {
  let u; try { u = decodeURIComponent(q.url.split('?')[0]); } catch { s.writeHead(400); return s.end(); }
  if (u === '/') u = '/index.html';
  const p = path.resolve(root, `.${u}`);
  if (!p.startsWith(root + path.sep) || !fs.existsSync(p) || !fs.statSync(p).isFile()) { s.writeHead(404); return s.end(); }
  const type = p.endsWith('.js') ? 'text/javascript' : p.endsWith('.html') ? 'text/html' : 'application/octet-stream';
  s.writeHead(200, { 'Content-Type': type });
  fs.createReadStream(p).on('error', () => { if (!s.headersSent) s.writeHead(500); s.end(); }).pipe(s);
}).listen(0);
await new Promise(r => srv.on('listening', r));
const drop = /^--(in-process-gpu|single-process|no-zygote|use-gl|use-angle|enable-unsafe-swiftshader|enable-features|disable-features|ignore-gpu-blocklist|disable-dev-shm-usage)$/;
const baseArgs = chromiumPkg.args.filter(a => !drop.test(a));
const b = await pw.launch({ executablePath: await chromiumPkg.executablePath(), headless: true,
  args: [...baseArgs, '--use-gl=swiftshader', '--enable-unsafe-swiftshader'] });
const pg = await b.newPage({ viewport: { width: 720, height: 1280 } });
pg.on('pageerror', e => console.log('ERR', e.message));
pg.on('console', m => { const t = m.text(); if (/error/i.test(t)) console.log('PAGE', t.slice(0, 200)); });
await pg.goto(`http://localhost:${srv.address().port}/index.html?sc=${SC}&csc=${CSC}&ms=0&sm=512${process.env.QS || ''}`);
await pg.waitForFunction(() => window.ready || window.err, null, { timeout: 300000 });
const err = await pg.evaluate(() => window.err || null);
if (err) { console.log('page error:', err); process.exit(1); }
await pg.evaluate(([OW, OH]) => {
  window.__c = document.createElement('canvas'); window.__c.width = OW; window.__c.height = OH;
  window.__x = window.__c.getContext('2d', { willReadFrequently: true }); window.__x.imageSmoothingQuality = 'high';
  window.__c3 = document.getElementById('c'); window.__cap = document.getElementById('caption');
  window.__batch = (list, q) => {
    const out = []; let i = 0;
    return new Promise((resolve) => {
      const step = () => {
        if (i >= list.length) return resolve(out);
        window.renderFrame(list[i++]);
        const x = window.__x, c = window.__c;
        x.clearRect(0, 0, c.width, c.height);
        x.drawImage(window.__c3, 0, 0, c.width, c.height);
        x.drawImage(window.__cap, 0, 0, c.width, c.height);
        const fa = window.fadeAmt ? window.fadeAmt(list[i - 1]) : 1;
        if (fa < 1) { x.save(); x.globalAlpha = 1 - fa; x.fillStyle = '#000'; x.fillRect(0, 0, c.width, c.height); x.restore(); }
        c.toBlob((bl) => bl.arrayBuffer().then((ab) => { out.push(new Uint8Array(ab)); step(); }), 'image/jpeg', q);
      };
      step();
    });
  };
}, [Math.round(720 * CSC), Math.round(1280 * CSC)]);
const t0 = Date.now(); let n = 0;
for (let start = F0; start <= F1; start += BATCH) {
  const list = [];
  for (let f = start; f <= Math.min(start + BATCH - 1, F1); f++) if (f % STEP === 0) list.push(f);
  const todo = list.filter(f => !(process.env.RESUME && fs.existsSync(path.join(outdir, `f${String(f).padStart(5, '0')}.jpg`))));
  if (!todo.length) continue;
  const arr = await pg.evaluate(([l, q]) => window.__batch(l, q), [todo, +qual]);
  todo.forEach((f, i) => fs.writeFileSync(path.join(outdir, `f${String(f).padStart(5, '0')}.jpg`), Buffer.from(arr[i])));
  n += todo.length;
  const el = (Date.now() - t0) / 1000;
  const fps = n / el, eta = (F1 - start - list.length + todo.length + (list.length - todo.length)) / Math.max(fps, 0.01);
  if (n % (BATCH * 4) < BATCH) console.log(`[${F0}-${F1}] ${n}/${F1 - F0 + 1}  ${fps.toFixed(2)} f/s  eta ${eta.toFixed(0)}s`);
}
console.log(`DONE ${F0}-${F1} ${n} frames ${((Date.now() - t0) / 1000 / n).toFixed(2)} s/frame`);
await b.close(); srv.close();
