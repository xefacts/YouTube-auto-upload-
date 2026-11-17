// Blocky Shorts engine: reads story.json (+ build/timing.json) and renders deterministic frames.
// window.ENGINE = {
// window.ENGINE = { info(), events(), frame(i), frameAt(t), sheet(times), debugCam(t) }
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { clamp, lerp, inv, E, V, toV, deg, rng, hash, noise1 } from './util.js';
import { makeCharacter, randomSpec, applyFace, setTint, PRESETS } from './characters.js';
import { EXPRESSIONS } from './faces.js';
import { REST, BASES, ACTIONS, blend, applyPose, clapTimes, slamTimes } from './poses.js';
import { SETS } from './sets.js';
import { makeProp, PROPS } from './props.js';
import * as OV from './overlays.js';

const Q = new URLSearchParams(location.search);
const PROJECT = (Q.get('project') || '/project/').replace(/\/?$/, '/');
const warnings = []; const warn = (m) => { if (!warnings.includes(m)) warnings.push(m); };

async function getJSON(url, optional) { const r = await fetch(url); if (!r.ok) { if (optional) return null; throw new Error('Cannot load ' + url); } return r.json(); }
const story = await getJSON(PROJECT + 'story.json');
const timingFile = await getJSON(PROJECT + 'build/timing.json', true);
const style = story.style || {};
const FPS = Number(Q.get('fps') || story.fps || 30);
const SCALE = Number(Q.get('scale') || 1);
const W = Math.round((story.width || 720) * SCALE), H = Math.round((story.height || 1280) * SCALE);
const ASPECT = W / H;

// ============================================================== timeline (lines + shots)
const normalize = s => String(s).toLowerCase().replace(/\*/g, '').replace(/[^a-z0-9À-￿]+/g, ' ').trim();
const LINES = []; // {text, shot, i, start, end}
story.shots.forEach((sh, si) => { (sh.lines || []).forEach(l => { const o = typeof l === 'string' ? { text: l } : { ...l }; o.shot = si; o.i = LINES.length; LINES.push(o); }); });
export function estimateLine(text, speed = 1) {
  const p = OV.plain(text); if (!p.trim()) return .5;
  const words = p.trim().split(/\s+/).length; let d = .1 + words * .25;
  if (/[.!?]["']?$/.test(p.trim())) d += .12; if (/(\.\.\.|…)$/.test(p.trim())) d += .2; if (/,$/.test(p.trim())) d += .05;
  return Math.max(.32, d) / speed;
}
{
  const tl = timingFile && Array.isArray(timingFile.lines) && timingFile.lines.length === LINES.length ? timingFile.lines : null;
  if (timingFile && !tl) warn(`build/timing.json has ${timingFile.lines?.length} lines but story has ${LINES.length}; using estimated timing. Re-run timing.py.`);
  let t = story.lead || 0;
  story.shots.forEach((sh, si) => {
    const ls = LINES.filter(l => l.shot === si);
    ls.forEach(l => { if (tl) { l.start = tl[l.i].start; l.end = tl[l.i].end; } else { l.start = t; l.end = t + (l.dur ?? estimateLine(l.text || '', story.speed || 1)); t = l.end + (l.pause || 0); } });
    if (!tl) t += ls.length ? (sh.hold || 0) : (sh.dur || 1);
  });
}
const SHOTS = story.shots.map((sh, si) => ({ ...sh, si }));
SHOTS.forEach((s, si) => { s.lines_ = LINES.filter(l => l.shot === si); });
SHOTS.forEach((s, si) => {
  s.start = si ? SHOTS[si - 1].end : 0;
  const nxt = SHOTS[si + 1], L = s.lines_;
  if (L.length) {
    if (!nxt) s.end = L[L.length - 1].end + (story.tail ?? .6);
    else if (nxt.lines_.length) s.end = nxt.lines_[0].start;
    else s.end = L[L.length - 1].end + (s.hold || 0);
  } else {
    const later = SHOTS.slice(si + 1).find(x => x.lines_.length);
    s.end = s.start + (s.dur || 1);
    if (timingFile && later && later === nxt) s.end = Math.max(s.start + .2, later.lines_[0].start);
    if (!nxt) s.end = s.start + (s.dur || 1);
  }
  s.end = Math.max(s.end, s.start + .1);
});
{ const last = SHOTS[SHOTS.length - 1]; if (timingFile?.total) last.end = Math.max(last.end, timingFile.total); }
const DURATION = SHOTS[SHOTS.length - 1].end;
const FRAMES = Math.round(DURATION * FPS);
// caption windows: from line start (or shot start for a shot's first line) to the next line / shot end
SHOTS.forEach(s => s.lines_.forEach((l, k) => { l.capStart = k === 0 ? s.start : l.start; l.capEnd = k < s.lines_.length - 1 ? s.lines_[k + 1].start : s.end; }));

// time reference resolver (relative to a shot)
function T(ref, shot, def) {
  if (ref == null) return def ?? shot.start;
  if (typeof ref === 'number') return shot.start + ref;
  if (typeof ref === 'object' && ref.line != null) { const l = shot.lines_[ref.line] || LINES[ref.line]; return l ? l.start : shot.start; }
  const m = String(ref).match(/^(.*?)\s*([+-]\s*\d*\.?\d+)?$/); const key = m[1].trim(); const off = m[2] ? parseFloat(m[2].replace(/\s/g, '')) : 0;
  if (key === 'start' || key === '') return shot.start + off;
  if (key === 'end') return shot.end + off;
  if (key === 'mid') return (shot.start + shot.end) / 2 + off;
  if (/^#\d+$/.test(key)) { const l = shot.lines_[+key.slice(1)]; if (l) return l.start + off; }
  if (/^\d*\.?\d+$/.test(key)) return shot.start + parseFloat(key) + off;
  const n = normalize(key);
  let l = shot.lines_.find(x => normalize(x.text || '') === n) || shot.lines_.find(x => normalize(x.text || '').includes(n));
  if (!l) { l = LINES.find(x => normalize(x.text || '') === n); if (l) warn(`time ref "${key}" used in shot ${shot.si + 1} belongs to shot ${l.shot + 1}`); }
  if (!l) { warn(`time ref "${key}" not found in shot ${shot.si + 1}; using shot start`); return shot.start + off; }
  return l.start + off;
}
const D = (spec, shot, t0, def) => spec.until != null ? Math.max(.05, T(spec.until, shot) - t0) : spec.dur != null ? spec.dur : def;

// ============================================================== renderer / world
const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.NeutralToneMapping;
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, ASPECT, .1, 2000); scene.add(camera);
const camLight = new THREE.PointLight('#9fb4ff', 0, 30, 1); camera.add(camLight);
const composer = new EffectComposer(renderer, new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: SCALE < 1 ? 0 : 4 }));
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), .3, .5, .92); composer.addPass(bloom); composer.addPass(new OutputPass());

const skyU = { top: { value: new THREE.Color() }, hor: { value: new THREE.Color() }, bot: { value: new THREE.Color() } };
const sky = new THREE.Mesh(new THREE.SphereGeometry(900, 32, 16), new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, fog: false, uniforms: skyU,
  vertexShader: 'varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }',
  fragmentShader: 'uniform vec3 top,hor,bot; varying vec3 vP; void main(){ float h=vP.y; vec3 c = h>0. ? mix(hor,top,pow(clamp(h*1.6,0.,1.),.55)) : mix(hor,bot,clamp(-h*4.,0.,1.)); gl_FragColor=vec4(c,1.); }' }));
