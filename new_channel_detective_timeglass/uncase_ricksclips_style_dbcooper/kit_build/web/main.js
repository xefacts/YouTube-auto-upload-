import * as THREE from './lib/three.module.js';
import * as T from './toon.js';
import * as P from './paint.js';
import { SHOTS, TOTAL, shotAt, camAt, dofAt, LIGHTS, lightFor, actorsAt, worldAt, fxAt } from './story.js';
import { CAPTIONS } from './captions.js';

const W = 720, H = 1280;
const canvas = document.getElementById('c');
const capCanvas=document.getElementById('caption'),capCtx=capCanvas.getContext('2d');
function drawCaption(f){capCtx.clearRect(0,0,W,H);const c=CAPTIONS.find(x=>f>=x.a&&f<x.b);if(!c)return;capCtx.save();capCtx.font='900 55px Arial Black, Arial, sans-serif';capCtx.textAlign='center';capCtx.textBaseline='middle';capCtx.lineJoin='round';capCtx.lineWidth=10;capCtx.strokeStyle='#111015';capCtx.fillStyle='#fff';capCtx.strokeText(c.text,W/2,923,670);capCtx.fillText(c.text,W/2,923,670);capCtx.restore();}
const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.NoToneMapping;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, W / H, 0.08, 1500);
const rx = (a) => a * Math.PI / 180;

// ---------- materials ----------
const grad = (() => { const d = new Uint8Array([90, 90, 90, 255, 255, 255, 255, 255]); const t = new THREE.DataTexture(d, 2, 1); t.minFilter = t.magFilter = THREE.NearestFilter; t.needsUpdate = true; return t; })();
const toon = (opts) => new THREE.MeshToonMaterial({ gradientMap: grad, ...opts });
const texM = (c, rx_ = 1, ry_ = 1, color = '#ffffff') => toon({ map: P.tex(c, rx_, ry_), color });
const M = {
  plank: texM(P.planks(1), 1, 6), beam: texM(P.beam(2), 1, 2), beamDark: texM(P.beam(3, [28, 36, 30]), 1, 2),
  rot: texM(P.rotten(4), 1, 1), rotB: texM(P.rotten(14), 1, 1),
  stone: texM(P.stone(4), 1, 1), stoneMoss: texM(P.mossy(P.stone(4), 5, 1.2), 1, 1),
  grass: texM(P.grass(6), 40, 40), dirt: texM(P.dirt(7), 6, 30), plaster: texM(P.plaster(8), 1, 1), plaster2: texM(P.plaster(18, 28), 1, 1),
  roof: texM(P.roof(9), 2, 2), marble: texM(P.marble(10), 1, 1), marbleTop: toon({ color: '#ece2cf' }),
  trunk: toon({ color: '#6a4a32' }), cypress: toon({ color: '#3f6b36' }), pine: toon({ color: '#5c8a3c' }), bush: toon({ color: '#6c9a42' }),
  hill: toon({ color: '#7aa64c' }), hillFar: toon({ color: '#86ad60' }), mount: toon({ color: '#8fa7b8' }), snow: toon({ color: '#f4f6fa' }),
  iron: toon({ color: '#5c5a57' }), bronze: toon({ color: '#b08a4a' }), wood: toon({ color: '#7a5434' }), door: toon({ color: '#5a3a24' }),
  window: toon({ color: '#2b2430' }), red: toon({ color: '#b8282b' }),
};
M.banner = new THREE.MeshToonMaterial({ gradientMap: grad, map: P.tex(P.banner()), alphaTest: 0.5, side: THREE.DoubleSide });
// helmet
const helmetIn = P.tex(P.helmetInside()); helmetIn.wrapS = helmetIn.wrapT = THREE.ClampToEdgeWrapping;
M.helmIn = new THREE.MeshToonMaterial({ gradientMap: grad, map: helmetIn, side: THREE.BackSide });
M.helmOut = toon({ color: '#8f8a7e' });

