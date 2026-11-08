// HD stills renderer: usage: node render_hd.mjs <outdir> <frames:"a-b" or "1,2,3"> [sc] [quality]
// renders at 720*sc x 1280*sc physical pixels (sc=1.5 -> true 1080x1920)
import { chromium as playwrightChromium } from 'playwright';
import chromiumPkg from '@sparticuz/chromium';
import http from 'http'; import fs from 'fs'; import path from 'path';
const [,, outdir, spec, scArg = '1.5', qual = '0.94'] = process.argv;
const SC = +scArg;
const PW = Math.round(720 * SC), PH = Math.round(1280 * SC);
fs.mkdirSync(outdir, { recursive: true });
let frames = [];
for (const part of spec.split(',')) { if (part.includes('-')) { const [a, b] = part.split('-').map(Number); for (let f = a; f <= b; f++) frames.push(f); } else frames.push(+part); }
const root = path.resolve(process.env.WEB || 'web');
const srv = http.createServer((q, s) => { let urlPath; try { urlPath = decodeURIComponent(q.url.split('?')[0]); } catch { s.writeHead(400); return s.end(); } if (urlPath === '/') urlPath = '/index.html'; const p = path.resolve(root, `.${urlPath}`); if (!p.startsWith(root + path.sep) || !fs.existsSync(p) || !fs.statSync(p).isFile()) { s.writeHead(404); return s.end(); } s.writeHead(200, { 'Content-Type': p.endsWith('.js') ? 'text/javascript' : 'text/html' }); fs.createReadStream(p).on('error', () => { if (!s.headersSent) s.writeHead(500); s.end(); }).pipe(s); }).listen(0);
await new Promise(r => srv.on('listening', r));
const b = await playwrightChromium.launch({ executablePath: await chromiumPkg.executablePath(), headless: true, args: [...chromiumPkg.args, '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const pg = await b.newPage({ viewport: { width: PW, height: PH } });
pg.on('console', m => console.log('PAGE', m.text())); pg.on('pageerror', e => console.log('ERR', e.message));
await pg.goto(`http://localhost:${srv.address().port}/index.html?sc=${SC}${process.env.QS||''}${process.env.HASH || ''}`);
await pg.waitForFunction(() => window.ready || window.err, null, { timeout: 240000 });
if (await pg.evaluate(() => window.err)) { console.log('page error'); process.exit(1); }
const t0 = Date.now();
for (const f of frames) {
  if (process.env.RESUME && fs.existsSync(path.join(outdir, `f${String(f).padStart(4, '0')}.jpg`))) continue;
  const d = await pg.evaluate(([f, q, PW, PH]) => {
    window.renderFrame(f);
    const c = document.createElement('canvas'); c.width = PW; c.height = PH;
    const x = c.getContext('2d'); x.imageSmoothingQuality = 'high';
    x.drawImage(document.getElementById('c'), 0, 0, PW, PH);
    x.drawImage(document.getElementById('caption'), 0, 0, PW, PH);
    return c.toDataURL('image/jpeg', q);
  }, [f, +qual, PW, PH]);
  fs.writeFileSync(path.join(outdir, `f${String(f).padStart(4, '0')}.jpg`), Buffer.from(d.split(',')[1], 'base64'));
  console.log(`frame ${f} ok (${((Date.now() - t0) / 1000).toFixed(1)}s)`);
}
console.log(`done ${frames.length} frames at ${PW}x${PH}, ${((Date.now() - t0) / frames.length / 1000).toFixed(2)} s/frame`);
await b.close(); srv.close();
