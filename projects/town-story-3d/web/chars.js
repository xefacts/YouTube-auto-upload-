// ============================================================================
// CHARS.JS — SQUARE R6 characters with SOFT ROUNDED EDGES (V5)
// Classic Roblox proportions (user spec): head 1x1x1, torso 2x2x1,
// limbs 1x2x1 — but every block is a ROUNDED BOX (no sharp corners).
// Outfit details: belt, collar, accent stripe, cuffs, rounded shoes.
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

// ---- rounded box geometry: square blocks with softly beveled edges ----
function roundedBoxGeo(w, h, d, r, seg = 4) {
  const g = new THREE.BoxGeometry(w, h, d, seg, seg, seg);
  const pos = g.attributes.position;
  const hx = Math.max(0.0001, w / 2 - r), hy = Math.max(0.0001, h / 2 - r), hz = Math.max(0.0001, d / 2 - r);
  const v = new THREE.Vector3(), q = new THREE.Vector3();
  for (let i = 0; i < pos.count; i++) {
    v.fromBufferAttribute(pos, i);
    q.set(
      THREE.MathUtils.clamp(v.x, -hx, hx),
      THREE.MathUtils.clamp(v.y, -hy, hy),
      THREE.MathUtils.clamp(v.z, -hz, hz)
    );
    if (v.distanceToSquared(q) > 1e-9) {
      const dir = v.sub(q).normalize().multiplyScalar(r);
      pos.setXYZ(i, q.x + dir.x, q.y + dir.y, q.z + dir.z);
    }
  }
  g.computeVertexNormals();
  return g;
}