// ---------- ink / normal-depth contract ----------
const NOINK = 'noink'; // userData flag: never outlined (cards, fx, water handled specially)
const ndMat = new THREE.ShaderMaterial({
  vertexShader: `varying vec3 vN; varying float vD; void main(){ vN = normalize(normalMatrix*normal); vec4 mv = modelViewMatrix*vec4(position,1.); vD = -mv.z; gl_Position = projectionMatrix*mv; }`,
  fragmentShader: `varying vec3 vN; varying float vD; void main(){ vec3 n = normalize(vN); if(!gl_FrontFacing) n = -n; gl_FragColor = vec4(n*.5+.5, vD); }`,
  side: THREE.DoubleSide,
});
const cardNd = (map) => new THREE.ShaderMaterial({
  uniforms: { map: { value: map } },
  vertexShader: `varying vec2 vUv; varying float vD; void main(){ vUv=uv; vec4 mv = modelViewMatrix*vec4(position,1.); vD=-mv.z; gl_Position=projectionMatrix*mv; }`,
  fragmentShader: `uniform sampler2D map; varying vec2 vUv; varying float vD; void main(){ if(texture2D(map,vUv).a<.5) discard; gl_FragColor=vec4(0.,0.,0.,vD); }`,
  side: THREE.DoubleSide,
});
const waterNd = new THREE.ShaderMaterial({
  vertexShader: `varying float vD; void main(){ vec4 mv = modelViewMatrix*vec4(position,1.); vD=-mv.z; gl_Position=projectionMatrix*mv; }`,
  fragmentShader: `varying float vD; void main(){ gl_FragColor=vec4(.5,1.,.5,vD); }`,
});

// ---------- helpers ----------
const add = (geo, mat, x = 0, y = 0, z = 0, parent = scene, opts = {}) => {
  const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = opts.cast ?? true; m.receiveShadow = true; parent.add(m); return m;
};
const box = (w, h, d) => new THREE.BoxGeometry(w, h, d);
const uvScale = (geo, su, sv) => { const uv = geo.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * su, uv.getY(i) * sv); return geo; };
/** box with world-scaled UVs per face (texel density 1 tile per `t` metres) */
const tbox = (w, h, d, t = 2) => {
  const g = box(w, h, d), uv = g.attributes.uv;
  const dims = [[d, h], [d, h], [w, d], [w, d], [w, h], [w, h]];
  for (let f = 0; f < 6; f++) for (let k = 0; k < 4; k++) { const i = f * 4 + k; uv.setXY(i, uv.getX(i) * dims[f][0] / t, uv.getY(i) * dims[f][1] / t); }
  return g;
};

