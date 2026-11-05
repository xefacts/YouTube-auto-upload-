import { camFromKeys, blinkAt, q, idle } from './motion.js';
export const FPS=30,TOTAL=1965,DECK=0.08;
export const SHOTS=[
 {id:'hook',a:0,b:137,location:'cabin',light:'golden'},
 {id:'moneyBack',a:138,b:242,location:'river',light:'golden'},
 {id:'boarding',a:243,b:563,location:'airport',light:'day'},
 {id:'name',a:564,b:641,location:'airport',light:'day'},
 {id:'demand',a:642,b:803,location:'cabin',light:'golden'},
 {id:'release',a:804,b:1004,location:'exchange',light:'golden'},
 {id:'jump',a:1005,b:1178,location:'jump',light:'night'},
 {id:'search',a:1179,b:1303,location:'search',light:'day'},
 {id:'find',a:1304,b:1452,location:'river',light:'golden'},
 {id:'serial',a:1453,b:1497,location:'search',light:'day'},
 {id:'unknown',a:1498,b:1643,location:'river',light:'golden'},
 {id:'resources',a:1644,b:1761,location:'archive',light:'day'},
 {id:'identity',a:1762,b:1821,location:'archive',light:'day'},
 {id:'question',a:1822,b:1894,location:'jump',light:'night'},
 {id:'lastWord',a:1895,b:1964,location:'river',light:'golden'},
];
export const shotAt=f=>SHOTS.find(s=>f>=s.a&&f<=s.b)||SHOTS[SHOTS.length-1];
const white={sky:'#d2d7d8',ground:'#70786f',hemi:1.05,sun:'#fff0d7',sunI:2.1,fog:'#c9d1d2',fogNear:35,fogFar:380,skyTop:'#4d83c0',skyHor:'#d5c7ac',sat:1.04,waterDeep:'#315a70',waterShal:'#739ba4',glint:'#e6dfcc',vig:.23,shadowExt:19};
export const LIGHTS={
 day:{...white,az:138,el:44,gain:'#fff8ed',lift:'#020202'},
 golden:{...white,az:8,el:11,sky:'#8b8095',ground:'#705b54',sun:'#ffb36b',sunI:2.5,fog:'#e2b493',skyTop:'#6b6f9b',skyHor:'#ffd09a',sat:1.08,gain:'#fff1df',waterDeep:'#3d596e',waterShal:'#bb9074',glint:'#ffe1b8',vig:.25,shadowExt:18},
 night:{...white,az:205,el:24,sky:'#414a60',ground:'#303848',hemi:.78,sun:'#879ab8',sunI:.95,fog:'#414a61',fogNear:16,fogFar:210,skyTop:'#25345a',skyHor:'#68758d',sat:.94,gain:'#e4e8f4',lift:'#03050b',waterDeep:'#293b54',waterShal:'#4b6176',glint:'#b5c0d0',vig:.28,shadowExt:25},
};
export const lightFor=(S)=>({...LIGHTS[S.light],fogNear:S.light==='night'?16:35});
const CAMS={
 hook:[{f:0,pos:[-.5,2.5,6.8],look:[-.3,1.35,.1],fov:36},{f:68,pos:[.3,2.3,5.9],look:[0,1.15,.15],fov:33},{f:137,pos:[.45,2.1,5.2],look:[.1,1.1,.1],fov:31}],
 moneyBack:[{f:138,pos:[1.6,2.3,8.2],look:[0,.7,-.2],fov:42},{f:190,pos:[.4,1.9,6.3],look:[0,.5,-.2],fov:36},{f:242,pos:[-.2,1.7,5.4],look:[.15,.45,-.25],fov:32}],
 boarding:[{f:243,pos:[-.9,4.5,14],look:[0,2.2,-7],fov:43},{f:405,pos:[.2,4.0,11.5],look:[0,2.0,-6],fov:39},{f:563,pos:[.55,3.45,9.2],look:[-.2,1.7,-5],fov:35}],
 name:[{f:564,pos:[1.0,3.0,7.2],look:[-.1,1.65,-1],fov:38},{f:603,pos:[.2,2.8,6.1],look:[-.3,1.6,-1],fov:34},{f:641,pos:[0,2.55,5.2],look:[-.35,1.55,-1],fov:31,roll:1}],
 demand:[{f:642,pos:[-.6,2.95,8.0],look:[0,1.5,-.2],fov:40},{f:722,pos:[.2,2.8,6.9],look:[.1,1.25,.2],fov:36},{f:803,pos:[.45,2.55,5.8],look:[.1,1.2,.3],fov:32}],
 release:[{f:804,pos:[-.2,4.0,13],look:[0,1.8,-4],fov:44},{f:900,pos:[.25,3.4,10.5],look:[0,1.55,-3],fov:39},{f:1004,pos:[-.35,3.0,8.2],look:[-.3,1.35,-2],fov:35}],
 jump:[{f:1005,pos:[0,4.8,8.5],look:[-2.5,3.1,-4.5],fov:39},{f:1090,pos:[-.4,3.9,7.0],look:[-3.0,2.7,-4.0],fov:36},{f:1178,pos:[-.8,3.2,6.0],look:[-3.3,2.0,-3.3],fov:33,roll:-1}],
 search:[{f:1179,pos:[-1.4,3.6,9.5],look:[0,2.2,-4],fov:41},{f:1240,pos:[.4,3.0,7.5],look:[0,1.9,-3],fov:36},{f:1303,pos:[.6,2.6,6.1],look:[.2,1.6,-2.8],fov:32}],
 find:[{f:1304,pos:[1.1,2.4,8],look:[0,.65,-.2],fov:42},{f:1375,pos:[.25,1.65,4.9],look:[0,.42,-.2],fov:32},{f:1452,pos:[.2,1.25,4.2],look:[.25,.38,-.25],fov:29}],
 serial:[{f:1453,pos:[.7,1.8,5.4],look:[0,1.05,-4],fov:37},{f:1475,pos:[.3,1.5,4.3],look:[0,.85,-4],fov:32},{f:1497,pos:[0,1.3,3.7],look:[0,.7,-4],fov:29}],
 unknown:[{f:1498,pos:[-.8,2.5,8.5],look:[0,1,-1],fov:42},{f:1570,pos:[0,2.25,6.5],look:[0,.85,-1],fov:37},{f:1643,pos:[.55,1.9,5.4],look:[0,.65,-1],fov:33}],
 resources:[{f:1644,pos:[1.0,3.4,9],look:[0,2.2,-4],fov:42},{f:1703,pos:[.2,3.0,7.3],look:[0,1.9,-3.5],fov:37},{f:1761,pos:[-.2,2.7,6.2],look:[0,1.6,-3],fov:33}],
 identity:[{f:1762,pos:[1.4,2.9,7],look:[0,2.3,-4.4],fov:38},{f:1792,pos:[1.0,2.7,5.7],look:[0,2.25,-4.4],fov:33},{f:1821,pos:[.5,2.55,4.7],look:[0,2.15,-4.4],fov:30,roll:1}],
 question:[{f:1822,pos:[.8,5.2,14],look:[0,3.1,-8],fov:43},{f:1858,pos:[.2,4.2,10.5],look:[0,2.8,-6],fov:38},{f:1894,pos:[-.4,3.4,8.3],look:[0,2.2,-5],fov:34,roll:2}],
 lastWord:[{f:1895,pos:[.5,2.3,7.5],look:[0,.8,-.3],fov:40},{f:1930,pos:[0,1.95,6.2],look:[0,.65,-.3],fov:35},{f:1964,pos:[-.25,1.7,5.4],look:[0,.5,-.3],fov:32}],
};
const CUTS=[1005,1453];
const KICKS=[{f:1008,a:.045},{f:1087,a:.025},{f:1453,a:.025},{f:1822,a:.035}];
export const camAt=f=>{const S=shotAt(f),K=CAMS[S.id],c=camFromKeys(K,f,{creep:.0012,kicks:KICKS});const cut=CUTS.find(x=>f>=x&&f<x+3);c.flash=cut!==undefined?.18*(1-(f-cut)/3):0;return c;};
export const dofAt=f=>{const S=shotAt(f),C=camAt(f);const target= S.id==='serial'?[0,.9,-4]:S.location==='river'?[.2,.55,-.3]:S.location==='archive'?[0,1.8,-4]:S.location==='cabin'?[0,1.4,0]:S.location==='jump'?[0,3.4,-7]:[0,1.5,-3];const d=Math.hypot(C.pos[0]-target[0],C.pos[1]-target[1],C.pos[2]-target[2]);const cinf={hook:14,moneyBack:10,boarding:0,name:13,demand:11,release:0,jump:0,search:0,find:14,serial:16,unknown:0,resources:0,identity:15,question:0,lastWord:0}[S.id]||0;return {focus:d,cinf,near:1};};
export const worldAt=f=>{const S=shotAt(f);return {location:S.location,old:f>=1304,jumpStart:1005};};
const actor=(T,key,o,pos,extra={})=>({key:key+JSON.stringify(o),draw:p=>T.romanFront(p,key,o),x:pos[0],y:pos[1],z:pos[2],...extra});
const pose=(f,seed,expr='neutral',extra={})=>({seed,expr,blink:blinkAt(f,seed),...idle(f,seed),...extra});
export const actorsAt=(f,T)=>{const S=shotAt(f),out=[];const add=(who,o,pos,x={})=>out.push(actor(T,who,o,pos,x));
 switch(S.id){
  case 'hook': add('cooper',pose(f,3,'stern',{L:'hip',R:'hang',facing:-.15,look:.2}),[-.25,0,.3]);add('attendant',pose(f,9,'nervous',{L:'hang',R:'point',facing:1,look:-.3}),[1.05,0,-1.1],{s:.94});break;
  case 'moneyBack': add('child',pose(f,13,'neutral',{L:'reach',R:'hang',facing:1,look:.4,reach:.65}),[-.55,0,.2],{s:.76});add('passenger',pose(f,15,'shock',{L:'point',R:'hang',facing:-1}),[.9,0,-1.2],{s:.9});break;
  case 'boarding': add('cooper',pose(f,3,'stern',{L:'hang',R:'hip',facing:1,look:.25,step:q((f-243)/90)}),[-.55,0,-1.8]);add('attendant',pose(f,9,'neutral',{L:'point',R:'hang',facing:-1}),[.7,0,-1.2],{s:.94});break;
  case 'name': add('cooper',pose(f,3,'stern',{L:'hang',R:'hang',facing:-.1,look:0,headTilt:q(Math.sin(f*.04)*2,1)}),[-.35,0,-1]);break;
  case 'demand': add('cooper',pose(f,3,'stern',{L:'point',R:'hip',facing:1,look:.3}),[-.75,0,.2]);add('attendant',pose(f,9,'nervous',{L:'hang',R:'hang',facing:-1}),[.72,0,-.15],{s:.95});add('passenger',pose(f,17,'shock',{L:'hang',R:'cheek',facing:1}),[1.1,0,-1.9],{s:.88});break;
  case 'release': {const walk=q(Math.min(1,(f-804)/170),2);add('cooper',pose(f,3,'stern',{L:'hip',R:'hang',facing:1}),[-.8,0,-1.3]);add('attendant',pose(f,9,'neutral',{L:'point',R:'hang',facing:1}),[.55,0,-1.2],{s:.95});add('passenger',pose(f,17,'neutral',{L:'hang',R:'wave',facing:1,step:walk}),[1.35+walk*.55,0,-2.4],{s:.9});break;}
  case 'jump': {const t=q(Math.max(0,Math.min(1,(f-1055)/100)),2);if(f<1162)add('cooper',pose(f,3,'stern',{L:'hang',R:'reach',facing:1,step:t}),[-3.55+t*.72,2.55-t*1.35,-2.6+t*.8],{s:1.02,ground:0,alpha:f>1148?Math.max(.15,1-(f-1148)/18):1});break;}
  case 'search': add('investigator',pose(f,21,'squint',{L:'point',R:'hip',facing:1,look:.4}),[-.68,0,-.2]);add('investigator',pose(f,22,'neutral',{L:'hang',R:'reach',facing:-1,look:-.2}),[.75,0,-1.35],{s:.96});break;
  case 'find': add('child',pose(f,13,'shock',{L:'reach',R:'hang',facing:1,look:.3,reach:.8}),[-.58,0,.1],{s:.76});add('investigator',pose(f,21,'squint',{L:'reach',R:'hang',facing:-1}),[.95,0,-1.05],{s:.97});break;
  case 'serial': add('investigator',pose(f,21,'squint',{L:'point',R:'hang',facing:0,look:0}),[0,0,-1.5],{s:1.05});break;
  case 'unknown': add('investigator',pose(f,21,'stern',{L:'hang',R:'hip',facing:1,look:.1}),[-.85,0,.1],{s:.98});break;
  case 'resources': add('investigator',pose(f,21,'neutral',{L:'hang',R:'reach',facing:-1,look:-.3}),[.5,0,.15],{s:.98});break;
  case 'identity': break;
  case 'question': if(f<1884)add('cooper',pose(f,3,'stern',{L:'hang',R:'hang',facing:0,look:0}),[0,0,-8],{s:.9,alpha:.8});break;
  case 'lastWord': break;
 }
 return out;};
export const fxAt=(f,T)=>[];
