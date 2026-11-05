import fs from 'node:fs';
import path from 'node:path';
import {spawn,execFileSync} from 'node:child_process';
import {once} from 'node:events';
import {JSDOM} from 'jsdom';
import {Resvg} from '@resvg/resvg-js';
const dom=new JSDOM('<!doctype html><html><body></body></html>');
globalThis.window=dom.window;globalThis.document=dom.window.document;globalThis.self=globalThis;globalThis.SVGElement=dom.window.SVGElement;
const THREE=await import('three');
const {SVGRenderer}=await import('three/addons/renderers/SVGRenderer.js');
const ROOT=path.dirname(new URL(import.meta.url).pathname);const OUT=ROOT;
const W=720,H=1280,FPS=30;
const meta=JSON.parse(fs.readFileSync(path.join(ROOT,'audio_timeline.json'),'utf8'));
const duration=meta.duration,clips=meta.clips,captions=meta.captions;
const WAV=path.join(ROOT,'master_mix.wav');
const ffmpeg=execFileSync(path.resolve(ROOT,'../../.venv/bin/python'),['-c','from imageio_ffmpeg import get_ffmpeg_exe; print(get_ffmpeg_exe())'],{encoding:'utf8'}).trim();
const clamp=(v,a=0,b=1)=>Math.min(b,Math.max(a,v));
const hex=c=>new THREE.Color(c);
const mat=(color,opts={})=>new THREE.MeshLambertMaterial({color,flatShading:true,...opts});
const basic=(color,opts={})=>new THREE.MeshBasicMaterial({color,...opts});
const group=(parent,x=0,y=0,z=0)=>{const g=new THREE.Group();g.position.set(x,y,z);parent.add(g);return g;};
function outline(m,width=1.8){const e=new THREE.LineSegments(new THREE.EdgesGeometry(m.geometry,25),new THREE.LineBasicMaterial({color:'#18233c',linewidth:width}));m.add(e);return m;}
function box(parent,w,h,d,color,x=0,y=0,z=0,opts={}){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat(color,opts));m.position.set(x,y,z);outline(m,1.6);parent.add(m);return m;}
function sphere(parent,r,color,x=0,y=0,z=0,sx=1,sy=1,sz=1,segments=12){const m=new THREE.Mesh(new THREE.SphereGeometry(r,segments,Math.max(8,Math.floor(segments*.65))),mat(color));m.position.set(x,y,z);m.scale.set(sx,sy,sz);parent.add(m);return m;}
function cyl(parent,rt,rb,h,color,x=0,y=0,z=0,segments=10){const m=new THREE.Mesh(new THREE.CylinderGeometry(rt,rb,h,segments),mat(color));m.position.set(x,y,z);outline(m,1.35);parent.add(m);return m;}
function cone(parent,r,h,color,x=0,y=0,z=0,segments=8){const m=new THREE.Mesh(new THREE.ConeGeometry(r,h,segments),mat(color));m.position.set(x,y,z);outline(m,1.55);parent.add(m);return m;}
function barBetween(parent,a,b,r,color){const A=new THREE.Vector3(...a),B=new THREE.Vector3(...b),dir=B.clone().sub(A),m=new THREE.Mesh(new THREE.CylinderGeometry(r,r,dir.length(),8),mat(color));m.position.copy(A.clone().add(B).multiplyScalar(.5));m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),dir.normalize());parent.add(m);return m;}
function plane(parent,w,d,color,x=0,y=0,z=0){const m=new THREE.Mesh(new THREE.PlaneGeometry(w,d),mat(color));m.rotation.x=-Math.PI/2;m.position.set(x,y,z);parent.add(m);return m;}
function lightScene(scene,bg,ground){scene.background=new THREE.Color(bg);scene.add(new THREE.HemisphereLight(0xffffff,0x68819c,2.0));const sun=new THREE.DirectionalLight(0xfff1d1,2.8);sun.position.set(-4,9,7);scene.add(sun);const fill=new THREE.DirectionalLight(0x91c7ff,.75);fill.position.set(5,5,-4);scene.add(fill);plane(scene,38,38,ground,0,-.05,0);}
function character(scene,x,z,{coat='#528459',scarf='#D4A95F',hair='#111827',pants='#111827',suit=false,host=false}={}){
 // Original 2D cutout over a code-built 3D set. Proportions follow the supplied mromidev measurements: adult ~3.5 head-heights, head H/W ~0.93, limbs ~5% of head width.
 const root=group(scene,x,0,z),body=group(root,0,0,0),head=group(body,0,0,0);
 const arms=[group(body),group(body)],legs=[group(body),group(body)];
 root.scale.setScalar(host ? 0.88 : 0.86);
 const mouth={scale:new THREE.Vector3(1,.08,1)},lip={scale:new THREE.Vector3(1,.04,1)};
 root.userData.characterStyle={coat:suit?'#18233c':coat,scarf,hair,pants,suit,host};
 return {root,body,head,mouth,lip,arms,legs,host};
}
function billStack(scene,x,z,n=3,scale=1){for(let i=0;i<n;i++){box(scene,.68*scale,.065*scale,.34*scale,'#4ca56c',x,.08*scale+i*.07*scale,z);box(scene,.1*scale,.07*scale,.36*scale,'#d9c57b',x,.08*scale+i*.07*scale,z);}}
function planeModel(scene,x,y,z,scale=1){const g=group(scene,x,y,z);const fus=cyl(g,.34,.42,4.2,'#F4F5F7',0,0,0,14);fus.rotation.z=Math.PI/2;const nose=sphere(g,.34,'#FFFFFF',2.1,0,0,1.3,1,1,10);box(g,2.1,.12,.8,'#486B93',0,-.02,0);box(g,.62,.85,.22,'#B6575A',-1.6,.16,0);box(g,.3,.9,.1,'#D4A95F',-1.75,.63,0);for(let i=-3;i<=3;i++){sphere(g,.07,'#18233c',i*.46,.05,.36,1,.7,.35,8);}g.scale.setScalar(scale);return g;}
function tree(scene,x,z,h=3,color='#528459') {cyl(scene,.12,.17,h*.42,'#B86B25',x,h*.21,z,7);for(let k=0;k<3;k++)cone(scene,h*(.32-k*.04),h*.42,k===0?'#496F4B':color,x,h*.46+k*h*.2,z,8);}
function cloud(scene,x,y,z,scale=1){const g=group(scene,x,y,z);for(const [dx,dy,r,sx,sy] of [[-.32,0,.34,.95,.85],[0,.12,.45,1.1,.9],[.38,0,.3,1,.8]]){const m=new THREE.Mesh(new THREE.SphereGeometry(r,10,7),basic('#f7f2e5'));m.position.set(dx*scale,dy*scale,0);m.scale.set(sx*scale,sy*scale,.55*scale);g.add(m);}return g;}
function questionMark(scene,x,y,z,scale=1){const g=group(scene,x,y,z);const pts=[[-.30,.30,0],[-.34,.56,0],[-.28,.82,0],[-.08,1.02,0],[.18,1.02,0],[.36,.86,0],[.35,.63,0],[.19,.47,0],[.035,.35,0],[.02,.16,0]].map(p=>new THREE.Vector3(...p));const curve=new THREE.CatmullRomCurve3(pts);const tube=new THREE.Mesh(new THREE.TubeGeometry(curve,32,.085,8,false),mat('#f0cf79'));g.add(tube);sphere(g,.105,'#f0cf79',.02,-.02,.02,1,1,.9,10);g.scale.setScalar(scale);return g;}
function parachute(scene,x,y,z,scale=1){const g=group(scene,x,y,z);const canopy=new THREE.Mesh(new THREE.SphereGeometry(.72,12,8,0,Math.PI*2,0,Math.PI*.58),mat('#df574b'));canopy.position.y=.8;canopy.scale.set(1.4,.7,1);g.add(canopy);for(const dx of [-.5,0,.5])barBetween(g,[dx*.8,.75,0],[0,.05,0],.018,'#f2e4c4');const payload=box(g,.25,.24,.2,'#a78147',0,-.08,0);g.scale.setScalar(scale);return g;}
function sceneBase(bg,ground){const s=new THREE.Scene();lightScene(s,bg,ground);return s;}
function buildRiver(){
 const s=sceneBase('#4C83C7','#B98A5C');plane(s,30,3.2,'#4C8997',0,.01,-3.2);const hill=new THREE.Mesh(new THREE.SphereGeometry(1,12,8),basic('#708F63'));hill.position.set(0,.55,-8.1);hill.scale.set(8,.85,.55);s.add(hill);
 sphere(s,.42,'#D1AA69',-2.9,5.35,-7.1,1,1,.22,12);cloud(s,-1.35,4.75,-6.5,1.05);cloud(s,1.55,5.2,-7,.95);cloud(s,3.05,4.55,-6.3,.82);
 for(let i=0;i<5;i++)tree(s,-4.4+i*2.2,-7.0,2.1+(i%2)*.3,'#528459');billStack(s,-.95,.6,3,1.35);billStack(s,-.05,1.05,2,1.15);billStack(s,.42,.28,2,1.05);
 const host=character(s,1.05,.4,{host:true,coat:'#44566B',scarf:'#B87A4B'});const family=character(s,-1.0,1.2,{coat:'#B6575A',scarf:'#D4A95F',hair:'#111827'});family.root.scale.setScalar(.78);return {scene:s,host,extra:[family],props:[]};
}
function buildAirport(){
 const s=sceneBase('#4C83C7','#BA8759');box(s,12,5,.25,'#B77F58',0,3.2,-4);for(let x=-4.5;x<=4.6;x+=1.5){box(s,1.1,2.3,.28,'#6E9EAD',x,3.0,-3.82);box(s,1.1,.12,.31,'#D4A95F',x,4.2,-3.7);}
 box(s,14,.1,.18,'#D1AA69',0,.02,0);for(let i=-5;i<=5;i++)box(s,.5,.035,.08,'#E3C891',i*1.1,.05,1.4);
 planeModel(s,.25,4.2,-3.0,.58);const host=character(s,.9,1.2,{host:true,coat:'#44566B',scarf:'#B87A4B'});const dan=character(s,-1.1,.8,{coat:'#486B93',scarf:'#B6575A',hair:'#111827',pants:'#111827',suit:true});
 return {scene:s,host,extra:[dan],props:[]};
}
function buildCabin(){
 const s=sceneBase('#566E9B','#AD7B52');box(s,10,6,.24,'#B79A70',0,3,-3);for(let x=-4;x<=4;x+=1.35){const w=box(s,.82,.72,.12,'#73AAB5',x,3.75,-2.8);w.rotation.z=.04;box(s,.06,.86,.14,'#D4A95F',x,3.75,-2.68);}
 for(let row=0;row<3;row++){const z=-1+row*1.1;for(let x=-1.8;x<=1.8;x+=1.2){box(s,.62,.62,.5,row===1?'#B6575A':'#486B93',x,.45,z);box(s,.62,.7,.3,row===1?'#B36B4F':'#528459',x,.93,z-.08);}}
 const host=character(s,-1.1,1.4,{host:true,coat:'#44566B',scarf:'#B87A4B'});const dan=character(s,0,1.1,{coat:'#303743',scarf:'#a94d4a',hair:'#322a2a',pants:'#212b38',suit:true});const crew=character(s,1.1,1.0,{coat:'#374958',scarf:'#d1d7d5',hair:'#4c3a31'});
 box(s,.65,.48,.48,'#282f39',0,.32,.48);box(s,.53,.07,.36,'#ad4647',0,.43,.48);for(let i=0;i<4;i++)parachute(s,-2.4+i*.4,.15,-.2,.26);
 return {scene:s,host,extra:[dan,crew],props:[]};
}
function buildExchange(){
 const s=sceneBase('#223056','#D98222');planeModel(s,.2,4.3,-3.5,.75);for(let i=-4;i<=4;i++){box(s,.5,.04,.08,'#D1AA69',i*.9,.02,1.7);}
 const host=character(s,-1.0,1.4,{host:true,coat:'#44566B',scarf:'#B87A4B'});const crew=character(s,.65,1.1,{coat:'#528459',scarf:'#D4A95F',hair:'#111827'});const passenger=character(s,1.45,1.3,{coat:'#B36B4F',scarf:'#D4A95F',hair:'#111827'});
 box(s,.55,.38,.42,'#735339',-.25,.22,1.1);box(s,.46,.05,.34,'#a68a5f',-.25,.42,1.1);return {scene:s,host,extra:[crew,passenger],props:[]};
}
function buildJump(){
 const s=sceneBase('#223056','#3A5372');for(let i=-5;i<=5;i++)tree(s,i*.92,-3.4-(i%2)*.5,3.3+(i%3)*.45,'#528459');
 const p=planeModel(s,0,4.25,-4,.72);p.rotation.z=-.06;const chute=parachute(s,.2,3.25,-.8,.55);const host=character(s,-1.0,.8,{host:true,coat:'#44566B',scarf:'#B87A4B'});const city=box(s,6,.18,.35,'#d29863',0,.12,-5.5);for(let i=0;i<9;i++)box(s,.18,.35,.18,'#e8c477',-2.7+i*.67,.42,-5.3);
 const rain=[];for(let i=0;i<12;i++){const r=barBetween(s,[-4+i*.7,4+(i%4)*.5,1.5],[-4+i*.7-.08,3.5+(i%4)*.5,1.5],.012,'#81aabd');rain.push(r);}return {scene:s,host,extra:[],props:[chute,p,...rain]};
}
function buildSearch(){
 const s=sceneBase('#486B93','#557750');for(let i=-5;i<=5;i++)tree(s,i*.93,-2.4-(i%3)*.65,3.6+(i%4)*.25,i%2?'#528459':'#496F4B');
 const host=character(s,-1.0,1.05,{host:true});const investigator=character(s,1.0,.6,{coat:'#D4A95F',scarf:'#486B93',hair:'#111827'});box(s,.9,.07,.7,'#947448',.1,.62,.55);box(s,.82,.035,.58,'#e2cc91',.1,.67,.55);for(let i=0;i<6;i++){const p=sphere(s,.08,'#bc5548',-.2+(i%3)*.28,.70,.57+Math.floor(i/3)*.18,1,1,.3,8);}barBetween(s,[-.18,.72,.63],[.35,.72,.63],.018,'#b54643');const lantern=group(s,1.45,1.4,1.1);box(lantern,.18,.28,.18,'#b87d36',0,0,0);sphere(lantern,.15,'#ffe19a',0,.05,.04,.7,1,.7,8);return {scene:s,host,extra:[investigator],props:[lantern]};
}
function buildArchive(){
 const s=sceneBase('#4C83C7','#D98222');box(s,12,7,.35,'#18345F',0,3.5,-3.2);for(let row=0;row<3;row++){box(s,9,.16,.65,'#B77F58',0,1.4+row*1.65,-2.7);for(let i=-4;i<=4;i++){const c=['#D4A95F','#6E9EAD','#B6575A','#528459'][((i+row+8)%4)];box(s,.64,1.05,.48,c,i*1.0,1.95+row*1.65,-2.65);box(s,.22,.07,.025,'#eee3c6',i*1.0,2.08+row*1.65,-2.39);}}
 const host=character(s,-1.0,1.3,{host:true,coat:'#44566B',scarf:'#B87A4B'});const board=box(s,2.4,2.2,.12,'#486B93',1.35,3.0,-1.5);const q=questionMark(s,1.45,2.25,-1.32,1.15);return {scene:s,host,extra:[],props:[board,q]};
}
const BUILDERS=[buildAirport,buildCabin,buildExchange,buildJump,buildSearch,buildRiver,buildArchive];
const scenes=BUILDERS.map(f=>f());
// Original 3D set meshes plus original code-drawn 2D character cutouts; all movement is procedural and narration-timed.
function readWaveEnvelope(file){const b=fs.readFileSync(file);let pos=12,channels=2,rate=48000,bits=16,dataOff=0,dataLen=0;while(pos+8<b.length){let id=b.toString('ascii',pos, pos+4),len=b.readUInt32LE(pos+4);if(id==='fmt '){channels=b.readUInt16LE(pos+10);rate=b.readUInt32LE(pos+12);bits=b.readUInt16LE(pos+22);}if(id==='data'){dataOff=pos+8;dataLen=len;break;}pos+=8+len+(len%2);}const step=Math.floor(rate*.08),total=Math.floor((dataLen/(bits/8)/channels));const out=[];for(let s=0;s<total;s+=step){let sum=0,c=0;for(let i=s;i<Math.min(total,s+step);i+=4){const v=b.readInt16LE(dataOff+i*channels*2)/32768;sum+=v*v;c++;}out.push(Math.sqrt(sum/Math.max(1,c)));}return out;}
const rms=readWaveEnvelope(WAV);const renderer=new SVGRenderer();renderer.setSize(W,H);renderer.setPrecision(2);
const CAMERA_PROFILES={
 0:[[-.15,1.85,3.72,14.6,39,0],[-.35,2.05,3.65,13.3,35,0],[.2,2.35,3.65,11.8,31.5,3.2]],
 1:[[-.25,1.9,3.75,14.5,38,0],[.15,2.0,3.65,13.1,34,0],[.45,2.35,3.62,11.8,31.5,3.2]],
 2:[[-.25,1.9,3.72,14.4,38,0],[.2,2.0,3.65,13.0,34,0],[.55,2.35,3.62,11.7,31.5,3.2]],
 3:[[.0,2.0,3.8,15.0,39,0],[.3,2.2,3.7,13.5,35,0],[-.35,2.45,3.65,12.0,32,3.2]],
 4:[[-.1,1.95,3.72,14.2,38,0],[.35,2.1,3.65,12.8,34,0],[-.2,2.35,3.62,11.5,31.5,3.2]],
 5:[[.0,1.8,3.72,14.6,39,0],[.35,2.0,3.65,13.3,35,0],[-.1,2.35,3.62,11.8,31.5,3.2]],
 6:[[.45,2.3,3.75,14.4,38,0],[.7,2.35,3.68,13.0,34,0],[-.45,2.15,3.6,11.8,31.5,3.2]],
};
const lerp=(a,b,p)=>a+(b-a)*p;
const ease3=p=>{p=clamp(p);return p*p*p*(p*(p*6-15)+10);};
const xml=new dom.window.XMLSerializer();
function esc(s){return String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');}
function projectPoint(v,cam){const p=v.clone().project(cam);return {x:p.x*W/2,y:-p.y*H/2};}
function characterSvg(char,cam,t,local,index,isHost=false,amp=0){
 const root=char.root,style=root.userData.characterStyle||{},pos=root.getWorldPosition(new THREE.Vector3()),scaleWorld=root.scale.y;
 const foot=projectPoint(new THREE.Vector3(pos.x,pos.y+.02,pos.z),cam),top=projectPoint(new THREE.Vector3(pos.x,pos.y+3.5*scaleWorld,pos.z),cam);
 const height=clamp(foot.y-top.y,300,700),s=height/850,bob=1.1*Math.sin(local*4.4+index*.7),wave=Math.sin(local*5.2+index)*8;
 const coat=style.coat||'#528459',scarf=style.scarf||'#D4A95F',hair=style.hair||'#111827',pants=style.pants||'#192334';
 const mouthH=clamp(6+amp*19,4,26);
 const hat=isHost?`<path d="M-106 -786 Q-90 -838 0 -840 Q87 -838 106 -786 L113 -772 L-113 -772Z" fill="#263653" stroke="#171723" stroke-width="8"/><path d="M-126 -780 Q0 -799 126 -780 Q111 -760 0 -764 Q-111 -760 -126 -780Z" fill="#3b4e70" stroke="#171723" stroke-width="7"/>`:`<path d="M-102 -780 Q-72 -822 -18 -817 Q52 -828 103 -780 Q44 -798 -10 -786 Q-62 -773 -102 -780Z" fill="${hair}" stroke="#171723" stroke-width="7"/>`;
 const jacket=style.suit?`<path d="M-69 -546 Q-104 -531 -100 -494 L-90 -288 Q0 -263 90 -288 L100 -494 Q104 -531 69 -546 L0 -514Z" fill="${coat}" stroke="#171723" stroke-width="8"/><path d="M-35 -540 L0 -488 L35 -540 L18 -426 L-17 -426Z" fill="#eee7d9" stroke="#171723" stroke-width="6"/><path d="M0 -488 L17 -428 L0 -382 L-17 -428Z" fill="#a94d4a" stroke="#171723" stroke-width="5"/>`:`<path d="M-69 -546 Q-104 -531 -100 -494 L-90 -288 Q0 -263 90 -288 L100 -494 Q104 -531 69 -546 L0 -518Z" fill="${coat}" stroke="#171723" stroke-width="8"/><path d="M-34 -540 L0 -490 L34 -540 L17 -436 L-17 -436Z" fill="#f5eee1" stroke="#171723" stroke-width="6"/><path d="M0 -490 L17 -432 L0 -384 L-17 -432Z" fill="${scarf}" stroke="#171723" stroke-width="5"/><circle cx="-38" cy="-363" r="5" fill="#e7c887"/><circle cx="38" cy="-363" r="5" fill="#e7c887"/>`;
 const armL=`<path d="M-72 -527 Q-123 -487 -111 -407 L-127 -338" fill="none" stroke="#171723" stroke-width="19" stroke-linecap="round"/><path d="M-72 -527 Q-123 -487 -111 -407 L-127 -338" fill="none" stroke="${coat}" stroke-width="11" stroke-linecap="round"/><circle cx="-129" cy="-330" r="10" fill="#171723"/>`;
 const armR=`<g transform="rotate(${wave*.25} 72 -527)"><path d="M72 -527 Q123 -487 111 -407 L128 -340" fill="none" stroke="#171723" stroke-width="19" stroke-linecap="round"/><path d="M72 -527 Q123 -487 111 -407 L128 -340" fill="none" stroke="${coat}" stroke-width="11" stroke-linecap="round"/><circle cx="130" cy="-332" r="10" fill="#171723"/></g>`;
 const face=`<ellipse cx="0" cy="-671" rx="108" ry="120" fill="#f8f5ed" stroke="#171723" stroke-width="9"/><path d="M57 -757 Q101 -718 91 -640 Q82 -581 46 -560 Q68 -624 62 -672 Q61 -718 57 -757Z" fill="#a8b8d5" opacity=".24"/><ellipse cx="-29" cy="-676" rx="18" ry="22" fill="#fff" stroke="#171723" stroke-width="5"/><ellipse cx="31" cy="-676" rx="18" ry="22" fill="#fff" stroke="#171723" stroke-width="5"/><circle cx="-25" cy="-674" r="5.5" fill="#171723"/><circle cx="35" cy="-674" r="5.5" fill="#171723"/><path d="M-64 -714 Q-42 -727 -19 -715" fill="none" stroke="#171723" stroke-width="8" stroke-linecap="round"/><path d="M13 -715 Q38 -730 62 -711" fill="none" stroke="#171723" stroke-width="8" stroke-linecap="round"/><ellipse cx="0" cy="-618" rx="12" ry="${mouthH.toFixed(1)}" fill="#171723"/><ellipse cx="0" cy="-614" rx="6" ry="${Math.max(1,mouthH*.38).toFixed(1)}" fill="#b6434c"/>`;
 return `<g transform="translate(${foot.x.toFixed(2)} ${(foot.y+bob).toFixed(2)}) scale(${s.toFixed(3)})"><ellipse cx="0" cy="2" rx="80" ry="13" fill="#101525" opacity=".18"/><path d="M-34 -283 Q-40 -183 -36 -39" stroke="#171723" stroke-width="22" stroke-linecap="round" fill="none"/><path d="M-34 -283 Q-40 -183 -36 -39" stroke="${pants}" stroke-width="13" stroke-linecap="round" fill="none"/><path d="M34 -283 Q39 -183 38 -39" stroke="#171723" stroke-width="22" stroke-linecap="round" fill="none"/><path d="M34 -283 Q39 -183 38 -39" stroke="${pants}" stroke-width="13" stroke-linecap="round" fill="none"/><ellipse cx="-56" cy="-20" rx="37" ry="13" fill="#171723"/><ellipse cx="55" cy="-20" rx="37" ry="13" fill="#171723"/>${armL}${armR}${jacket}${face}${hat}</g>`;
}
function viewFor(clip,t,captionTime=t){const entry=scenes[clip.scene],elapsed=t-clip.start,local=clamp(elapsed/Math.max(.01,clip.duration)),heroX=entry.host?.root.position.x||0;
 if(entry.host){entry.host.root.position.y=.025*Math.sin(local*7);const e=rms[Math.min(rms.length-1,Math.floor(t/.08))]||0;entry.host.mouth.scale.y=.06+clamp((e-.008)/.07)*.4;entry.host.lip.scale.y=.03+clamp((e-.008)/.07)*.18;}
 for(const [i,c] of (entry.extra||[]).entries()){c.root.position.y=.012*Math.sin(local*5+i);}
 for(const [i,p] of (entry.props||[]).entries()){if(p.type==='Group'){const by=p.userData.baseY??p.position.y;p.position.y=by+.045*Math.sin(local*4+i);}}
 const profile=CAMERA_PROFILES[clip.scene],segment=clip.duration/3,beat=Math.min(2,Math.floor(elapsed/segment)),within=elapsed-beat*segment,glide=beat<2?ease3(within/.78):0,a=profile[beat],b=profile[Math.min(2,beat+1)],state=a.map((v,i)=>lerp(v,b[i],glide)),phase=clip.scene*.73;const focus=state[0],lookY=state[1],camY=state[2],z=state[3]-Math.min(.62,elapsed*.048)+.06*Math.sin(local*Math.PI*2+phase),fov=state[4];const cam=new THREE.PerspectiveCamera(fov,W/H,.1,100);cam.position.set(focus+.16*Math.sin(local*Math.PI*2.1+phase),camY+.08*Math.sin(local*Math.PI*2+phase),z);cam.lookAt(focus+.06*Math.sin(local*Math.PI*2.1+phase),lookY+.05*Math.sin(local*Math.PI*2+phase),0);entry.scene.updateMatrixWorld(true);cam.updateMatrixWorld(true);const dof=state[5];
 renderer.render(entry.scene,cam);let svg=xml.serializeToString(renderer.domElement);const sky=clip.scene===3?'#1c2b63':'#4c83c7',skyMid=clip.scene===3?'#3e568d':'#99b9db';const vb=`<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="${sky}"/><stop offset="62%" stop-color="${skyMid}"/><stop offset="100%" stop-color="#d5b080"/></linearGradient>${dof>.25?`<filter id="dof" x="-12%" y="-12%" width="124%" height="124%"><feGaussianBlur stdDeviation="${dof.toFixed(2)}"/></filter>`:''}</defs><rect x="-${W/2}" y="-${H/2}" width="${W}" height="${H}" fill="url(#sky)"/>`;svg=svg.replace(/(<svg\b[^>]*>)/,`$1${vb}`);
 if(dof>.25)svg=svg.replace(vb,`${vb}<g filter="url(#dof)">`);const amplitude=clamp(((rms[Math.min(rms.length-1,Math.floor(t/.08))]||0)-.008)/.07),characters=[entry.host,...(entry.extra||[])].filter(Boolean);let chars='';characters.forEach((c,i)=>{chars+=characterSvg(c,cam,t,local,i,i===0,amplitude);});
 const cap=(captions.find(c=>captionTime>=c.start&&captionTime<c.end)?.text||'').replace(/[.,!?;:]/g,'').toLowerCase();const source=captionTime>duration-1.9?'<text x="0" y="-535" text-anchor="middle" font-family="DejaVu Sans, sans-serif" font-size="16" font-weight="800" letter-spacing="1" fill="#fff" stroke="#0A0A12" stroke-width="3" paint-order="stroke">SOURCES: FBI • NATIONAL ARCHIVES</text>':'';
 const caption=cap?`<text x="0" y="410" text-anchor="middle" font-family="DejaVu Sans, sans-serif" font-size="48" font-weight="900" fill="#fff" stroke="#0A0A12" stroke-width="10" paint-order="stroke fill" stroke-linejoin="round">${esc(cap)}</text>`:'';
 svg=svg.replace('</svg>',`${dof>.25?'</g>':''}${chars}${caption}${source}</svg>`);return new Resvg(svg,{font:{loadSystemFonts:true,sansSerifFamily:'DejaVu Sans'}}).render().pixels;
}
function blendPixels(a,b,mix){const out=Buffer.allocUnsafe(a.length),inv=1-mix;for(let i=0;i<a.length;i+=4){out[i]=a[i]*inv+b[i]*mix;out[i+1]=a[i+1]*inv+b[i+1]*mix;out[i+2]=a[i+2]*inv+b[i+2]*mix;out[i+3]=255;}return out;}
const testFrames=Number(process.env.TEST_FRAMES||0);const sceneTest=process.env.TEST_SCENES==='1';
const output=process.env.OUT_FILE||path.join(OUT,(testFrames||sceneTest)?'work_code3d_test.mp4':'UNCASE_DB_COOPER_CODE_RENDER_PRIVATE_REVIEW_1080x1920.mp4');
const args=['-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgba','-s',`${W}x${H}`,'-r',String(FPS),'-i','pipe:0','-i',WAV,'-map','0:v:0','-map','1:a:0','-vf','scale=1080:1920:flags=lanczos','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',output];
const enc=spawn(ffmpeg,args,{stdio:['pipe','ignore','inherit']});enc.on('error',e=>{throw e;});
const totalFrames=testFrames||(sceneTest?BUILDERS.length*FPS:Math.ceil(duration*FPS));
for(let f=0;f<totalFrames;f++){let t=f/FPS,clip=clips.at(-1);if(sceneTest){const sceneIndex=Math.floor(f/FPS);clip=clips.find(c=>c.scene===sceneIndex)||clips.at(-1);t=Math.min(clip.end-.12,clip.start+clip.duration*.78+(f%FPS)/FPS*.12);}else{for(const c of clips){if(t>=c.start&&t<c.end+.02){clip=c;break;}}}let pixels=viewFor(clip,t);if(!sceneTest){const idx=clips.indexOf(clip),prev=idx>0?clips[idx-1]:null,fadeFrames=18,elapsedFrames=(t-clip.start)*FPS;if(prev&&prev.scene!==clip.scene&&elapsedFrames>=0&&elapsedFrames<fadeFrames){const a=clamp(elapsedFrames/fadeFrames);const old=viewFor(prev,prev.end-.015,t);pixels=blendPixels(old,pixels,a*a*(3-2*a));}}if(!enc.stdin.write(pixels))await once(enc.stdin,'drain');if(f%150===0)console.log(`rendered ${f}/${totalFrames}`);}
enc.stdin.end();const code=await new Promise((resolve,reject)=>{enc.on('close',resolve);enc.on('error',reject);});if(code!==0)throw new Error(`ffmpeg exit ${code}`);console.log('finished',output,fs.statSync(output).size,'bytes',duration.toFixed(2),'s');
