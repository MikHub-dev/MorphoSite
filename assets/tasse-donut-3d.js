/* MorphoSite : la tasse et le donut en 3D (SVG + petit moteur de projection, sans bibliothèque).
   <svg data-3d="fraise">  : tasse rouge  ⇄ donut à la fraise
   <svg data-3d="choco">   : donut au chocolat ⇄ tasse chocolat
   Un seul paramètre k (0 = tasse, 1 = donut) déforme continûment l'objet : l'anse grossit et devient l'anneau,
   le corps de la tasse se tasse, perd son creux et se fond dans l'anneau. Rien n'est coupé ni recollé. */
(function(){
const NS='http://www.w3.org/2000/svg', F=600, D=600, S=70;
const RM=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
const f1=v=>Math.round(v*10)/10, PI=Math.PI;
const L=(()=>{const v=[-.5,.8,.6],n=Math.hypot(...v);return v.map(a=>a/n)})();
const lerp=(a,b,k)=>a+(b-a)*k, sm=(a,b,x)=>{const t=Math.max(0,Math.min(1,(x-a)/(b-a)));return t*t*(3-2*t)};
const hex=h=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16));
const mixc=(a,b,k)=>a.map((v,i)=>v+(b[i]-v)*k);
const rgb=c=>'rgb('+c.map(v=>Math.round(Math.max(0,Math.min(255,v)))).join(',')+')';
const sub=(a,b)=>[a[0]-b[0],a[1]-b[1],a[2]-b[2]];
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
function rot(p,c){const x1=p[0]*c.cy+p[2]*c.sy,z1=-p[0]*c.sy+p[2]*c.cy;return[x1,p[1]*c.cp-z1*c.sp,p[1]*c.sp+z1*c.cp];}
function proj(v,c){const s=F/(D-v[2]);return[c.x+v[0]*s,c.y-v[1]*s,s];}

const THEMES={
  /* tasse rouge → donut fraise */
  fraise:{cup:hex('#d62f3c'),dough:hex('#e0a868'),glaze:hex('#f58bb4'),
    spr:['#ffffff','#ffe066','#7cd7ff','#9be38a','#ff5d7a'],shadow:'#f58bb4',start:0,period:14,yaw0:.5},
  /* donut chocolat → tasse chocolat */
  choco:{cup:hex('#7a4528'),dough:hex('#d99c5e'),glaze:hex('#4a2614'),
    spr:['#ff6b9a','#ffd23f','#6ec6ff','#8ce07a','#ffffff'],shadow:'#c08457',start:.5,period:17,yaw0:-.6}
};

/* ---------- géométrie déformable ---------- */
const NU=40, NV=16, NA=32;
function shape(k){
  const hc=lerp(.8,0,k), Rm=lerp(.36,1,k), rt=lerp(.1,.42,sm(0,.9,k)), phi=lerp(.7*PI,PI,sm(0,.85,k));
  const bx=lerp(0,-1,k), Rb=lerp(.64,.3,sm(.05,.95,k)), h=lerp(.6,.26,sm(.05,.95,k));
  const dpt=lerp(-h+.12,h,sm(.1,.5,k)), w=.07;
  return{hc,Rm,rt,phi,bx,Rb,h,dpt,w};
}
/* anse / anneau : tube le long d'un arc du plan xy, centré en (hc,0) */
function handle(g,k){
  const P=[];
  for(let i=0;i<=NU;i++){
    const a=-g.phi+2*g.phi*i/NU, ca=Math.cos(a), sa=Math.sin(a);
    const cx=g.hc+g.Rm*ca, cy=g.Rm*sa, row=[];
    for(let j=0;j<=NV;j++){const v=2*PI*j/NV;row.push([cx+g.rt*Math.cos(v)*ca, cy+g.rt*Math.cos(v)*sa, g.rt*Math.sin(v)]);}
    P.push(row);
  }
  return P;
}
/* corps : surface de révolution autour de l'axe vertical passant par (bx,·,0) */
function body(g){
  const{Rb,h,dpt,w}=g, c=.07;
  const prof=[[0,-h],[Rb-c,-h],[Rb-c*.3,-h+c*.3],[Rb,-h+c],[Rb,h-.02],[Rb-w*.5,h],[Rb-w,h-.02],[Rb-w,Math.min(h-.02,dpt+.06)],[Rb-w-.05,dpt],[0,dpt]];
  const P=[];
  for(const[r,y]of prof){const row=[];for(let j=0;j<=NA;j++){const a=2*PI*j/NA;row.push([g.bx+r*Math.cos(a),y,r*Math.sin(a)]);}P.push(row);}
  return P;
}
/* bascule finale : l'anneau (plan xy) se couche (plan xz), le dessus devient +z local */
function place(k){
  const t=-PI/2*sm(.45,1,k), c=Math.cos(t), s=Math.sin(t), ox=lerp(-.25,0,k), oy=lerp(.02,-.08,k);
  return p=>{const x=p[0]+ox, y=p[1]*c-p[2]*s, z=p[1]*s+p[2]*c;return[x*S,(y+oy)*S,z*S];};
}