sky.renderOrder = -1; scene.add(sky);
const stars = (() => { const g = new THREE.BufferGeometry(); const r = rng(77); const p = []; for (let i = 0; i < 1500; i++) { const th = r() * Math.PI * 2, ph = Math.acos(r() * .95); p.push(800 * Math.sin(ph) * Math.cos(th), 800 * Math.cos(ph), 800 * Math.sin(ph) * Math.sin(th)); } g.setAttribute('position', new THREE.Float32BufferAttribute(p, 3)); return new THREE.Points(g, new THREE.PointsMaterial({ color: '#cfe0ff', size: 2.2 * SCALE, sizeAttenuation: false, fog: false })); })();
scene.add(stars);
const moon = new THREE.Mesh(new THREE.SphereGeometry(18, 24, 16), new THREE.MeshBasicMaterial({ color: '#f4f1d0', fog: false })); moon.position.set(-260, 300, -600); scene.add(moon);
const clouds = new THREE.Group(); scene.add(clouds);
{ const r = rng(5); const cm = new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: 1, emissive: '#dfe9ff', emissiveIntensity: .35, fog: false });
  for (let i = 0; i < 12; i++) { const g = new THREE.Group(); const a = r() * Math.PI * 2; const d = 380 + r() * 200; g.position.set(Math.cos(a) * d, 70 + r() * 70, Math.sin(a) * d); for (let j = 0; j < 5; j++) { const s = new THREE.Mesh(new THREE.SphereGeometry(18 + r() * 14, 10, 8), cm); s.position.set((j - 2) * 20 + r() * 8, r() * 10, r() * 10); s.scale.y = .6; g.add(s); } g.lookAt(0, g.position.y, 0); clouds.add(g); }
  clouds.userData.mat = cm; }
scene.fog = new THREE.Fog('#a8d0ff', 70, 320);
const hemi = new THREE.HemisphereLight('#cfe6ff', '#6f6a5c', 1.6); scene.add(hemi);
const sun = new THREE.DirectionalLight('#fff3dc', 3.2); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -.0004; sun.shadow.normalBias = .03; sun.shadow.radius = 3; scene.add(sun, sun.target);
const nightFill = new THREE.PointLight('#6b8cff', 0, 40, 1.2); scene.add(nightFill);

// ============================================================== sets
const SETCACHE = {};
function getSet(name, opts = {}) {
  const key = name + JSON.stringify(opts);
  if (SETCACHE[key]) return SETCACHE[key];
  const f = SETS[name]; if (!f) { warn(`unknown set "${name}" — using studio`); return getSet('studio', opts); }
  const s = f(opts); s.name = name; s.group.visible = false; scene.add(s.group); SETCACHE[key] = s; return s;
}
const spotOf = (set, name) => set.spots?.[name];

// ============================================================== cast
const CAST = {};
function castMember(name) {
  if (CAST[name]) return CAST[name];
  let spec = story.cast?.[name];
  if (!spec) { if (PRESETS[name]) spec = { preset: name }; else spec = randomSpec(hash(name)); }
  const c = makeCharacter(spec, name); c.root.visible = false; scene.add(c.root); CAST[name] = c; return c;
}
const NPCS = [];
function npc(i) { while (NPCS.length <= i) { const c = makeCharacter(randomSpec(1000 + NPCS.length * 7919 + (story.seed || 0)), 'npc' + NPCS.length); c.root.visible = false; scene.add(c.root); NPCS.push(c); } return NPCS[i]; }

