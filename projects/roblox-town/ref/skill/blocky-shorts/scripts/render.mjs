#!/usr/bin/env node
// Blocky Shorts renderer driver — zero npm dependencies (talks to headless Chrome over the DevTools protocol).
//
//   node render.mjs check   <project>                      validate story, write build/info.json + build/events.json
//   node render.mjs preview <project> [--every 0.5|--times 1,2.5] [--scale 0.5] [--cols 6] [--out name.jpg] [--frames]
//                                                           -> build/preview/sheet.jpg (+ single frames with --frames)
//   node render.mjs frames  <project> [--fps 30] [--from N] [--to M] [--budget 280] [--workers 1] [--gpu]
//                                                           -> build/frames/00000.jpg ... (resumable; skips existing)
//
// Env: CHROME_PATH to force a browser binary.
import { spawn, execSync } from 'node:child_process';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path'; import os from 'node:os';

const SKILL = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const [cmd, projArg, ...rest] = process.argv.slice(2);
const opt = {}; for (let i = 0; i < rest.length; i++) { if (rest[i].startsWith('--')) { const k = rest[i].slice(2); const v = rest[i + 1] && !rest[i + 1].startsWith('--') ? rest[++i] : true; opt[k] = v; } }
if (!cmd || !projArg) { console.log(fs.readFileSync(new URL(import.meta.url)).toString().split('\n').slice(1, 10).join('\n')); process.exit(1); }
const PROJ = path.resolve(projArg); const BUILD = path.join(PROJ, 'build'); fs.mkdirSync(BUILD, { recursive: true });
if (!fs.existsSync(path.join(PROJ, 'story.json'))) { console.error('No story.json in ' + PROJ); process.exit(1); }