function makeMat(hex) {
  const col = new THREE.Color(hex);
  const em = col.clone().multiplyScalar(0.15);
  return new THREE.MeshLambertMaterial({ color: col, emissive: em });
}
// rounded block mesh helper
const rbox = (w, h, d, mat, r = 0.055) => new THREE.Mesh(roundedBoxGeo(w, h, d, r), mat);

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

    const U = 0.61;                    // 1 Roblox unit
    const RR = 0.075;                  // edge rounding radius

    const skinM = makeMat(cfg.skin || '#f2c96e');
    const shirtM = makeMat(cfg.shirt);
    const pantsM = makeMat(cfg.pants);
    const shoesM = makeMat(cfg.shoes || '#2e2e34');
    const hairM = cfg.hair ? makeMat(cfg.hair.color) : null;
    const capM = cfg.cap ? makeMat(cfg.cap) : null;
    const accentM = cfg.accent ? makeMat(cfg.accent) : null;

    // ---- legs: 1x2x1 rounded, pivot at hip (y=2U) ----
    const mkLeg = (side) => {
      const pivot = new THREE.Group();
      pivot.position.set(side * 0.5 * U, 2 * U, 0);
      const leg = rbox(1 * U, 2 * U, 1 * U, pantsM, RR);
      leg.position.y = -1 * U;
      pivot.add(leg);
      const shoe = rbox(1.04 * U, 0.32 * U, 1.3 * U, shoesM, 0.06);
      shoe.position.set(0, -1.82 * U, 0.10 * U);
      pivot.add(shoe);
      return pivot;
    };
    this.legL = mkLeg(-1); this.legR = mkLeg(1);
    this.group.add(this.legL, this.legR);

    // ---- torso: 2x2x1 rounded ----
    this.torso = rbox(2 * U, 2 * U, 1 * U, shirtM, RR);
    this.torso.position.y = 3 * U;
    this.group.add(this.torso);
    // belt + buckle
    const belt = rbox(2.05 * U, 0.22 * U, 1.05 * U, makeMat('#33383f'), 0.04);
    belt.position.y = 2.06 * U;
    this.group.add(belt);
    const buckle = rbox(0.26 * U, 0.16 * U, 0.07 * U, makeMat('#f5d76e'), 0.02);
    buckle.position.set(0, 2.06 * U, -0.54 * U);
    this.group.add(buckle);
    // collar
    const collar = rbox(0.92 * U, 0.2 * U, 1.08 * U, shirtM, 0.04);
    collar.position.y = 3.94 * U;
    this.group.add(collar);
    // accent stripe + pocket
    if (cfg.accent) {
      const stripe = rbox(0.42 * U, 2 * U, 0.06 * U, accentM, 0.02);
      stripe.position.set(-0.5 * U, 3 * U, 0.53 * U);
      this.group.add(stripe);
      const pocket = rbox(0.4 * U, 0.34 * U, 0.06 * U, accentM, 0.02);
      pocket.position.set(0.55 * U, 2.66 * U, 0.53 * U);
      this.group.add(pocket);
    }

    // ---- arms: 1x2x1 rounded, pivot at shoulder (y=4U) ----
    const mkArm = (side) => {
      const pivot = new THREE.Group();
      pivot.position.set(side * 1.5 * U, 4 * U, 0);
      const arm = rbox(1 * U, 2 * U, 1 * U, shirtM, RR);
      arm.position.y = -1 * U;
      pivot.add(arm);
      const cuff = rbox(1.03 * U, 0.2 * U, 1.03 * U, accentM || shirtM, 0.04);
      cuff.position.y = -1.2 * U;
      pivot.add(cuff);
      const hand = rbox(1.03 * U, 0.34 * U, 1.03 * U, skinM, 0.05);
      hand.position.y = -1.8 * U;
      pivot.add(hand);
      return pivot;
    };
    this.armL = mkArm(-1); this.armR = mkArm(1);
    this.group.add(this.armL, this.armR);

    // ---- head: 1x1x1 ROUNDED cube, flat face decal on front ----
    const headS = 1.06 * U;
    const headTop = 4 * U;
    this.faces = {};
    for (const e of EXPRS) this.faces[e] = makeFaceTex(cfg, e);
    this.faceMat = new THREE.MeshLambertMaterial({ map: this.faces.neutral, transparent: true });
    this.head = rbox(headS, headS, headS, skinM, 0.09);
    this.head.position.y = headTop + headS / 2;
    this.group.add(this.head);
    // face decal (flat plane on the flat front region)
    const facePlane = new THREE.Mesh(
      new THREE.PlaneGeometry(headS - 0.17, headS - 0.17),
      this.faceMat
    );
    facePlane.position.set(0, headTop + headS / 2, headS / 2 + 0.006);
    this.group.add(facePlane);
    this.headGroup = new THREE.Group();
    this.group.add(this.headGroup);

    // ---- hair / cap (rounded slabs) ----
    const hw = headS + 0.06 * U;
    if (cfg.hair && cfg.hair.style === 'block') {
      const top = rbox(hw, 0.38 * U, hw, hairM, 0.07);
      top.position.y = headTop + headS - 0.02 * U;
      this.group.add(top);
      const back = rbox(hw, 0.74 * U, 0.30 * U, hairM, 0.07);
      back.position.set(0, headTop + headS * 0.60, -(headS / 2 + 0.09 * U));
      this.group.add(back);
      for (const sx of [-1, 1]) {
        const tuft = rbox(0.20 * U, 0.6 * U, headS * 0.9, hairM, 0.05);
        tuft.position.set(sx * (headS / 2 + 0.05 * U), headTop + headS * 0.64);
        this.group.add(tuft);
      }
    }
    if (cfg.hair && cfg.hair.style === 'bun') {
      const top = rbox(hw, 0.38 * U, hw, hairM, 0.07);
      top.position.y = headTop + headS - 0.02 * U;
      this.group.add(top);
      const back = rbox(hw, 0.86 * U, 0.30 * U, hairM, 0.07);
      back.position.set(0, headTop + headS * 0.56, -(headS / 2 + 0.09 * U));
      this.group.add(back);
      for (const sx of [-1, 1]) {
        const side = rbox(0.22 * U, 0.72 * U, headS * 0.92, hairM, 0.05);
        side.position.set(sx * (headS / 2 + 0.06 * U), headTop + headS * 0.58);
        this.group.add(side);
      }
      const bun = new THREE.Mesh(new THREE.SphereGeometry(0.30 * U, 14, 10), hairM);
      bun.position.set(0, headTop + headS * 0.95, -(headS / 2 + 0.15 * U));
      this.group.add(bun);
    }
    if (cfg.cap) {
      const crown = rbox(hw, 0.42 * U, hw, capM, 0.08);
      crown.position.y = headTop + headS - 0.02 * U;
      this.group.add(crown);
      const brim = rbox(0.96 * U, 0.12 * U, 0.64 * U, capM, 0.05);
      brim.position.set(0, headTop + headS - 0.16 * U, headS / 2 + 0.22 * U);
      this.group.add(brim);
      const button = new THREE.Mesh(new THREE.SphereGeometry(0.09 * U, 10, 8), makeMat('#f5d76e'));
      button.position.y = headTop + headS + 0.14 * U;
      this.group.add(button);
    }

    // cane (old man)
    if (cfg.cane) {
      this.cane = new THREE.Mesh(
        new THREE.CylinderGeometry(0.05, 0.05, 1.45 * U, 12),
        makeMat('#8a6a45')
      );
      this.cane.geometry.translate(0, -0.72 * U, 0);
      const knob = new THREE.Mesh(new THREE.SphereGeometry(0.10 * U, 10, 8), makeMat('#f5d76e'));
      this.cane.add(knob);
      this.cane.position.set(1.62 * U, 1.95 * U, 0.16 * U);
      this.cane.rotation.x = 0.10;
      this.group.add(this.cane);
    }
    // moving box (arrival scene)
    if (cfg.carryBox) {
      this.carry = rbox(1.5 * U, 1.0 * U, 1.1 * U, makeMat('#c8a05a'), 0.05);
      this.carry.position.set(0, 3.45 * U, 0.8 * U);
      const tape = rbox(1.54 * U, 1.02 * U, 0.16 * U, makeMat('#e8d8b0'), 0.03);
      tape.position.set(0, 3.45 * U, 0.8 * U);
      this.group.add(this.carry, tape);
    }

    // ---- blob shadow ----
    const shadow = new THREE.Mesh(
      new THREE.CircleGeometry(1.1 * U, 24),
      new THREE.MeshBasicMaterial({ color: '#000000', transparent: true, opacity: 0.24, depthWrite: false })
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