// ============================================================== build per-shot plans
const yawToward = (from, to) => Math.atan2(to.x - from.x, to.z - from.z) * 180 / Math.PI;
const FACING = { front: 0, camera: 0, back: 180, away: 180, left: -90, right: 90 };
function resolvePos(spec, set, fallback) {
  if (Array.isArray(spec)) return toV(spec);
  if (typeof spec === 'string') { const sp = spotOf(set, spec); if (sp) return toV(sp.pos); warn(`spot "${spec}" not found in set ${set.name}`); }
  return fallback ? fallback.clone() : V();
}
function makePlans() {
  for (const sh of SHOTS) {
    sh.set = getSet(sh.set || 'studio', sh.setOpts || {});
    sh.actors = {};
    const castEntries = Object.entries(sh.cast || {});
    // pass 1: positions
    for (const [name, a] of castEntries) {
      const c = castMember(name); const sp = typeof a.spot === 'string' ? spotOf(sh.set, a.spot) : null;
      const pos = a.at ? toV(a.at) : sp ? toV(sp.pos) : resolvePos(null, sh.set, V(0, 0, 6));
      const base = a.base || (sp?.seat != null ? 'sit' : sp?.bed != null ? 'lie' : 'idle');
      sh.actors[name] = { c, a, pos, yaw: 0, base, baseOpts: { seat: a.seat ?? sp?.seat, bed: a.bed ?? sp?.bed, recline: a.recline ?? sp?.recline }, spotYaw: sp?.yaw, ph: (hash(name) % 1000) / 160 };
    }
    // pass 2: facing + timeline
    for (const [name, A] of Object.entries(sh.actors)) {
      const a = A.a; const f = a.face ?? (A.spotYaw != null ? A.spotYaw : 'front');
      A.yaw = faceYaw(f, A.pos, sh, A.yaw);
      // timeline events
      A.moves = []; A.turns = []; A.acts = []; A.exprs = [{ t: -1, e: a.expr || A.c.spec.expr || 'smile' }]; A.bases = [{ t: -1, b: A.base, o: A.baseOpts }]; A.vis = [];
      let cur = A.pos.clone(), curYaw = A.yaw;
      const list = (a.do || []).map(d => ({ ...d, name: d.do || d.a || d.action }));
      list.forEach(d => d._t = T(d.at, sh));
      list.sort((x, y) => x._t - y._t);
      for (const d of list) {
        const t0 = d._t; const n = d.name;
        if (d.expr) A.exprs.push({ t: t0, e: d.expr });
        if (!n) continue;
        if (['walk', 'run', 'sneak', 'move', 'slide'].includes(n)) {
          const to = d.to ? resolveTarget(d.to, sh, cur) : cur.clone().add(V(0, 0, 3)); const dist = to.distanceTo(cur);
          const sp = n === 'run' ? 9 : n === 'sneak' ? 2.2 : n === 'slide' ? 8 : 4.6; const dur = D(d, sh, t0, Math.max(.25, dist / sp));
          const dir = yawToward(cur, to);
          A.moves.push({ t0, t1: t0 + dur, from: cur.clone(), to, kind: n === 'move' ? 'walk' : n, yaw: dist > .05 ? dir : curYaw, endYaw: d.face != null ? faceYaw(d.face, to, sh, dir) : (dist > .05 ? dir : curYaw) });
          cur = to; curYaw = A.moves[A.moves.length - 1].endYaw; continue;
        }
        if (n === 'turn') { const y = faceYaw(d.to ?? d.face ?? 'front', cur, sh, curYaw); A.turns.push({ t0, t1: t0 + (d.dur ?? .3), from: curYaw, to: y }); curYaw = y; continue; }
        if (['sit', 'stand', 'lie', 'idle', 'float'].includes(n)) { A.bases.push({ t: t0, b: n === 'stand' ? 'idle' : n, o: { seat: d.seat ?? A.baseOpts.seat, bed: d.bed ?? A.baseOpts.bed, recline: d.recline } }); continue; }
        if (n === 'appear' || n === 'vanish' || n === 'hide' || n === 'show') { A.vis.push({ t: t0, on: n === 'appear' || n === 'show', pop: n === 'appear' || n === 'vanish' }); continue; }
        if (n === 'expr') { A.exprs.push({ t: t0, e: d.face || d.expr || 'smile' }); continue; }
        if (!ACTIONS[n]) { warn(`unknown action "${n}" for ${name} in shot ${sh.si + 1}`); continue; }
        const defDur = { clap: 1.0, wave: 1.2, bow: .6, jump: .55, slam: .5, shrug: .8, yawn: 1.4, fall: .6, faint: .7, spin: .6, nod: .6, headshake: .7, stretch: 1.2, talk: 1.5 }[n] ?? 1.0;
        A.acts.push({ n, t0, dur: D(d, sh, t0, defDur), p: d, fade: d.fade ?? (['fall', 'faint', 'spin', 'jump'].includes(n) ? .02 : .12), hold: !!d.hold });
      }
      A.exprs.sort((x, y) => x.t - y.t);
      if (a.hold) attachHeld(A, a.hold);
    }
    // extras
    sh.walkers = 0; sh.crowd = null;
    const ex = sh.extras || {};
    if (ex.walkers) sh.walkers = ex.walkers;
    if (ex.crowd) sh.crowd = planCrowd(ex.crowd, sh);
    // props
    sh.props = (sh.props || []).map(p => { const pr = makeProp(p.type, p); if (!pr) { warn(`unknown prop "${p.type}"`); return null; } pr.obj.visible = false; scene.add(pr.obj); const pos = resolvePos(p.at ?? p.spot, sh.set, V(0, 0, 4)); return { pr, spec: p, pos, yaw: p.yaw || 0, mv: p.move ? { to: resolveTarget(p.move.to, sh, pos), t0: T(p.move.at ?? 0, sh), dur: p.move.dur ?? 1 } : null }; }).filter(Boolean);
    sh.fx = (sh.fx || []).map(f => ({ ...f, _t: T(f.at, sh) }));
    sh.cam = sh.camera || {};
  }
}
function faceYaw(f, pos, sh, cur = 0) {
  if (typeof f === 'number') return f;
  if (Array.isArray(f)) return yawToward(pos, V(f[0], 0, f[f.length - 1]));
  if (FACING[f] != null) return FACING[f];
  if (typeof f === 'string' && sh.actors?.[f]) return yawToward(pos, sh.actors[f].pos);
  if (typeof f === 'string' && spotOf(sh.set, f)) return yawToward(pos, toV(spotOf(sh.set, f).pos));
  return cur;
}
function resolveTarget(to, sh, cur) {
  if (Array.isArray(to)) return toV(to);
  if (typeof to === 'string') { if (sh.actors[to]) { const p = sh.actors[to].pos.clone(); const dir = cur.clone().sub(p).setY(0).normalize(); return p.add(dir.multiplyScalar(2.6)); } const sp = spotOf(sh.set, to); if (sp) return toV(sp.pos); }
  if (to && typeof to === 'object' && to.dx != null) return cur.clone().add(V(to.dx || 0, 0, to.dz || 0));
  warn(`unknown move target ${JSON.stringify(to)}`); return cur.clone();
}
const HELD = [];
function attachHeld(A, h) {
  const spec = typeof h === 'string' ? { type: h } : h; const pr = makeProp(spec.type, spec); if (!pr) { warn(`unknown held prop ${spec.type}`); return; }
  const arm = spec.arm === 'L' ? A.c.armL : A.c.armR; const hold = pr.hold || { pos: [0, 0, .4], rot: [0, 0, 0] };
  pr.obj.position.set(...hold.pos); pr.obj.rotation.set(...hold.rot); arm.userData.hand.add(pr.obj); pr.obj.visible = false;
  HELD.push(pr); A.held = pr; A.heldArm = spec.arm === 'L' ? 'aL' : 'aR'; A.holdPose = spec.pose !== false;
}
function planCrowd(cs, sh) {
  const n = cs.n || 24, rows = cs.rows || Math.ceil(n / 7), per = Math.ceil(n / rows), sp = cs.spacing || 2.7;
  const center = toV(cs.center || sh.set.crowd?.center || [0, 0, 14]); const yaw = cs.yaw ?? sh.set.crowd?.yaw ?? 180; const r = rng(7 + (cs.seed || 0));
  const members = []; let i = 0;
  const fw = V(Math.sin(deg(yaw)), 0, Math.cos(deg(yaw))), side = V(Math.cos(deg(yaw)), 0, -Math.sin(deg(yaw)));
  for (let row = 0; row < rows; row++) for (let k = 0; k < per && i < n; k++, i++) {
    let x = (k - (per - 1) / 2) * sp + (row % 2) * sp * .45 + (r() - .5) * .5;
    if (cs.aisle !== false && Math.abs(x) < 1.7) x = Math.sign(x || 1) * 1.7 + x * .3;
    const p = center.clone().add(side.clone().multiplyScalar(x)).add(fw.clone().multiplyScalar(-row * 2.4 + (r() - .5) * .5));
    members.push({ c: npc(i + (cs.offset || 0)), pos: p, yaw: yaw + (r() - .5) * 8, ph: r() * 6 });
  }
  const acts = (Array.isArray(cs.do) ? cs.do : []).map(d => ({ n: d.do || d.a, t0: T(d.at, sh), dur: D(d, sh, T(d.at, sh), 1e3), p: d, fade: .12, expr: d.expr })).filter(a => ACTIONS[a.n] || warn(`unknown crowd action ${a.n}`));
  return { members, acts, expr: cs.expr || 'smile', tint: cs.tint };
}

