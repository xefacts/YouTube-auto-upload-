// ============================================================================
// CHARS.JS — SMOOTH ROUNDED characters (V4 "smooth capsule" pass)
// No sharp squares: pill/capsule body, capsule limbs with sphere hands,
// rounded CYLINDER head with a curved face decal wrapped on the front.
// Proportions keep the same world heights as V3 (camera framing untouched).
// Expressions: neutral, smile, happy, worried, scared, shocked, creepy, talk.
// All animation is a pure function of time (deterministic re-render).
// ============================================================================
import * as THREE from 'three';

const cv = (w, h) => {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  return [c, c.getContext('2d')];
};
const tex = (c) => {
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
};

function makeMat(hex) {
  const col = new THREE.Color(hex);
  const em = col.clone().multiplyScalar(0.15);
  return new THREE.MeshLambertMaterial({ color: col, emissive: em });
}
const capGeo = (r, len) => new THREE.CapsuleGeometry(r, len, 6, 16);
const sphGeo = (r) => new THREE.SphereGeometry(r, 20, 14);

// ------------------------------------------------------------- face factory
function makeFaceTex(cfg, expr) {
  const [c, g] = cv(320, 320);
  g.clearRect(0, 0, 320, 320);
  const ink = '#1c2027';
  const skin = cfg.skin || '#f2c96e';

  const drawEye = (x, y, ew, eh, opts = {}) => {
    g.fillStyle = '#ffffff';
    g.beginPath(); g.ellipse(x, y, ew, eh, 0, 0, 7); g.fill();
    g.lineWidth = 6; g.strokeStyle = ink;
    g.beginPath(); g.ellipse(x, y, ew, eh, 0, 0, 7); g.stroke();
    const pd = opts.pupil || { dx: 0, dy: 0, r: 11 };
    g.fillStyle = ink;
    g.beginPath(); g.arc(x + pd.dx, y + pd.dy, pd.r, 0, 7); g.fill();
    g.fillStyle = '#ffffff';
    g.beginPath(); g.arc(x + pd.dx - pd.r * 0.38, y + pd.dy - pd.r * 0.42, pd.r * 0.34, 0, 7); g.fill();
    if (opts.lid) {
      g.fillStyle = skin;
      g.beginPath(); g.ellipse(x, y - eh + opts.lid, ew + 3, opts.lid + 2, 0, Math.PI, 0); g.fill();
      g.strokeStyle = ink; g.lineWidth = 5;
      g.beginPath(); g.moveTo(x - ew, y - eh + opts.lid); g.lineTo(x + ew, y - eh + opts.lid); g.stroke();
    }
  };
  const drawEyes = (ex, ey, ew, eh, opts) => {
    drawEye(160 - ex, ey, ew, eh, opts);
    drawEye(160 + ex, ey, ew, eh, opts);
  };
  const mouth = (kind) => {
    g.strokeStyle = ink; g.fillStyle = ink; g.lineWidth = 9; g.lineCap = 'round';
    if (kind === 'smile') { g.beginPath(); g.arc(160, 178, 48, 0.22 * Math.PI, 0.78 * Math.PI); g.stroke(); }
    if (kind === 'bigsmile') {
      g.beginPath(); g.arc(160, 172, 52, 0.12 * Math.PI, 0.88 * Math.PI); g.closePath(); g.fill();
      g.fillStyle = '#ffffff';
      g.beginPath(); g.moveTo(122, 196); g.lineTo(198, 196); g.lineTo(192, 210); g.lineTo(128, 210); g.closePath(); g.fill();
      g.fillStyle = '#ff9d9d';
      g.beginPath(); g.ellipse(160, 186, 14, 8, 0, 0, 7); g.fill();
    }
    if (kind === 'frown') { g.beginPath(); g.arc(160, 250, 46, 1.28 * Math.PI, 1.72 * Math.PI); g.stroke(); }
    if (kind === 'open') {
      g.beginPath(); g.ellipse(160, 226, 30, 36, 0, 0, 7); g.fill();
      g.fillStyle = '#ff9d9d';
      g.beginPath(); g.ellipse(160, 244, 16, 10, 0, 0, 7); g.fill();
    }
    if (kind === 'worry') { g.beginPath(); g.moveTo(122, 232); g.quadraticCurveTo(160, 252, 198, 232); g.stroke(); }
    if (kind === 'shout') {
      g.beginPath(); g.ellipse(160, 238, 34, 44, 0, 0, 7); g.fill();
      g.fillStyle = '#ff8a8a';
      g.beginPath(); g.ellipse(160, 262, 18, 12, 0, 0, 7); g.fill();
    }
    if (kind === 'flat') { g.beginPath(); g.moveTo(126, 224); g.lineTo(194, 224); g.stroke(); }
    if (kind === 'smirk') { g.beginPath(); g.moveTo(128, 226); g.quadraticCurveTo(170, 236, 200, 210); g.stroke(); }
  };
  const brows = (ang, lift) => {
    g.strokeStyle = ink; g.lineWidth = 11; g.lineCap = 'round';
    for (const sx of [-1, 1]) {
      const x = 160 + sx * 50;
      g.beginPath();
      g.moveTo(x - sx * 28, 108 + lift + ang);
      g.lineTo(x + sx * 28, 108 + lift - ang);
      g.stroke();
    }
  };
  const blush = () => {
    g.fillStyle = 'rgba(255,120,120,0.30)';
    for (const sx of [-1, 1]) { g.beginPath(); g.ellipse(160 + sx * 78, 196, 20, 12, 0, 0, 7); g.fill(); }
  };
  const sweat = () => {
    g.fillStyle = '#9fd8ff'; g.strokeStyle = '#5aa7d8'; g.lineWidth = 4;
    g.beginPath(); g.ellipse(246, 96, 13, 18, 0.4, 0, 7); g.fill(); g.stroke();
  };

  switch (expr) {
    case 'neutral':
      drawEyes(52, 132, 26, 30, { pupil: { r: 11 } }); mouth('flat'); break;
    case 'smile':
      drawEyes(52, 132, 26, 30, { pupil: { r: 11 } }); mouth('smile'); blush(); break;
    case 'happy':
      drawEyes(52, 128, 28, 32, { pupil: { r: 10 } }); brows(7, -5); mouth('bigsmile'); blush(); break;
    case 'worried':
      drawEyes(52, 128, 27, 33, { pupil: { r: 10, dy: 3 }, lid: 10 }); brows(15, 7); mouth('worry'); sweat(); break;
    case 'scared':
      drawEyes(54, 124, 31, 38, { pupil: { r: 9, dy: 3 } }); brows(22, 13); mouth('shout'); sweat();
      g.fillStyle = 'rgba(120,160,255,0.16)'; g.fillRect(0, 0, 320, 320); break;
    case 'shocked':
      drawEyes(56, 122, 33, 41, { pupil: { r: 8, dy: 3 } }); brows(26, 15); mouth('open'); sweat();
      g.fillStyle = 'rgba(120,160,255,0.16)'; g.fillRect(0, 0, 320, 320); break;
    case 'creepy':
      for (const sx of [-1, 1]) {
        const x = 160 + sx * 54;
        g.fillStyle = '#ffffff'; g.beginPath(); g.ellipse(x, 128, 32, 36, 0, 0, 7); g.fill();
        g.strokeStyle = ink; g.lineWidth = 6; g.beginPath(); g.ellipse(x, 128, 32, 36, 0, 0, 7); g.stroke();
        g.fillStyle = ink; g.beginPath(); g.arc(x, 130, 7, 0, 7); g.fill();
      }
      mouth('bigsmile');
      g.strokeStyle = ink; g.lineWidth = 7;
      g.beginPath(); g.moveTo(120, 250); g.lineTo(200, 250); g.stroke();
      g.fillStyle = 'rgba(30,20,40,0.20)'; g.fillRect(0, 0, 320, 52); break;
    case 'talk0':
      drawEyes(52, 130, 26, 30, { pupil: { r: 11 } }); mouth('flat'); break;
    case 'talk1':
      drawEyes(52, 130, 26, 30, { pupil: { r: 11 } }); mouth('open'); break;
    default:
      drawEyes(52, 132, 26, 30, { pupil: { r: 11 } }); mouth('flat');
  }
  if (cfg.freckles) {
    g.fillStyle = 'rgba(150,95,45,0.55)';
    for (const [fx, fy] of [[112, 182], [122, 192], [208, 182], [198, 192], [160, 174]]) {
      g.beginPath(); g.arc(fx, fy, 4, 0, 7); g.fill();
    }
  }
  return tex(c);
}