// ---------- sky ----------
const skyU = { top: { value: new THREE.Color() }, hor: { value: new THREE.Color() }, sunDir: { value: new THREE.Vector3() }, sunCol: { value: new THREE.Color() }, sunSize: { value: 0 } };
const sky = new THREE.Mesh(new THREE.SphereGeometry(1200, 32, 16), new THREE.ShaderMaterial({
  uniforms: skyU, side: THREE.BackSide, depthWrite: false, fog: false,
  vertexShader: `varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
  fragmentShader: `uniform vec3 top, hor, sunDir, sunCol; uniform float sunSize; varying vec3 vP;
    void main(){ float h = clamp(vP.y,0.,1.); vec3 c = mix(hor, top, pow(h, .55)); if(vP.y<0.) c = hor;
      float s = dot(normalize(vP), normalize(sunDir)); c += sunCol * (smoothstep(1.-sunSize, 1.-sunSize*.6, s) + .35*pow(max(s,0.), 24.)*step(.001,sunSize));
      gl_FragColor = vec4(c,1.); }`,
}));
sky.userData.sky = true; scene.add(sky);

// ---------- lights ----------
const hemi = new THREE.HemisphereLight('#ffffff', '#ffffff', 1); scene.add(hemi);
const sun = new THREE.DirectionalLight('#ffffff', 2); sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024); sun.shadow.bias = -0.0006; sun.shadow.normalBias = 0.03; sun.shadow.radius = 2;
scene.add(sun); scene.add(sun.target);
scene.fog = new THREE.Fog('#ffffff', 40, 600);

// ---------- D.B. Cooper world (original code-built sets; painted textures from paint.js) ----------
const DECK = 0.08, world = new THREE.Group(); scene.add(world);
const clouds=[]; // no billboard cloud assets are needed for these original sets
const waterU={t:{value:0},deep:{value:new THREE.Color('#315a70')},shal:{value:new THREE.Color('#739ba4')},glint:{value:new THREE.Color('#e6dfcc')}};
const mats={
  floor:toon({color:'#747269'}), wall:texM(P.plaster(31,36),2,2), cream:toon({color:'#e4d6ba'}), glass:toon({color:'#89aeb7',transparent:true,opacity:.62}),
  navy:toon({color:'#293b50'}), red:toon({color:'#8b4c4a'}), seat:toon({color:'#5b3941'}), metal:toon({color:'#727a7d'}), darkMetal:toon({color:'#3b4144'}), white:toon({color:'#e5e2d9'}),
  leather:toon({color:'#705338'}), paper:texM(P.plaster(18,43),1,1), folder:toon({color:'#9c7952'}), bill:toon({color:'#89936c'}), billLine:toon({color:'#d4c69c'}), tree:toon({color:'#4d6f50'}), leaf:toon({color:'#647d59'}),
  river:toon({color:'#3a748b'}), sand:texM(P.dirt(44),2,2), riverbank:texM(P.dirt(44),2,2,'#7c8177'), case:toon({color:'#393c40'}), gold:toon({color:'#b28a4f'}), lamp:toon({color:'#d9b875'}),
};
const sets={}; const ref={};
const stage=(name)=>{const g=new THREE.Group();g.name=name;g.visible=false;world.add(g);sets[name]=g;return g;};
const bx=(p,w,h,d,m,x,y,z,t=1)=>add(tbox(w,h,d,t),m,x,y,z,p);
const pl=(p,w,d,m,x,y,z)=>{const o=add(new THREE.PlaneGeometry(w,d),m,x,y,z,p,{cast:false});o.rotation.x=-Math.PI/2;return o;};
const cyl=(p,r1,r2,h,m,x,y,z,seg=12)=>add(new THREE.CylinderGeometry(r1,r2,h,seg),m,x,y,z,p);
const post=(p,a,b,r,m)=>{const A=new THREE.Vector3(...a),B=new THREE.Vector3(...b),v=B.clone().sub(A),o=add(new THREE.CylinderGeometry(r,r,v.length(),8),m,...A.clone().add(B).multiplyScalar(.5).toArray(),p);o.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),v.normalize());return o;};
const stone=(p,x,z,s=1)=>{const o=add(new THREE.DodecahedronGeometry(.26*s,0),mats.metal,x,.18*s,z,p);o.scale.set(1.5,0.75,1);return o;};
function tree3(p,x,z,h=4,seed=0){cyl(p,.16,.23,h*.42,M.trunk,x,h*.21,z,8);for(let i=0;i<3;i++){const m=add(new THREE.ConeGeometry(h*(.31-i*.045),h*.42,7),i===0?mats.tree:mats.leaf,x,h*(.5+i*.19),z,p);m.rotation.z=((seed+i)%3-1)*.06;}}
function plane727(p,x,y,z,s=1){const g=new THREE.Group();g.position.set(x,y,z);g.scale.setScalar(s);p.add(g);const fus=cyl(g,.52,.52,7.2,mats.white,0,0,0,16);fus.rotation.z=Math.PI/2;const nose=add(new THREE.SphereGeometry(.52,14,10),mats.white,3.55,0,0,g);nose.scale.set(1.5,1,1);const tail=add(new THREE.ConeGeometry(.52,1.2,12),mats.white,-3.75,0,0,g);tail.rotation.z=-Math.PI/2;bx(g,2.5,.12,1.7,mats.white,.1,-.12,0);bx(g,1.05,.12,.65,mats.metal,-.8,-.22,0);bx(g,.55,1.75,.12,mats.white,-3.05,.55,0);bx(g,1.5,.12,.8,mats.white,-3.15,.15,0);for(let i=0;i<9;i++){const w=add(new THREE.SphereGeometry(.075,10,8),mats.navy,2.55-i*.58,.08,.48,g);w.scale.set(1,.8,.32);}for(const zz of [-.46,.46]){const e=cyl(g,.19,.2,1.05,mats.darkMetal,-2.25,.12,zz,10);e.rotation.z=Math.PI/2;const e2=cyl(g,.17,.18,.75,mats.metal,-2.95,.15,zz,10);e2.rotation.z=Math.PI/2;}g.userData.base={x,y,z};return g;}
function case3(p,x,y,z,s=1){const g=new THREE.Group();g.position.set(x,y,z);g.scale.setScalar(s);p.add(g);bx(g,.72,.42,.5,mats.case,0,.22,0);bx(g,.32,.08,.06,mats.gold,0,.24,.28);post(g,[-.19,.43,.0],[.19,.43,0],.025,mats.gold);return g;}
function money3(p,x,y,z,s=1){const g=new THREE.Group();g.position.set(x,y,z);g.scale.setScalar(s);p.add(g);for(let k=0;k<7;k++){const yy=.012+k*.012;bx(g,.34,.009,.17,mats.bill,(k%2)*.008,yy,0,.6);for(let q=-1;q<=1;q++)bx(g,.22,.002,.003,mats.billLine,(k%2)*.008,yy+.006,q*.035,1);bx(g,.035,.014,.18,mats.gold,(k%2)*.008,yy,.005,1);}g.userData.baseY=y;return g;}
function ground(p,color=mats.floor,w=42,d=35){pl(p,w,d,color,0,0,0);}

// 1971 Seattle terminal: painted plaster, glass mullions, period airplane outside.
{
 const g=stage('airport');ground(g,mats.sand,50,38);bx(g,15,1.1,.35,mats.wall,0,6.55,-7,3);bx(g,15,.65,.35,mats.wall,0,.48,-7,3);for(let x=-7;x<=7;x+=2){bx(g,.13,5.45,.22,mats.wood,x,3.62,-6.78,1);if(x<6.5) {const glass=add(new THREE.PlaneGeometry(1.85,5.35),mats.glass,x+1,3.62,-6.84,g,{cast:false});glass.userData.ndSkip=true;}}
 bx(g,15,.22,.48,mats.wood,0,1.05,-6.68,1);bx(g,15,.22,.48,mats.wood,0,6.3,-6.68,1);
 for(let x=-5;x<=5;x+=2.5){bx(g,1.8,.55,.42,mats.navy,x,.34,-1.5,1);bx(g,1.8,.13,.42,mats.red,x,.68,-1.5,1);}
 bx(g,8,.08,1.2,mats.navy,0,.85,2.4,1);for(let i=-3;i<=3;i++)bx(g,.08,.8,.08,mats.gold,i*1.1,1.28,2.5,1);
 ref.airportPlane=plane727(g,0,2.7,-11,.9);bx(g,22,.12,5,mats.darkMetal,0,.03,-8,2);
 for(let i=-4;i<=4;i++)bx(g,.65,.025,.12,mats.cream,i*2,.05,-2,1);
}
// Aircraft cabin: rows of padded seats, oval windows, overhead bins and the briefcase.
{
 const g=stage('cabin');ground(g,mats.floor,18,24);bx(g,12,5.4,.28,mats.cream,0,3,-5.4,2);bx(g,12,.3,.4,mats.navy,0,5.72,-5.18,2);bx(g,12,.16,.35,mats.navy,0,.25,-5.15,2);
 for(let x=-4.5;x<=4.5;x+=1.5){cyl(g,.55,.55,.1,mats.navy,x,3.65,-5.18,16).rotation.x=Math.PI/2;cyl(g,.43,.43,.12,mats.glass,x,3.65,-5.1,16).rotation.x=Math.PI/2;}
 for(let row=0;row<4;row++)for(const x of [-2.5,-1.4,1.4,2.5]){const z=1.3-row*1.65;bx(g,.8,.55,.72,mats.seat,x,.52,z,1);bx(g,.8,1.15,.28,mats.red,x,.98,z-.22,1);bx(g,.78,.13,.28,mats.navy,x,.38,z-.36,1);post(g,[x,.12,z],[x,.48,z],.035,mats.metal);}
 bx(g,12,.35,.55,mats.navy,0,4.85,-3.8,1);for(let x=-5;x<=5;x+=2.5)bx(g,2.05,.55,.7,mats.cream,x,4.38,-3.75,2);
 ref.case=case3(g,.45,.74,1.4,1.0);ref.cabinWindow=null;
}
// Apron exchange: plane, rear stairs and ground crew/passenger path.
{
 const g=stage('exchange');ground(g,mats.sand,60,42);bx(g,34,.04,18,mats.darkMetal,0,.02,-4,4);for(let i=-7;i<=7;i++)bx(g,.75,.035,.16,mats.cream,i*2,.05,3,1);
 ref.exchangePlane=plane727(g,0,3.4,-7,1);ref.stairs=new THREE.Group();g.add(ref.stairs);for(let i=0;i<9;i++){bx(ref.stairs,1.3,.11,.8,mats.wood,-2.8+i*.38,.45+i*.29,-4.3+i*.03,1);}for(const x of [-3.0,.15])post(ref.stairs,[x,.12,-4.3],[x+2.7,3.35,-4.0],.07,mats.metal);
 bx(g,3,.08,1.2,mats.navy,-3,.1,1,1);ref.exchangeCash=money3(g,-3,.16,.9,.8);
}
// Stormy night: dark pine ridge, moving 727, rear airstair, canopy and rain streaks.
{
 const g=stage('jump');ground(g,M.grass,70,60);for(let i=-10;i<=10;i++)tree3(g,i*2.7,-14-(i%3),4.5+(i%4)*.4,i);
 ref.jumpPlane=plane727(g,0,6,-6,.9);ref.jumpStairs=new THREE.Group();g.add(ref.jumpStairs);for(let i=0;i<10;i++)bx(ref.jumpStairs,1.15,.11,.52,mats.wood,-5.15,.32+i*.58,-2.8-i*.28,1);post(ref.jumpStairs,[-5.75,.2,-2.5],[-5.75,5.9,-5.5],.06,mats.metal);post(ref.jumpStairs,[-4.55,.2,-2.5],[-4.55,5.9,-5.5],.06,mats.metal);ref.jumpChute=new THREE.Group();g.add(ref.jumpChute);const canopy=add(new THREE.SphereGeometry(1,18,10,0,Math.PI*2,0,Math.PI/2),mats.red,0,0,0,ref.jumpChute);canopy.scale.set(1.45,.62,1.05);for(let x=-1;x<=1;x++){post(ref.jumpChute,[x*.8,0,0],[0,-1.4,0],.02,mats.cream);}bx(ref.jumpChute,.22,.24,.18,mats.folder,0,-1.5,0,1);ref.jumpChute.position.set(-4.2,4.5,-3.5);
 for(let i=-9;i<=9;i++){post(g,[i*.85,8,2],[i*.85-.25,6,2],.012,mats.glass);}
}
// FBI search room with a painted case board, paper cards and pin/string geometry.
{
 const g=stage('search');ground(g,mats.floor,22,24);bx(g,11,6,.35,mats.wall,0,3,-5,3);bx(g,7,4,.14,mats.navy,0,3,-4.72,2);
 for(let i=0;i<8;i++){const x=-2.8+(i%4)*1.85,y=4.25-Math.floor(i/4)*1.75;bx(g,.95,1.25,.08,i%3===0?mats.folder:mats.paper,x,y,-4.55,1);bx(g,.5,.04,.04,mats.red,x,y+.18,-4.48,1);}
 for(let i=0;i<7;i++)post(g,[-2.8+(i%4)*1.85,4.25-Math.floor(i/4)*1.75,-4.42],[-2.8+((i+1)%4)*1.85,4.25-Math.floor((i+1)/4)*1.75,-4.42],.018,mats.red);
 bx(g,5,.25,2.2,mats.wood,0,1.35,0,1);for(let i=0;i<4;i++)bx(g,.55,.12,.75,mats.folder,-1.5+i,.75,-.2,1);bx(g,.6,.04,.45,mats.paper,1.2,1.52,.1,1);
 const lamp=add(new THREE.SphereGeometry(.18,10,8),mats.lamp,-1,2.4,-.1,g);lamp.scale.set(1.8,.35,1);
}
// Columbia River bank and forest: grass/dirt paint, reeds, rocks, driftwood, submerged cash.
{
 const g=stage('river');ground(g,M.grass,90,70);pl(g,23,11,mats.river,0,.022,-6.2);const bank=new THREE.Shape();bank.moveTo(-4.5,-.8);bank.lineTo(-3,-1.65);bank.lineTo(-1,-1.25);bank.lineTo(.5,-1.9);bank.lineTo(2.5,-1.15);bank.lineTo(4.5,-.75);bank.lineTo(3.8,.45);bank.lineTo(2.0,1.45);bank.lineTo(.1,1.05);bank.lineTo(-1.5,1.8);bank.lineTo(-3.6,1.0);bank.closePath();const bankMesh=add(new THREE.ShapeGeometry(bank),mats.riverbank,0,.035,.1,g,{cast:false});bankMesh.rotation.x=-Math.PI/2;
 for(let i=-12;i<=12;i++)tree3(g,i*3.3,-24-(i%4)*.8,3.8+(i%3)*.35,i);
 for(let i=0;i<18;i++){const x=-9+i*1.08;stone(g,x,-1.9+(i%3)*.28,.55);if(i%3===0){post(g,[x,.08,-1.25],[x+.03,.55,-1.3],.02,mats.leaf);post(g,[x+.2,.08,-1.05],[x+.28,.42,-1.1],.016,mats.leaf);}}
 for(let i=0;i<5;i++){const log=add(new THREE.CylinderGeometry(.08,.11,1.15,8),M.wood,-7+i*3.4,.1,-9+(i%2)*.45,g);log.rotation.z=Math.PI/2;}
 ref.riverCash=money3(g,.25,.06,-.25,1.05);
}
// Archive: painted shelves, boxed files and the unknown identity board.
{
 const g=stage('archive');ground(g,mats.floor,26,25);bx(g,14,7,.35,mats.navy,0,3.55,-5,3);for(let y=1.2;y<6.5;y+=1.65){bx(g,13,.14,.75,mats.wood,0,y,-4.45,1);for(let i=0;i<10;i++){const col=[mats.folder,mats.paper,mats.red,mats.navy][(i+Math.round(y))%4];bx(g,.72,1.18,.5,col,-5.65+i*1.25,y+.63,-4.3,1);bx(g,.25,.045,.03,mats.cream,-5.65+i*1.25,y+.68,-4.02,1);}}
 bx(g,5,.25,2.2,mats.wood,0,1.3,0,1);for(let i=0;i<4;i++)bx(g,.75,.3,.9,mats.folder,-1.25+i*.85,1.62,.1,1);ref.finalFile=bx(g,1.8,.08,1.15,mats.paper,0,1.78,.18,1);
}
const helmet = new THREE.Group(); scene.add(helmet); // retained engine slot; no helmet is used in this story
// ---------- cards ----------
const CW = 1200, CH = 2000, CM = 2.25; // canvas px, card height in metres (design 600x1000 -> 2.25 m)
const cardGeo = new THREE.PlaneGeometry(CM * 0.6, CM); cardGeo.translate(0, CM / 2 - CM * 0.025, 0);
const blobTex = P.tex(P.radial('20,14,30', 0.6));
class Card {
  constructor(scale = 1) {
    [this.c, this.g] = (() => { const c = document.createElement('canvas'); c.width = CW; c.height = CH; return [c, c.getContext('2d')]; })();
    this.t = new THREE.CanvasTexture(this.c); this.t.colorSpace = THREE.SRGBColorSpace; this.t.anisotropy = 4;
    this.mat = new THREE.MeshBasicMaterial({ map: this.t, transparent: true, alphaTest: 0.02, side: THREE.DoubleSide, fog: true });
    this.mesh = new THREE.Mesh(cardGeo, this.mat); this.mesh.userData.nd = cardNd(this.t); this.mesh.castShadow = true;
    this.mesh.customDepthMaterial = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, map: this.t, alphaTest: 0.5 });
    this.blob = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: blobTex, transparent: true, depthWrite: false, fog: true }));
    this.blob.rotation.x = -Math.PI / 2; this.blob.userData.ndSkip = true; this.blob.renderOrder = 1;
    scene.add(this.mesh); scene.add(this.blob); this.key = ''; this.mesh.visible = this.blob.visible = false;
  }
  draw(key, fn) {
    if (key === this.key) return; this.key = key;
    const g = this.g; g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, CW, CH); g.setTransform(CW / 600, 0, 0, CH / 1000, 0, 0);
    const p = new T.Pen(g); fn(p); this.t.needsUpdate = true;
  }
}
const cards = []; const getCard = (i) => cards[i] || (cards[i] = new Card());

// ---------- render targets & post ----------
const rtColor = new THREE.WebGLRenderTarget(W, H, { samples: 2, type: THREE.HalfFloatType });
const rtNd = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter });
const rtInk = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType });
const fsCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1), fsGeo = new THREE.PlaneGeometry(2, 2);
const fs = (mat) => { const s = new THREE.Scene(); s.add(new THREE.Mesh(fsGeo, mat)); return s; };
const inkU = { col: { value: rtColor.texture }, nd: { value: rtNd.texture }, res: { value: new THREE.Vector2(W, H) }, px: { value: 1.6 }, fogCol: { value: new THREE.Color() },
  sat: { value: 1.08 }, lift: { value: new THREE.Color(0, 0, 0) }, gain: { value: new THREE.Color(1, 1, 1) }, vig: { value: 0.22 }, flash: { value: 0 } };
const inkScene = fs(new THREE.ShaderMaterial({ uniforms: inkU, vertexShader: `varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position.xy,0.,1.); }`,
  fragmentShader: `uniform sampler2D col, nd; uniform vec2 res; uniform float px, sat, vig, flash; uniform vec3 fogCol, lift, gain; varying vec2 vUv;
  float edgeAt(vec2 uv, float r){
    vec4 c = texture2D(nd, uv); if (dot(c.rgb,c.rgb) < .01) return 0.; float d = c.a; vec3 n = c.rgb*2.-1.;
    float e = 0.; float rr = r * clamp(7./d, .62, 1.25);
    for (int i=0;i<16;i++){ float a = float(i)*.785398 + (i>7 ? .39 : 0.); float k = i>7 ? .5 : 1.;
      vec2 o = vec2(cos(a), sin(a))*rr*k/res; vec4 s = texture2D(nd, uv+o);
      float ds = s.a; bool card = dot(s.rgb,s.rgb) < .01;
      if (card && ds > 0.) continue;            // character cards: never outlined by the world ink
      if (card) ds = 1e4;                        // sky
      vec3 ns = s.rgb*2.-1.;
      e = max(e, smoothstep(.006, .02, (ds - d)/d));                           // depth jump, near side only
      if (!card && abs(ds-d)/d < .06) e = max(e, smoothstep(.88, .72, dot(n, ns)) * .9); // crease
    }
    return e * (1. - smoothstep(140., 520., d)*.8);
  }
  void main(){
    vec3 c = texture2D(col, vUv).rgb;
    float e = edgeAt(vUv, px);
    c = mix(c, vec3(.012,.01,.014), e);
    if (flash < -0.5) c = vec3(e);
    float l = dot(c, vec3(.299,.587,.114)); c = mix(vec3(l), c, sat);
    c = c*gain + lift;
    vec2 q = vUv-.5; c *= 1. - vig*dot(q*vec2(1.,.75), q*vec2(1.,.75))*2.2;
    c = mix(c, vec3(1.), flash);
    gl_FragColor = vec4(c,1.); }` }));
const dofU = { src: { value: rtInk.texture }, nd: { value: rtNd.texture }, res: { value: new THREE.Vector2(W, H) }, focus: { value: 5 }, cinf: { value: 0 }, near: { value: 1 } };
const dofScene = fs(new THREE.ShaderMaterial({ uniforms: dofU, vertexShader: `varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position.xy,0.,1.); }`,
  fragmentShader: `uniform sampler2D src, nd; uniform vec2 res; uniform float focus, cinf, near; varying vec2 vUv;
  float coc(vec2 uv){ float d = texture2D(nd, uv).a; if (d <= 0.) d = 2000.; float k = 1. - focus/d; return k > 0. ? cinf*k : min(-k*cinf*near, cinf*1.4); }
  void main(){
    float c0 = coc(vUv);
    if (cinf < .5 || c0 < .6) { gl_FragColor = linearToOutputTexel(vec4(texture2D(src, vUv).rgb, 1.)); return; }
    vec3 acc = vec3(0.); float wsum = 0.;
    for (int i=0;i<48;i++){ float fi = float(i); float r = sqrt((fi+.5)/48.); float a = fi*2.39996;
      vec2 o = vec2(cos(a), sin(a))*r*c0/res; float cs = coc(vUv+o);
      float w = smoothstep(r*c0-1.5, r*c0+.5, cs + .5);
      acc += texture2D(src, vUv+o).rgb*w; wsum += w; }
    gl_FragColor = linearToOutputTexel(vec4(acc/max(wsum,1e-3), 1.)); }` }));
// final copy with sRGB handled by the renderer output (we render to screen with linear->sRGB in the shader chunk)
dofScene.children[0].material.toneMapped = false;

// ---------- per-frame state ----------
const tmpV = new THREE.Vector3();
function applyLight(L, f) {
  hemi.color.set(L.sky); hemi.groundColor.set(L.ground); hemi.intensity = L.hemi;
  sun.color.set(L.sun); sun.intensity = L.sunI;
  scene.fog.color.set(L.fog); scene.fog.near = L.fogNear; scene.fog.far = L.fogFar;
  skyU.top.value.set(L.skyTop); skyU.hor.value.set(L.skyHor); skyU.sunCol.value.set(L.sunDisc || '#000'); skyU.sunSize.value = L.sunSize || 0;
  inkU.sat.value = L.sat; inkU.gain.value.set(L.gain || '#ffffff'); inkU.lift.value.set(L.lift || '#000000');
  waterU.deep.value.set(L.waterDeep); waterU.shal.value.set(L.waterShal); waterU.glint.value.set(L.glint);
}
function placeSun(L, focus) {
  // sun direction from azimuth/elevation in world space
  const az = rx(L.az), el = rx(L.el); tmpV.set(Math.cos(el) * Math.cos(az), Math.sin(el), Math.cos(el) * Math.sin(az));
  skyU.sunDir.value.copy(tmpV);
  sun.position.copy(focus).addScaledVector(tmpV, 80); sun.target.position.copy(focus);
  const ext = L.shadowExt || 30, sc = sun.shadow.camera; sc.left = -ext; sc.right = ext; sc.top = ext; sc.bottom = -ext; sc.near = 1; sc.far = 200; sc.updateProjectionMatrix();
}

function worldState(S, f) {
  for (const [name,g] of Object.entries(sets)) g.visible=name===S.location;
  const sec=f/30;
  if(ref.airportPlane){ref.airportPlane.position.x=0.08*Math.sin(sec*.35);}
  if(ref.exchangePlane){ref.exchangePlane.position.x=0.06*Math.sin(sec*.4);}
  if(ref.jumpPlane){ref.jumpPlane.position.x=-.7+sec*.08;ref.jumpPlane.position.y=7+.12*Math.sin(sec*1.1);}
  if(ref.jumpChute){const p=Math.max(0,Math.min(1,(f-(S.jumpStart||1005))/90));ref.jumpChute.position.y=4.6-2.3*p;ref.jumpChute.position.x=-4.0+.4*Math.sin(sec*1.4);}
  if(ref.case?.children?.length){const lid=ref.case.children[0];if(lid)lid.rotation.x=-.02*Math.sin(sec*.9);}
  if(ref.riverCash){ref.riverCash.position.y=.04+.015*Math.sin(sec*2);}
  waterU.t.value=sec;
}
function drawActors(list, cam) {
  cards.forEach((c) => { c.mesh.visible = c.blob.visible = false; });
  list.forEach((a, i) => {
    const c = getCard(i);
    c.draw(a.key, a.draw);
    c.mesh.visible = true; c.mesh.position.set(a.x, a.y, a.z);
    const s = a.s || 1; c.mesh.scale.set(s * (a.flip ? -1 : 1), s, s);
    c.mesh.rotation.set(0, Math.atan2(cam.position.x - a.x, cam.position.z - a.z) + (a.yaw || 0), a.roll || 0);
    c.mat.color.set(a.tint || '#ffffff'); c.mat.opacity = a.alpha ?? 1;
    c.mesh.castShadow = a.shadow !== false;
    c.mesh.renderOrder = a.order || 2;
    if (a.blob !== false && a.y < DECK + 0.5) { c.blob.visible = true; c.blob.position.set(a.x, (a.ground ?? DECK) + 0.02, a.z); c.blob.scale.set(0.95 * s, 0.6 * s, 1); }
  });
}

const helmetState = (h) => {
  helmet.visible = !!h; if (!h) return;
  helmet.position.set(h.x, h.y, h.z); helmet.rotation.set(h.rx || 0, h.ry || 0, h.rz || 0); helmet.scale.setScalar(h.s || 0.17);
};

const swapForNd = (on) => {
  scene.traverse((o) => {
    if (!o.isMesh) return;
    if (on) {
      o.userData.mat0 = o.material;
      if (o.userData.ndSkip) { o.userData.vis0 = o.visible; o.visible = false; return; }
      if (o === sky || o.userData.sky) { o.userData.vis0 = o.visible; o.visible = false; return; }
      o.material = o.userData.nd || ndMat;
    } else {
      o.material = o.userData.mat0; if (o.userData.vis0 !== undefined) { o.visible = o.userData.vis0; delete o.userData.vis0; }
    }
  });
};

window.renderFrame = (f) => {
  const S = shotAt(f), L = lightFor(S, f), C = camAt(f);
  applyLight(L, f);
  camera.position.set(...C.pos); camera.up.set(0, 1, 0); camera.lookAt(...C.look); camera.rotateZ(rx(C.roll || 0));
  camera.fov = C.fov; camera.updateProjectionMatrix(); camera.updateMatrixWorld();
  const W_ = worldAt(f); worldState(W_, f);
  placeSun(L, new THREE.Vector3(...(C.shadowAt || C.look)));
  drawActors([...actorsAt(f, T), ...fxAt(f, T)], camera);
  helmetState(W_.helmet);
  sky.position.copy(camera.position);
  for (const c of clouds) c.quaternion.copy(camera.quaternion);
  // pass A: colour
  renderer.setRenderTarget(rtColor); renderer.setClearColor(0x000000, 1); renderer.clear(); renderer.render(scene, camera);
  // pass B: normal + depth
  const fog = scene.fog; scene.fog = null; const sm = renderer.shadowMap.enabled; renderer.shadowMap.enabled = false; renderer.shadowMap.autoUpdate = false;
  swapForNd(true); renderer.setRenderTarget(rtNd); renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(scene, camera); swapForNd(false);
  scene.fog = fog; renderer.shadowMap.enabled = sm; renderer.shadowMap.autoUpdate = true;
  if (window.DEBUG_ND) { const dm = new THREE.MeshBasicMaterial({ map: rtNd.texture }); const ds = fs(dm); renderer.setRenderTarget(null); renderer.render(ds, fsCam); return true; }
  // ink + grade
  const D = dofAt(f);
  inkU.px.value = 2.0; inkU.flash.value = window.DEBUG_E ? -1 : (C.flash || 0); inkU.vig.value = L.vig ?? 0.22;
  renderer.setRenderTarget(rtInk); renderer.render(inkScene, fsCam);
  // lens
  dofU.focus.value = D.focus; dofU.cinf.value = D.cinf * (H / 1920); dofU.near.value = D.near ?? 1;
  renderer.setRenderTarget(null); renderer.render(dofScene, fsCam);
  drawCaption(f);
  return true;
};
window.TOTAL = TOTAL;
window.ready = true;