// ============================================================== per-frame actor evaluation
function evalActor(A, t, sh) {
  const c = A.c; let pos = A.pos.clone(), yaw = A.yaw, moving = null;
  for (const m of A.moves) { if (t < m.t0) break; const k = clamp((t - m.t0) / (m.t1 - m.t0)); pos = m.from.clone().lerp(m.to, m.kind === 'slide' ? E.out(k) : k); if (t < m.t1) { moving = m; yaw = m.yaw; } else yaw = m.endYaw; }
  for (const tr of A.turns) { if (t < tr.t0) break; let d = ((tr.to - tr.from + 540) % 360) - 180; yaw = tr.from + d * E.inout(clamp((t - tr.t0) / (tr.t1 - tr.t0))); }
  let bs = A.bases[0]; for (const b of A.bases) if (t >= b.t) bs = b;
  const P = REST();
  blend(P, (BASES[bs.b] || BASES.idle)(t, A.ph, bs.o || {}), 1);
  if (moving) blend(P, (BASES[moving.kind === 'run' ? 'run' : 'walk'])(t, A.ph), clamp(Math.min((t - moving.t0) / .12, (moving.t1 - t) / .12)) || 1);
  if (moving?.kind === 'sneak') blend(P, ACTIONS.sneak(t - moving.t0, 0, {}), 1);
  let faceOverride = null, talk = false;
  for (const a of A.acts) {
    const lt = t - a.t0; if (lt < 0 || (lt > a.dur + a.fade && !a.hold)) continue;
    const w = a.hold && lt > a.dur ? 1 : Math.min(clamp(lt / Math.max(.01, a.fade)), clamp((a.dur - lt) / Math.max(.01, a.fade) + (lt > a.dur ? 0 : 0)));
    const part = ACTIONS[a.n](lt, clamp(lt / a.dur), a.p, { t, dur: a.dur, ph: A.ph });
    blend(P, part, a.hold && lt > a.dur ? 1 : w);
    if (part._face && w > .5) faceOverride = part._face; if (part._talk && w > .2) talk = true;
  }
  if (A.held && A.holdPose && !A.acts.some(a => t >= a.t0 && t <= a.t0 + a.dur)) { const arm = A.heldArm; P[arm][0] = lerp(P[arm][0], -1.0, .85); }
  // say bubbles drive talking too
  if (sh.fx.some(f => f.say != null && (f.on === A.c.name) && t >= f._t && t <= f._t + (f.dur ?? 1.4))) talk = true;
  // visibility pop
  let vis = !(A.a.hidden || (A.vis.length && A.vis[0].on)), sc = 1; for (const v of A.vis) if (t >= v.t) { vis = v.on; if (v.pop) { const k = clamp((t - v.t) / .22); if (v.on) sc = Math.max(.001, E.back(k)); else if (k < 1) { vis = true; sc = Math.max(.001, 1 - E.in(k)); } } }
  P.scale = sc;
  applyPose(c, P);
  c.root.position.copy(pos); c.root.rotation.set(0, deg(yaw), 0); c.root.visible = vis;
  // face
  let ex = A.exprs[0].e; for (const e of A.exprs) if (t >= e.t) ex = e.e;
  if (faceOverride) ex = faceOverride;
  const blinkP = 2.6 + (A.ph % 1.3); const bt = (t + A.ph) % blinkP; const blink = A.a.blink !== false && bt < .1;
  const mouthOpen = talk && (Math.sin(t * 17 + A.ph) + .5 * Math.sin(t * 29) > .1);
  applyFace(c, ex, { blink, mouthOpen });
  const tint = EXPRESSIONS[ex]?.tint; setTint(c, tint || A.a.tint, tint ? .5 : A.a.tint ? .4 : 0);
  if (A.held) A.held.obj.visible = vis;
  A.now = { pos, yaw };
}
function evalCrowd(cr, t) {
  for (const m of cr.members) {
    const c = m.c; c.root.visible = true; const P = REST(); blend(P, BASES.idle(t, m.ph), 1); let ex = cr.expr, talk = false;
    for (const a of cr.acts) { const lt = t - a.t0 - m.ph * .012; if (lt < 0 || lt > a.dur + a.fade) continue; const w = Math.min(clamp(lt / a.fade), clamp((a.dur - lt) / a.fade)); const part = ACTIONS[a.n](lt + m.ph, clamp(lt / a.dur), a.p, {}); blend(P, part, w); if (a.expr && lt >= 0) ex = a.expr; if (part._face) ex = part._face; if (part._talk) talk = true; }
    applyPose(c, P); c.root.position.copy(m.pos); c.root.rotation.set(0, deg(m.yaw), 0);
    applyFace(c, ex, { blink: ((t + m.ph) % 3.1) < .1, mouthOpen: talk && Math.sin(t * 15 + m.ph) > 0 });
    const tint = EXPRESSIONS[ex]?.tint || cr.tint; setTint(c, tint, tint ? .5 : 0);
  }
}
function evalWalkers(n, t, set, offset = 0) {
  const z = set.walkZone || { x: [-14, 14], z: [-10, 2] };
  for (let i = 0; i < n; i++) {
    const c = npc(i + offset); const r = rng(500 + i); const zz = z.z[0] + r() * (z.z[1] - z.z[0]); const dir = r() < .5 ? 1 : -1; const sp = 2.2 + r() * 1.2; const span = z.x[1] - z.x[0];
    const x = z.x[0] + (((r() * span + dir * sp * t) % span) + span) % span;
    const P = REST(); blend(P, BASES.walk(t, r()), 1); applyPose(c, P);
    c.root.position.set(x, set.name === 'street' ? .3 : 0, zz); c.root.rotation.set(0, dir * Math.PI / 2, 0); c.root.visible = true; applyFace(c, 'smile', {}); setTint(c, null, 0);
  }
}

