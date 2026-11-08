import { chromium as pw } from 'playwright';
import chromiumPkg from '@sparticuz/chromium';
import http from 'http'; import fs from 'fs'; import path from 'path';
const FR = process.argv.slice(2).map(Number);
const root = path.resolve('web');
const srv = http.createServer((q, s) => {
  let u = decodeURIComponent(q.url.split('?')[0]); if (u === '/') u = '/index.html';
  const p = path.resolve(root, `.${u}`);
  if (!fs.existsSync(p)) { s.writeHead(404); return s.end(); }
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
for (const f of FR) {
  const r = await pg.evaluate((f) => {
    window.renderFrame(f);
    const out = [];
    window.__scene.children.forEach((o) => {
      if (!o.isMesh) return;
      const m = o.material;
      if (!m || !m.map || !m.map.image || m.map.image.width !== 1200) return;
      const g = m.map.image.getContext('2d');
      const d = g.getImageData(0, 0, 1200, 2000).data;
      let nz = 0; for (let i = 3; i < d.length; i += 4000) if (d[i] > 40) nz++;
      out.push({ vis: o.visible, pos: o.position.toArray().map(v => +v.toFixed(2)), sc: +o.scale.x.toFixed(2), rot: o.rotation.toArray().slice(0, 3).map(v => +(+v).toFixed(2)), alphaNZ: nz, op: m.opacity, tr: m.transparent, order: o.renderOrder });
    });
    return out;
  }, f);
  console.log(f, JSON.stringify(r));
}
await b.close(); srv.close();
