#!/usr/bin/env python3
"""Build full TD game: 5 polygons x5 waves, 5 towers, bosses, animated bg."""
import json, base64, pathlib, os, sys
BASE = pathlib.Path(__file__).resolve().parent
LEGACY = pathlib.Path.home()/".openclaw/workspace/glados/.openclaw/tmp/assets"

def find(name):
    for c in (BASE, BASE/"assets", BASE.parent, BASE.parent/"assets", LEGACY):
        p = c/name
        if p.exists():
            return p
    raise SystemExit("missing asset: %s (looked next to script and in legacy dir)" % name)

ATLAS_PNG = find("atlas_final.png")
ATLAS_JSON = find("atlas_final.json")
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else BASE/"td-full.html"
print("atlas:", ATLAS_PNG)
print("out:  ", OUT)

rects = json.load(open(ATLAS_JSON))
b64 = base64.b64encode(open(ATLAS_PNG,'rb').read()).decode()

game_js = r"""
"use strict";
// ============ DATA (BALANCE.md 14.11.2026) ============
// Пути — ломаные только из 0/30/45/90, скругления считает roundRoute().
// Ветвь — дуга: подъём, полка, спуск. net dy = 0, поэтому слияние точное,
// а после него идёт общий хвост — на нём стоит единственный туннель карты.
// Пути — ломаные только из 0/30/45/90, скругления считает roundRoute().
// Вход → петля-ветвь (net dy = 0, точное слияние) → серпантин общего хвоста.
// Серпантин не для красоты: он держит длину маршрута 1150-1260, иначе враг
// проходит арену слишком быстро и баланс валится.
const POLYGONS=[
 {id:"trava",name:"Трава",hpk:1.00,spdk:1.00,gold:320,
  start:[-40,250],
  steps:[[0,70.0],[45,80.0],[0,90.0],[-45,80.0],[-45,140.0],[0,60.0],[45,140.0],[0,60.0],[-45,140.0],[0,60.0],[45,140.0],[0,60.0],[0,65.9]],
  altSteps:[[0,70.0],[-45,80.0],[0,90.0],[45,80.0],[-45,140.0],[0,60.0],[45,140.0],[0,60.0],[-45,140.0],[0,60.0],[45,140.0],[0,60.0],[0,65.9]],
  tex:"gravel",
  road:{base:"#6f6240",top:"#9a865a",edge:"#57503a",plank:"#8a6f45"},narrow:[0.16,0.86],bridgeAt:0.3},
 {id:"les",name:"Лес",hpk:1.30,spdk:1.12,gold:320,
  start:[-40,242],
  steps:[[0,71.4],[45,81.6],[0,91.8],[-45,81.6],[-45,142.8],[0,61.2],[45,142.8],[0,61.2],[-45,142.8],[0,61.2],[45,142.8],[0,61.2],[0,67.2]],
  altSteps:[[0,71.4],[-45,81.6],[0,91.8],[45,81.6],[-45,142.8],[0,61.2],[45,142.8],[0,61.2],[-45,142.8],[0,61.2],[45,142.8],[0,61.2],[0,67.2]],
  tex:"gravel",
  road:{base:"#5f5138",top:"#84744e",edge:"#4a4030",plank:"#77593a"},narrow:[0.14,0.84],bridgeAt:0.28},
 {id:"pustynya",name:"Пустыня",hpk:1.70,spdk:1.14,gold:340,
  start:[-40,256],
  steps:[[0,68.6],[45,78.4],[0,88.2],[-45,78.4],[-45,137.2],[0,58.8],[45,137.2],[0,58.8],[-45,137.2],[0,58.8],[45,137.2],[0,58.8],[0,64.6]],
  altSteps:[[0,68.6],[-45,78.4],[0,88.2],[45,78.4],[-45,137.2],[0,58.8],[45,137.2],[0,58.8],[-45,137.2],[0,58.8],[45,137.2],[0,58.8],[0,64.6]],
  tex:"sand",
  road:{base:"#8f7448",top:"#c2a068",edge:"#6e5a38",plank:"#9a7a4a"},narrow:[0.16,0.82],bridgeAt:0.32},
 {id:"ostrova",name:"Острова",hpk:2.15,spdk:1.18,gold:360,
  start:[-40,246],
  steps:[[0,70.0],[45,80.0],[0,90.0],[-45,80.0],[-45,140.0],[0,60.0],[45,140.0],[0,60.0],[-45,140.0],[0,60.0],[45,140.0],[0,60.0],[0,65.9]],
  altSteps:[[0,70.0],[-45,80.0],[0,90.0],[45,80.0],[-45,140.0],[0,60.0],[45,140.0],[0,60.0],[-45,140.0],[0,60.0],[45,140.0],[0,60.0],[0,65.9]],
  tex:"asphalt",
  road:{base:"#5c5f63",top:"#7b7f84",edge:"#43464a",plank:"#7d6242"},narrow:[0.15,0.8],bridgeAt:0.3},
 {id:"vulkany",name:"Вулканы",hpk:2.70,spdk:1.22,gold:380,
  start:[-40,254],
  steps:[[0,72.8],[45,83.2],[0,93.6],[-45,83.2],[-45,145.6],[0,62.4],[45,145.6],[0,62.4],[-45,145.6],[0,62.4],[45,145.6],[0,62.4],[0,68.5]],
  altSteps:[[0,72.8],[-45,83.2],[0,93.6],[45,83.2],[-45,145.6],[0,62.4],[45,145.6],[0,62.4],[-45,145.6],[0,62.4],[45,145.6],[0,62.4],[0,68.5]],
  tex:"boulder",
  road:{base:"#41332f",top:"#6a4c40",edge:"#2c211e",plank:"#4e3a30"},narrow:[0.15,0.82],bridgeAt:0.34},
];
const TOWERS=[
 {name:"Лучник",    cost:60,   rate:1.0, dmg:10,  splash:0,  burn:0,  up:[50,110,200],    spr:"t1", desc:"1 стрела/с"},
 {name:"Арбалетчик",cost:150,  rate:2.0, dmg:10,  splash:0,  burn:0,  up:[120,250,440],   spr:"t2", desc:"2 стрелы/с"},
 {name:"Скорострел",cost:320,  rate:3.0, dmg:10,  splash:0,  burn:0,  up:[240,430,740],   spr:"t3", desc:"3 стрелы/с"},
 {name:"Пушка",     cost:620,  rate:1.0, dmg:50,  splash:38, burn:0,  up:[420,760,1300],  spr:"t2", desc:"ядро 5 стрел+сплэш"},
 {name:"Огненная",  cost:1150, rate:0.5, dmg:100, splash:52, burn:12, up:[740,1350,2200], spr:"t4", desc:"горящее ядро 10 стрел"},
];
const WAVE_DEF=[{n:8,hp:1.00,spd:1.00},{n:10,hp:1.55,spd:1.05},{n:12,hp:2.25,spd:1.10},{n:14,hp:3.15,spd:1.15},{n:16,hp:4.40,spd:1.20}];
const BASE_HP=44, BASE_SPD=36, RANGE=240, LIVES0=20;
// Правка баланса 15.11.2026 (запрос @Dr_Chernikov): доход растёт как sqrt(hpk), а не линейно;
// скорость врагов компенсирует длину пути, чтобы время под обстрелом падало монотонно.
const TUNE={incExp:0.50, waveBase:520, waveK:0.45, repairCost:400};
const UNITS=["pawn","arch","warr","lanc","pawn"];

// ============ canvas ============
const cv=document.getElementById("c"), ctx=cv.getContext("2d");
const W=cv.width,H=cv.height,T=64; ctx.imageSmoothingEnabled=false;
const RECTS=__RECTS__;
const atlas=new Image(); let atlasReady=false;
atlas.onload=()=>{atlasReady=true;};
atlas.src="data:image/png;base64,__ATLAS__";
function spr(name,frame,cx,bottom,h,flip){
  if(!atlasReady) return;
  const list=RECTS[name]; if(!list) return;
  const r=Array.isArray(list)?list[((frame%list.length)+list.length)%list.length]:list;
  const sc=h/r.h,w=r.w*sc;
  ctx.save(); ctx.translate(cx,bottom); if(flip) ctx.scale(-1,1);
  ctx.drawImage(atlas,r.x,r.y,r.w,r.h,-w/2,-h, w,h); ctx.restore();
}
function sprXY(g,n,x,y,sc,flip){
  const r=RECTS[n]; if(!r||!atlasReady) return;
  const rr=Array.isArray(r)?r[0]:r;
  const w=rr.w*sc,h=rr.h*sc;
  if(flip){g.save();g.translate(x+w,y);g.scale(-1,1);g.drawImage(atlas,rr.x,rr.y,rr.w,rr.h,0,0,w,h);g.restore();}
  else g.drawImage(atlas,rr.x,rr.y,rr.w,rr.h,x,y,w,h);
}
function rnd32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
function hash2(x,y){let h=(x*73856093)^(y*19349663);h=(h^(h>>>13))>>>0;return h}

// ============ animated bg ============
function buildScene(biome){
  const rng=rnd32(biome.length*7919+biome.charCodeAt(0)*131);
  const d=[]; const add=(k,o)=>d.push(Object.assign({k,x:Math.round(rng()*(W-80))+20,y:Math.round(rng()*(H-70))+40,sc:0.9+rng()*0.5,ph:rng()*6.283,fl:rng()<0.5},o||{}));
  const pick=(pre,n)=>pre+(1+Math.floor(rng()*n));
  if(biome==='trava'){for(let i=0;i<30;i++)add(pick('tuft',4),{sc:0.9+rng()*0.8});for(let i=0;i<10;i++)add(pick('bush',4));for(let i=0;i<5;i++)add(pick('tree',3),{sc:0.85+rng()*0.4});for(let i=0;i<9;i++)add(pick('rock',4));}
  if(biome==='les'){for(let i=0;i<16;i++)add(pick('tree',3),{sc:0.9+rng()*0.45});for(let i=0;i<12;i++)add(pick('bush',4));for(let i=0;i<16;i++)add(pick('tuft',4),{sc:0.8+rng()*0.6});for(let i=0;i<5;i++)add(pick('dead',2));for(let i=0;i<6;i++)add(pick('rock',4));}
  if(biome==='pustynya'){for(let i=0;i<14;i++)add(pick('rock',4),{sc:1+rng()*0.7});for(let i=0;i<9;i++)add(pick('dead',2),{sc:1+rng()*0.6});for(let i=0;i<9;i++)add(pick('tuft',4),{sc:0.7+rng()*0.4});for(let i=0;i<3;i++)add(pick('bush',4),{sc:0.7});}
  if(biome==='ostrova'){for(let i=0;i<12;i++)add(pick('wrock',4),{sc:1+rng()*0.5});for(let i=0;i<8;i++)add(pick('tuft',4),{sc:0.8+rng()*0.5});for(let i=0;i<4;i++)add(pick('tree',3),{sc:0.7+rng()*0.35});for(let i=0;i<3;i++)add(pick('bush',4),{sc:0.8});}
  if(biome==='vulkany'){for(let i=0;i<16;i++)add(pick('rock',4),{sc:1+rng()*0.8});for(let i=0;i<10;i++)add(pick('dead',2),{sc:1+rng()*0.6});for(let i=0;i<6;i++)add('fire',{sc:1.1+rng()*0.7});}
  d.sort((a,b)=>a.y-b.y); return d;
}
const scenes={}; POLYGONS.forEach(p=>scenes[p.id]=buildScene(p.id));
const isles=(()=>{const r=rnd32(777),a=[];for(let i=0;i<8;i++)a.push({x:r()*W,y:r()*H,r:55+r()*95});return a})();
const lavaCells=(()=>{const r=rnd32(4242),a=[];for(let i=0;i<10;i++)a.push([Math.floor(r()*14),Math.floor(r()*8)]);return a})();
function groundNames(biome){
  if(biome==='ostrova')return['water0','water1','water2'];
  if(biome==='les')return['les0','les1','les2'];
  if(biome==='pustynya')return['pustynya0','pustynya1','pustynya2'];
  if(biome==='vulkany')return['vulkany0','vulkany1','vulkany2'];
  return['trava0','trava1','trava2'];
}
function drawGround(g,biome,t){
  const names=groundNames(biome), water=(biome==='ostrova');
  for(let gy=0;gy<8;gy++)for(let gx=0;gx<15;gx++){
    const n=names[hash2(gx,gy)%3];
    let ox=0,oy=0;
    if(water){ox=Math.round(Math.sin(t*0.9+gx*0.7)*2);oy=Math.round(Math.cos(t*0.7+gy*0.9)*2);}
    sprXY(g,n,gx*T+ox,gy*T+oy,1);
  }
  if(water){isles.forEach((is,i)=>{
    const cx=is.x+Math.sin(t*0.25+i)*3, cy=is.y+Math.cos(t*0.2+i)*2;
    g.save();g.beginPath();g.ellipse(cx,cy,is.r,is.r*0.7,0,0,Math.PI*2);g.clip();
    for(let gy=0;gy<8;gy++)for(let gx=0;gx<15;gx++)sprXY(g,'pustynya'+(hash2(gx+7,gy+3)%3),gx*T,gy*T,1);
    g.restore();
    g.save();g.beginPath();g.ellipse(cx,cy,is.r*0.72,is.r*0.46,0,0,Math.PI*2);g.clip();
    for(let gy=0;gy<8;gy++)for(let gx=0;gx<15;gx++)sprXY(g,'trava'+(hash2(gx+11,gy+5)%3),gx*T,gy*T,1);
    g.restore();
    g.save();g.globalAlpha=0.20+0.12*Math.sin(t*1.4+i*2.1);g.strokeStyle='#dfeef2';g.lineWidth=2;
    g.beginPath();g.ellipse(cx,cy,is.r+1,is.r*0.7+1,0,0,Math.PI*2);g.stroke();g.restore();
  });}
  if(biome==='vulkany'){lavaCells.forEach(([gx,gy],i)=>{
    const p=0.16+0.12*Math.sin(t*1.6+i*1.9);
    g.save();g.globalCompositeOperation='lighter';g.globalAlpha=p;
    const grd=g.createRadialGradient(gx*T+32,gy*T+32,2,gx*T+32,gy*T+32,44);
    grd.addColorStop(0,'rgba(255,140,40,0.55)');grd.addColorStop(0.45,'rgba(220,70,10,0.22)');grd.addColorStop(1,'rgba(180,40,0,0)');
    g.fillStyle=grd;g.fillRect(gx*T-20,gy*T-20,T+40,T+40);g.restore();
  });}
}
function drawDecor(g,biome,t){
  for(const o of scenes[biome]){
    let x=o.x,y=o.y; const k=o.k;
    if(k.startsWith('tree'))x+=Math.sin(t*0.7+o.ph)*2.4;
    else if(k.startsWith('bush')||k.startsWith('dead'))x+=Math.sin(t*1.2+o.ph)*1.0;
    else if(k.startsWith('tuft'))x+=Math.sin(t*1.7+o.ph)*1.2;
    if(k==='fire'){
      const f=Math.floor(t*11+o.ph*3)%10;
      g.save();g.globalCompositeOperation='lighter';g.globalAlpha=0.72;
      const r=RECTS['fire'+f]; const sc=o.sc;
      if(r&&atlasReady)g.drawImage(atlas,r.x,r.y,r.w,r.h,x-32*sc,y-62*sc,64*sc,64*sc);
      g.restore(); continue;
    }
    const r0=RECTS[k]; const rr=Array.isArray(r0)?r0[0]:r0; if(!rr||!atlasReady)continue;
    g.drawImage(atlas,rr.x,rr.y,rr.w,rr.h,x-rr.w*o.sc/2,y-rr.h*o.sc,o.sc*rr.w,o.sc*rr.h);
  }
}

// ============ state ============
const S={screen:"menu",pi:0,gold:0,lives:LIVES0,wave:0,waveActive:false,enemies:[],towers:[],shots:[],parts:[],spawnQueue:[],spawnTimer:0,betweenTimer:0,time:0,selTower:0,msg:"",finished:{}};
let ROUTES=[],RSEG=[],RTOT=[],DECOYS=[],FORK=null,REJOIN=null;
function noise2(x,y){const h=Math.sin(x*12.9898+y*78.233)*43758.5453;return h-Math.floor(h);}
// Строит маршрут из start и шагов [угол, длина]. Углы только 0/30/45/90.
// Внутренние вершины скругляются квадратичной кривой и семплируются в точки,
// чтобы posAt() считал длину по дуге, а не по хорде.
function roundRoute(start,steps,radius){
  const raw=[{x:start[0],y:start[1]}];
  let x=start[0],y=start[1];
  for(const st of steps){
    const a=st[0]*Math.PI/180, ln=st[1];
    x+=Math.cos(a)*ln; y+=Math.sin(a)*ln;
    raw.push({x,y});
  }
  const out=[raw[0]];
  for(let i=1;i<raw.length-1;i++){
    const p0=raw[i-1],p1=raw[i],p2=raw[i+1];
    const v1={x:p0.x-p1.x,y:p0.y-p1.y}, v2={x:p2.x-p1.x,y:p2.y-p1.y};
    const l1=Math.hypot(v1.x,v1.y)||1, l2=Math.hypot(v2.x,v2.y)||1;
    const r=Math.min(radius,l1*0.45,l2*0.45);
    const a1={x:p1.x+v1.x/l1*r,y:p1.y+v1.y/l1*r};
    const a2={x:p1.x+v2.x/l2*r,y:p1.y+v2.y/l2*r};
    out.push(a1);
    const N=7;
    for(let k=1;k<=N;k++){
      const t=k/N, mt=1-t;
      out.push({x:mt*mt*a1.x+2*mt*t*p1.x+t*t*a2.x, y:mt*mt*a1.y+2*mt*t*p1.y+t*t*a2.y});
    }
    out.push(a2);
  }
  out.push(raw[raw.length-1]);
  return out;
}
function bakeRoute(pts){
  const P=pts.map(p=>({x:p.x!==undefined?p.x:p[0],y:p.y!==undefined?p.y:p[1]}));
  const seg=[];let tot=0;
  for(let k=0;k<P.length-1;k++){const a=P[k],b=P[k+1];const len=Math.hypot(b.x-a.x,b.y-a.y);seg.push({a,b,len,start:tot});tot+=len;}
  return{P,seg,tot};
}
function setPolygon(i){
  S.pi=i; const P=POLYGONS[i];
  ROUTES=[roundRoute(P.start,P.steps,26), roundRoute(P.start,P.altSteps,26)];
  RSEG=[];RTOT=[];
  for(const r of ROUTES){const b=bakeRoute(r);RSEG.push(b.seg);RTOT.push(b.tot);}
  // fork/rejoin: общий хвост ищем по совпадению ВЕРШИН с конца.
  // Сравнивать posAt(d,0) и posAt(d,1) по одной дуговой длине нельзя:
  // после скруглений длины ветвей расходятся на несколько пикселей, и
  // одинаковые d указывают на разные точки — слияние «не находится».
  (function(){
    const A=ROUTES[0], B=ROUTES[1];
    const eps=0.75;
    const eq=(p,q)=>Math.abs(p.x-q.x)<eps&&Math.abs(p.y-q.y)<eps;
    // сколько вершин с конца совпадают
    let n=0;
    while(n<A.length-1 && n<B.length-1 && eq(A[A.length-1-n],B[B.length-1-n])) n++;
    // индекс первой вершины общего хвоста в маршруте 0
    const tailStart=A.length-n;
    // длина хвоста по дуге
    let tailLen=0;
    for(let k=tailStart;k<A.length-1;k++)tailLen+=Math.hypot(A[k+1].x-A[k].x,A[k+1].y-A[k].y);
    // точка слияния — её дуговая координата на маршруте 0
    let mergeD=0;
    for(let k=0;k<tailStart;k++)mergeD+=Math.hypot(A[k+1].x-A[k].x,A[k+1].y-A[k].y);
    FORK=posAt(Math.max(0,mergeD*0.30),0);
    REJOIN=posAt(mergeD,0);
    // туннель: короткий, на общем хвосте, с отступом от слияния и от выхода
    const len=Math.min(110,tailLen-60);
    P._tun=len>50?[mergeD+24,mergeD+24+len]:null;
  })();
  // площадки: обе стороны проверяются, выбирается та, что дальше от ОБЕИХ дорог; отступ растёт пока <38px
  (function(){
    function minDist(x,y){
      let best=1e9;
      for(let ri=0;ri<2;ri++){const tot=RTOT[ri];
        for(let d=0;d<=tot;d+=12){const p=posAt(d,ri);const dd=Math.hypot(p.x-x,p.y-y);if(dd<best)best=dd;}}
      return best;
    }
    const fracs=[0.10,0.27,0.43,0.59,0.75,0.90],out=[];
    for(let k=0;k<fracs.length;k++){
      const f=fracs[k],tot=RTOT[0];
      const p0=posAt(f*tot,0),p1=posAt(Math.min(f*tot+12,tot),0);
      let dx=p1.x-p0.x,dy=p1.y-p0.y;const L=Math.hypot(dx,dy)||1;dx/=L;dy/=L;
      let best=null,bd=-1;
      for(const side of (k%2?[1,-1]:[-1,1])){
        for(const off of [58,80,102]){
          const sx=Math.max(40,Math.min(860,Math.round(p0.x+(-dy*side)*off)));
          const sy=Math.max(50,Math.min(450,Math.round(p0.y+(dx*side)*off)));
          const dd=minDist(sx,sy);
          if(dd>bd){bd=dd;best=[sx,sy];}
          if(dd>=38)break;
        }
        if(bd>=38)break;
      }
      out.push(best);
    }
    P.slots=out;
  })();
  // декоративные тупики: 2 коротких ответвления
  DECOYS=[];
  const d1=posAt(RTOT[0]*0.34,0),d2=posAt(RTOT[0]*0.58,0);
  DECOYS.push([d1,{x:d1.x+64,y:d1.y-54}]);
  DECOYS.push([d2,{x:d2.x-54,y:d2.y+64}]);
  S.gold=P.gold;S.lives=LIVES0;S.wave=0;S.waveActive=false;S.enemies=[];S.towers=[];S.shots=[];S.parts=[];S.spawnQueue=[];S.betweenTimer=0;S.selTower=0;
}
function posAt(d,ri){ri=ri||0;const seg=RSEG[ri],tot=RTOT[ri];if(!seg)return{x:0,y:0};
  d=Math.max(0,Math.min(d,tot));for(const s of seg){if(d<=s.start+s.len){const t=s.len?(d-s.start)/s.len:0;return{x:s.a.x+(s.b.x-s.a.x)*t,y:s.a.y+(s.b.y-s.a.y)*t};}}
  const e=ROUTES[ri][ROUTES[ri].length-1];return{x:e.x,y:e.y};}
function routeLen(ri){return RTOT[ri||0]||1;}
function waveComp(wi){
  const P=POLYGONS[S.pi],D=WAVE_DEF[wi];
  const hp=Math.round(BASE_HP*P.hpk*D.hp), spd=BASE_SPD*P.spdk*D.spd;
  const unit=UNITS[wi%UNITS.length];
  return{n:D.n,hp,spd,unit,miniHp:hp*6,bossHp:hp*18};
}
function startWave(){
  if(S.waveActive||S.wave>=5||S.screen!=="game")return;
  const c=waveComp(S.wave); S.wave++;
  S.waveActive=true;S.spawnQueue=[];let t=0;
  for(let i=0;i<c.n;i++){S.spawnQueue.push({hp:c.hp,maxHp:c.hp,spd:c.spd,unit:c.unit,boss:0,delay:t,ri:i%2});t+=0.65;}
  S.spawnQueue.push({hp:c.miniHp,maxHp:c.miniHp,spd:c.spd*0.85,unit:c.unit,boss:1,delay:t+0.5,ri:0});
  if(S.wave===5){S.spawnQueue.push({hp:c.bossHp,maxHp:c.bossHp,spd:c.spd*0.70,unit:"warr",boss:2,delay:t+1.5,ri:1});}
  S.spawnTimer=0;
}
function towerAt(x,y){let best=null,bd=26;for(const t of S.towers){const d=Math.hypot(t.x-x,t.y-y);if(d<bd){bd=d;best=t;}}return best;}
function slotAt(x,y){for(const s of POLYGONS[S.pi].slots){if(Math.hypot(s[0]-x,s[1]-y)<26&&!S.towers.some(t=>t.sx===s[0]&&t.sy===s[1]))return s;}return null;}
cv.addEventListener("click",(e)=>{
  if(S.screen==="menu"){
    const r=cv.getBoundingClientRect(),x=(e.clientX-r.left)*(W/r.width),y=(e.clientY-r.top)*(H/r.height);
    for(let i=0;i<5;i++){const bx=60+i*160,by=330;
      if(x>bx&&x<bx+140&&y>by&&y<by+90){setPolygon(i);S.screen="game";return;}}
    return;
  }
  if(S.screen==="win"){S.screen="menu";return;}
  if(S.screen!=="game")return;
  const r=cv.getBoundingClientRect(),x=(e.clientX-r.left)*(W/r.width),y=(e.clientY-r.top)*(H/r.height);
  // shop row
  if(y>H-64){
    for(let i=0;i<5;i++){if(x>8+i*178&&x<8+i*178+170){S.selTower=i;return;}}
    return;
  }
  const t=towerAt(x,y);
  if(t){
    const def=TOWERS[t.ti];
    if(t.level<4){const c=def.up[t.level-1];if(S.gold>=c){S.gold-=c;t.level++;t.dmg*=1.45;t.splash*=1.10;}}
    return;
  }
  const s=slotAt(x,y);
  if(s){const def=TOWERS[S.selTower];if(S.gold>=def.cost){S.gold-=def.cost;
    S.towers.push({sx:s[0],sy:s[1],x:s[0],y:s[1],ti:S.selTower,range:RANGE,dmg:def.dmg* (def.rate?1:1),rate:def.rate,splash:def.splash,burn:def.burn,timer:0,level:1,angle:0,spr:def.spr,burnTick:0});}}
});
addEventListener("keydown",(e)=>{if(e.code==="Space"){e.preventDefault();if(S.screen==="game")startWave();}});

function inTunnel(en){
  const P=POLYGONS[S.pi]; if(!P._tun)return false;
  return en.d>=P._tun[0]&&en.d<=P._tun[1];
}
function damage(e,dmg,burn){
  if(inTunnel(e))return;
  e.hp-=dmg; if(burn>0){e.burnT=3;e.burnDps=burn;}
}
function update(dt){
  if(S.screen!=="game")return;
  S.time+=dt;
  if(S.waveActive&&S.spawnQueue.length){S.spawnTimer+=dt;
    while(S.spawnQueue.length&&S.spawnTimer>=S.spawnQueue[0].delay){
      const c=S.spawnQueue.shift();
      S.enemies.push({d:0,ri:c.ri||0,hp:c.hp,maxHp:c.hp,unit:c.unit,spd:c.spd*(0.9+Math.random()*0.2),anim:Math.random()*2,dead:false,boss:c.boss,burnT:0,burnDps:0,scale:c.boss===2?2.2:(c.boss===1?1.5:1)});
    }}
  for(const en of S.enemies){
    if(en.dead)continue;
    if(en.burnT>0){if(!inTunnel(en)){en.burnT-=dt;en.hp-=en.burnDps*dt;}}
    en.d+=en.spd*dt;en.anim+=dt;
    if(en.hp<=0){en.dead=true;
      let rw=Math.round(en.maxHp*0.10*Math.pow(POLYGONS[S.pi].hpk,-TUNE.incExp));if(en.boss>0)rw=Math.round(rw*1.8);S.gold+=rw;
      const dp=posAt(en.d,en.ri);
      for(let i=0;i<(en.boss?14:5);i++)S.parts.push({x:dp.x,y:dp.y,vx:(Math.random()-0.5)*90,vy:-40-Math.random()*60,life:0.5});
      continue;}
    if(en.d>=routeLen(en.ri)){en.dead=true;S.lives--;}
  }
  for(const t of S.towers){
    t.timer-=dt; if(t.timer>0)continue;
    let target=null;
    for(const en of S.enemies){if(en.dead)continue;if(inTunnel(en))continue;const p=posAt(en.d,en.ri);
      if(Math.hypot(p.x-t.x,p.y-t.y)>t.range)continue;
      if(!target||(en.d/routeLen(en.ri))>(target.d/routeLen(target.ri)))target=en;}
    if(target){const def=TOWERS[t.ti];t.timer=1/Math.max(0.2,def.rate*(1+(t.level-1)*0.06));
      const p=posAt(target.d,target.ri);t.angle=Math.atan2(p.y-t.y,p.x-t.x);
      const dmg=t.dmg*(t.level>1?1:1);
      if(t.splash>0){const sp=t.splash;
        for(const en of S.enemies){if(en.dead)continue;const q=posAt(en.d,en.ri);
          if(Math.hypot(q.x-p.x,q.y-p.y)<=sp)damage(en,dmg,t.burn);}
        S.parts.push({x:p.x,y:p.y,vx:0,vy:0,life:0.3,boom:sp});
      }else{damage(target,dmg,t.burn);S.shots.push({x1:t.x,y1:t.y-30,x2:p.x,y2:p.y-20,a:t.angle,life:0.14});}
    }
  }
  // fix dmg scaling: base dmg * 1.45^(level-1)
  for(const t of S.towers){const def=TOWERS[t.ti];t.dmg=def.dmg*Math.pow(1.45,t.level-1);t.splash=def.splash*(1+0.10*(t.level-1));}
  S.enemies=S.enemies.filter(e=>!e.dead);
  S.shots=S.shots.filter(s=>(s.life-=dt)>0);
  for(const p of S.parts){p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=220*dt;p.life-=dt;}
  S.parts=S.parts.filter(p=>p.life>0);
  if(S.waveActive&&!S.spawnQueue.length&&!S.enemies.length){
    S.waveActive=false;
    const P=POLYGONS[S.pi];
    S.gold+=Math.round(TUNE.waveBase*(1+Math.pow(P.hpk,0.5)*TUNE.waveK));
    if(S.wave>=5){S.finished[P.id]=true;const all=POLYGONS.every(q=>S.finished[q.id]);
      S.screen=all?"win":"menu";S.msg=all?"Все 5 полигонов пройдены":"Полигон пройден";}
    else S.betweenTimer=3;
  }
  if(!S.waveActive&&S.betweenTimer>0){S.betweenTimer-=dt;if(S.betweenTimer<=0)startWave();}
  if(S.lives<=0){S.lives=0;S.waveActive=false;S.screen="dead";}
}

// ============ draw ============
function widthAt(frac,P){
  // сужения в заданных точках: 44 -> 26 с плавным переходом
  let w=44;
  for(const n of (P.narrow||[])){const dd=Math.abs(frac-n);if(dd<0.06){const k=Math.cos(dd/0.06*Math.PI/2);w=Math.min(w,44-18*k);}}
  return w;
}
function strokeRoute(pts,color,width,ox,oy,dash){
  ctx.save();ctx.lineJoin="round";ctx.lineCap="round";
  if(dash)ctx.setLineDash(dash);
  ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();
  ctx.moveTo(pts[0].x+(ox||0),pts[0].y+(oy||0));
  for(let i=1;i<pts.length;i++)ctx.lineTo(pts[i].x+(ox||0),pts[i].y+(oy||0));
  ctx.stroke();ctx.restore();
}
function drawRouteTexture(P,t){
  const tex=P.tex||"gravel";
  ctx.save();
  for(let ri=0;ri<ROUTES.length;ri++){
    const tot=RTOT[ri];
    for(let d=6;d<tot-6;d+=9){
      const a=posAt(d,ri), b=posAt(Math.min(d+9,tot),ri);
      const ang=Math.atan2(b.y-a.y,b.x-a.x);
      const nx=-Math.sin(ang), ny=Math.cos(ang);
      const n1=noise2(d*0.13,ri*7.1), n2=noise2(d*0.41+3,ri*2.7);
      const off=(n1-0.5)*24;
      const px=a.x+nx*off, py=a.y+ny*off;
      if(tex==="gravel"){
        ctx.fillStyle=n2>0.62?"rgba(255,255,255,0.13)":"rgba(0,0,0,0.20)";
        const r1=1+n1*2.2;
        ctx.beginPath();ctx.ellipse(px,py,r1,r1*0.72,ang,0,Math.PI*2);ctx.fill();
      }else if(tex==="sand"){
        ctx.strokeStyle=n2>0.5?"rgba(255,240,200,0.16)":"rgba(90,70,40,0.18)";
        ctx.lineWidth=1.6;
        ctx.beginPath();ctx.moveTo(px-nx*7,py-ny*7);
        ctx.quadraticCurveTo(px+nx*1+Math.cos(ang)*3,py+ny*1+Math.sin(ang)*3,px+nx*7,py+ny*7);
        ctx.stroke();
      }else if(tex==="asphalt"){
        if(n2>0.74){ctx.strokeStyle="rgba(0,0,0,0.28)";ctx.lineWidth=1.4;
          ctx.beginPath();ctx.moveTo(px,py);
          ctx.lineTo(px+nx*4+Math.cos(ang)*7,py+ny*4+Math.sin(ang)*7);
          ctx.lineTo(px+nx*9+Math.cos(ang)*11,py+ny*9+Math.sin(ang)*11);ctx.stroke();}
        else if(n1>0.55){ctx.fillStyle="rgba(255,255,255,0.10)";
          ctx.fillRect(px-1,py-1,2,2);}
      }else{
        const r1=1.8+n2*3.4;
        ctx.fillStyle=n2>0.5?"rgba(0,0,0,0.26)":"rgba(160,140,130,0.16)";
        ctx.beginPath();ctx.ellipse(px,py,r1,r1*0.78,ang+n1,0,Math.PI*2);ctx.fill();
        if(n2>0.72){ctx.fillStyle="rgba(255,140,40,0.10)";
          ctx.beginPath();ctx.ellipse(px,py,r1*1.5,r1*1.1,ang,0,Math.PI*2);ctx.fill();}
      }
    }
    // туннель: проход под скалой. Читается не как труба, а как тень:
    // затемнение нарастает от порталов к середине, портал — две скалы по бокам.
    if(P._tun&&ri===0){
      const d0=P._tun[0], d1=P._tun[1], span=d1-d0;
      // 1. затемнение полотна с плавным входом и выходом
      for(let d=d0;d<d1;d+=6){
        const t=(d-d0)/span;                       // 0..1
        const k=Math.sin(Math.PI*t);                // 0 на порталах, 1 в середине
        const a=posAt(d,ri), b=posAt(Math.min(d+6,tot),ri);
        const ang=Math.atan2(b.y-a.y,b.x-a.x);
        ctx.save();ctx.translate(a.x,a.y);ctx.rotate(ang);
        ctx.fillStyle="rgba(4,4,8,"+(0.86*k).toFixed(3)+")";
        ctx.fillRect(0,-22,6.5,44);
        ctx.restore();
      }
      // 2. порталы: две скалы по бокам, без кольца вокруг дороги
      for(const [d,k] of [[d0,1],[d1,-1]]){
        const c=posAt(d,ri), n=posAt(Math.min(Math.max(d+8*k,0),tot),ri);
        const ang=Math.atan2(n.y-c.y,n.x-c.x), nx=-Math.sin(ang), ny=Math.cos(ang);
        for(const side of [1,-1]){
          ctx.save();
          ctx.fillStyle="rgba(0,0,0,0.32)";
          ctx.beginPath();ctx.ellipse(c.x+nx*30*side,c.y+ny*30*side+5,15,19,ang,0,Math.PI*2);ctx.fill();
          ctx.fillStyle="#4a4a53";
          ctx.beginPath();ctx.ellipse(c.x+nx*30*side,c.y+ny*30*side,13,17,ang,0,Math.PI*2);ctx.fill();
          ctx.fillStyle="rgba(255,255,255,0.14)";
          ctx.beginPath();ctx.ellipse(c.x+nx*30*side-3,c.y+ny*30*side-4,7,9,ang,0,Math.PI*2);ctx.fill();
          ctx.restore();
        }
      }
    }
  }
  ctx.restore();
}
function drawRoads(P,t){
  // 1. декоративные тупики (тонкие тропы в никуда)
  for(const dec of DECOYS){strokeRoute(dec,"rgba(0,0,0,0.25)",20,0,7);strokeRoute(dec,P.road.base,16,0,0);}
  for(let ri=0;ri<ROUTES.length;ri++){
    const pts=ROUTES[ri],tot=RTOT[ri];
    // 2. тень-насыпь: дорога как часть ландшафта, лежит на подушке
    strokeRoute(pts,"rgba(0,0,0,0.35)",54,0,9);
    // 3. боковая стенка (псевдо-3D: торец вниз)
    strokeRoute(pts,P.road.edge,48,0,6);
    // 4. основное полотно
    strokeRoute(pts,P.road.base,44,0,0);
    // 5. верхняя плоскость светлее
    strokeRoute(pts,P.road.top,32,0,-2);
    // 6. сужения: тёмные горловины
    for(const n of (P.narrow||[])){
      const p=posAt(n*tot,ri);
      ctx.save();ctx.fillStyle="rgba(0,0,0,0.30)";
      ctx.beginPath();ctx.ellipse(p.x,p.y-2,20,26,0,0,Math.PI*2);ctx.fill();ctx.restore();
      strokeRoute([pts[0]],P.road.top,1,0,0);
    }
    // 7. кромка: пунктир камней по краям
    ctx.save();ctx.lineJoin="round";
    ctx.strokeStyle="rgba(255,255,255,0.10)";ctx.lineWidth=2;ctx.setLineDash([2,14]);
    ctx.beginPath();ctx.moveTo(pts[0].x,pts[0].y-20);
    for(let i=1;i<pts.length;i++)ctx.lineTo(pts[i].x,pts[i].y-20);
    ctx.stroke();ctx.restore();
  }
  // 8. перекрёстки: площади в fork/rejoin
  for(const c of [FORK,REJOIN]){
    if(!c)continue;
    ctx.save();
    ctx.fillStyle="rgba(0,0,0,0.30)";ctx.beginPath();ctx.ellipse(c.x,c.y+9,44,30,0,0,Math.PI*2);ctx.fill();
    ctx.fillStyle=P.road.edge;ctx.beginPath();ctx.ellipse(c.x,c.y+5,42,28,0,0,Math.PI*2);ctx.fill();
    ctx.fillStyle=P.road.top;ctx.beginPath();ctx.ellipse(c.x,c.y+1,34,22,0,0,Math.PI*2);ctx.fill();
    // знак-указатель
    ctx.fillStyle="#4a3520";ctx.fillRect(c.x-2,c.y-34,4,22);
    ctx.fillStyle="#8a6a3a";ctx.fillRect(c.x-14,c.y-40,28,10);
    ctx.restore();
  }
  // 9. мосты: настил + перила поперёк хода
  for(let ri=0;ri<ROUTES.length;ri++){
    const tot=RTOT[ri],P0=POLYGONS[S.pi];
    const f=P0.bridgeAt||0.5, c=posAt(f*tot,ri), c2=posAt(f*tot+10,ri);
    const ang=Math.atan2(c2.y-c.y,c2.x-c.x), nx=-Math.sin(ang), ny=Math.cos(ang);
    ctx.save();
    // русло под мостом: вода на островах, лава на вулканах, ручей иначе
    ctx.translate(c.x,c.y);ctx.rotate(ang);
    if(P0.id==="ostrova"){ctx.fillStyle="#2e6f8a";ctx.fillRect(-70,-16,140,32);
      ctx.fillStyle="rgba(255,255,255,0.25)";ctx.fillRect(-70,-16,140,5);ctx.fillRect(-70,11,140,5);}
    else if(P0.id==="vulkany"){ctx.fillStyle="#3a1005";ctx.fillRect(-70,-18,140,36);
      ctx.save();ctx.globalCompositeOperation="lighter";
      ctx.fillStyle="rgba(255,90,10,"+(0.5+0.2*Math.sin(t*3.1+ri))+")";ctx.fillRect(-70,-9,140,18);ctx.restore();}
    else{ctx.fillStyle="rgba(30,60,40,0.55)";ctx.fillRect(-70,-13,140,26);
      ctx.fillStyle="rgba(120,170,200,0.50)";ctx.fillRect(-70,-7,140,14);}
    ctx.restore();
    ctx.save();
    // тень под мостом
    ctx.fillStyle="rgba(0,0,0,0.35)";
    ctx.beginPath();ctx.ellipse(c.x,c.y+12,46,20,ang,0,Math.PI*2);ctx.fill();
    // настил
    ctx.translate(c.x,c.y);ctx.rotate(ang);
    ctx.fillStyle=P0.road.plank;ctx.fillRect(-44,-24,88,48);
    ctx.strokeStyle="rgba(0,0,0,0.35)";ctx.lineWidth=2;
    for(let x=-44;x<44;x+=9){ctx.beginPath();ctx.moveTo(x,-24);ctx.lineTo(x,24);ctx.stroke();}
    // перила
    ctx.fillStyle="#3a2a18";ctx.fillRect(-46,-28,92,6);ctx.fillRect(-46,22,92,6);
    ctx.fillStyle="#5a4228";
    for(let x=-44;x<=44;x+=22){ctx.fillRect(x-2,-32,4,10);ctx.fillRect(x-2,22,4,10);}
    ctx.restore();
  }
  // 10. текстура полотна по биому + единственный туннель карты
  drawRouteTexture(P,t);
  // 11. вулканы: светящиеся трещины вдоль полотна
  if(P.id==="vulkany"){
    ctx.save();ctx.globalCompositeOperation="lighter";
    ctx.strokeStyle="rgba(255,110,20,"+(0.25+0.12*Math.sin(t*2.2))+")";ctx.lineWidth=3;ctx.setLineDash([12,26]);
    ctx.lineDashOffset=-t*30;
    ctx.beginPath();const pts=ROUTES[0];ctx.moveTo(pts[0].x,pts[0].y);
    for(let i=1;i<pts.length;i++)ctx.lineTo(pts[i].x,pts[i].y);
    ctx.stroke();ctx.restore();
  }
}
function draw(){
  ctx.clearRect(0,0,W,H);
  if(S.screen==="menu"){
    drawGround(ctx,"trava",S.time);drawDecor(ctx,"trava",S.time);
    ctx.fillStyle="rgba(13,17,23,.82)";ctx.fillRect(0,0,W,H);
    ctx.textAlign="center";ctx.fillStyle="#f0f6fc";ctx.font="bold 30px sans-serif";
    ctx.fillText("Полигоны · TD",W/2,70);
    ctx.fillStyle="#8b949e";ctx.font="14px sans-serif";
    ctx.fillText("5 полигонов × 5 волн · 5 башен · боссы · "+(S.msg||"выбери полигон"),W/2,100);
    POLYGONS.forEach((p,i)=>{
      const bx=60+i*160,by=330;
      ctx.fillStyle=S.finished[p.id]?"#1a4d2e":"#161b22";ctx.strokeStyle=S.finished[p.id]?"#3fb950":"#30363d";ctx.lineWidth=2;
      ctx.beginPath();ctx.roundRect(bx,by,140,90,10);ctx.fill();ctx.stroke();
      ctx.fillStyle="#f0f6fc";ctx.font="bold 15px sans-serif";ctx.fillText(p.name,bx+70,by+26);
      ctx.fillStyle="#8b949e";ctx.font="12px sans-serif";ctx.fillText("HP×"+p.hpk,bx+70,by+46);
      ctx.fillText(S.finished[p.id]?"пройден ✓":"старт "+p.gold+" золота",bx+70,by+64);
    });
    return;
  }
  const P=POLYGONS[S.pi],biome=P.id;
  drawGround(ctx,biome,S.time);drawDecor(ctx,biome,S.time);
  drawRoads(P,S.time);
  const end=ROUTES[0][ROUTES[0].length-1];
  spr("base",0,end.x-34,end.y+44,104,false);
  for(const s of P.slots){
    if(S.towers.some(t=>t.sx===s[0]&&t.sy===s[1]))continue;
    ctx.strokeStyle="rgba(255,255,255,.42)";ctx.setLineDash([4,5]);ctx.lineWidth=2;
    ctx.beginPath();ctx.arc(s[0],s[1]+6,20,0,Math.PI*2);ctx.stroke();ctx.setLineDash([]);
  }
  for(const t of S.towers){
    ctx.fillStyle="rgba(46,160,67,0.07)";ctx.beginPath();ctx.arc(t.x,t.y,t.range,0,Math.PI*2);ctx.fill();
    ctx.strokeStyle="rgba(31,111,67,0.35)";ctx.lineWidth=1;ctx.stroke();
    const hh=t.spr==="t4"?120:76;
    spr(t.spr,0,t.x,t.y+34,hh,false);
    ctx.fillStyle="rgba(0,0,0,.6)";ctx.font="bold 10px sans-serif";ctx.textAlign="center";
    ctx.fillText(TOWERS[t.ti].name+" L"+t.level,t.x,t.y+44);
  }
  for(const s of S.shots){
    const k=1-s.life/0.14,px=s.x1+(s.x2-s.x1)*(0.35+0.65*k),py=s.y1+(s.y2-s.y1)*(0.35+0.65*k);
    ctx.save();ctx.globalAlpha=Math.min(1,s.life/0.09);ctx.translate(px,py);ctx.rotate(s.a);
    if(atlasReady){const r=RECTS.arrow;const h=14,w=r.w*(h/r.h);ctx.drawImage(atlas,r.x,r.y,r.w,r.h,-w/2,-h/2,w,h);}
    ctx.restore();
  }
  for(const en of S.enemies){
    const p=posAt(en.d,en.ri),ahead=posAt(Math.min(en.d+8,routeLen(en.ri)),en.ri);
    const flip=ahead.x<p.x-0.5,frame=Math.floor(en.anim*9);
    const h=44*en.scale;
    spr(en.unit,frame,p.x,p.y+20*h/44,h,flip);
    const frac=Math.max(0,en.hp/en.maxHp);
    ctx.fillStyle="rgba(0,0,0,.55)";ctx.fillRect(p.x-13*en.scale,p.y-26*en.scale,26*en.scale,5);
    ctx.fillStyle=en.boss===2?"#ff7b00":(en.boss===1?"#e3b341":(frac>0.5?"#3fb950":frac>0.25?"#e3b341":"#f85149"));
    ctx.fillRect(p.x-12*en.scale,p.y-25*en.scale,24*en.scale*frac,3);
    if(en.boss>0){ctx.fillStyle=en.boss===2?"#ff7b00":"#e3b341";ctx.font="bold 10px sans-serif";ctx.textAlign="center";ctx.fillText(en.boss===2?"BOSS":"mini",p.x,p.y-30*en.scale);}
  }
  for(const p of S.parts){
    ctx.save();ctx.globalAlpha=Math.max(0,p.life*2);
    if(p.boom){ctx.strokeStyle="#ffb347";ctx.lineWidth=3;ctx.beginPath();ctx.arc(p.x,p.y,p.boom*(1-p.life/0.3+0.2),0,Math.PI*2);ctx.stroke();}
    else{ctx.fillStyle="#ffd866";ctx.fillRect(p.x-2,p.y-2,4,4);}
    ctx.restore();
  }
  if(S.screen==="dead"){
    ctx.fillStyle="rgba(13,17,23,.84)";ctx.fillRect(0,0,W,H);
    ctx.textAlign="center";ctx.fillStyle="#f85149";ctx.font="bold 34px sans-serif";
    ctx.fillText("Прорыв",W/2,H/2-40);
    ctx.fillStyle="#8b949e";ctx.font="14px sans-serif";
    ctx.fillText("Полигон "+P.name+" · волна "+S.wave+" · клик — в меню",W/2,H/2);
  }
}
function syncHud(){
  document.getElementById("gold").textContent=S.gold;
  document.getElementById("lives").textContent=S.lives;
  document.getElementById("wave").textContent=S.wave;
  document.getElementById("poly").textContent=S.screen==="game"?POLYGONS[S.pi].name:"—";
  const shop=document.getElementById("shop");
  if(S.screen==="game"){
    shop.style.display="flex";
    [...shop.children].forEach((el,i)=>{
      const d=TOWERS[i];
      el.classList.toggle("sel",i===S.selTower);
      el.innerHTML="<b>"+d.name+"</b><span>"+d.cost+" · "+d.desc+"</span>";
    });
  }else shop.style.display="none";
  const rb=document.getElementById("repair");
  if(rb){const can=S.screen==="game"&&S.lives<LIVES0&&S.gold>=TUNE.repairCost;
    rb.style.opacity=can?"1":"0.4";rb.style.pointerEvents=can?"auto":"none";}
}
let last=performance.now();
function loop(now){const dt=Math.min((now-last)/1000,0.05);last=now;
  if(S.screen==="menu"||S.screen==="win")S.time+=dt;
  update(dt);draw();syncHud();requestAnimationFrame(loop);}
cv.addEventListener("click",()=>{if(S.screen==="dead")S.screen="menu";});
document.getElementById("playmenu").addEventListener("click",()=>{setPolygon(0);S.screen="game";});
document.getElementById("nextwave").addEventListener("click",()=>startWave());
document.getElementById("repair").addEventListener("click",()=>{
  if(S.screen!=="game")return;
  if(S.lives>=LIVES0||S.gold<TUNE.repairCost)return;
  S.gold-=TUNE.repairCost;S.lives++;
});
setPolygon(0);S.screen="menu";
requestAnimationFrame(loop);
"""