// ============================================================== camera
const SHOTSIZE = { extreme: { S: 2.6, k: 'head', o: -.1 }, close: { S: 4.0, k: 'head', o: -.55 }, medium: { S: 6.8, k: 'head', o: -1.5 }, cowboy: { S: 8.6, k: 'head', o: -2.4 }, full: { S: 10.5, k: 'feet', o: 3.3 }, wide: { S: 16, k: 'feet', o: 4.8 }, establishing: { S: 28, k: 'feet', o: 7 } };
const FROM = { front: 0, 'front-left': -35, 'front-right': 35, left: -80, right: 80, behind: 180, back: 180, 'behind-left': -150, 'behind-right': 150 };
function anchorOf(name, sh, t) {
  const A = sh.actors[name]; if (!A) return null;
  if (!A.headOff) { // pose at shot start to measure head offset
    evalActor(A, sh.start + .001, sh); A.c.root.updateMatrixWorld(true); const hp = new THREE.Vector3(); A.c.neck.localToWorld(hp.set(0, .6, 0)); A.headOff = hp.sub(A.c.root.position); evalActor(A, t, sh); A.nowT = t;
  }
  const pos = A.now && A.nowT === t ? A.now.pos : null;
  const p = pos || A.pos; return { feet: p.clone(), head: p.clone().add(A.headOff), yaw: A.yaw };
}
function targetsOf(on, sh, t) {
  const list = Array.isArray(on) && typeof on[0] !== 'number' ? on : [on];
  const out = [];
  for (const o of list) {
    if (o == null) continue;
    if (Array.isArray(o)) { const p = toV(o); out.push({ feet: p.clone().setY(p.y - 2.6), head: p, yaw: 0 }); continue; }
    if (o === 'crowd' && sh.crowd) { const ms = sh.crowd.members; const c = ms.reduce((a, m) => a.add(m.pos), V()).multiplyScalar(1 / ms.length); out.push({ feet: c, head: c.clone().add(V(0, 4.6, 0)), yaw: sh.crowd.members[0].yaw, spread: 10 }); continue; }
    const a = anchorOf(o, sh, t); if (a) { out.push(a); continue; }
    const sp = spotOf(sh.set, o); if (sp) { const p = toV(sp.pos); out.push({ feet: p, head: p.clone().add(V(0, 4.6, 0)), yaw: sp.yaw || 0 }); continue; }
    warn(`camera target "${o}" not found in shot ${sh.si + 1}`);
  }
  if (!out.length) out.push({ feet: V(0, 0, 5), head: V(0, 4.6, 5), yaw: 0 });
  return out;
}
function frameShot(spec, sh, t, fovIn) {
  const tg = targetsOf(spec.on ?? Object.keys(sh.actors)[0] ?? 'crowd', sh, t);
  const feet = tg.reduce((a, x) => a.add(x.feet), V()).multiplyScalar(1 / tg.length);
  const head = tg.reduce((a, x) => a.add(x.head), V()).multiplyScalar(1 / tg.length);
  let spread = 0; for (const a of tg) for (const b of tg) spread = Math.max(spread, Math.hypot(a.feet.x - b.feet.x, a.feet.z - b.feet.z)); spread = Math.max(spread, tg[0].spread || 0);
  const size = SHOTSIZE[spec.shot || (tg.length > 1 ? 'full' : 'full')] || SHOTSIZE.full;
  let S = size.S; if (tg.length > 1 || spread) S = Math.max(S, (spread + 4.6) / ASPECT);
  const fov = fovIn ?? spec.fov ?? 50;
  const d = (S / 2) / Math.tan(deg(fov / 2));
  const look = size.k === 'head' ? head.clone().add(V(0, size.o, 0)) : feet.clone().add(V(0, Math.min(size.o, S * .36), 0));
  if (size.k === 'head' && tg.length > 1) look.y = head.y + size.o;
  const yaw = (spec.yaw ?? (tg.length === 1 ? tg[0].yaw : (tg[0].yaw + (tg[1]?.yaw ?? tg[0].yaw)) / 2 * 0)) + (typeof spec.from === 'number' ? spec.from : FROM[spec.from || 'front'] ?? 0) + (spec.side ?? 10);
  const ang = spec.angle || 'eye';
  let dy = { eye: .06 * d, low: -.42 * d, high: .5 * d, top: 1.1 * d, worm: -look.y + .5 }[ang] ?? .06 * d;
  let camY = look.y + dy; if (ang === 'low') camY = Math.max(feet.y + .7, camY);
  const horiz = Math.sqrt(Math.max(d * d * .25, d * d - (camY - look.y) ** 2));
  const pos = V(look.x + Math.sin(deg(yaw)) * horiz, camY, look.z + Math.cos(deg(yaw)) * horiz);
  if (spec.look) look.add(toV(spec.look)); if (spec.offset) pos.add(toV(spec.offset));
  return { pos, look, fov, S };
}
function applyMove(F, spec, u) {
  const move = spec.move || 'push'; const a = spec.amount ?? ({ push: .22, pull: .22, static: .04, 'zoom-in': .2, 'zoom-out': .2, 'crane-up': .5, 'crane-down': .5, 'track-left': .5, 'track-right': .5, 'orbit-left': .5, 'orbit-right': .5, handheld: 1 }[move] ?? .2);
  const e = (E[spec.ease || 'inout'] || E.inout)(u); const off = F.pos.clone().sub(F.look);
  const perp = V(off.z, 0, -off.x).normalize();
  switch (move) {
    case 'push': case 'static': case 'drift': F.pos = F.look.clone().add(off.multiplyScalar(lerp(1 + a / 2, 1 - a / 2, e))); break;
    case 'pull': F.pos = F.look.clone().add(off.multiplyScalar(lerp(1 - a / 2, 1 + a / 2, e))); break;
    case 'zoom-in': F.fov *= lerp(1, 1 - a, e); break;
    case 'zoom-out': F.fov *= lerp(1 - a, 1, e); break;
    case 'crane-up': case 'crane-down': { const k = a * F.S * .5 * (move === 'crane-up' ? 1 : -1); F.pos.y += lerp(-k, k, e); F.look.y += lerp(-k, k, e) * .25; F.pos.y = Math.max(.4, F.pos.y); break; }
    case 'track-left': case 'track-right': { const k = a * F.S * .9 * (move === 'track-right' ? 1 : -1); const o = perp.multiplyScalar(lerp(-k, k, e)); F.pos.add(o); F.look.add(o); break; }
    case 'orbit-left': case 'orbit-right': { const ang = deg(a * 45) * (move === 'orbit-right' ? 1 : -1) * lerp(-1, 1, e); const c = Math.cos(ang), s = Math.sin(ang); F.pos = F.look.clone().add(V(off.x * c + off.z * s, off.y, -off.x * s + off.z * c)); break; }
    case 'handheld': break;
    default: warn(`unknown camera move "${move}"`);
  }
  return F;
}
function cameraFor(sh, t) {
  const spec = sh.cam; const u = inv(sh.start, sh.end, t);
  if (spec.raw) { const a = spec.raw.from, b = spec.raw.to || a; const k = (E[spec.ease || 'inout'])(u); const F = { pos: toV(a.pos).lerp(toV(b.pos), k), look: toV(a.look).lerp(toV(b.look), k), fov: lerp(a.fov || 50, b.fov || a.fov || 50, k), S: 6 }; return finishCam(F, sh, t, spec); }
  let F = applyMove(frameShot(spec, sh, t), spec, u);
  if (spec.whip) { const w = spec.whip, t0 = T(w.at, sh), dur = w.dur ?? .26; const B = applyMove(frameShot({ ...spec, ...w, on: w.to ?? w.on, move: w.move || 'push' }, sh, t), { ...spec, move: w.move || 'push' }, u); const k = E.inout(inv(t0, t0 + dur, t)); if (k > 0) { F.pos.lerp(B.pos, k); F.look.lerp(B.look, k); F.fov = lerp(F.fov, B.fov, k); F.fov *= 1 + .12 * Math.sin(k * Math.PI); } }
  if (spec.crash) { const c = spec.crash, t0 = T(c.at, sh), dur = c.dur ?? .36; const C = frameShot({ ...spec, on: c.on ?? spec.on, shot: c.shot || 'close', angle: 'eye', from: c.from ?? spec.from }, sh, t); const k = E.in(inv(t0, t0 + dur, t)); if (k > 0) { const y = lerp(F.pos.y, C.pos.y, Math.pow(k, 3)); F.pos.lerp(C.pos, k); F.pos.y = Math.max(y, C.pos.y); F.look.lerp(C.look, k); F.fov = lerp(F.fov, C.fov * .95, k); if (t > t0 + dur) { const st = t - t0 - dur; F.pos.add(V(0, 0, 0)); F.settle = .06 * Math.exp(-st * 10) * Math.sin(st * 60); } } }
  return finishCam(F, sh, t, spec);
}
function finishCam(F, sh, t, spec) {
  let fov = F.fov, shake = 0;
  for (const f of sh.fx) {
    if (f.punch != null && t >= f._t) fov *= 1 - (f.punch === true ? .2 : f.punch) * E.out(clamp((t - f._t) / .13));
    if (f.shake != null && t >= f._t) { const dur = f.dur ?? .28, k = (t - f._t) / dur; if (k < 1) shake += (f.shake === true ? .1 : f.shake) * Math.pow(1 - k, 2); }
  }
  if (sh.cam.move === 'handheld' || sh.cam.handheld) F.pos.add(V(noise1(t * 1.7, 1) * .08, noise1(t * 1.3, 2) * .06, 0));
  camera.position.copy(F.pos); camera.fov = fov; camera.updateProjectionMatrix();
  if (shake) { camera.position.x += Math.sin(t * 97.3) * shake + Math.sin(t * 41.1) * shake * .6; camera.position.y += Math.sin(t * 83.7 + 1) * shake; }
  if (F.settle) camera.position.y += F.settle;
  camera.lookAt(F.look); if (shake) camera.rotateZ(Math.sin(t * 61.7) * shake * .04);
  if (spec.roll) camera.rotateZ(deg(spec.roll));
  // shadows follow the subject
  const span = clamp(F.S * 1.6, 10, 40); sun.target.position.copy(F.look).setY(0); sun.position.copy(sun.target.position).add(curSunDir.clone().multiplyScalar(40));
  const sc = sun.shadow.camera; sc.left = -span; sc.right = span; sc.top = span; sc.bottom = -span; sc.near = 1; sc.far = 120; sc.updateProjectionMatrix();
  return F;
}