/* paillettes du glaçage, tirées une fois pour toutes */
function sprinkles(th){
  let seed=th===THEMES.fraise?7:13;const rnd=()=>(seed=(seed*16807)%2147483647)/2147483647;
  const o=[];
  for(let i=0;i<46;i++){const u=rnd()*2*PI, v=PI*(.12+.76*rnd()), d=rnd()*PI;o.push({u,v,d,c:th.spr[i%th.spr.length]});}
  return o;
}

function Scene(svg,key){
  const th=THEMES[key];this.svg=svg;svg.__scene=this;this.th=th;this.spr=sprinkles(th);
  this.uy=0;this.up=0;this.hy=0;this.hp=0;this.thy=0;this.thp=0;
  const d=document.createElementNS(NS,'defs');
  d.innerHTML=`<radialGradient id="ombre-${key}"><stop offset="0" stop-color="${th.shadow}" stop-opacity=".38"/><stop offset=".6" stop-color="${th.shadow}" stop-opacity=".1"/><stop offset="1" stop-color="${th.shadow}" stop-opacity="0"/></radialGradient>`;
  svg.appendChild(d);
  this.g=document.createElementNS(NS,'g');svg.appendChild(this.g);
  let drag=null;
  svg.style.touchAction='pan-y';svg.style.cursor='grab';
  svg.addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY,uy:this.uy,up:this.up};svg.style.cursor='grabbing';});
  window.addEventListener('pointerup',()=>{if(drag){drag=null;svg.style.cursor='grab';}});
  svg.addEventListener('pointermove',e=>{
    const r=svg.getBoundingClientRect();
    if(drag){this.uy=drag.uy+(e.clientX-drag.x)*.012;this.up=Math.max(-.3,Math.min(.6,drag.up+(e.clientY-drag.y)*.006));}
    else{this.thy=((e.clientX-r.left)/r.width-.5)*.6;this.thp=((e.clientY-r.top)/r.height-.5)*.3;}
  });
  svg.addEventListener('pointerleave',()=>{this.thy=0;this.thp=0;});
}
/* cycle : pause, déformation lente, pause, retour */
Scene.prototype.k=function(t){
  const th=this.th;if(RM)return th.start;
  const s=((t/th.period)+th.start)%1;
  let k= s<.2?0 : s<.5?sm(.2,.5,s) : s<.7?1 : 1-sm(.7,1,s);
  return k;
};
Scene.prototype.frame=function(t){
  const th=this.th,k=this.k(t),g=shape(k),W=place(k);
  this.hy+=(this.thy-this.hy)*.08;this.hp+=(this.thp-this.hp)*.08;
  const yaw=th.yaw0+(RM?0:t*.32)+this.uy+this.hy, pit=.42+this.up+this.hp;
  const C={cy:Math.cos(yaw),sy:Math.sin(yaw),cp:Math.cos(pit),sp:Math.sin(pit),x:120,y:128};
  const cupMix=1-sm(.25,.85,k), items=[];
  const face=(q,col,spec)=>{
    const V=q.map(p=>rot(W(p),C));
    const n=cross(sub(V[1],V[0]),sub(V[3],V[0]));let nl=Math.hypot(...n);
    if(nl<1e-6){const n2=cross(sub(V[2],V[1]),sub(V[0],V[1]));nl=Math.hypot(...n2);if(nl<1e-6)return;n[0]=n2[0];n[1]=n2[1];n[2]=n2[2];}
    const cx=(V[0][0]+V[1][0]+V[2][0]+V[3][0])/4,cy=(V[0][1]+V[1][1]+V[2][1]+V[3][1])/4,cz=(V[0][2]+V[1][2]+V[2][2]+V[3][2])/4;
    if(n[0]*(-cx)+n[1]*(-cy)+n[2]*(D-cz)<=0)return;
    const u=n.map(a=>a/nl), lam=Math.max(0,u[0]*L[0]+u[1]*L[1]+u[2]*L[2]);
    const hl=[L[0],L[1],L[2]+1],hn=Math.hypot(...hl),sp=Math.pow(Math.max(0,(u[0]*hl[0]+u[1]*hl[1]+u[2]*hl[2])/hn),24)*(spec||.5);
    let c=mixc(col.map(v=>v*.28),col,.25+.75*lam);c=mixc(c,[255,255,255],sp);
    items.push({d:cz,s:`<polygon points="${q.map((_,i)=>{const P=proj(V[i],C);return f1(P[0])+','+f1(P[1])}).join(' ')}" fill="${rgb(c)}" stroke="${rgb(c)}" stroke-width=".6" stroke-linejoin="round"/>`});
  };
  /* couleur du donut : glaçage sur le dessus (bord ondulé), pâte dessous */
  const donutCol=(u,v)=>{const edge=-.18+.12*Math.sin(5*u)+.06*Math.sin(11*u+1);return Math.sin(v)>edge?th.glaze:th.dough;};
  const H=handle(g,k);
  for(let i=0;i<NU;i++)for(let j=0;j<NV;j++){
    const u=-g.phi+2*g.phi*(i+.5)/NU, v=2*PI*(j+.5)/NV, dc=donutCol(u,v);
    face([H[i][j],H[i+1][j],H[i+1][j+1],H[i][j+1]],mixc(dc,th.cup,cupMix),dc===th.glaze?.9:.35);
  }
  const B=body(g), bcol=mixc(th.glaze,th.cup,cupMix);
  for(let i=0;i<B.length-1;i++)for(let j=0;j<NA;j++)
    face([B[i][j],B[i+1][j],B[i+1][j+1],B[i][j+1]],i>=6?mixc(bcol.map(v=>v*.8),bcol,.4):bcol,.7);
  /* paillettes : posées sur le glaçage quand le donut est formé */
  const so=sm(.82,1,k);
  if(so>0.01)for(const p of this.spr){
    const ca=Math.cos(p.u),sa=Math.sin(p.u),r=g.rt*1.02;
    const at=(du,dv)=>{const v=p.v+dv,u=p.u+du,cu=Math.cos(u),su=Math.sin(u);return[g.hc+(g.Rm+r*Math.cos(v))*cu,(g.Rm+r*Math.cos(v))*su,r*Math.sin(v)];};
    const A=rot(W(at(.045*Math.cos(p.d),.13*Math.sin(p.d))),C),Bp=rot(W(at(-.045*Math.cos(p.d),-.13*Math.sin(p.d))),C);
    const W0=W([0,0,0]),[nx,ny,nz]=rot(sub(W([ca*Math.cos(p.v),sa*Math.cos(p.v),Math.sin(p.v)]),W0),C);
    const mx=(A[0]+Bp[0])/2,my=(A[1]+Bp[1])/2,mz=(A[2]+Bp[2])/2;
    if(nx*(-mx)+ny*(-my)+nz*(D-mz)<=0)continue;
    const P1=proj(A,C),P2=proj(Bp,C);
    items.push({d:mz+.5,s:`<line x1="${f1(P1[0])}" y1="${f1(P1[1])}" x2="${f1(P2[0])}" y2="${f1(P2[1])}" stroke="${p.c}" stroke-width="${f1(2.6*P1[2])}" stroke-linecap="round" opacity="${so}"/>`});
  }
  items.sort((a,b)=>a.d-b.d);
  /* ombre au sol */
  const fl=[];for(let i=0;i<=40;i++){const a=2*PI*i/40;fl.push(proj(rot([Math.cos(a)*S*1.55,-S*.66,Math.sin(a)*S*1.55],C),C));}
  let o=`<polygon points="${fl.map(P=>f1(P[0])+','+f1(P[1])).join(' ')}" fill="url(#ombre-${this.svg.getAttribute('data-3d')})"/>`;
  /* vapeur au-dessus de la tasse */
  const st=1-sm(0,.18,k);
  if(st>.01){const top=W([g.bx,g.h,0]);
    for(let s=0;s<3;s++){let d='';const ph=t*1.6+s*2.1;
      for(let i=0;i<=12;i++){const y=top[1]+8+i*4.2,x=top[0]+(s-1)*9+4*Math.sin(ph+i*.55);const P=proj(rot([x,y,top[2]+(s-1)*3],C),C);d+=f1(P[0])+','+f1(P[1])+' ';}
      o+=`<polyline points="${d}" fill="none" stroke="#e8e6ff" stroke-width="2.8" stroke-linecap="round" opacity="${f1(st*(.35+.15*Math.sin(t*1.3+s))*100)/100}"/>`;}
  }
  for(const it of items)o+=it.s;
  this.g.innerHTML=o;
};

const scenes=[];
document.querySelectorAll('svg[data-3d]').forEach(svg=>{const k=svg.getAttribute('data-3d');if(THEMES[k])scenes.push(new Scene(svg,k));});
if(!scenes.length)return;
const t0=performance.now();let vis=true;
document.addEventListener('visibilitychange',()=>{vis=!document.hidden;});
function loop(now){if(vis){const t=(now-t0)/1000;for(const s of scenes){const r=s.svg.getBoundingClientRect();if(r.bottom>0&&r.top<innerHeight)s.frame(t);}}if(!RM)requestAnimationFrame(loop);}
scenes.forEach(s=>s.frame(0));if(!RM)requestAnimationFrame(loop);else addEventListener('pointermove',()=>scenes.forEach(s=>s.frame(0)));
})();