html_tpl = """<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8"><title>Полигоны · TD — 5×5</title>
<style>
html,body{margin:0;min-height:100%;background:#0d1117;color:#c9d1d9;font-family:-apple-system,Segoe UI,Roboto,sans-serif;display:flex;align-items:center;justify-content:center}
#wrap{position:relative;padding-bottom:78px}
canvas{display:block;border-radius:10px;background:#4a6b32;box-shadow:0 0 0 1px #30363d;cursor:pointer}
#hud{position:absolute;top:10px;left:14px;right:14px;display:flex;gap:22px;font-size:14px;pointer-events:none;text-shadow:0 1px 3px #000,0 0 6px #000}
#hud b{color:#f0f6fc}#hud .gold{color:#e3b341}#hud .life{color:#f85149}#hud .wave{color:#79c0ff}#hud .poly{color:#a5d6ff}
#shop{position:absolute;left:0;right:0;bottom:-72px;display:none;gap:6px}
#shop div{flex:1;background:#161b22;border:1px solid #30363d;border-radius:8px;padding:6px 4px;font-size:11px;text-align:center;cursor:pointer;line-height:1.3}
#shop div.sel{border-color:#3fb950;background:#0f2a18}
#shop b{display:block;font-size:12px;color:#f0f6fc}#shop span{color:#8b949e}
#bar{position:absolute;left:0;right:0;bottom:-30px;display:flex;gap:8px;justify-content:center;font-size:12px;color:#6e7681}
button{background:#238636;border:0;color:#fff;padding:6px 14px;border-radius:8px;font-size:13px;cursor:pointer;font-weight:600}
button:hover{background:#2ea043}
</style></head><body>
<div id="wrap"><canvas id="c" width="900" height="500"></canvas>
<div id="hud"><span class="gold">💰 <b id="gold">0</b></span><span class="life">❤ <b id="lives">20</b></span><span class="wave">🌊 <b id="wave">0</b>/5</span><span class="poly">📍 <b id="poly">—</b></span></div>
<div id="shop"><div></div><div></div><div></div><div></div><div></div></div>
<div id="bar"><span>1–5 выбор башни · клик по площадке — построить · клик по башне — апгрейд (до L4) · пробел — волна · ремонт +1 ❤ за 400</span><button id="playmenu">Играть</button><button id="nextwave">Волна</button><button id="repair">Ремонт 400</button></div>
</div><script>
__GAME__
</script></body></html>
"""

game_js = game_js.replace("__RECTS__", json.dumps(rects))
game_js = game_js.replace("__ATLAS__", b64)
html = html_tpl.replace("__GAME__", game_js)
OUT.parent.mkdir(parents=True, exist_ok=True)
open(OUT,"w").write(html)
print(f"wrote {OUT} {len(html)} bytes")