// ============================================================== moods
let curSunDir = V(14, 26, 18).normalize(); let curMood = null, curSetForMood = null;
const MOODS = {
  day: { top: '#1548d6', hor: '#8cc3ff', bot: '#6aa8f0', fog: ['#a6cdff', 70, 320], hemi: ['#d4e8ff', '#77705e', 1.7], sun: ['#fff2d8', 3.3, [14, 26, 18]], stars: 0, clouds: 1, bloom: [.28, .95], exp: 1.0 },
  sunset: { top: '#2e2a78', hor: '#ff9a5c', bot: '#d97a50', fog: ['#f0a070', 60, 260], hemi: ['#ffd2b0', '#5a4050', 1.25], sun: ['#ffb070', 2.8, [-22, 10, 14]], stars: 0, clouds: 1, bloom: [.4, .85], exp: 1.0 },
  night: { top: '#010208', hor: '#0a1636', bot: '#050b1e', fog: ['#060c22', 30, 200], hemi: ['#2a3f8a', '#0a0d18', .9], sun: ['#7f9cff', .55, [-10, 26, 12]], stars: 1, clouds: 0, bloom: [.55, .72], exp: 1.05 },
};
function setMood(mood, set) {
  if (mood === curMood && set === curSetForMood) return; curMood = mood; curSetForMood = set;
  const m = MOODS[mood] || MOODS.day; if (!MOODS[mood]) warn(`unknown mood "${mood}" (use day, sunset, night)`);
  skyU.top.value.set(m.top); skyU.hor.value.set(m.hor); skyU.bot.value.set(m.bot);
  scene.fog.color.set(m.fog[0]); scene.fog.near = m.fog[1]; scene.fog.far = m.fog[2];
  hemi.color.set(m.hemi[0]); hemi.groundColor.set(m.hemi[1]); hemi.intensity = m.hemi[2] * (set.interior ? .8 : 1);
  sun.color.set(m.sun[0]); sun.intensity = m.sun[1] * (set.interior ? .55 : 1); curSunDir = V(...m.sun[2]).normalize();
  stars.visible = !!m.stars && !set.noSky; moon.visible = mood === 'night' && !set.noSky; clouds.visible = !!m.clouds && !set.noSky; clouds.userData.mat.emissive.set(mood === 'sunset' ? '#ffb090' : '#dfe9ff');
  sky.visible = !set.noSky; scene.fog.far = set.noSky ? 2000 : m.fog[2]; scene.background = set.noSky ? null : null;
  bloom.strength = m.bloom[0]; bloom.threshold = m.bloom[1]; renderer.toneMappingExposure = m.exp;
  camLight.intensity = mood === 'night' ? (set.interior ? 5 : 7) : 0;
  const nl = set.nightLight; if (mood === 'night' && nl) { nightFill.position.set(...nl.pos); nightFill.color.set(nl.color); nightFill.intensity = nl.intensity; } else nightFill.intensity = 0;
  set.setMood?.(mood);
}
function moodAt(sh, t) {
  let m = sh.mood || 'day';
  for (const f of sh.fx) {
    if (f.mood && t >= f._t) m = f.mood;
    if (f.flicker && t >= f._t) { const until = f.until != null ? T(f.until, sh) : sh.end; if (t < until) { const seq = f.flicker, every = f.every || .22; m = seq[Math.floor((t - f._t) / every) % seq.length]; } else m = f.end || f.flicker[f.flicker.length - 1]; }
  }
  return m;
}

// ============================================================== scene state per frame
let lastShot = null;
const bulbs = new Map();
function stageFrame(t) {
  const sh = SHOTS.find(s => t >= s.start && t < s.end) || SHOTS[SHOTS.length - 1];
  if (lastShot !== sh) {
    for (const s of SHOTS) { s.set.group.visible = false; s.props.forEach(p => p.pr.obj.visible = false); }
    for (const c of Object.values(CAST)) c.root.visible = false; for (const c of NPCS) c.root.visible = false;
    for (const b of bulbs.values()) b.obj.visible = false; for (const p of HELD) p.obj.visible = false;
    sh.set.group.visible = true; lastShot = sh;
  }
  for (const A of Object.values(sh.actors)) { evalActor(A, t, sh); A.nowT = t; }
  // NPCs: hide all then show the ones in use (walkers + crowd)
  for (const c of NPCS) c.root.visible = false;
  if (sh.walkers) evalWalkers(sh.walkers, t, sh.set, sh.crowd ? sh.crowd.members.length : 0);
  if (sh.crowd) evalCrowd(sh.crowd, t);
  for (const p of sh.props) { let pos = p.pos.clone(); if (p.mv) { const k = E.inout(inv(p.mv.t0, p.mv.t0 + p.mv.dur, t)); pos.lerp(p.mv.to, k); } p.pr.obj.position.copy(pos); p.pr.obj.rotation.y = deg(p.yaw); p.pr.obj.visible = true; p.pr.update?.(t); }
  sh.set.update?.(t);
  for (const A of Object.values(sh.actors)) A.held?.update?.(t);
  // 3D bulbs
  for (const f of sh.fx) if (f.bulb) { const key = sh.si + ':' + f.bulb + ':' + f._t; if (!bulbs.has(key)) { const b = makeProp('bulb'); scene.add(b.obj); bulbs.set(key, b); } const b = bulbs.get(key); const A = sh.actors[f.bulb]; if (!A) { warn(`bulb target ${f.bulb} missing`); continue; } const on = t >= f._t; b.obj.visible = on; if (on) { const hp = A.c.neck.localToWorld(V(0, 2.1, 0)); const k = inv(f._t, f._t + .45, t); b.obj.position.copy(hp); b.obj.position.y += .25 * Math.sin((t - f._t) * 9) * (1 - inv(f._t, f._t + .6, t)); b.obj.scale.setScalar(Math.max(.001, E.elastic(k) * .72)); b.obj.rotation.z = .25 * Math.sin((t - f._t) * 14) * (1 - inv(f._t, f._t + .6, t)); } }
  setMood(moodAt(sh, t), sh.set);
  const F = cameraFor(sh, t);
  scene.updateMatrixWorld(true);
  return { sh, F };
}

// ============================================================== compositor
const out = document.createElement('canvas'); out.width = W; out.height = H; const ctx = out.getContext('2d');
const tmp = document.createElement('canvas'); tmp.width = W; tmp.height = H; const tctx = tmp.getContext('2d');
const grade = `saturate(${style.saturate ?? 1.18}) contrast(${style.contrast ?? 1.06}) brightness(${style.brightness ?? 1})`;
const toScreen = (v) => { const p = v.clone().project(camera); return { x: (p.x + 1) / 2 * W, y: (1 - p.y) / 2 * H, z: p.z }; };
const handsOf = (A) => A.c.armL.localToWorld(V(0, -1.9, 0)).add(A.c.armR.localToWorld(V(0, -1.9, 0))).multiplyScalar(.5);
const headOf = (A) => A.c.neck.localToWorld(V(0, 1.25, 0));
function blurWindows(sh) { const w = []; const c = sh.cam; if (c.whip) { const t0 = T(c.whip.at, sh); w.push([t0 - .02, t0 + (c.whip.dur ?? .26) + .02]); } if (c.crash) { const t0 = T(c.crash.at, sh); w.push([t0, t0 + (c.crash.dur ?? .36)]); } if (sh.blur) w.push([T(sh.blur[0], sh), T(sh.blur[1], sh)]); return w; }

