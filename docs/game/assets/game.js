(function(){
"use strict";

var PATTERNS = (window.GAME_DATA && window.GAME_DATA.patterns) || [];
var BY_ID = {};
PATTERNS.forEach(function(p){ BY_ID[p.id] = p; });

/* ============================ utils ============================ */
function $(sel, root){ return (root||document).querySelector(sel); }
function ce(tag, cls, html){ var e=document.createElement(tag); if(cls) e.className=cls; if(html!=null) e.innerHTML=html; return e; }
function esc(s){ return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
function randInt(n){ return Math.floor(Math.random()*n); }
function choice(arr){ return arr[randInt(arr.length)]; }
function shuffle(arr){ var a=arr.slice(); for(var i=a.length-1;i>0;i--){ var j=randInt(i+1); var t=a[i]; a[i]=a[j]; a[j]=t; } return a; }
function uniq(arr){ var seen={}, out=[]; arr.forEach(function(x){ if(!seen[x]){ seen[x]=1; out.push(x); } }); return out; }
function sample(arr, n){ return shuffle(arr).slice(0, n); }

/* ============================ persistence ============================ */
var LS_KEY = "pf-save-v1";
var save = (function(){
  var d = { xp:0, high:0, bestStreak:0, mastery:{}, sound:true, haptics:true };
  try{ var raw=localStorage.getItem(LS_KEY); if(raw){ var p=JSON.parse(raw); for(var k in p) d[k]=p[k]; } }catch(e){}
  return d;
})();
function persist(){ try{ localStorage.setItem(LS_KEY, JSON.stringify(save)); }catch(e){} }

var RANKS = [
  {n:"White Belt",min:0},{n:"Yellow Belt",min:300},{n:"Orange Belt",min:800},
  {n:"Green Belt",min:1700},{n:"Blue Belt",min:3000},{n:"Purple Belt",min:4800},
  {n:"Brown Belt",min:7200},{n:"Black Belt",min:10500},{n:"Grandmaster",min:15000}
];
function rankFor(xp){ var r=RANKS[0]; for(var i=0;i<RANKS.length;i++){ if(xp>=RANKS[i].min) r=RANKS[i]; } return r.n; }
function masteryCount(id){ return save.mastery[id]||0; }
function masteryStars(id){ var c=masteryCount(id); return c>=15?3:c>=7?2:c>=3?1:0; }

/* ============================ poison: line mutation engine ============================ */
/* Each rule turns a correct line into a plausible-but-buggy one — exactly the
   off-by-one / operator / direction mistakes the guide's "watch out" boxes warn about. */
var LINE_RULES = [
  [/<=/, "<"], [/>=/, ">"],
  [/ \+ 2\b/, " - 2"], [/ \+ 1\b/, " - 1"], [/ - 1\b/, " + 1"],
  [/\+= /, "-= "], [/-= /, "+= "],
  [/\bmin\(/, "max("], [/\bmax\(/, "min("],
  [/\bleft\b/, "right"], [/\bright\b/, "left"],
  [/\bslow\b/, "fast"], [/\bfast\b/, "slow"],
  [/\bprev1\b/, "prev2"], [/\bprev2\b/, "prev1"],
  [/\bprev\b/, "curr"], [/\bcurr\b/, "prev"],
  [/ or /, " and "], [/ and /, " or "],
  [/\bi - 1\b/, "i + 1"], [/\bi \+ 1\b/, "i - 1"],
  [/\bj - 1\b/, "j + 1"], [/\bj \+ 1\b/, "j - 1"],
  [/, -1\)/, ", 1)"],
  [/\bTrue\b/, "False"], [/\bFalse\b/, "True"],
  [/ < /, " > "], [/ > /, " < "]
];
function mutateLine(line){
  var out = [];
  for(var i=0;i<LINE_RULES.length;i++){
    var r=LINE_RULES[i];
    if(r[0].test(line)){
      var m=line.replace(r[0], r[1]);
      if(m!==line) out.push(m);
    }
  }
  return uniq(out);
}

/* token-level distractors for cloze blanks */
var TOKEN_MUT = {
  "<=":["<",">="], ">=":[">","<="], "==":["!=","<="], "!=":["==",">="],
  "<":[">","<="], ">":["<",">="],
  "min":["max"], "max":["min"], "left":["right"], "right":["left"],
  "slow":["fast"], "fast":["slow"], "prev":["curr"], "curr":["prev"],
  "and":["or"], "or":["and"], "True":["False"], "False":["True"]
};
var TOKEN_RE = /(<=|>=|==|!=|\bmin\b|\bmax\b|\bleft\b|\bright\b|\bslow\b|\bfast\b|\bprev\b|\bcurr\b|\band\b|\bor\b|\bTrue\b|\bFalse\b|<|>)/g;

function findBlanks(lines){
  var cands=[];
  lines.forEach(function(line, li){
    TOKEN_RE.lastIndex=0; var m;
    while((m=TOKEN_RE.exec(line))!==null){
      var tok=m[0];
      if(TOKEN_MUT[tok]){ cands.push({li:li, start:m.index, tok:tok}); }
    }
  });
  return cands;
}

/* ============================ audio (synth, no files) ============================ */
var AC=null;
function actx(){ if(!save.sound) return null; try{ if(!AC) AC=new (window.AudioContext||window.webkitAudioContext)(); if(AC.state==="suspended") AC.resume(); return AC; }catch(e){ return null; } }
function tone(freq, dur, type, vol, delay){
  var ac=actx(); if(!ac) return;
  var t=ac.currentTime+(delay||0);
  var o=ac.createOscillator(), g=ac.createGain();
  o.type=type||"sine"; o.frequency.setValueAtTime(freq, t);
  g.gain.setValueAtTime(0.0001, t);
  g.gain.exponentialRampToValueAtTime(vol||0.18, t+0.012);
  g.gain.exponentialRampToValueAtTime(0.0001, t+dur);
  o.connect(g); g.connect(ac.destination); o.start(t); o.stop(t+dur+0.02);
}
var SFX={
  click:function(){ tone(420,0.05,"square",0.06); },
  correct:function(){ tone(660,0.10,"sine",0.16,0); tone(990,0.14,"sine",0.16,0.08); },
  combo:function(n){ var b=520+Math.min(n,10)*60; tone(b,0.08,"triangle",0.14,0); tone(b*1.5,0.12,"triangle",0.13,0.06); },
  wrong:function(){ tone(200,0.18,"sawtooth",0.14,0); tone(150,0.22,"sawtooth",0.12,0.06); },
  level:function(){ [523,659,784,1046].forEach(function(f,i){ tone(f,0.16,"triangle",0.16,i*0.09); }); },
  over:function(){ [392,330,262,196].forEach(function(f,i){ tone(f,0.22,"sawtooth",0.14,i*0.12); }); },
  win:function(){ [523,659,784,1046,1318].forEach(function(f,i){ tone(f,0.18,"sine",0.17,i*0.08); }); }
};

/* ============================ haptics ============================ */
function buzz(p){ if(save.haptics && navigator.vibrate){ try{ navigator.vibrate(p); }catch(e){} } }

/* ============================ confetti ============================ */
var fx=$("#fx"), fxctx=fx?fx.getContext("2d"):null, parts=[], fxRAF=null;
function sizeFx(){ if(!fx) return; fx.width=innerWidth; fx.height=innerHeight; }
window.addEventListener("resize", sizeFx); sizeFx();
function confetti(n){
  if(!fxctx) return; sizeFx();
  var colors=["#a371f7","#f778ba","#ffa657","#3fb950","#58a6ff"];
  for(var i=0;i<(n||80);i++){
    parts.push({x:innerWidth/2,y:innerHeight*0.3,vx:(Math.random()-0.5)*9,vy:Math.random()*-9-3,g:0.28,
      s:4+Math.random()*6, c:colors[randInt(colors.length)], a:1, rot:Math.random()*6, vr:(Math.random()-0.5)*0.4});
  }
  if(!fxRAF) fxRAF=requestAnimationFrame(stepFx);
}
function stepFx(){
  fxctx.clearRect(0,0,fx.width,fx.height);
  for(var i=parts.length-1;i>=0;i--){
    var p=parts[i]; p.vy+=p.g; p.x+=p.vx; p.y+=p.vy; p.rot+=p.vr; p.a-=0.012;
    if(p.a<=0||p.y>fx.height+30){ parts.splice(i,1); continue; }
    fxctx.save(); fxctx.globalAlpha=Math.max(p.a,0); fxctx.translate(p.x,p.y); fxctx.rotate(p.rot);
    fxctx.fillStyle=p.c; fxctx.fillRect(-p.s/2,-p.s/2,p.s,p.s*0.6); fxctx.restore();
  }
  if(parts.length){ fxRAF=requestAnimationFrame(stepFx); } else { fxRAF=null; }
}
function floatPoints(txt){
  var e=ce("div","floatpts",esc(txt)); e.style.left=(innerWidth/2-20)+"px"; e.style.top="38%";
  document.body.appendChild(e); setTimeout(function(){ e.remove(); }, 900);
}

/* ============================ game state ============================ */
var G={};
var MODES=[
  {id:"forge",  emoji:"&#128296;", name:"Code Forge",        desc:"Rebuild the code. Easy lines &rarr; Hard tokens."},
  {id:"cloze",  emoji:"&#129513;", name:"Fill the Gap",      desc:"Drop the right token into every blank."},
  {id:"bug",    emoji:"&#128030;", name:"Bug Hunt",          desc:"One line was poisoned. Hunt it down."},
  {id:"name",   emoji:"&#128373;", name:"Name That Pattern", desc:"Match the clue to its pattern."},
  {id:"bigo",   emoji:"&#128200;", name:"Big-O Climb",       desc:"Recall time & space complexity."},
  {id:"mnemo",  emoji:"&#129504;", name:"Mnemonic Match",    desc:"Match the pattern to its memory hook."},
  {id:"survival",emoji:"&#128128;",name:"The Gauntlet",      desc:"All modes. 3 lives. A ticking clock. How far?"}
];
var SCOPES=[{id:"all",n:"All 37"},{id:"core",n:"Core 15"},{id:"dp",n:"DP 20"},{id:"advanced",n:"Advanced"}];
var DIFFS=[{id:"easy",n:"Easy"},{id:"medium",n:"Medium"},{id:"hard",n:"Hard"}];
var DIFF_DESC={
  easy:"Reorder whole lines &mdash; dodge the poison lines.",
  medium:"Rebuild from jumbled code chunks &mdash; order matters.",
  hard:"Rebuild from single tokens &mdash; some are poison."
};
var scope="all";
var diff="easy";    /* difficulty for Code Forge: easy | medium | hard */
var forgeSrc="template"; /* which snippet Code Forge rebuilds: template | example */
var focusId=null;   /* when set (via ?pattern=...), every "main" question targets this one pattern */

function pool(){
  if(focusId) return [BY_ID[focusId]];
  return scope==="all" ? PATTERNS : PATTERNS.filter(function(p){ return p.cat===scope; });
}
function withTemplate(maxLines){ return pool().filter(function(p){ return p.template && p.template.length>=3 && p.template.length<=(maxLines||13); }); }
function clearFocus(){ focusId=null; try{ history.replaceState(null,"",location.pathname); }catch(e){} renderHome(); show(homeEl); }

/* ============================ screens ============================ */
var homeEl=$("#home"), gameEl=$("#game"), sumEl=$("#summary");

function show(which){
  [homeEl,gameEl,sumEl].forEach(function(s){ s.classList.add("hidden"); });
  which.classList.remove("hidden");
  window.scrollTo(0,0);
}

function renderHome(){
  var stars=0, total=0; pool().forEach(function(p){ stars+=masteryStars(p.id); total+=3; });
  var h="";
  h+='<div class="hero"><h1>Pattern Forge</h1>'+
     '<p>Forge the 37 DSA templates into muscle memory. Reorder code, fill the gaps, hunt the poison, and survive the gauntlet.</p></div>';
  if(focusId){
    h+='<div class="focus-banner">&#127919; Drilling <b>'+esc(BY_ID[focusId].name)+'</b>'+
       '<button id="clearFocus" class="focus-exit">&#10005; all patterns</button></div>';
  }
  h+='<div class="statbar">'+
     '<div class="stat"><b>'+save.high+'</b><span>High score</span></div>'+
     '<div class="stat"><b>'+save.bestStreak+'</b><span>Best streak</span></div>'+
     '<div class="stat"><b>'+save.xp+'</b><span>Total XP</span></div>'+
     '<div class="stat"><b>'+stars+'/'+total+'</b><span>Mastery &#9733;</span></div>'+
     '</div>';
  if(!focusId){ h+='<div class="section-label">Pattern pack</div><div class="scope" id="scope"></div>'; }
  h+='<div class="section-label">Code Forge difficulty</div><div class="scope" id="diffSel"></div>'+
     '<div class="diff-note" id="diffNote">'+DIFF_DESC[diff]+'</div>';
  h+='<div class="section-label">'+(focusId?'Pick a drill for this pattern':'Choose your trial')+'</div><div class="modes" id="modeGrid"></div>';
  h+='<div class="section-label">How it works</div><div class="howto">'+
     '<b>Memorize by doing.</b> Each mode quizzes the real templates &amp; examples from your study guide. '+
     'Wrong answers are <b>poisoned</b> with the exact off-by-one, operator and direction bugs the guide warns about &mdash; '+
     'so you learn to spot them. Build streaks for combo multipliers, earn XP to climb belts, and chase mastery stars on every pattern. '+
     'Sound &amp; vibration give you instant feedback (toggle them up top).</div>';
  h+='<div class="section-label">Mastery board</div><div class="mastery" id="masteryGrid"></div>';
  homeEl.innerHTML=h;

  var cf=$("#clearFocus"); if(cf) cf.onclick=function(){ SFX.click(); clearFocus(); };
  var sc=$("#scope");
  if(sc) SCOPES.forEach(function(s){
    var b=ce("button", s.id===scope?"active":"", s.n);
    b.onclick=function(){ scope=s.id; SFX.click(); renderHome(); };
    sc.appendChild(b);
  });
  var ds=$("#diffSel");
  if(ds) DIFFS.forEach(function(d){
    var b=ce("button", d.id===diff?"active":"", d.n);
    b.onclick=function(){ diff=d.id; SFX.click(); renderHome(); };
    ds.appendChild(b);
  });
  var mg=$("#modeGrid");
  MODES.forEach(function(m){
    var c=ce("button","mode-card"+(m.id==="survival"?" boss":""));
    c.innerHTML='<div class="emoji">'+m.emoji+'</div><h3>'+m.name+'</h3><p>'+m.desc+'</p>';
    c.onclick=function(){ SFX.click(); startSession(m.id); };
    mg.appendChild(c);
  });
  var bd=$("#masteryGrid");
  pool().forEach(function(p){
    var st=masteryStars(p.id);
    var stars5=""; for(var i=0;i<3;i++){ stars5+='<span class="'+(i<st?"star-on":"star-off")+'">&#9733;</span>'; }
    var t=ce("div","mtile");
    t.innerHTML='<div class="cat">'+p.cat+'</div><div class="mn">'+esc(p.name)+'</div><div class="ms">'+stars5+'</div>';
    bd.appendChild(t);
  });
  updateChips();
}

/* ============================ session flow ============================ */
function startSession(mode, opts){
  opts=opts||{};
  G={ mode:mode, survival:(mode==="survival"),
      diff:opts.diff||diff, src:(opts.src==="example"?"example":"template"),
      score:0, streak:0, combo:0,
      lives:(mode==="survival"?3:0), qIndex:0, qTotal:(mode==="survival"?Infinity:10),
      correct:0, answered:false, curId:null, timer:null, timeLeft:0, timeMax:0 };
  show(gameEl); nextQuestion();
}

function timeForMode(mode){
  var forgeBase=(G.diff==="hard")?60:(G.diff==="medium")?46:34;
  var base={forge:forgeBase,cloze:28,bug:20,name:13,bigo:15,mnemo:13}[mode]||16;
  return Math.max(7, base - Math.floor(G.qIndex/4));
}

function nextQuestion(){
  if(!G.survival && G.qIndex>=G.qTotal){ return endSession(); }
  G.qIndex++; G.answered=false; stopTimer();
  var primary = G.survival ? choice(["forge","cloze","bug","name","bigo","mnemo"]) : G.mode;
  var order=[primary];
  /* when drilling one pattern, gracefully fall back to whatever builds for it */
  if(focusId) order=order.concat(["cloze","bug","forge","name","bigo","mnemo"]);
  var mode=primary, built=null;
  for(var oi=0; oi<order.length && !built; oi++){
    var tries=0; while(!built && tries<25){ tries++; built=BUILDERS[order[oi]](); }
    if(built) mode=order[oi];
  }
  if(!built){ mode="name"; built=BUILDERS.name(); }   /* name mode always works */
  G.curId=built.patternId;
  renderQuestion(mode, built);
  if(G.survival){ startTimer(timeForMode(mode)); }
}

function renderQuestion(mode, built){
  var modeName=(function(){ for(var i=0;i<MODES.length;i++) if(MODES[i].id===mode) return MODES[i].name; return mode; })();
  var hud='<div class="hud">'+
    '<button class="btn-back" id="quitBtn">&#8592; Quit</button>'+
    '<div class="hud-score"><small>Score</small>'+G.score+'</div>'+
    (G.combo>1?'<span class="combo-flag">&#128293; x'+comboMult().toFixed(2)+'</span>':'<span class="streak">'+(G.streak>0?("&#128293; "+G.streak):"")+'</span>')+
    (G.survival?('<div class="lives">'+livesHTML()+'</div>'):('<div class="qcount">'+G.qIndex+' / '+G.qTotal+'</div>'))+
    '</div>';
  var timer=G.survival?'<div class="timer-wrap"><div class="timer-bar" id="timerBar"></div></div>':'';
  var card='<div class="qcard"><div class="qmode">'+modeName+'</div>'+
           '<div class="qinstr">'+built.instr+'</div>'+
           '<div id="qbody"></div>'+
           '<div id="qactions"></div>'+
           '<div id="qfeedback"></div></div>';
  gameEl.innerHTML=hud+timer+card;
  $("#quitBtn").onclick=function(){ SFX.click(); stopTimer(); renderHome(); show(homeEl); };
  built.mount($("#qbody"), $("#qactions"), finishQuestion);
}

function comboMult(){ return 1 + Math.min(Math.max(G.combo-1,0),9)*0.15; }
function livesHTML(){ var s=""; for(var i=0;i<3;i++){ s+= (i<G.lives)?"&#10084;&#65039;":"&#128420;"; } return s; }

function finishQuestion(correct, revealHTML){
  if(G.answered) return; G.answered=true; stopTimer();
  var pts=0;
  if(correct){
    G.correct++; G.streak++; G.combo++;
    var speed=1;
    if(G.survival && G.timeMax>0){ speed=0.6+0.4*(G.timeLeft/G.timeMax); }
    pts=Math.round(100*comboMult()*speed);
    G.score+=pts; save.xp+=Math.round(pts/8);
    save.mastery[G.curId]=(save.mastery[G.curId]||0)+1;
    if(G.streak>save.bestStreak) save.bestStreak=G.streak;
    persist(); updateChips();
    if(G.combo>=2){ SFX.combo(G.combo); } else { SFX.correct(); }
    buzz(G.combo>=5?[18,40,18]:30);
    if(G.combo>0 && G.combo%5===0){ confetti(90); SFX.level(); buzz([20,30,20,30,40]); }
    floatPoints("+"+pts);
  } else {
    G.streak=0; G.combo=0;
    if(G.survival) G.lives--;
    SFX.wrong(); buzz([60,40,90]);
  }
  showFeedback(correct, pts, revealHTML);
}

function showFeedback(correct, pts, revealHTML){
  var fb=$("#qfeedback");
  var head=correct?("&#9989; Forged!"):("&#10060; Poisoned!");
  var ptsHTML=correct?('<span class="points">+'+pts+'</span>'):"";
  fb.innerHTML='<div class="feedback '+(correct?"good":"bad")+'">'+
    '<div class="fb-head">'+head+ptsHTML+'</div>'+
    (revealHTML?('<div class="fb-body">'+revealHTML+'</div>'):'')+'</div>';
  var act=$("#qactions"); act.innerHTML="";
  var gameOver = G.survival && G.lives<=0;
  var b=ce("button","btn btn-primary", gameOver?"See results &#8594;":(!G.survival && G.qIndex>=G.qTotal?"Finish &#8594;":"Next &#8594;"));
  b.onclick=function(){ SFX.click(); gameOver?endSession():nextQuestion(); };
  act.appendChild(b);
  if(gameOver){ setTimeout(endSession, 1400); }
  else if(G.survival){ /* keep manual to let players read the reveal */ }
}

function endSession(){
  stopTimer();
  var newHigh = G.score>save.high;
  if(newHigh) save.high=G.score; persist();
  var acc = G.qIndex>0 ? Math.round(100*G.correct/Math.max(G.qIndex - (G.survival?0:0),1)) : 0;
  if(G.survival && G.lives<=0){ SFX.over(); } else if(acc>=80){ SFX.win(); confetti(160); } else { SFX.correct(); }
  buzz(newHigh?[30,40,30,40,60]:[40]);
  var ranked=rankFor(save.xp);
  var h='<div class="sum-wrap">';
  h+='<h2>'+(G.survival?"Gauntlet over":"Round complete")+'</h2>';
  h+='<div class="sum-score">'+G.score+'</div>';
  if(newHigh) h+='<div class="new-best">&#127881; New high score!</div>';
  h+='<div class="sum-grid">'+
     '<div class="stat"><b>'+G.correct+'</b><span>Correct</span></div>'+
     '<div class="stat"><b>'+acc+'%</b><span>Accuracy</span></div>'+
     '<div class="stat"><b>'+save.bestStreak+'</b><span>Best streak</span></div>'+
     '<div class="stat"><b>'+ranked+'</b><span>Belt</span></div>'+
     '</div>';
  h+='<div class="actions">'+
     '<button class="btn btn-primary" id="againBtn">Play again</button>'+
     '<button class="btn" id="homeBtn">Home</button></div>';
  h+='</div>';
  sumEl.innerHTML=h; show(sumEl);
  $("#againBtn").onclick=function(){ SFX.click(); startSession(G.mode,{diff:G.diff, src:G.src}); };
  $("#homeBtn").onclick=function(){ SFX.click(); renderHome(); show(homeEl); };
}

/* ============================ timer ============================ */
function startTimer(secs){
  G.timeMax=secs; G.timeLeft=secs;
  var bar=$("#timerBar"); if(bar) bar.style.width="100%";
  var tick=80; 
  G.timer=setInterval(function(){
    G.timeLeft-=tick/1000;
    var frac=Math.max(0,G.timeLeft/G.timeMax);
    if(bar){ bar.style.width=(frac*100)+"%"; bar.classList.toggle("warn", frac<0.33); }
    if(G.timeLeft<=0){ stopTimer(); if(!G.answered){ finishQuestion(false, "&#9203; Time ran out."); } }
  }, tick);
}
function stopTimer(){ if(G.timer){ clearInterval(G.timer); G.timer=null; } }

/* ============================ option helper ============================ */
function renderOptions(host, options, correctVal, isMono, finish, revealFn){
  var grid=ce("div","opts"+(isMono?"":" "));
  if(options.length<=3 && isMono) grid.className="opts one";
  options.forEach(function(opt){
    var b=ce("button","opt"+(isMono?" mono":""), esc(opt.label!=null?opt.label:opt));
    var val=opt.val!=null?opt.val:opt;
    b.onclick=function(){
      if(G.answered) return;
      var ok = (val===correctVal);
      Array.prototype.forEach.call(grid.children,function(c){ c.classList.add("disabled"); });
      b.classList.add(ok?"correct":"wrong");
      if(!ok){ b.classList.add("shake");
        Array.prototype.forEach.call(grid.children,function(c){
          if(c.getAttribute("data-val")===String(correctVal)) c.classList.add("correct");
        });
      }
      finish(ok, revealFn?revealFn(ok):"");
    };
    b.setAttribute("data-val", String(val));
    grid.appendChild(b);
  });
  host.appendChild(grid);
}

/* ============================ builders ============================ */
var BUILDERS={};

/* --- token helpers (Medium / Hard forge) --- */
function tokenizeLine(line, fine){
  var t=line.trim();
  if(!fine){ return t.split(/\s+/).filter(function(x){ return x.length; }); }
  var re=/(<=|>=|==|!=|\/\/|\*\*|->|"[^"]*"|'[^']*'|\w+|[^\s\w])/g;
  var out=[], m; while((m=re.exec(t))!==null){ out.push(m[0]); }
  return out;
}
function mutateToken(tok){
  var out=(TOKEN_MUT[tok]||[]).slice();
  if(/^\d+$/.test(tok)){ var n=parseInt(tok,10); out.push(String(n+1)); if(n>0) out.push(String(n-1)); }
  return uniq(out);
}
function indentUnits(line){
  var s=(line&&(line.match(/^[ \t]*/)||[""])[0])||"";
  return s.replace(/\t/g,"    ").length;
}
/* strip a trailing "# ..." comment (respecting quotes) so puzzles don't tokenize prose */
function stripComment(line){
  var inS=false, q="";
  for(var i=0;i<line.length;i++){
    var ch=line.charAt(i);
    if(inS){ if(ch===q && line.charAt(i-1)!=="\\") inS=false; }
    else if(ch==='"'||ch==="'"){ inS=true; q=ch; }
    else if(ch==="#"){ return line.slice(0,i); }
  }
  return line;
}
/* code with inline + full-line comments removed (blank lines dropped) */
function codeNoComments(code){
  var out=[];
  code.forEach(function(line){
    var s=stripComment(line).replace(/\s+$/,"");
    if(s.trim().length) out.push(s);
  });
  return out.length>=2 ? out : code.slice();
}

/* --- Code Forge: three difficulties, over the template OR the worked example --- */
BUILDERS.forge=function(){
  var src=(G.src==="example")?"example":"template";
  var dff=G.diff||"easy";
  var maxLines=(dff==="easy")?13:9;
  if(focusId){
    var fp=BY_ID[focusId];
    var fcode=fp[src]||fp.template||fp.example;
    if(!fcode || fcode.length<2) return null;
    return (dff==="easy")?forgeEasy(fp,fcode,src):forgeTokens(fp,fcode,dff,src);
  }
  var cands=pool().filter(function(p){ var c=p[src]; return c && c.length>=3 && c.length<=maxLines; });
  if(!cands.length && src==="example"){
    src="template";
    cands=pool().filter(function(p){ return p.template && p.template.length>=3 && p.template.length<=maxLines; });
  }
  if(!cands.length) return null;
  var p=choice(cands);
  var code=p[src]||p.template;
  return (dff==="easy")?forgeEasy(p,code,src):forgeTokens(p,code,dff,src);
};

/* Easy: reorder whole lines, avoid poison decoy lines (the classic mode) */
function forgeEasy(p, correctSrc, src){
  var correct=correctSrc.slice();
  var decoys=[];
  var attempts=0;
  while(decoys.length<3 && attempts<30){
    attempts++;
    var base=choice(correct);
    var muts=mutateLine(base);
    if(muts.length){
      var d=choice(muts);
      if(correct.indexOf(d)===-1 && decoys.indexOf(d)===-1) decoys.push(d);
    }
  }
  /* nasty cross-pattern decoy */
  var others=pool().filter(function(q){ return q.template && q.id!==p.id; });
  if(others.length){
    var ol=choice(choice(others).template);
    if(correct.indexOf(ol)===-1 && decoys.indexOf(ol)===-1) decoys.push(ol);
  }
  decoys=decoys.slice(0,3);
  var poolLines=shuffle(correct.concat(decoys));
  var picked=[]; /* array of line strings in chosen order */

  return {
    patternId:p.id,
    instr:'<b>Easy.</b> Tap the lines in the right order to rebuild the <b>'+esc(p.name)+'</b> '+(src==="example"?"example":"template")+'. Some lines are <b>poison</b> &mdash; leave them out.',
    mount:function(body, actions, finish){
      var sol=ce("div","code-list"); var solEmpty=ce("div","empty-hint","Tap lines below to start building&hellip;");
      body.appendChild(ce("div","pool-label","Your build"));
      body.appendChild(sol); sol.appendChild(solEmpty);
      body.appendChild(ce("div","pool-label","Line bank"));
      var bank=ce("div","code-list"); body.appendChild(bank);

      function draw(){
        sol.innerHTML=""; 
        if(!picked.length){ sol.appendChild(solEmpty); }
        picked.forEach(function(line,idx){
          var row=ce("button","code-row picked");
          row.innerHTML='<span class="num">'+(idx+1)+'</span><span class="txt">'+esc(line)+'</span>';
          row.onclick=function(){ if(G.answered) return; picked.splice(idx,1); SFX.click(); draw(); };
          sol.appendChild(row);
        });
        bank.innerHTML="";
        /* render bank as remaining (account for duplicates) */
        var remaining=poolLines.slice();
        picked.forEach(function(l){ var i=remaining.indexOf(l); if(i>=0) remaining.splice(i,1); });
        remaining.forEach(function(line){
          var row=ce("button","code-row");
          row.innerHTML='<span class="num">+</span><span class="txt">'+esc(line)+'</span>';
          row.onclick=function(){ if(G.answered) return; picked.push(line); SFX.click(); draw(); };
          bank.appendChild(row);
        });
      }
      draw();

      var check=ce("button","btn btn-primary","Check build");
      check.onclick=function(){
        if(G.answered) return;
        var ok = picked.length===correct.length && picked.every(function(l,i){ return l===correct[i]; });
        /* visual diff */
        Array.prototype.forEach.call(sol.querySelectorAll(".code-row"),function(row,i){
          row.classList.remove("picked");
          row.classList.add(picked[i]===correct[i]?"correct":"wrong");
          if(picked[i]!==correct[i]) row.classList.add("shake");
        });
        var reveal='The correct '+(src==="example"?"example":"template")+':<br><br><span class="mono" style="white-space:pre-wrap">'+esc(correct.join("\n"))+'</span>';
        finish(ok, reveal);
      };
      actions.appendChild(check);
    }
  };
}

/* Medium (chunks) / Hard (single tokens + poison): assemble tokens into wrapping lines.
   Each token is a chip of natural width but uniform height; a ↵ chip ends a line. */
function forgeTokens(p, rawCode, dff, src){
  var fine=(dff==="hard");
  var code=codeNoComments(rawCode);  /* puzzle uses code w/o comments; reveal keeps them */
  var stripped=code.length!==rawCode.length || code.some(function(l,i){ return l!==rawCode[i]; });
  var target=[]; /* ordered cells: {kind:'tok',val} | {kind:'nl'} */
  code.forEach(function(line, li){
    tokenizeLine(line, fine).forEach(function(tk){ target.push({kind:"tok", val:tk}); });
    if(li<code.length-1) target.push({kind:"nl"});
  });
  var chips=[]; var cid=0;
  target.forEach(function(cell){
    chips.push(cell.kind==="nl" ? {id:cid++, kind:"nl"} : {id:cid++, kind:"tok", val:cell.val});
  });
  if(dff==="hard"){
    var toks=target.filter(function(c){ return c.kind==="tok"; });
    var added=0, tries=0;
    while(added<3 && tries<50 && toks.length){
      tries++;
      var muts=mutateToken(choice(toks).val);
      if(muts.length){ chips.push({id:cid++, kind:"tok", val:choice(muts), poison:true}); added++; }
    }
  }
  var bank=shuffle(chips);
  var byId={}; bank.forEach(function(c){ byId[c.id]=c; });
  var picked=[]; /* chip ids in chosen order */

  return {
    patternId:p.id,
    instr:(fine
      ? '<b>Hard.</b> This <b>'+esc(p.name)+'</b> '+(src==="example"?"example":"template")+' is smashed into single <b>tokens</b> &mdash; a few are <b>poison</b>. Tap them in order; use <b>&#8629;</b> to end each line.'
      : '<b>Medium.</b> This <b>'+esc(p.name)+'</b> '+(src==="example"?"example":"template")+' is broken into <b>chunks</b>. Tap them in the right order; use <b>&#8629;</b> to end each line.'),
    mount:function(body, actions, finish){
      body.appendChild(ce("div","pool-label","Your build"));
      var build=ce("div","forge-lines"); body.appendChild(build);
      body.appendChild(ce("div","pool-label","Token bank"));
      var bankEl=ce("div","tok-bank"); body.appendChild(bankEl);

      function newRow(lineIdx){
        var row=ce("div","forge-row");
        row.style.paddingLeft=(indentUnits(code[lineIdx])*0.55)+"em";
        build.appendChild(row);
        return row;
      }
      function draw(){
        build.innerHTML="";
        var lineIdx=0, row=newRow(0);
        if(!picked.length){ row.appendChild(ce("span","tok-hint","Tap tokens below to start building&hellip;")); }
        picked.forEach(function(id, pos){
          var chip=byId[id];
          var b=ce("button","tok picked"+(chip.kind==="nl"?" nl":""), chip.kind==="nl"?"&#8629;":esc(chip.val));
          b.onclick=(function(pp){ return function(){ if(G.answered) return; picked.splice(pp,1); SFX.click(); draw(); }; })(pos);
          row.appendChild(b);
          if(chip.kind==="nl"){ lineIdx++; row=newRow(lineIdx); }
        });
        bankEl.innerHTML="";
        bank.forEach(function(chip){
          if(picked.indexOf(chip.id)>=0) return;
          var b=ce("button","tok"+(chip.kind==="nl"?" nl":""), chip.kind==="nl"?"&#8629;":esc(chip.val));
          b.onclick=function(){ if(G.answered) return; picked.push(chip.id); SFX.click(); draw(); };
          bankEl.appendChild(b);
        });
      }
      draw();

      var check=ce("button","btn btn-primary","Check build");
      check.onclick=function(){
        if(G.answered) return;
        var cells=picked.map(function(id){ return byId[id]; });
        var ok = cells.length===target.length && cells.every(function(c,i){
          var t=target[i]; if(!t||t.kind!==c.kind) return false;
          return t.kind==="tok" ? (c.val===t.val) : true;
        });
        Array.prototype.forEach.call(build.querySelectorAll(".tok"),function(el,i){
          el.classList.remove("picked");
          var t=target[i], c=cells[i];
          var good = !!t && t.kind===c.kind && (t.kind!=="tok" || t.val===c.val);
          el.classList.add(good?"correct":"wrong");
          if(!good) el.classList.add("shake");
        });
        var reveal='The correct '+(src==="example"?"example":"template")+':<br><br><span class="mono" style="white-space:pre-wrap">'+esc(rawCode.join("\n"))+'</span>'+
          (stripped?'<br><br><span style="color:var(--dim)">Comments are shown for reference &mdash; the puzzle leaves them out.</span>':'');
        finish(ok, reveal);
      };
      actions.appendChild(check);
    }
  };
}

/* --- Fill the Gap (cloze) --- */
BUILDERS.cloze=function(){
  var cands=pool().filter(function(p){ return p.template && p.template.length<=16; });
  cands=shuffle(cands);
  for(var c=0;c<cands.length;c++){
    var p=cands[c];
    var lines=(p.example&&p.example.length<=16)? (Math.random()<0.5?p.example:p.template) : p.template;
    var blanks=findBlanks(lines);
    if(blanks.length<1) continue;
    var chosen=sample(blanks, Math.min(3,blanks.length));
    /* avoid two blanks on same position */
    return makeCloze(p, lines, chosen);
  }
  return null;
};
function makeCloze(p, lines, chosen){
  /* group chosen by line, build HTML with selects */
  var byLine={}; chosen.forEach(function(b){ (byLine[b.li]=byLine[b.li]||[]).push(b); });
  var slots=[]; /* {id, correct} */
  var sid=0;
  var htmlLines=lines.map(function(line, li){
    var marks=(byLine[li]||[]).slice().sort(function(a,b){ return b.start-a.start; });
    var s=line;
    marks.forEach(function(b){
      var id="b"+(sid++);
      slots.push({id:id, correct:b.tok});
      s = s.slice(0,b.start) + "\u0001"+id+"\u0001" + s.slice(b.start+b.tok.length);
    });
    return s;
  });
  var joined=esc(htmlLines.join("\n"));
  slots.forEach(function(sl){
    var opts=uniq([sl.correct].concat(TOKEN_MUT[sl.correct]||[]));
    opts=shuffle(opts);
    var sel='<select class="blank" data-correct="'+esc(sl.correct)+'" id="'+sl.id+'"><option value="">?</option>'+
      opts.map(function(o){ return '<option value="'+esc(o)+'">'+esc(o)+'</option>'; }).join("")+'</select>';
    joined=joined.replace("\u0001"+sl.id+"\u0001", sel);
  });
  return {
    patternId:p.id,
    instr:'Fill every blank in this <b>'+esc(p.name)+'</b> snippet. Watch for sneaky look-alikes.',
    mount:function(body, actions, finish){
      var pre=ce("div","cloze"); pre.innerHTML=joined; body.appendChild(pre);
      var check=ce("button","btn btn-primary","Check");
      check.onclick=function(){
        if(G.answered) return;
        var all=true;
        slots.forEach(function(sl){
          var el=$("#"+sl.id, pre); var ok=el.value===el.getAttribute("data-correct");
          el.classList.add(ok?"ok":"no"); el.disabled=true; if(!ok) all=false;
        });
        var reveal = all? "Clean code &mdash; every token correct." :
          ('Correct tokens: '+slots.map(function(s){ return '<code>'+esc(s.correct)+'</code>'; }).join(", "));
        finish(all, reveal);
      };
      actions.appendChild(check);
    }
  };
}

/* --- Bug Hunt: one poisoned line --- */
BUILDERS.bug=function(){
  var cands=withTemplate(14).filter(function(p){ return p.template.length>=4; });
  cands=shuffle(cands);
  for(var c=0;c<cands.length;c++){
    var p=cands[c];
    var idxs=shuffle(p.template.map(function(_,i){ return i; }));
    for(var k=0;k<idxs.length;k++){
      var i=idxs[k]; var muts=mutateLine(p.template[i]);
      if(muts.length){
        var bug=choice(muts);
        var lines=p.template.slice(); var orig=lines[i]; lines[i]=bug;
        return makeBug(p, lines, i, orig, bug);
      }
    }
  }
  return null;
};
function makeBug(p, lines, bugIdx, orig, bug){
  return {
    patternId:p.id,
    instr:'Exactly one line of this <b>'+esc(p.name)+'</b> template was poisoned. Tap the buggy line.',
    mount:function(body, actions, finish){
      var list=ce("div","code-list");
      lines.forEach(function(line, idx){
        var row=ce("button","code-row");
        row.innerHTML='<span class="num">'+(idx+1)+'</span><span class="txt">'+esc(line)+'</span>';
        row.onclick=function(){
          if(G.answered) return;
          var ok=(idx===bugIdx);
          Array.prototype.forEach.call(list.children,function(r){ r.classList.add("disabled"); });
          list.children[bugIdx].classList.add("correct");
          if(!ok){ row.classList.add("wrong","shake"); }
          var reveal='Line '+(bugIdx+1)+' should be:<br><span class="mono">'+esc(orig)+'</span>';
          finish(ok, reveal);
        };
        list.appendChild(row);
      });
      body.appendChild(list);
    }
  };
}

/* --- Name That Pattern --- */
BUILDERS.name=function(){
  var p = focusId ? BY_ID[focusId] : choice(pool());
  var distract=(p.confus||[]).map(function(id){ return BY_ID[id]; }).filter(Boolean);
  var others=shuffle(PATTERNS.filter(function(q){ return q.id!==p.id && distract.indexOf(q)===-1; }));
  var opts=[p].concat(sample(distract,2));
  while(opts.length<4 && others.length) opts.push(others.pop());
  opts=shuffle(uniq(opts.map(function(x){return x.id;}))).map(function(id){ return BY_ID[id]; });
  return {
    patternId:p.id,
    instr:'A problem gives you this hint. Which pattern do you reach for?',
    mount:function(body, actions, finish){
      body.appendChild(ce("div","qclue","&ldquo;"+esc(p.clue)+"&rdquo;"));
      var grid=ce("div","opts");
      opts.forEach(function(o){
        var b=ce("button","opt",esc(o.name));
        b.setAttribute("data-val",o.id);
        b.onclick=function(){
          if(G.answered) return;
          var ok=o.id===p.id;
          Array.prototype.forEach.call(grid.children,function(c){ c.classList.add("disabled");
            if(c.getAttribute("data-val")===p.id) c.classList.add("correct"); });
          if(!ok) b.classList.add("wrong","shake");
          finish(ok, ok?"":("It was <b>"+esc(p.name)+"</b> &mdash; "+esc(p.mnemonic||"")));
        };
        grid.appendChild(b);
      });
      body.appendChild(grid);
    }
  };
};

/* --- Big-O Climb --- */
var TIME_LADDER=["O(1)","O(log n)","O(n)","O(n log n)","O(n²)","O(n³)","O(2^n)","O(n!)"];
BUILDERS.bigo=function(){
  var p=choice(pool());
  var askSpace=Math.random()<0.5;
  var correct=askSpace?p.space:p.time;
  var poolVals=uniq(PATTERNS.map(function(q){ return askSpace?q.space:q.time; }));
  poolVals=poolVals.filter(function(v){ return v!==correct; });
  var opts=uniq([correct].concat(sample(poolVals,3))).slice(0,4);
  opts=shuffle(opts).map(function(v){ return {label:v, val:v}; });
  return {
    patternId:p.id,
    instr:'What is the typical <b>'+(askSpace?"space":"time")+'</b> complexity of this pattern?',
    mount:function(body, actions, finish){
      body.appendChild(ce("div","qbig",esc(p.name)));
      if(p.mnemonic) body.appendChild(ce("div","qclue","&ldquo;"+esc(p.mnemonic)+"&rdquo;"));
      renderOptions(body, opts, correct, false, finish, function(ok){
        return ok?"":("Correct: <code>"+esc(correct)+"</code> (the other is <code>"+esc(askSpace?p.time:p.space)+"</code>).");
      });
    }
  };
};

/* --- Mnemonic Match --- */
BUILDERS.mnemo=function(){
  var allM=PATTERNS.filter(function(p){ return p.mnemonic; });
  if(allM.length<4) return null;
  var p = focusId ? BY_ID[focusId] : choice(pool().filter(function(q){ return q.mnemonic; }));
  if(!p || !p.mnemonic) return null;
  var others=shuffle(allM.filter(function(q){ return q.id!==p.id; })).slice(0,3);
  var opts=shuffle([p].concat(others)).map(function(x){ return {label:x.mnemonic, val:x.id}; });
  return {
    patternId:p.id,
    instr:'Which memory hook belongs to this pattern?',
    mount:function(body, actions, finish){
      body.appendChild(ce("div","qbig",esc(p.name)));
      renderOptions(body, opts, p.id, true, finish, function(ok){
        return ok?"":("Its hook: &ldquo;"+esc(p.mnemonic)+"&rdquo;");
      });
    }
  };
};

/* ============================ settings + chrome ============================ */
function updateChips(){
  var rc=$("#rankChip"); if(rc) rc.textContent=rankFor(save.xp);
  var sb=$("#soundBtn"), hb=$("#hapticBtn");
  if(sb){ sb.classList.toggle("off",!save.sound); sb.innerHTML=save.sound?"&#128266;":"&#128263;"; }
  if(hb){ hb.classList.toggle("off",!save.haptics); }
}
function applyTheme(t){ document.documentElement.setAttribute("data-theme",t); localStorage.setItem("dsa-theme",t);
  var tb=$("#themeBtn"); if(tb) tb.innerHTML=(t==="dark")?"&#9789;":"&#9728;"; }

$("#soundBtn").onclick=function(){ save.sound=!save.sound; persist(); updateChips(); if(save.sound){ actx(); SFX.correct(); } };
$("#hapticBtn").onclick=function(){ save.haptics=!save.haptics; persist(); updateChips(); buzz(40); };
$("#themeBtn").onclick=function(){ applyTheme(document.documentElement.getAttribute("data-theme")==="dark"?"light":"dark"); };

applyTheme(localStorage.getItem("dsa-theme")||"dark");
updateChips();

/* deep-link: ?pattern=<id>&mode=<mode>&src=template|example&diff=easy|medium|hard */
(function initFromURL(){
  try{
    var params=new URLSearchParams(location.search);
    var fp=params.get("pattern"), fm=params.get("mode");
    var fd=params.get("diff"), fs=params.get("src");
    if(fd==="easy"||fd==="medium"||fd==="hard") diff=fd;
    if(fs==="example"||fs==="template") forgeSrc=fs;
    if(fp && BY_ID[fp]){
      focusId=fp;
      if(fm && BUILDERS[fm]){ startSession(fm,{diff:diff, src:forgeSrc}); return; }
    }
  }catch(e){}
  renderHome();
})();
})();
