/* ============================ per-frame (lights) ============================ */
const tmpV = new THREE.Vector3();
function applyLight(L) {
  hemi.color.set(L.sky); hemi.groundColor.set(L.ground); hemi.intensity = L.hemi;
  sun.color.set(L.sun); sun.intensity = L.sunI;
  scene.fog.color.set(L.fog); scene.fog.near = L.fogNear; scene.fog.far = L.fogFar;
  skyU.top.value.set(L.skyTop); skyU.hor.value.set(L.skyHor); skyU.sunCol.value.set(L.sunDisc || '#000'); skyU.sunSize.value = L.sunSize || 0;
  inkU.sat.value = L.sat; inkU.gain.value.set(L.gain || '#ffffff'); inkU.lift.value.set(L.lift || '#000000'); inkU.vig.value = L.vig ?? 0.24;
}
function placeSun(L, focus) {
  const az = rx(L.az), el = rx(L.el);
  tmpV.set(Math.cos(el) * Math.cos(az), Math.sin(el), Math.cos(el) * Math.sin(az));
  skyU.sunDir.value.copy(tmpV);
  sun.position.copy(focus).addScaledVector(tmpV, 120); sun.target.position.copy(focus);
  const ext = L.shadowExt || 40, sc = sun.shadow.camera;
  sc.left = -ext; sc.right = ext; sc.top = ext; sc.bottom = -ext; sc.near = 1; sc.far = 320; sc.updateProjectionMatrix();
}

/* ============================ per-frame (world) ============================ */
const EMPTY_FROM = {
  s8: ['vermeer', 'storm', 'lady', 'obelisk'],
  s10: ['vermeer', 'storm', 'lady', 'obelisk', 'tortoni', 'degas', 'degas2', 'portrait2'],
};
EMPTY_FROM.s11 = EMPTY_FROM.s10; EMPTY_FROM.s12 = EMPTY_FROM.s10;

function worldState(S, f, t) {
  for (const [name, g] of Object.entries(sets)) g.visible = name === S.loc;
  const k = Math.max(0, Math.min(1, (f - S.a) / Math.max(1, S.b - S.a)));

  /* --- paintings: on the wall, being cut, or gone --- */
  const gone = EMPTY_FROM[S.id] || [];
  for (const [key, art] of Object.entries(ref)) {
    if (!art || !art.canvas) continue;
    art.canvas.visible = !gone.includes(key);
    art.canvas.position.set(0, 0, 0.012);
    art.canvas.rotation.set(0, 0, 0);
  }
  if (S.id === 's7' && ref.vermeer) {           // the canvas is peeled down out of its frame
    const p = Math.min(1, Math.max(0, (k - 0.22) / 0.44));
    const e = p * p * (3 - 2 * p);
    ref.vermeer.canvas.visible = k < 0.86;
    ref.vermeer.canvas.position.set(0.05 * e, -ref.vermeer.h * 0.46 * e, 0.012 + 0.34 * e);
    ref.vermeer.canvas.rotation.set(0, 0.16 * e, -0.30 * e);
  }

  /* --- room lights --- */
  const dutch = S.loc === 'dutch';
  const cellar = S.loc === 'cellar', hall = S.loc === 'hall', street = S.loc === 'street';
  if (ref.fire) {
    ref.fire.visible = dutch;
    const fl = 0.72 + 0.28 * Math.sin(t * 9.1) * Math.sin(t * 3.3 + 1.7);
    ref.fire.intensity = (S.light === 'dutchDawn' ? 3.2 : 8.0) * fl;
  }
  if (ref.dutchAmb) ref.dutchAmb.visible = dutch;
  if (ref.cellarBulb) { ref.cellarBulb.visible = cellar; ref.cellarBulb.intensity = 16 + Math.sin(t * 21) * 1.1; }
  if (ref.deskLamp) ref.deskLamp.visible = hall;

  /* --- flashlights --- */
  const tor = dutch && (S.id === 's5' || S.id === 's6' || S.id === 's7' || S.id === 's8');
  ref.torches.forEach(({ sp, cone }) => {
    sp.visible = cone.visible = tor;
    if (!tor) return;
  });

  /* --- fireflies of dust in the torch light --- */
  if (ref.motes) ref.motes.visible = dutch;
}