function frame(i) {
  const t = i / FPS; const sh0 = SHOTS.find(s => t >= s.start && t < s.end) || SHOTS[SHOTS.length - 1];
  const blurOn = blurWindows(sh0).some(([a, b]) => t >= a && t <= b) && SCALE >= 1;
  ctx.filter = grade; ctx.globalAlpha = 1;
  if (blurOn) { const N = style.blurSamples || 10, shut = (1 / FPS) * .9; for (let j = 0; j < N; j++) { const tj = clamp(t + (j / (N - 1) - .5) * shut, sh0.start, sh0.end - 1e-4); stageFrame(tj); composer.render(); ctx.globalAlpha = 1 / (j + 1); ctx.drawImage(renderer.domElement, 0, 0); } ctx.globalAlpha = 1; }
  else { stageFrame(t); composer.render(); ctx.drawImage(renderer.domElement, 0, 0); }
  const { sh } = stageFrame(t); // restore exact state for overlay projections
  ctx.filter = 'none';
  // transition in
  const age = t - sh.start; const tin = typeof sh.in === 'string' ? { type: sh.in } : (sh.in || {});
  if (tin.type === 'zoom' && age < .18) { tctx.drawImage(out, 0, 0); const k = 1 - age / .18; for (let j = 1; j <= 5; j++) { const s = 1 + .05 * j * k; ctx.globalAlpha = .22 * k; ctx.drawImage(tmp, W / 2 - W * s / 2, H / 2 - H * s / 2, W * s, H * s); } ctx.globalAlpha = 1; }
  if (tin.type === 'whip' && age < .14) { tctx.drawImage(out, 0, 0); const k = 1 - age / .14; for (let j = 1; j <= 6; j++) { ctx.globalAlpha = .2 * k; ctx.drawImage(tmp, -j * 24 * k, 0); } ctx.globalAlpha = 1; }
  if (tin.type === 'glitch' && age < .16) { tctx.drawImage(out, 0, 0); const r = rng(Math.floor(t * 60)); for (let j = 0; j < 9; j++) { const y = r() * H, h = 10 + r() * 60, dx = (r() - .5) * 60; ctx.drawImage(tmp, 0, y, W, h, dx, y, W, h); } ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = .35; ctx.drawImage(tmp, 8, 0); ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1; }
  // 2D impact shake for stamps
  for (const f of sh.fx) if (f.stamp != null) { const a = t - f._t; if (a >= .1 && a < .28) { tctx.drawImage(out, 0, 0); const k = 14 * Math.pow(1 - (a - .1) / .18, 2); ctx.drawImage(tmp, Math.sin(t * 190) * k - W * .02, Math.cos(t * 170) * k - H * .02, W * 1.04, H * 1.04); } }
  OV.vignette(ctx, W, H, style.vignette ?? .42);
  const S2 = SCALE; ctx.save(); ctx.scale(S2, S2); const W2 = W / S2, H2 = H / S2; const scr = (v) => { const p = toScreen(v); return { x: p.x / S2, y: p.y / S2 }; };
  // per-actor action overlays (clap bursts)
  for (const A of Object.values(sh.actors)) for (const a of A.acts) { if (a.n === 'clap' && a.p.burst !== false && (a.p.burst || style.clapBursts)) for (const tt of clapTimes(a.t0, a.dur, a.p.rate || 4.5).slice(0, a.p.burst === 'all' ? 99 : 2)) OV.drawBurst(ctx, t, tt, scr(handsOf(A))); }
  for (const f of sh.fx) {
    const A = f.on ? sh.actors[f.on] : null;
    if (f.burst) { const B = sh.actors[f.burst]; if (B) OV.drawBurst(ctx, t, f._t, scr(handsOf(B))); }
    if (f.sparkle) { const B = sh.actors[f.sparkle]; const p = B ? headOf(B).add(V(0, f.sparkle && sh.fx.some(x => x.bulb === f.sparkle) ? 1.4 : .2, 0)) : toV(f.sparkle); OV.drawSparkles(ctx, t, f._t, scr(p)); }
    if (f.glint) { const B = sh.actors[f.glint]; const p = B ? B.c.neck.localToWorld(V(.5, .9, .7)) : toV(f.glint); OV.drawGlint(ctx, t, f._t, scr(p)); }
    if (f.icon && A) OV.drawFloatIcon(ctx, t, f._t, f.dur ?? 1.2, scr(headOf(A)), f.icon, f.size || 90);
    if (f.icon && !A && f.pos) OV.drawFloatIcon(ctx, t, f._t, f.dur ?? 1.2, { x: f.pos[0] * W2, y: f.pos[1] * H2 }, f.icon, f.size || 110);
    if (f.say != null && A) OV.drawBubble(ctx, W2, H2, t, f._t, f.dur ?? 1.4, scr(headOf(A)), f.say, f);
  }
  for (const f of sh.fx) if (f.stamp != null) OV.drawStamp(ctx, W2, H2, t, f._t, typeof f.stamp === 'string' ? { text: f.stamp } : f.stamp);
  for (const f of sh.fx) if (f.sign != null) { const o = typeof f.sign === 'string' ? { text: f.sign } : f.sign; const until = f.until != null ? T(f.until, sh) : 1e9; if (t < until) OV.drawSign(ctx, W2, H2, t, f.instant ? f._t - 1 : f._t, o); }
  // captions
  if (sh.captions !== false && style.captions !== false) { const l = sh.lines_.find(l => t >= l.capStart && t < l.capEnd && l.text && !l.nocap); if (l) OV.drawCaption(ctx, W2, H2, OV.parseCaption(l.text), t - l.capStart, style.caption || {}); }
  for (const f of sh.fx) if (f.title) OV.drawTitle(ctx, W2, H2, t, f._t, f.dur ?? 1.0, typeof f.title === 'string' ? { text: f.title, style: f.style, bg: f.bg, color: f.color, size: f.size } : f.title);
  // flashes / fades
  if (tin.type === 'flash') OV.flash(ctx, W2, H2, 1 - clamp(age / .15));
  if (tin.type === 'fade') OV.flash(ctx, W2, H2, 1 - clamp(age / (tin.dur || .3)), '#000');
  const tout = typeof sh.out === 'string' ? { type: sh.out } : (sh.out || {}); if (tout.type === 'fade') OV.flash(ctx, W2, H2, clamp((t - (sh.end - (tout.dur || .3))) / (tout.dur || .3)), '#000');
  for (const f of sh.fx) { if (f.flash && t >= f._t) OV.flash(ctx, W2, H2, 1 - clamp((t - f._t) / .15), f.color || '#ffffff'); if (f.fade && t >= f._t) OV.flash(ctx, W2, H2, f.fade === 'out' ? clamp((t - f._t) / (f.dur || .4)) : 1 - clamp((t - f._t) / (f.dur || .4)), '#000'); }
  if (style.progress) OV.progressBar(ctx, W2, H2, t / DURATION, style.highlight);
  ctx.restore();
  return out.toDataURL('image/jpeg', Number(Q.get('q') || .93));
}

