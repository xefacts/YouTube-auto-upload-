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
await pg.goto(`http://localhost:${srv.address().port}/index.html?sc=0.42&ms=0&sm=256`);
await pg.waitForFunction(() => window.ready || window.err, null, { timeout: 240000 });
const d = await pg.evaluate(() => {
  window.renderFrame(3600);
  // paint the two cards flat red, keep geometry
  const T = window.__THREE;
  window.__scene.children.forEach((o) => {
    if (!o.isMesh) return;
    const m = o.material;
    if (!m || !m.map || !m.map.image || m.map.image.width !== 1200) return;
    m.alphaTest = 0; m.needsUpdate = true;
  });
  window.renderFrame(3600);
  return document.getElementById('c').toDataURL('image/jpeg', 0.9);
});
fs.writeFileSync('/tmp/redcard.jpg', Buffer.from(d.split(',')[1], 'base64'));
await b.close(); srv.close(); console.log('ok');
