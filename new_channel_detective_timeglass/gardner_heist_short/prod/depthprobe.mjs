import { chromium as pw } from 'playwright';
import chromiumPkg from '@sparticuz/chromium';
import http from 'http'; import fs from 'fs'; import path from 'path';
const root = path.resolve('web');
const srv = http.createServer((q, s) => {
  let u = decodeURIComponent(q.url.split('?')[0]); if (u === '/') u = '/index.html';
  const p = path.resolve(root, `.${u}`); if (!fs.existsSync(p)) { s.writeHead(404); return s.end(); }
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
const r = await pg.evaluate(() => {
  window.renderFrame(3600);
  const out = [];
  window.__scene.children.forEach((o) => {
    if (!o.isMesh) return;
    if (o.material && o.material.map === null && o.userData.nd) return;
    const m = o.material;
    const kind = m && m.map && m.map.image ? (m.map.image.width === 1200 ? 'CARD' : 'tex') : 'plain';
    out.push({ kind, vis: o.visible, pos: o.position.toArray().map(v => +v.toFixed(1)), z: +o.renderOrder, ndSkip: !!o.userData.ndSkip, tr: !!m.transparent, depthW: m.depthWrite, op: m.opacity });
  });
  return out.filter(x => x.kind === 'CARD' || x.ndSkip || x.tr);
});
console.log(JSON.stringify(r, null, 0).slice(0, 1500));
await b.close(); srv.close();