// ---------------------------------------------------------------- find chrome
export function findChrome() {
  const c = [process.env.CHROME_PATH];
  for (const n of ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'chrome', 'chrome-headless-shell', 'headless_shell']) { try { c.push(execSync(`command -v ${n}`, { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim()); } catch { } }
  c.push('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium', 'C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe');
  const home = os.homedir();
  for (const base of [path.join(home, '.cache/ms-playwright'), path.join(home, '.cache/puppeteer'), path.join(home, 'Library/Caches/ms-playwright'), '/ms-playwright', '/opt/pw-browsers']) {
    try { for (const f of walk(base, 4)) if (/(chrome|headless_shell|chrome-headless-shell|Chromium)$/.test(f) && fs.statSync(f).isFile()) c.push(f); } catch { }
  }
  return c.find(p => p && fs.existsSync(p));
}
function* walk(dir, depth) { if (depth < 0) return; for (const e of fs.readdirSync(dir, { withFileTypes: true })) { const p = path.join(dir, e.name); if (e.isDirectory()) yield* walk(p, depth - 1); else yield p; } }

// ---------------------------------------------------------------- static server: skill at /, project at /project/
const TYPES = { '.js': 'text/javascript', '.mjs': 'text/javascript', '.html': 'text/html', '.json': 'application/json', '.otf': 'font/otf', '.ttf': 'font/ttf', '.png': 'image/png', '.jpg': 'image/jpeg' };
function serve() {
  return new Promise(res => {
    const srv = http.createServer((q, r) => {
      const u = decodeURIComponent(q.url.split('?')[0]);
      const file = u.startsWith('/project/') ? path.join(PROJ, u.slice(9)) : path.join(SKILL, u);
      fs.readFile(file, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-store' }); r.end(d); });
    }).listen(0, '127.0.0.1', () => res(srv));
  });
}
// ---------------------------------------------------------------- minimal CDP client
async function getWS() { if (globalThis.WebSocket) return globalThis.WebSocket; try { return (await import('ws')).default; } catch { console.error('Need Node 22+ (built-in WebSocket) or `npm i ws`.'); process.exit(1); } }
async function launch(chrome, gpu) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'bs-chrome-'));
  const args = ['--headless=new', '--no-sandbox', '--remote-debugging-port=0', `--user-data-dir=${dir}`, '--no-first-run', '--mute-audio', '--hide-scrollbars', '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--disable-background-networking', '--disable-component-update', '--no-default-browser-check', '--disable-sync', '--ignore-gpu-blocklist', 'about:blank'];
  if (!gpu) args.unshift('--use-angle=swiftshader', '--enable-unsafe-swiftshader');
  const p = spawn(chrome, args, { stdio: ['ignore', 'ignore', 'pipe'] });
  const wsUrl = await new Promise((res, rej) => { let buf = ''; const to = setTimeout(() => rej(new Error('Chrome did not start:\n' + buf)), 30000); p.stderr.on('data', d => { buf += d; const m = buf.match(/DevTools listening on (ws:\/\/\S+)/); if (m) { clearTimeout(to); res(m[1]); } }); p.on('exit', c => rej(new Error('Chrome exited ' + c + '\n' + buf))); });
  const WS = await getWS(); const ws = new WS(wsUrl); await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
  let id = 0; const pend = new Map();
  ws.onmessage = (m) => { const msg = JSON.parse(typeof m.data === 'string' ? m.data : m.data.toString()); if (msg.id && pend.has(msg.id)) { const { res, rej } = pend.get(msg.id); pend.delete(msg.id); msg.error ? rej(new Error(msg.error.message)) : res(msg.result); } };
  const send = (method, params = {}, sessionId) => new Promise((res, rej) => { const i = ++id; pend.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params, sessionId })); });
  const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
  const evaluate = async (expr) => { const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true }, sessionId); if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text); return r.result.value; };
  const close = () => { try { ws.close(); } catch { } p.kill('SIGKILL'); try { fs.rmSync(dir, { recursive: true, force: true }); } catch { } };
  return { send, sessionId, evaluate, close };
}
async function openEngine(chrome, port, q = '') {
  const b = await launch(chrome, !!opt.gpu);
  await b.send('Page.navigate', { url: `http://127.0.0.1:${port}/engine/index.html?project=/project/${q}` }, b.sessionId);
  const t0 = Date.now();
  while (true) {
    const st = await b.evaluate('JSON.stringify({ready: !!window.READY, err: window.ENGINE_ERROR || null})').catch(() => '{}');
    const s = JSON.parse(st || '{}'); if (s.ready) break; if (s.err) { b.close(); throw new Error('Engine error: ' + s.err); }
    if (Date.now() - t0 > 180000) { b.close(); throw new Error('Engine did not become ready in 180 s'); }
    await new Promise(r => setTimeout(r, 250));
  }
  return b;
}
const save = (file, dataUrl) => fs.writeFileSync(file, Buffer.from(dataUrl.split(',')[1], 'base64'));