window.torchState = (list) => {   // list: [{from:[x,y,z], to:[x,y,z]}] from story.js
  ref.torches.forEach(({ sp, cone }, i) => {
    const s = list[i]; if (!s) { sp.visible = cone.visible = false; return; }
    sp.position.set(...s.from); sp.target.position.set(...s.to);
    sp.target.updateMatrixWorld();
    const A = new THREE.Vector3(...s.from), Bp = new THREE.Vector3(...s.to);
    const v = Bp.clone().sub(A), len = v.length();
    cone.position.copy(A).addScaledVector(v, 0.5);
    cone.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), v.clone().normalize());
    cone.scale.set(1, len / 5.2, 1);
  });
};
window.torchLevel = (v) => { ref.torches.forEach(({ sp, cone }) => { sp.intensity = 26 * v; cone.material.opacity = 0.075 * v; }); };

/* ============================ render ============================ */
window.renderFrame = (f) => {
  const S = shotAt(f), L = lightFor(S), C = window.__freeCam || camAt(f), t = f / 30;
  window.__lastF = f;
  applyLight(L);
  camera.position.set(...C.pos); camera.up.set(0, 1, 0); camera.lookAt(...C.look); camera.rotateZ(rx(C.roll || 0));
  camera.fov = C.fov; camera.updateProjectionMatrix(); camera.updateMatrixWorld();
  worldState(S, f, t);
  if (window.torchState && window.__torch) window.torchState(window.__torch(f));
  placeSun(L, new THREE.Vector3(...(C.shadowAt || C.look)));
  if (window.NOACT) drawActors([], camera); else drawActors([...actorsAt(f, T), ...fxAt(f, T)], camera);
  sky.position.copy(camera.position);
  renderer.setRenderTarget(rtColor); renderer.setClearColor(0x000000, 1); renderer.clear(); renderer.render(scene, camera);
  const fog = scene.fog; scene.fog = null; const sm = renderer.shadowMap.enabled; renderer.shadowMap.enabled = false; renderer.shadowMap.autoUpdate = false;
  swapForNd(true); renderer.setRenderTarget(rtNd); renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(scene, camera); swapForNd(false);
  scene.fog = fog; renderer.shadowMap.enabled = sm; renderer.shadowMap.autoUpdate = true;
  const D = dofAt(f);
  inkU.px.value = 2.0;
  renderer.setRenderTarget(rtInk); renderer.render(inkScene, fsCam);
  dofU.focus.value = D.focus; dofU.cinf.value = D.cinf * (H / 1920); dofU.near.value = D.near ?? 1;
  renderer.setRenderTarget(null); renderer.render(dofScene, fsCam);
  drawCaption(f);
  return true;
};
window.__probeCam = (pos, look, fov, pts) => {   // try a camera without touching story.js
  camera.position.set(...pos); camera.up.set(0, 1, 0); camera.lookAt(...look);
  camera.fov = fov; camera.updateProjectionMatrix(); camera.updateMatrixWorld();
  return window.__proj(pts);
};
window.__actorNdc = () => {     // where the current shot's actors land on screen
  const S = shotAt(__lastF), out = [];
  for (const a of actorsAt(__lastF, T)) {
    const v = new THREE.Vector3(a.x, a.y + 1.0, a.z).project(camera);
    out.push({ key: a.key, ndc: [+v.x.toFixed(2), +v.y.toFixed(2), +v.z.toFixed(2)], pos: [a.x, a.y, a.z], s: a.s, alpha: a.alpha });
  }
  return out;
};
window.__proj = (pts) => {     // world point -> NDC (-1..1), for framing checks
  const out = [];
  for (const p of pts) { const v = new THREE.Vector3(...p); v.project(camera); out.push([+v.x.toFixed(2), +v.y.toFixed(2), +v.z.toFixed(2)]); }
  return out;
};
window.__scene = scene; window.__THREE = THREE; window.__cam = camera;
window.TOTAL = TOTAL;
window.fadeAmt = (f) => Math.min(1, Math.max(0, Math.min(f / 30, (TOTAL - 1 - f) / 40)));
window.ready = true;