// ============================================================== sound events (for the mixer)
function events() {
  const ev = []; const add = (t, sfx, gain = 1, why = '') => { if (sfx && t >= 0 && t <= DURATION) ev.push({ t: +t.toFixed(3), sfx, gain, why }); };
  const pick = (f, def, g = 1) => { if (f.sfx === false) return; add(f._t + (f.sfxOffset || 0), f.sfx || def, (f.gain ?? 1) * g, Object.keys(f).find(k => !k.startsWith('_') && k !== 'at') || ''); };
  SHOTS.forEach((sh, si) => {
    if (si > 0 && style.cutSfx) add(sh.start, style.cutSfx === true ? 'tick' : style.cutSfx, style.cutGain ?? .35, 'cut');
    const tin = typeof sh.in === 'string' ? sh.in : sh.in?.type; if (tin) add(sh.start, { flash: 'flash', zoom: 'whoosh', whip: 'whoosh', glitch: 'glitch', fade: null }[tin], .8, 'transition');
    let prevMood = sh.mood || 'day';
    for (const f of sh.fx) {
      if (f.mood) { pick(f, f.mood === 'night' ? 'night_hit' : 'day_chime', f.mood === 'night' ? 1 : .7); prevMood = f.mood; }
      if (f.flicker) { const until = f.until != null ? T(f.until, sh) : sh.end, every = f.every || .22; for (let tt = f._t, k = 0; tt < until - .01; tt += every, k++) add(tt, f.sfx || (f.flicker[k % f.flicker.length] === 'night' ? 'night_hit' : 'day_chime'), .55, 'flicker'); }
      if (f.punch != null) pick(f, 'swish', .7); if (f.shake != null && (f.shake === true || f.shake >= .08)) pick(f, 'impact', clamp((f.shake === true ? .1 : f.shake) * 7, .4, 1));
      if (f.sign != null && !f.instant) pick(f, 'pop'); if (f.stamp != null) pick(f, 'stamp'); if (f.bulb) pick(f, 'ding'); if (f.sparkle || f.glint) pick(f, 'sparkle', .8);
      if (f.icon) pick(f, { zzz: 'snore', exclaim: 'alert', question: 'boop', heart: 'pop_small', anger: 'grr' }[f.icon] || 'pop_small', .8);
      if (f.say != null) pick(f, 'blip', .5); if (f.title) pick(f, (f.style || f.title.style) === 'banner' ? 'pop' : 'whoosh', .8);
      if (f.flash) pick(f, 'flash'); if (f.sfx && !['mood', 'flicker', 'punch', 'shake', 'sign', 'stamp', 'bulb', 'sparkle', 'glint', 'icon', 'say', 'title', 'flash'].some(k => f[k] != null)) add(f._t, f.sfx, f.gain ?? 1, 'sfx');
    }
    void prevMood;
    if (sh.cam.whip) add(T(sh.cam.whip.at, sh), 'whoosh', 1, 'whip');
    if (sh.cam.crash) { const t0 = T(sh.cam.crash.at, sh); add(t0 - .05, 'whoosh_long', 1, 'crash'); add(t0 + (sh.cam.crash.dur ?? .36), 'impact', .8, 'crash'); }
    for (const A of Object.values(sh.actors)) {
      for (const a of A.acts) {
        if (a.p.sfx === false) continue; const g = a.p.gain ?? 1;
        if (a.n === 'clap') clapTimes(a.t0, a.dur, a.p.rate || 4.5).forEach(tt => add(tt, a.p.sfx || 'clap', .9 * g, 'clap'));
        if (a.n === 'slam') slamTimes(a.t0, a.dur, a.p.times || 1).forEach(tt => add(tt, a.p.sfx || 'impact', .9 * g, 'slam'));
        if (a.n === 'jump') add(a.t0, a.p.sfx || 'boing', .8 * g, 'jump');
        if (a.n === 'fall' || a.n === 'faint') add(a.t0 + a.dur * .62, a.p.sfx || 'thud', g, a.n);
        if (a.n === 'spin') add(a.t0, a.p.sfx || 'whoosh', .7 * g, 'spin');
        if (a.p.sfx && !['clap', 'slam', 'jump', 'fall', 'faint', 'spin'].includes(a.n)) add(a.t0, a.p.sfx, g, a.n);
      }
      for (const v of A.vis) if (v.pop) add(v.t, v.on ? 'pop' : 'poof', .8, 'appear');
      for (const m of A.moves) if (m.kind === 'slide') add(m.t0, 'whoosh', .6, 'slide');
    }
    if (sh.crowd) for (const a of sh.crowd.acts) { if (a.n === 'clap' && a.p.sfx !== false) add(a.t0, a.p.sfx || 'applause', a.p.gain ?? 1, 'crowd clap'); if (a.n === 'cheer' && a.p.sfx !== false) add(a.t0, a.p.sfx || 'applause', .8, 'crowd cheer'); if (a.p.sfx && !['clap', 'cheer'].includes(a.n)) add(a.t0, a.p.sfx, a.p.gain ?? 1, 'crowd'); }
  });
  ev.sort((a, b) => a.t - b.t); return ev;
}

// ============================================================== boot
makePlans();
// warm-up: compile shaders for every shot
for (const sh of SHOTS) { stageFrame((sh.start + sh.end) / 2); renderer.compile(scene, camera); }
lastShot = null;
await document.fonts.load("800 50px 'BS Bold'"); await document.fonts.load("900 50px 'BS Black'");
window.ENGINE = {
  debugCam: (t) => { const { sh, F } = stageFrame(t); return { shot: sh.si, pos: F.pos.toArray().map(v => +v.toFixed(2)), look: F.look.toArray().map(v => +v.toFixed(2)), fov: +F.fov.toFixed(1), S: F.S }; },
  info: () => ({ fps: FPS, frames: FRAMES, duration: DURATION, width: story.width || 720, height: story.height || 1280, renderWidth: W, renderHeight: H, timing: timingFile ? (timingFile.source || 'file') : 'estimated', shots: SHOTS.map(s => ({ i: s.si, start: +s.start.toFixed(3), end: +s.end.toFixed(3), set: s.set.name, lines: s.lines_.map(l => l.text) })), lines: LINES.map(l => ({ text: l.text, start: +l.start.toFixed(3), end: +l.end.toFixed(3) })), warnings, library: { sets: Object.keys(SETS), props: Object.keys(PROPS), actions: Object.keys(ACTIONS), expressions: Object.keys(EXPRESSIONS), presets: Object.keys(PRESETS), icons: OV.ICONS } }),
  events, frame,
  frameAt: (t) => frame(Math.round(t * FPS)),
  sheet: (times, cols = 6, tw = 240) => {
    const th = Math.round(tw * H / W), rows = Math.ceil(times.length / cols); const c = document.createElement('canvas'); c.width = cols * tw; c.height = rows * th; const g = c.getContext('2d'); g.fillStyle = '#000'; g.fillRect(0, 0, c.width, c.height);
    times.forEach((tt, k) => { frame(Math.round(tt * FPS)); const x = (k % cols) * tw, y = Math.floor(k / cols) * th; g.drawImage(out, x, y, tw, th); g.fillStyle = 'rgba(0,0,0,.7)'; g.fillRect(x, y, 64, 22); g.fillStyle = '#ffdc1f'; g.font = "bold 15px sans-serif"; g.fillText(tt.toFixed(2) + 's', x + 5, y + 16); const sh = SHOTS.find(s => tt >= s.start && tt < s.end); if (sh && Math.abs(tt - sh.start) < .06) { g.fillStyle = '#ff3b30'; g.fillRect(x, y, 4, th); } });
    return c.toDataURL('image/jpeg', .85);
  },
};
window.READY = true;