// ---------------------------------------------------------------- main
const chrome = findChrome();
if (!chrome) { console.error('No Chrome/Chromium found. Run scripts/setup.sh, or set CHROME_PATH.'); process.exit(2); }
const srv = await serve(); const port = srv.address().port;
const qs = (o) => Object.entries(o).filter(([, v]) => v != null).map(([k, v]) => `&${k}=${v}`).join('');
try {
  if (cmd === 'check') {
    const b = await openEngine(chrome, port, qs({ scale: .25 }));
    const info = await b.evaluate('ENGINE.info()'); const ev = await b.evaluate('ENGINE.events()');
    fs.writeFileSync(path.join(BUILD, 'info.json'), JSON.stringify(info, null, 1)); fs.writeFileSync(path.join(BUILD, 'events.json'), JSON.stringify(ev, null, 1));
    console.log(`OK  duration ${info.duration.toFixed(2)}s  ${info.shots.length} shots  ${info.lines.length} lines  timing: ${info.timing}  sound events: ${ev.length}`);
    info.shots.forEach(s => console.log(`  shot ${s.i + 1}  ${s.start.toFixed(2)}–${s.end.toFixed(2)}s  [${s.set}]  ${s.lines.join(' / ')}`));
    if (info.warnings.length) { console.log('\nWARNINGS:'); info.warnings.forEach(w => console.log('  - ' + w)); } else console.log('\nNo warnings.');
    b.close();
  } else if (cmd === 'preview') {
    const scale = Number(opt.scale || .5); const fps = Number(opt.fps || 30);
    const b = await openEngine(chrome, port, qs({ scale, fps, q: .85 }));
    const info = await b.evaluate('ENGINE.info()');
    let times = opt.times ? String(opt.times).split(',').map(Number) : null;
    if (!times) { const every = Number(opt.every || 0); times = every ? [] : info.shots.flatMap(s => [s.start + .05, (s.start + s.end) / 2, s.end - .08]); if (every) for (let t = 0; t < info.duration; t += every) times.push(+t.toFixed(3)); }
    const dir = path.join(BUILD, 'preview'); fs.mkdirSync(dir, { recursive: true });
    const cols = Number(opt.cols || 6); const name = opt.out || 'sheet.jpg';
    save(path.join(dir, name), await b.evaluate(`ENGINE.sheet(${JSON.stringify(times)}, ${cols}, ${Number(opt.thumb || 240)})`));
    if (opt.frames) for (const t of times) save(path.join(dir, `t${t.toFixed(2).padStart(6, '0')}.jpg`), await b.evaluate(`ENGINE.frameAt(${t})`));
    b.close(); console.log(`contact sheet (${times.length} frames): ${path.join(dir, name)}`);
    const w = info.warnings; if (w.length) { console.log('WARNINGS:'); w.forEach(x => console.log('  - ' + x)); }
  } else if (cmd === 'frames') {
    const fps = Number(opt.fps || 0) || undefined; const workers = Number(opt.workers || 1); const budget = Number(opt.budget || 0) * 1000;
    const dir = path.join(BUILD, 'frames'); fs.mkdirSync(dir, { recursive: true });
    const probe = await openEngine(chrome, port, qs({ fps, scale: .25 })); const info = await probe.evaluate('ENGINE.info()'); probe.close();
    fs.writeFileSync(path.join(BUILD, 'render.json'), JSON.stringify({ fps: info.fps, frames: info.frames, duration: info.duration, width: info.width, height: info.height }));
    const from = Number(opt.from || 0), to = Math.min(Number(opt.to ?? info.frames), info.frames);
    const todo = []; for (let i = from; i < to; i++) if (!fs.existsSync(path.join(dir, String(i).padStart(5, '0') + '.jpg'))) todo.push(i);
    console.log(`${info.frames} frames @ ${info.fps}fps (${info.duration.toFixed(2)}s). ${todo.length} to render, ${workers} worker(s).`);
    const T0 = Date.now(); let done = 0, stopped = false;
    await Promise.all(Array.from({ length: workers }, async (_, w) => {
      const b = await openEngine(chrome, port, qs({ fps }));
      for (let k = w; k < todo.length; k += workers) {
        if (budget && Date.now() - T0 > budget) { stopped = true; break; }
        const i = todo[k]; save(path.join(dir, String(i).padStart(5, '0') + '.jpg'), await b.evaluate(`ENGINE.frame(${i})`)); done++;
        if (done % 30 === 0) { const el = (Date.now() - T0) / 1000; console.log(`  ${done}/${todo.length}  ${el.toFixed(0)}s elapsed, ~${(el / done * (todo.length - done)).toFixed(0)}s left`); }
      }
      b.close();
    }));
    const left = todo.length - done;
    console.log(stopped || left ? `PAUSED: ${left} frames left — run the same command again to continue.` : `DONE: all ${info.frames} frames in ${dir}`);
  } else if (cmd === 'eval') {
    const b = await openEngine(chrome, port, qs({ scale: .25 })); console.log(JSON.stringify(await b.evaluate(String(opt.js)), null, 1)); b.close();
  } else { console.error('unknown command ' + cmd); process.exit(1); }
} catch (e) { console.error(String(e.stack || e)); process.exitCode = 1; }
srv.close();
