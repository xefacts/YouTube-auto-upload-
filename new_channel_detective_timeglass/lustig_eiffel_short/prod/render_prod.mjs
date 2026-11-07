// production stills renderer: 3D at sc (720p) + captions at csc (1080p), composited to 1080x1920 JPEG
// usage: node render_prod.mjs <outdir> <"a-b"> [sc] [csc] [quality]
import { chromium as playwrightChromium } from 'playwright';
import chromiumPkg from '@sparticuz/chromium';
import http from 'http'; import fs from 'fs'; import path from 'path';
const [,, outdir, spec, scArg = '1', cscArg = '1.5', qual = '0.92'] = process.argv;
const SC = +scArg, CSC = +cscArg;
const PW = Math.round(720 * SC), PH = Math.round(1280 * SC);
const OW = Math.round(720 * CSC), OH = Math.round(1280 * CSC);
fs.mkdirSync(outdir, { recursive: true });
let frames;
if (spec.includes('-')) { const [a, b] = spec.split('-').map(Number); frames = []; for (let f = a; f <= b; f++) frames.push(f); }
else frames = spec.split(',').map(Number);
const a = frames[0], b = frames[frames.length - 1];
const root = path.resolve(process.env.WEB || 'web');
const srv = http.createServer((q, s) => { let u; try { u = decodeURIComponent(q.url.split('?')[0]); } catch { s.writeHead(400); return s.end(); } if (u === '/') u = '/index.html'; const p = path.resolve(root, `.${u}`); if (!p.startsWith(root + path.sep) || !fs.existsSync(p) || !fs.statSync(p).isFile()) { s.writeHead(404); return s.end(); } s.writeHead(200, { 'Content-Type': p.endsWith('.js') ? 'text/javascript' : 'text/html' }); fs.createReadStream(p).on('error', () => { if (!s.headersSent) s.writeHead(500); s.end(); }).pipe(s); }).listen(0);
await new Promise(r => srv.on('listening', r));
const b2 = await playwrightChromium.launch({ executablePath: await chromiumPkg.executablePath(), headless: true, args: [...chromiumPkg.args, '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const pg = await b2.newPage({ viewport: { width: 720, height: 1280 } });
pg.on('console', m => { const t = m.text(); if (/ERR|error/i.test(t)) console.log('PAGE', t); });
pg.on('pageerror', e => console.log('ERR', e.message));
await pg.goto(`http://localhost:${srv.address().port}/index.html?sc=${SC}&csc=${CSC}&ms=0&sm=512${process.env.QS || ""}`);
await pg.waitForFunction(() => window.ready || window.err, null, { timeout: 240000 });
if (await pg.evaluate(() => window.err)) { console.log('page error'); process.exit(1); }
await pg.evaluate(([PW, PH, OW, OH]) => {
  window.__c = document.createElement('canvas'); window.__c.width = OW; window.__c.height = OH;
  window.__x = window.__c.getContext('2d'); window.__x.imageSmoothingQuality = 'high';
  window.__c3 = document.getElementById('c'); window.__cap = document.getElementById('caption');
}, [PW, PH, OW, OH]);
const t0 = Date.now(); let n = 0;
for (const f of frames) {
  const name = path.join(outdir, `f${String(f).padStart(5, '0')}.jpg`);
  if (process.env.RESUME && fs.existsSync(name)) continue;
  const d = await pg.evaluate(([f, q]) => {
    window.renderFrame(f);
    const x = window.__x, c = window.__c;
    x.clearRect(0, 0, c.width, c.height);
    x.drawImage(window.__c3, 0, 0, c.width, c.height);
    x.drawImage(window.__cap, 0, 0, c.width, c.height);
    return c.toDataURL('image/jpeg', q);
  }, [f, +qual]);
  fs.writeFileSync(name, Buffer.from(d.split(',')[1], 'base64'));
  n++;
  if (n % 40 === 0) { const el = (Date.now() - t0) / 1000; console.log(`[${a}-${b}] ${n}/${frames.length}  ${(el / n).toFixed(2)} s/frame  eta ${Math.round((frames.length - n) * el / n)}s`); }
}
console.log(`DONE ${a}-${b}  ${n} frames  ${((Date.now() - t0) / n / 1000).toFixed(2)} s/frame`);
await b2.close(); srv.close();