const EXPRS = ['neutral', 'smile', 'happy', 'worried', 'scared', 'shocked', 'creepy', 'talk0', 'talk1'];

// ------------------------------------------------------------- character
export class BlockChar {
  constructor(scene, cfg) {
    // cfg: { name, skin, shirt, accent, pants, shoes, hair:{style,color}|null,
    //        cap: color|null, scale, freckles, cane, carryBox }
    this.cfg = cfg;
    this.scale = cfg.scale || 1;
    this.group = new THREE.Group();
    scene.add(this.group);

    const skinM = makeMat(cfg.skin || '#f2c96e');
    const shirtM = makeMat(cfg.shirt);
    const pantsM = makeMat(cfg.pants);
    const shoesM = makeMat(cfg.shoes || '#2e2e34');
    const hairM = cfg.hair ? makeMat(cfg.hair.color) : null;
    const capM = cfg.cap ? makeMat(cfg.cap) : null;
    const accentM = cfg.accent ? makeMat(cfg.accent) : null;

    const mesh = (geo, mat) => new THREE.Mesh(geo, mat);

    // ---- legs: capsule limbs, pivot at hip (y=1.22) ----
    const mkLeg = (side) => {
      const pivot = new THREE.Group();
      pivot.position.set(side * 0.20, 1.22, 0);
      const leg = mesh(capGeo(0.155, 0.78), pantsM);   // total ~1.09
      leg.position.y = -0.55;
      pivot.add(leg);
      // smooth rounded foot (flattened sphere, slightly forward)
      const foot = mesh(sphGeo(0.185), shoesM);
      foot.scale.set(1.0, 0.62, 1.35);
      foot.position.set(0, -1.06, 0.07);
      pivot.add(foot);
      return pivot;
    };
    this.legL = mkLeg(-1); this.legR = mkLeg(1);
    this.group.add(this.legL, this.legR);

    // ---- torso: smooth pill (capsule) ----
    this.torso = mesh(capGeo(0.46, 0.42), shirtM);     // total ~1.34
    this.torso.position.y = 1.86;
    this.group.add(this.torso);
    // belt (thin torus-ish ring via flattened cylinder)
    const belt = mesh(new THREE.CylinderGeometry(0.465, 0.465, 0.09, 24), makeMat('#33383f'));
    belt.position.y = 1.34;
    this.group.add(belt);
    // accent chest band
    if (cfg.accent) {
      const band = mesh(new THREE.CylinderGeometry(0.468, 0.468, 0.16, 24), accentM);
      band.position.y = 2.06;
      this.group.add(band);
    }
    // neck
    const neck = mesh(new THREE.CylinderGeometry(0.13, 0.13, 0.14, 12), skinM);
    neck.position.y = 2.52;
    this.group.add(neck);

    // ---- arms: capsule limbs, pivot at shoulder (y=2.42) ----
    const mkArm = (side) => {
      const pivot = new THREE.Group();
      pivot.position.set(side * 0.585, 2.42, 0);
      const shoulder = mesh(sphGeo(0.145), shirtM);
      pivot.add(shoulder);
      const arm = mesh(capGeo(0.125, 0.68), shirtM);   // total ~0.93
      arm.position.y = -0.44;
      pivot.add(arm);
      const hand = mesh(sphGeo(0.155), skinM);
      hand.position.y = -0.88;
      pivot.add(hand);
      if (cfg.accent) {
        const cuff = mesh(new THREE.CylinderGeometry(0.132, 0.132, 0.09, 16), accentM);
        cuff.position.y = -0.62;
        pivot.add(cuff);
      }
      return pivot;
    };
    this.armL = mkArm(-1); this.armR = mkArm(1);
    this.group.add(this.armL, this.armR);

    // ---- head: ROUNDED CYLINDER (cyl body + hemisphere top) ----
    const HR = 0.305, HCYL = 0.34;                     // head radius / cylinder height
    const headBase = 2.56;                             // bottom of head
    const headGroup = new THREE.Group();
    headGroup.position.y = 0;
    const headCyl = mesh(new THREE.CylinderGeometry(HR, HR, HCYL, 28), skinM);
    headCyl.position.y = headBase + HCYL / 2;
    headGroup.add(headCyl);
    const headTop = mesh(new THREE.SphereGeometry(HR, 28, 16, 0, Math.PI * 2, 0, Math.PI / 2), skinM);
    headTop.position.y = headBase + HCYL;
    headGroup.add(headTop);
    const headBot = mesh(new THREE.SphereGeometry(HR, 28, 16, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), skinM);
    headBot.position.y = headBase;
    headGroup.add(headBot);
    this.head = headCyl; // main ref (kept for camera/aim code)
    this.headMeshGroup = headGroup;

    // ---- curved FACE decal wrapped on the front of the head ----
    this.faces = {};
    for (const e of EXPRS) this.faces[e] = makeFaceTex(cfg, e);
    this.faceMat = new THREE.MeshLambertMaterial({ map: this.faces.neutral, transparent: true });
    const faceArc = mesh(
      new THREE.CylinderGeometry(HR + 0.012, HR + 0.012, 0.46, 28, 1, true, -1.05, 2.10),
      this.faceMat
    );
    faceArc.material.side = THREE.DoubleSide;
    faceArc.position.y = headBase + HCYL / 2 + 0.02;
    headGroup.add(faceArc);
    this.faceArc = faceArc;
    this.group.add(headGroup);

    // ---- hair / cap (smooth) ----
    if (cfg.hair && cfg.hair.style === 'block') {
      const dome = mesh(new THREE.SphereGeometry(HR + 0.045, 28, 16, 0, Math.PI * 2, 0, Math.PI * 0.62), hairM);
      dome.position.y = headBase + HCYL * 0.42;
      this.group.add(dome);
      const back = mesh(new THREE.CylinderGeometry(HR + 0.045, HR + 0.045, 0.30, 28, 1, true, Math.PI * 0.62, Math.PI * 1.76), hairM);
      back.material = new THREE.MeshLambertMaterial({ color: cfg.hair.color });
      back.material.side = THREE.DoubleSide;
      back.position.y = headBase + HCYL * 0.45;
      this.group.add(back);
    }
    if (cfg.hair && cfg.hair.style === 'bun') {
      const dome = mesh(new THREE.SphereGeometry(HR + 0.045, 28, 16, 0, Math.PI * 2, 0, Math.PI * 0.58), hairM);
      dome.position.y = headBase + HCYL * 0.50;
      this.group.add(dome);
      const back = mesh(new THREE.CylinderGeometry(HR + 0.045, HR + 0.045, 0.34, 28, 1, true, Math.PI * 0.66, Math.PI * 1.68), new THREE.MeshLambertMaterial({ color: cfg.hair.color, side: THREE.DoubleSide }));
      back.position.y = headBase + HCYL * 0.42;
      this.group.add(back);
      const bun = mesh(sphGeo(0.145), makeMat(cfg.hair.color));
      bun.position.set(0, headBase + HCYL + 0.16, -(HR + 0.02));
      this.group.add(bun);
    }
    if (cfg.cap) {
      const crown = mesh(new THREE.SphereGeometry(HR + 0.05, 28, 16, 0, Math.PI * 2, 0, Math.PI * 0.55), capM);
      crown.position.y = headBase + HCYL * 0.55;
      this.group.add(crown);
      const brim = mesh(new THREE.CylinderGeometry(0.30, 0.30, 0.05, 20, 1, false, -0.85, 1.70), capM);
      brim.position.set(0, headBase + HCYL * 0.62, 0.02);
      this.group.add(brim);
      const button = mesh(sphGeo(0.05), makeMat('#f5d76e'));
      button.position.y = headBase + HCYL + 0.42;
      this.group.add(button);
    }

    // cane (old man)
    if (cfg.cane) {
      this.cane = mesh(new THREE.CylinderGeometry(0.045, 0.045, 1.0, 12), makeMat('#8a6a45'));
      this.cane.geometry.translate(0, -0.5, 0);
      const knob = mesh(sphGeo(0.07), makeMat('#f5d76e'));
      this.cane.add(knob);
      this.cane.position.set(0.72, 1.25, 0.16);
      this.cane.rotation.x = 0.10;
      this.group.add(this.cane);
    }
    // moving box (arrival scene)
    if (cfg.carryBox) {
      this.carry = mesh(new THREE.BoxGeometry(0.72, 0.5, 0.52), makeMat('#c8a05a'));
      this.carry.position.set(0, 1.98, 0.50);
      const tape = mesh(new THREE.BoxGeometry(0.74, 0.52, 0.10), makeMat('#e8d8b0'));
      tape.position.set(0, 1.98, 0.50);
      this.group.add(this.carry, tape);
    }

    // ---- soft blob shadow ----
    const shadow = new THREE.Mesh(
      new THREE.CircleGeometry(0.52, 24),
      new THREE.MeshBasicMaterial({ color: '#000000', transparent: true, opacity: 0.22, depthWrite: false })
    );
    shadow.rotation.x = -Math.PI / 2;
    shadow.position.y = 0.02;
    this.group.add(shadow);

    this.group.scale.setScalar(this.scale);
    this.setPose('stand', 0);
    this.setExpression('neutral');
    this.group.visible = false;
  }

