import { chromium as pw } from 'playwright';
import chromiumPkg from '@sparticuz/chromium';
import http from 'http'; import fs from 'fs'; import path from 'path';
const root = path.resolve('web');
const srv = http.createServer((q,s)=>{let u=decodeURIComponent(q.url.split('?')[0]); if(u==='/')u='/index.html'; const p=path.resolve(root,`.${u}`); if(!fs.existsSync(p)||!fs.statSync(p).isFile()){s.writeHead(404);return s.end();} s.writeHead(200,{'Content-Type':p.endsWith('.js')?'text/javascript':'text/html'}); fs.createReadStream(p).pipe(s);}).listen(0);
await new Promise(r=>srv.on('listening',r));
const b = await pw.launch({ executablePath: await chromiumPkg.executablePath(), headless:true, args:[...chromiumPkg.args,'--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const pg = await b.newPage({viewport:{width:1080,height:1920}});
await pg.goto(`http://localhost:${srv.address().port}/index.html?sc=1.5&ms=0&sm=512`);
await pg.waitForFunction(()=>window.ready||window.err,null,{timeout:120000});
const r = await pg.evaluate(()=>{
  const out=[]; const c=document.createElement('canvas'); c.width=1080;c.height=1920; const x=c.getContext('2d');
  for (const f of [600,610,620,630]) {
    let t0=performance.now(); window.renderFrame(f); let t1=performance.now();
    x.drawImage(document.getElementById('c'),0,0); x.drawImage(document.getElementById('caption'),0,0); let t2=performance.now();
    const d=c.toDataURL('image/jpeg',0.88); let t3=performance.now();
    out.push([Math.round(t1-t0), Math.round(t2-t1), Math.round(t3-t2), d.length]);
  }
  return out;
});
console.log(JSON.stringify(r));
await b.close(); srv.close();
