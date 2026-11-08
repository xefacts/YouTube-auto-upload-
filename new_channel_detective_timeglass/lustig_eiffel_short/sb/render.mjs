// usage: node render.mjs <outdir> <frames: "a-b" or "1,2,3"> [step] [quality]
import { chromium as playwrightChromium } from 'playwright'; import chromiumPkg from '@sparticuz/chromium'; import http from 'http'; import fs from 'fs'; import path from 'path';
const [,, outdir, spec, step = '1', qual = '0.96'] = process.argv;
fs.mkdirSync(outdir, { recursive: true });
let frames = [];
for (const part of spec.split(',')) { if (part.includes('-')) { const [a, b] = part.split('-').map(Number); for (let f = a; f <= b; f += +step) frames.push(f); } else frames.push(+part); }
const root = path.resolve(process.env.WEB || 'web');
const srv = http.createServer((q, s) => { let urlPath; try { urlPath = decodeURIComponent(q.url.split('?')[0]); } catch { s.writeHead(400); return s.end(); } if (urlPath === '/') urlPath = '/index.html'; const p = path.resolve(root, `.${urlPath}`); if (!p.startsWith(root + path.sep) || !fs.existsSync(p) || !fs.statSync(p).isFile()) { s.writeHead(404); return s.end(); } s.writeHead(200, { 'Content-Type': p.endsWith('.js') ? 'text/javascript' : 'text/html' }); fs.createReadStream(p).on('error', () => { if (!s.headersSent) s.writeHead(500); s.end(); }).pipe(s); }).listen(0);
await new Promise(r => srv.on('listening', r));
const b = await playwrightChromium.launch({ executablePath: await chromiumPkg.executablePath(), headless: true, args: [...chromiumPkg.args, '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const pg = await b.newPage({ viewport: { width: 720, height: 1280 } });
pg.on('console', m => console.log('PAGE', m.text())); pg.on('pageerror', e => console.log('ERR', e.message));
await pg.goto(`http://localhost:${srv.address().port}/index.html${process.env.HASH||""}`);
await pg.waitForFunction(() => window.ready || window.err, null, { timeout: 180000 });
if (await pg.evaluate(() => window.err)) { console.log('page error'); process.exit(1); }
const t0 = Date.now();
for (const f of frames) {
  if (process.env.RESUME && fs.existsSync(path.join(outdir, `f${String(f).padStart(4, '0')}.jpg`))) continue;
  const d = await pg.evaluate(([f, q]) => { if (window.location.hash==="#nd") window.DEBUG_ND=1; if (window.location.hash==="#e") window.DEBUG_E=1; window.renderFrame(f); const c=document.createElement('canvas');c.width=720;c.height=1280;const x=c.getContext('2d');x.drawImage(document.getElementById('c'),0,0);x.drawImage(document.getElementById('caption'),0,0);return c.toDataURL('image/jpeg',q); }, [f, +qual]);
  fs.writeFileSync(path.join(outdir, `f${String(f).padStart(4, '0')}.jpg`), Buffer.from(d.split(',')[1], 'base64'));
  if ((f + 1) % 50 === 0) console.log(`rendered through frame ${f + 1}/${frames.at(-1) + 1}`);
}
console.log(`done ${frames.length} frames, ${((Date.now() - t0) / frames.length / 1000).toFixed(2)} s/frame`);
await b.close(); srv.close();