  setExpression(e, talkPhase = 0) {
    if (e === 'talk') e = (Math.sin(talkPhase) > 0) ? 'talk1' : 'talk0';
    const t = this.faces[e] || this.faces.neutral;
    if (this.faceMat.map !== t) { this.faceMat.map = t; this.faceMat.needsUpdate = true; }
  }

  // pose from deterministic time — walk cycles, idle bob, wave, point, reach
  setPose(mode, t, opts = {}) {
    const g = this.group;
    if (mode === 'walk' || mode === 'run') {
      const spd = mode === 'run' ? 11.0 : 6.4;
      const amp = mode === 'run' ? 0.95 : 0.62;
      const ph = t * spd + (opts.phase || 0);
      this.legL.rotation.x = Math.sin(ph) * amp * 0.9;
      this.legR.rotation.x = -Math.sin(ph) * amp * 0.9;
      this.armL.rotation.x = -Math.sin(ph) * amp;
      this.armR.rotation.x = Math.sin(ph) * amp;
      this.armL.rotation.z = 0.08; this.armR.rotation.z = -0.08;
      g.position.y = Math.abs(Math.sin(ph)) * (mode === 'run' ? 0.09 : 0.05);
      g.rotation.z = Math.sin(ph) * (mode === 'run' ? 0.05 : 0.02);
    } else if (mode === 'stumble') {
      const ph = t * 9;
      this.legL.rotation.x = Math.sin(ph) * 0.55 - 0.25;
      this.legR.rotation.x = -Math.sin(ph) * 0.45 + 0.15;
      this.armL.rotation.x = -1.9 + Math.sin(ph) * 0.3; // arms flailing up
      this.armR.rotation.x = -1.7 - Math.sin(ph) * 0.3;
      this.armL.rotation.z = 0.5; this.armR.rotation.z = -0.5;
      g.position.y = 0;
      g.rotation.z = Math.sin(t * 3.1) * 0.16; // wobble
    } else if (mode === 'wave') {
      this.legL.rotation.x = 0; this.legR.rotation.x = 0;
      this.armR.rotation.x = -2.6;
      this.armR.rotation.z = Math.sin(t * 8.0) * 0.35;
      this.armL.rotation.x = 0;
      g.position.y = 0; g.rotation.z = 0;
    } else if (mode === 'point') {
      this.legL.rotation.x = 0; this.legR.rotation.x = 0;
      this.armR.rotation.x = -1.5;
      this.armR.rotation.z = 0;
      this.armL.rotation.x = 0;
      g.position.y = 0; g.rotation.z = 0;
    } else if (mode === 'reach-down') {
      this.legL.rotation.x = 0.25; this.legR.rotation.x = -0.1;
      this.armR.rotation.x = -0.55 + Math.sin(t * 2) * 0.06;
      this.armL.rotation.x = 0.15;
      g.position.y = -0.16; g.rotation.z = 0.22;
    } else if (mode === 'cower') {
      this.legL.rotation.x = 0.5; this.legR.rotation.x = 0.5;
      this.armL.rotation.x = -1.1; this.armR.rotation.x = -1.1;
      this.armL.rotation.z = 0.7; this.armR.rotation.z = -0.7;
      g.position.y = -0.34; g.rotation.z = 0.3;
    } else { // stand / idle
      const bob = Math.sin(t * 2.2 + (opts.phase || 0)) * 0.022;
      this.legL.rotation.x = 0; this.legR.rotation.x = 0;
      this.armL.rotation.x = Math.sin(t * 2.2) * 0.05;
      this.armR.rotation.x = -Math.sin(t * 2.2) * 0.05;
      this.armL.rotation.z = 0.08; this.armR.rotation.z = -0.08;
      g.position.y = bob; g.rotation.z = 0;
    }
  }

  setAt(x, z, ry = 0) {
    this.group.position.x = x;
    this.group.position.z = z;
    this.group.rotation.y = ry;
  }
  setVisible(v) { this.group.visible = v; }
}
