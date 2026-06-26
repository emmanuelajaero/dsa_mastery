#!/usr/bin/env python3
"""
Build a standalone, offline HTML site from the DSA-mastery Markdown files.

Run:
    python3 build_site.py

Output:
    site/index.html and one page per chapter, plus shared assets/ and vendor/.

The Markdown is base64-embedded into each page and rendered in the browser by
the vendored marked.js + highlight.js (no server, no internet, no CORS issues).
Re-run this script any time you edit the .md files to refresh the HTML.
"""
import base64
import pathlib
import re as _re

import build_game  # shares the curated pattern REGISTRY (id <-> section name)

HERE = pathlib.Path(__file__).resolve().parent
SITE = HERE / "site"
ASSETS = SITE / "assets"


def _gkey(text):
    """Normalize a heading/section title to match the game's pattern map."""
    return _re.sub(r'[^a-z0-9]', '', text.lower())


# map normalized section title -> game pattern id, so site pages can deep-link
GAME_INDEX = {}
for _e in build_game.REGISTRY:
    GAME_INDEX[_gkey(_e["section"])] = _e["id"]
    GAME_INDEX[_gkey(_e["name"])] = _e["id"]
import json as _json
GAME_INDEX_JSON = _json.dumps(GAME_INDEX, ensure_ascii=False)

# (source markdown, output html, sidebar title)
PAGES = [
    ("README.md",                    "index.html",                    "Home & Roadmap"),
    ("00-complexity-foundations.md", "00-complexity-foundations.html","0 · Complexity Foundations"),
    ("01-core-patterns.md",          "01-core-patterns.html",         "1 · 15 Core Patterns"),
    ("02-dynamic-programming.md",    "02-dynamic-programming.html",   "2 · 20 DP Patterns"),
    ("03-flashcards.md",             "03-flashcards.html",            "3 · Flashcards & Review"),
    ("04-advanced-patterns.md",      "04-advanced-patterns.html",     "4 · Advanced Patterns"),
    ("05-progress-tracker.md",       "05-progress-tracker.html",      "5 · Progress Tracker"),
]

NAV_JSON = ",".join(
    '{{"href":"{html}","title":"{title}"}}'.format(html=html, title=title)
    for _, html, title in PAGES
) + ',{"href":"game/index.html","title":"\\u25B6 Play: Pattern Forge"}'

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ · DSA Mastery</title>
<link rel="stylesheet" href="vendor/github-dark.min.css" id="hljs-dark">
<link rel="stylesheet" href="vendor/github.min.css" id="hljs-light" disabled>
<link rel="stylesheet" href="assets/app.css">
</head>
<body>
<header class="topbar">
  <button id="menuBtn" class="icon-btn" aria-label="Toggle navigation">&#9776;</button>
  <a class="brand" href="index.html"><span class="brand-mark">{ }</span> DSA Mastery</a>
  <div class="spacer"></div>
  <a id="gameBtn" class="icon-btn game-btn" href="game/index.html" aria-label="Play Pattern Forge" title="Pattern Forge — full game mode">&#127918;</a>
  <button id="themeBtn" class="icon-btn" aria-label="Toggle theme" title="Toggle light / dark">&#9789;</button>
  <button id="searchBtn" class="icon-btn search-toggle" aria-label="Search" title="Search patterns">&#128269;</button>
</header>

<div id="searchOverlay" class="search-overlay">
  <div class="search-bar">
    <input id="searchInput" type="search" placeholder="Search patterns, topics, keywords…" autocomplete="off">
    <button id="searchClose" class="icon-btn" aria-label="Close search">&#10005;</button>
  </div>
  <ul id="searchResults" class="search-results"></ul>
</div>

<div class="layout">
  <nav id="sidebar" class="sidebar">
    <div class="sidebar-section">Chapters</div>
    <ul id="navList" class="nav-list"></ul>
    <div class="sidebar-foot">Generated from Markdown · regenerate with <code>build_site.py</code></div>
  </nav>

  <main class="content">
    <article id="article" class="markdown-body"></article>
    <footer class="page-foot">
      <span>DSA Mastery — pattern playbook</span>
    </footer>
  </main>

  <aside id="toc" class="toc">
    <div class="toc-title">On this page</div>
    <ul id="tocList" class="toc-list"></ul>
  </aside>
</div>

<button id="topBtn" class="top-btn" title="Back to top">&#8593;</button>

<script type="text/markdown" id="md-content">__B64__</script>
<script>window.__NAV__ = [__NAVDATA__];</script>
<script>window.__SEARCH_INDEX__ = [__SEARCHINDEX__];</script>
<script>window.__GAME_INDEX__ = __GAMEINDEX__;</script>
<script src="vendor/marked.min.js"></script>
<script src="vendor/highlight.min.js"></script>
<script src="assets/app.js"></script>
</body>
</html>
"""

APP_CSS = r""":root{
  --bg:#0d1117; --bg-soft:#161b22; --bg-code:#161b22; --panel:#10151c;
  --text:#c9d1d9; --text-dim:#8b949e; --heading:#f0f6fc;
  --border:#21262d; --accent:#58a6ff; --accent-soft:#1f6feb33;
  --quote-bar:#3fb950; --table-stripe:#0f141a; --shadow:rgba(0,0,0,.4);
}
html[data-theme="light"]{
  --bg:#ffffff; --bg-soft:#f6f8fa; --bg-code:#f6f8fa; --panel:#ffffff;
  --text:#1f2328; --text-dim:#656d76; --heading:#1f2328;
  --border:#d0d7de; --accent:#0969da; --accent-soft:#0969da1a;
  --quote-bar:#1a7f37; --table-stripe:#f6f8fa; --shadow:rgba(140,149,159,.2);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0; background:var(--bg); color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  font-size:16px; line-height:1.6;
}
code,pre,kbd{font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace}

/* Top bar */
.topbar{
  position:sticky; top:0; z-index:50; display:flex; align-items:center; gap:12px;
  height:56px; padding:0 16px; background:var(--panel);
  border-bottom:1px solid var(--border); box-shadow:0 1px 0 var(--shadow);
}
.brand{display:flex; align-items:center; gap:8px; font-weight:700; color:var(--heading); text-decoration:none; font-size:17px}
.brand-mark{color:var(--accent); font-family:monospace; font-weight:800}
.spacer{flex:1}
.icon-btn{
  background:transparent; border:1px solid var(--border); color:var(--text);
  width:38px; height:38px; border-radius:8px; cursor:pointer; font-size:18px; line-height:1;
}
.icon-btn:hover{background:var(--bg-soft); border-color:var(--accent)}
#menuBtn{display:none}

/* Layout */
.layout{display:grid; grid-template-columns:260px minmax(0,1fr) 230px; gap:0; align-items:start}
.sidebar{
  position:sticky; top:56px; align-self:start; height:calc(100vh - 56px);
  overflow-y:auto; padding:20px 14px; border-right:1px solid var(--border); background:var(--panel);
}
.sidebar-section{font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:var(--text-dim); margin:4px 8px 10px}
.nav-list{list-style:none; margin:0; padding:0}
.nav-list li{margin:2px 0}
.nav-list a{
  display:block; padding:9px 12px; border-radius:8px; color:var(--text);
  text-decoration:none; font-size:14.5px; border:1px solid transparent;
}
.nav-list a:hover{background:var(--bg-soft)}
.nav-list a.active{background:var(--accent-soft); color:var(--accent); border-color:var(--accent); font-weight:600}
.sidebar-foot{margin-top:20px; padding:10px 8px; font-size:11.5px; color:var(--text-dim); border-top:1px solid var(--border)}
.sidebar-foot code{font-size:11px}

.content{padding:32px 44px 80px; min-width:0}
.toc{
  position:sticky; top:56px; align-self:start; height:calc(100vh - 56px); overflow-y:auto;
  padding:24px 16px; font-size:13px;
}
.toc-title{font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:var(--text-dim); margin-bottom:10px}
.toc-list{list-style:none; margin:0; padding:0; border-left:1px solid var(--border)}
.toc-list a{display:block; padding:5px 12px; color:var(--text-dim); text-decoration:none; border-left:2px solid transparent; margin-left:-1px}
.toc-list a:hover{color:var(--text)}
.toc-list a.active{color:var(--accent); border-left-color:var(--accent); font-weight:600}
.toc-list a.lvl3{padding-left:24px; font-size:12.5px}

/* Markdown body */
.markdown-body{max-width:860px}
.markdown-body h1,.markdown-body h2,.markdown-body h3,.markdown-body h4{
  color:var(--heading); line-height:1.25; scroll-margin-top:72px; position:relative;
}
.markdown-body h1{font-size:2em; padding-bottom:.3em; border-bottom:1px solid var(--border); margin-top:0}
.markdown-body h2{font-size:1.5em; padding-bottom:.3em; border-bottom:1px solid var(--border); margin-top:2em}
.markdown-body h3{font-size:1.2em; margin-top:1.6em}
.markdown-body h4{font-size:1.02em; margin-top:1.3em}
.markdown-body p,.markdown-body li{color:var(--text)}
.markdown-body a{color:var(--accent); text-decoration:none}
.markdown-body a:hover{text-decoration:underline}
.markdown-body .anchor{
  opacity:0; margin-left:8px; color:var(--text-dim); font-weight:400; text-decoration:none; font-size:.8em;
}
.markdown-body h1:hover .anchor,.markdown-body h2:hover .anchor,
.markdown-body h3:hover .anchor,.markdown-body h4:hover .anchor{opacity:1}

/* inline code */
.markdown-body :not(pre) > code{
  background:var(--bg-soft); padding:.15em .4em; border-radius:6px; font-size:.88em;
  border:1px solid var(--border);
}
/* code blocks */
.markdown-body pre{
  position:relative; background:var(--bg-code); border:1px solid var(--border);
  border-radius:10px; padding:16px 16px; overflow:auto; font-size:13.5px; line-height:1.5;
  -webkit-overflow-scrolling:touch; overscroll-behavior-x:contain;
}
.markdown-body pre code{background:transparent; border:0; padding:0; font-size:inherit}
.copy-btn{
  position:absolute; top:8px; right:8px; padding:4px 9px; font-size:11px; border-radius:6px;
  background:var(--panel); color:var(--text-dim); border:1px solid var(--border); cursor:pointer; opacity:0; transition:opacity .15s;
}
.markdown-body pre:hover .copy-btn{opacity:1}
.copy-btn:hover{color:var(--accent); border-color:var(--accent)}
.copy-btn.copied{color:var(--quote-bar); border-color:var(--quote-bar)}

/* video prompt block: readable, wrapped, copyable callout */
.markdown-body pre.prompt-block{
  white-space:normal; background:var(--bg-soft); border:1px solid var(--border);
  border-left:4px solid var(--quote-bar); padding:34px 16px 14px;
}
.markdown-body pre.prompt-block code{
  white-space:pre-wrap; word-break:break-word; display:block; color:var(--text); line-height:1.55;
}
.markdown-body pre.prompt-block::before{
  content:"VIDEO PROMPT \00B7 8s \00B7 copy me"; position:absolute; top:9px; left:16px;
  font-size:11px; letter-spacing:.08em; font-weight:700; color:var(--quote-bar);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
}

/* blockquote = mnemonic callout */
.markdown-body blockquote{
  margin:1.1em 0; padding:12px 16px 12px 44px; position:relative;
  background:var(--accent-soft); border:1px solid var(--border);
  border-left:4px solid var(--accent); border-radius:8px; color:var(--text);
}
.markdown-body blockquote::before{
  content:"\1F4A1"; position:absolute; left:14px; top:11px; font-size:16px;
}
.markdown-body blockquote p{margin:.3em 0}

/* tables */
.markdown-body table{border-collapse:collapse; width:100%; margin:1.2em 0; display:block; overflow-x:auto; font-size:14px; -webkit-overflow-scrolling:touch; overscroll-behavior-x:contain}
.markdown-body th,.markdown-body td{border:1px solid var(--border); padding:8px 12px; text-align:left; vertical-align:top}
.markdown-body th{background:var(--bg-soft); color:var(--heading); font-weight:600}
.markdown-body tbody tr:nth-child(even){background:var(--table-stripe)}

.markdown-body hr{border:0; border-top:1px solid var(--border); margin:2em 0}
.markdown-body ul,.markdown-body ol{padding-left:1.5em}
.markdown-body li{margin:.25em 0}

.page-foot{margin-top:60px; padding-top:16px; border-top:1px solid var(--border); color:var(--text-dim); font-size:13px}

.top-btn{
  position:fixed; right:22px; bottom:22px; width:42px; height:42px; border-radius:50%;
  background:var(--accent); color:#fff; border:0; font-size:18px; cursor:pointer; display:none;
  box-shadow:0 4px 14px var(--shadow); z-index:40;
}
.top-btn.show{display:block}

/* responsive */
@media (max-width:1100px){
  .layout{grid-template-columns:240px minmax(0,1fr)}
  .toc{display:none}
}
@media (max-width:820px){
  .layout{grid-template-columns:1fr}
  #menuBtn{display:inline-flex; align-items:center; justify-content:center}
  .icon-btn{width:44px; height:44px}     /* comfortable tap target */
  .sidebar{
    position:fixed; top:56px; left:0; bottom:0; width:280px; z-index:45;
    transform:translateX(-100%); transition:transform .2s ease; box-shadow:2px 0 16px var(--shadow);
  }
  .sidebar.open{transform:translateX(0)}
  .content{padding:24px 16px 70px}
  /* dense ASCII diagrams + tables: shrink so more fits before side-scroll */
  .markdown-body pre{font-size:12px; padding:14px 12px}
  .markdown-body table{font-size:13px}
  .markdown-body th,.markdown-body td{padding:6px 9px}
  .markdown-body pre.prompt-block{font-size:14px}   /* keep prompts readable */
}
@media (max-width:480px){
  .content{padding:20px 12px 64px}
  .markdown-body pre{font-size:11px}
  .markdown-body h1{font-size:1.6em}
  .markdown-body h2{font-size:1.3em}
  .brand{font-size:15px}
}
.scrim{position:fixed; inset:56px 0 0 0; background:rgba(0,0,0,.45); z-index:44; display:none}
.scrim.show{display:block}
@media (min-width:821px){.scrim{display:none!important}}

/* Search overlay */
.search-toggle{font-size:16px}
.search-overlay{
  display:none; position:fixed; top:56px; left:0; right:0; z-index:55;
  background:var(--panel); border-bottom:1px solid var(--border);
  box-shadow:0 8px 32px var(--shadow); flex-direction:column; max-height:70vh;
}
.search-overlay.open{display:flex}
.search-bar{
  display:flex; align-items:center; gap:8px; padding:12px 16px;
  border-bottom:1px solid var(--border);
}
.search-bar input{
  flex:1; padding:10px 14px; border-radius:8px; border:1px solid var(--border);
  background:var(--bg-soft); color:var(--text); font-size:15px; outline:none;
}
.search-bar input:focus{border-color:var(--accent); box-shadow:0 0 0 3px var(--accent-soft)}
.search-bar input::placeholder{color:var(--text-dim)}
.search-results{
  list-style:none; margin:0; padding:0; overflow-y:auto; max-height:calc(70vh - 60px);
}
.search-results li{margin:0}
.search-results a{
  display:block; padding:10px 20px; color:var(--text); text-decoration:none;
  border-bottom:1px solid var(--border); font-size:14px;
}
.search-results a:hover{background:var(--bg-soft)}
.search-results .sr-page{font-size:11px; color:var(--text-dim); margin-left:8px}
.search-results .sr-empty{padding:20px; color:var(--text-dim); text-align:center; font-size:14px}

/* Watch-out callout blocks */
.markdown-body h3 .watchout-icon{margin-right:4px}

/* ---- "Play this" deep-link buttons injected next to gamified concepts ---- */
.game-btn{display:inline-flex; align-items:center; justify-content:center; text-decoration:none;
  background:linear-gradient(135deg,#a371f7,#f778ba); color:#fff; border-color:transparent}
.game-btn:hover{filter:brightness(1.08); border-color:transparent}
.gp-bar{margin:8px 0 16px}
.gp-bar-sm{margin:-6px 0 16px}
.play-btn{display:inline-flex; align-items:center; gap:6px; text-decoration:none; font-weight:600; font-size:13px;
  color:#fff !important; background:linear-gradient(135deg,#a371f7,#f778ba); border:0; border-radius:999px;
  padding:7px 14px; cursor:pointer; box-shadow:0 2px 10px var(--shadow); line-height:1.1}
.play-btn:hover{filter:brightness(1.08); text-decoration:none}
.play-btn-sm{font-size:12px; padding:5px 11px; background:linear-gradient(135deg,#1f6feb,#a371f7)}

/* Progress tracker tables - ensure horizontal scroll on mobile */
.markdown-body table{-webkit-overflow-scrolling:touch; overscroll-behavior-x:contain}

@media (max-width:820px){
  .search-bar input{font-size:16px}  /* prevent iOS zoom on focus */
}
@media (max-width:480px){
  .search-bar{padding:10px 12px}
  .search-results a{padding:10px 14px; font-size:13px}
}
"""

APP_JS = r"""(function(){
  // ---- decode embedded markdown (UTF-8 safe) ----
  var b64 = document.getElementById('md-content').textContent.trim();
  var bytes = Uint8Array.from(atob(b64), function(c){ return c.charCodeAt(0); });
  var md = new TextDecoder('utf-8').decode(bytes);

  // ---- GitHub-style slug (matches the in-doc #anchor links) ----
  function slugify(text){
    return text.toLowerCase().trim()
      .replace(/[^\w\s-]/g,'')
      .replace(/\s/g,'-');
  }

  // ---- render markdown ----
  marked.setOptions({ gfm:true, breaks:false, headerIds:false, mangle:false });
  var article = document.getElementById('article');
  article.innerHTML = marked.parse(md);

  // ---- headings: ids, anchors, collect for TOC ----
  var used = {};
  var headings = article.querySelectorAll('h1,h2,h3,h4');
  var tocItems = [];
  headings.forEach(function(h){
    var base = slugify(h.textContent);
    var id = base, i = 1;
    while(used[id]){ id = base + '-' + i; i++; }
    used[id] = true;
    h.id = id;
    var a = document.createElement('a');
    a.className = 'anchor'; a.href = '#' + id; a.textContent = '#';
    h.appendChild(a);
    if(h.tagName === 'H2' || h.tagName === 'H3'){
      tocItems.push({ id:id, text:h.textContent.replace(/#$/,''), level:h.tagName });
    }
  });

  // ---- rewrite .md links -> .html ----
  article.querySelectorAll('a[href]').forEach(function(a){
    var href = a.getAttribute('href');
    if(/\.md($|#)/.test(href)){ a.setAttribute('href', href.replace(/\.md($|#)/, '.html$1')); }
  });

  // ---- mark video-prompt blocks (not real code -> don't highlight) ----
  article.querySelectorAll('pre > code.language-prompt').forEach(function(block){
    block.parentElement.classList.add('prompt-block');
  });

  // ---- syntax highlight only language-tagged blocks (skip prompt blocks) ----
  article.querySelectorAll('pre code[class*="language-"]:not(.language-prompt)').forEach(function(block){
    try{ hljs.highlightElement(block); }catch(e){}
  });

  // ---- copy buttons on code blocks ----
  article.querySelectorAll('pre').forEach(function(pre){
    var btn = document.createElement('button');
    btn.className = 'copy-btn'; btn.textContent = 'Copy';
    btn.addEventListener('click', function(){
      var code = pre.querySelector('code');
      navigator.clipboard.writeText(code ? code.textContent : pre.textContent).then(function(){
        btn.textContent = 'Copied'; btn.classList.add('copied');
        setTimeout(function(){ btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 1400);
      });
    });
    pre.appendChild(btn);
  });

  // ---- inject "Play this" deep-links next to gamified concepts/templates/examples ----
  (function(){
    var GIDX = window.__GAME_INDEX__ || {};
    function gnorm(s){ return s.toLowerCase().replace(/[^a-z0-9]/g,''); }
    function stripLabel(s){ return s.replace(/^\s*([0-9]+|[a-zA-Z])\.\s*/, ''); }
    function gameHref(id, mode){ return 'game/index.html?pattern=' + encodeURIComponent(id) + (mode ? ('&mode=' + mode) : ''); }
    function playLink(id, mode, label, small){
      var a = document.createElement('a');
      a.className = 'play-btn' + (small ? ' play-btn-sm' : '');
      a.href = gameHref(id, mode);
      a.innerHTML = label;
      return a;
    }
    // 1) concept buttons on each pattern heading
    article.querySelectorAll('h2').forEach(function(h){
      var txt = h.textContent.replace(/#$/, '');
      var id = GIDX[gnorm(stripLabel(txt))];
      if(!id){ return; }
      h.setAttribute('data-pattern', id);
      var bar = document.createElement('div'); bar.className = 'gp-bar';
      bar.appendChild(playLink(id, '', '&#127918; Play this pattern', false));
      if(h.nextSibling){ h.parentNode.insertBefore(bar, h.nextSibling); } else { h.parentNode.appendChild(bar); }
    });
    // 2) template/example buttons on each Python code block within a pattern section
    article.querySelectorAll('pre > code.language-python').forEach(function(code){
      var pre = code.parentElement;
      var p = pre.previousElementSibling, sub = '', secId = null;
      while(p){
        if(p.tagName === 'H3' && !sub){ sub = p.textContent.replace(/#$/, ''); }
        if(p.tagName === 'H2'){ secId = p.getAttribute('data-pattern'); break; }
        p = p.previousElementSibling;
      }
      if(!secId){ return; }
      var isExample = /worked example/i.test(sub);
      var mode = isExample ? 'cloze' : 'forge';
      var label = isExample ? '&#127918; Play this example' : '&#127918; Play this template';
      var bar = document.createElement('div'); bar.className = 'gp-bar gp-bar-sm';
      bar.appendChild(playLink(secId, mode, label, true));
      if(pre.nextSibling){ pre.parentNode.insertBefore(bar, pre.nextSibling); } else { pre.parentNode.appendChild(bar); }
    });
  })();

  // ---- sidebar nav ----
  var navList = document.getElementById('navList');
  var here = location.pathname.split('/').pop() || 'index.html';
  (window.__NAV__ || []).forEach(function(item){
    var li = document.createElement('li');
    var a = document.createElement('a');
    a.href = item.href; a.textContent = item.title;
    if(item.href === here){ a.classList.add('active'); }
    li.appendChild(a); navList.appendChild(li);
  });

  // ---- on-this-page TOC ----
  var tocList = document.getElementById('tocList');
  tocItems.forEach(function(it){
    var li = document.createElement('li');
    var a = document.createElement('a');
    a.href = '#' + it.id; a.textContent = it.text;
    if(it.level === 'H3'){ a.classList.add('lvl3'); }
    li.appendChild(a); tocList.appendChild(li);
  });
  if(tocItems.length === 0){ document.getElementById('toc').style.display = 'none'; }

  // ---- scroll-spy for TOC ----
  var tocLinks = Array.prototype.slice.call(tocList.querySelectorAll('a'));
  var spyTargets = tocItems.map(function(it){ return document.getElementById(it.id); });
  function onScroll(){
    var top = window.scrollY + 90; var current = -1;
    for(var i=0;i<spyTargets.length;i++){ if(spyTargets[i] && spyTargets[i].offsetTop <= top){ current = i; } }
    tocLinks.forEach(function(l,idx){ l.classList.toggle('active', idx === current); });
    document.getElementById('topBtn').classList.toggle('show', window.scrollY > 600);
  }
  window.addEventListener('scroll', onScroll, { passive:true }); onScroll();

  // ---- back to top ----
  document.getElementById('topBtn').addEventListener('click', function(){ window.scrollTo({top:0, behavior:'smooth'}); });

  // ---- theme toggle ----
  var dark = document.getElementById('hljs-dark');
  var light = document.getElementById('hljs-light');
  function applyTheme(t){
    document.documentElement.setAttribute('data-theme', t);
    var isDark = t === 'dark';
    dark.disabled = !isDark; light.disabled = isDark;
    document.getElementById('themeBtn').innerHTML = isDark ? '&#9789;' : '&#9728;';
    localStorage.setItem('dsa-theme', t);
  }
  applyTheme(localStorage.getItem('dsa-theme') || 'dark');
  document.getElementById('themeBtn').addEventListener('click', function(){
    applyTheme(document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
  });

  // ---- mobile sidebar ----
  var sidebar = document.getElementById('sidebar');
  var scrim = document.createElement('div'); scrim.className = 'scrim'; document.body.appendChild(scrim);
  function closeNav(){ sidebar.classList.remove('open'); scrim.classList.remove('show'); }
  document.getElementById('menuBtn').addEventListener('click', function(){
    sidebar.classList.toggle('open'); scrim.classList.toggle('show');
  });
  scrim.addEventListener('click', closeNav);
  navList.addEventListener('click', closeNav);

  // ---- search ----
  var searchBtn = document.getElementById('searchBtn');
  var searchOverlay = document.getElementById('searchOverlay');
  var searchInput = document.getElementById('searchInput');
  var searchClose = document.getElementById('searchClose');
  var searchResults = document.getElementById('searchResults');

  // Build local index from rendered headings + first paragraph
  var localIndex = [];
  headings.forEach(function(h){
    if(h.tagName === 'H1' || h.tagName === 'H2' || h.tagName === 'H3'){
      var text = h.textContent.replace(/#$/,'').trim();
      // grab following paragraph text for richer search
      var next = h.nextElementSibling;
      var snippet = '';
      if(next && (next.tagName === 'P' || next.tagName === 'BLOCKQUOTE')){
        snippet = next.textContent.substring(0, 120);
      }
      localIndex.push({text:text, snippet:snippet, id:h.id, page:here, pageTitle:''});
    }
  });

  // Merge with cross-page index
  var fullIndex = (window.__SEARCH_INDEX__ || []).filter(function(e){ return e.page !== here; });
  fullIndex = localIndex.concat(fullIndex);

  function openSearch(){
    searchOverlay.classList.add('open');
    setTimeout(function(){ searchInput.focus(); }, 50);
  }
  function closeSearch(){
    searchOverlay.classList.remove('open');
    searchInput.value = '';
    searchResults.innerHTML = '';
  }
  searchBtn.addEventListener('click', openSearch);
  searchClose.addEventListener('click', closeSearch);
  // Close on Escape
  document.addEventListener('keydown', function(e){
    if(e.key === 'Escape' && searchOverlay.classList.contains('open')){ closeSearch(); }
    // Ctrl/Cmd + K to open search
    if((e.ctrlKey || e.metaKey) && e.key === 'k'){ e.preventDefault(); openSearch(); }
  });

  var searchTimer;
  searchInput.addEventListener('input', function(){
    clearTimeout(searchTimer);
    searchTimer = setTimeout(doSearch, 150);
  });

  function doSearch(){
    var q = searchInput.value.trim().toLowerCase();
    searchResults.innerHTML = '';
    if(!q){ return; }
    var matches = fullIndex.filter(function(item){
      return item.text.toLowerCase().indexOf(q) !== -1 ||
             item.snippet.toLowerCase().indexOf(q) !== -1;
    }).slice(0, 20);
    if(matches.length === 0){
      searchResults.innerHTML = '<li class="sr-empty">No results for \"' + q.replace(/</g,'&lt;') + '\"</li>';
      return;
    }
    matches.forEach(function(m){
      var li = document.createElement('li');
      var a = document.createElement('a');
      if(m.page === here){
        a.href = '#' + m.id;
        a.addEventListener('click', closeSearch);
      } else {
        a.href = m.page + '#' + m.id;
      }
      a.textContent = m.text;
      if(m.page !== here && m.pageTitle){
        var span = document.createElement('span');
        span.className = 'sr-page';
        span.textContent = m.pageTitle;
        a.appendChild(span);
      }
      li.appendChild(a);
      searchResults.appendChild(li);
    });
  }
})();
"""


def _slugify(text):
    """GitHub-style slug for heading anchors."""
    import re
    return re.sub(r'\s', '-', re.sub(r'[^\w\s-]', '', text.lower().strip()))


def _extract_headings(md_text, html_file, page_title):
    """Pull h1/h2/h3 from markdown text and return search-index entries."""
    import re
    entries = []
    used = {}
    for m in re.finditer(r'^(#{1,3})\s+(.+)', md_text, re.MULTILINE):
        level = len(m.group(1))
        text = m.group(2).strip()
        base = _slugify(text)
        slug = base
        i = 1
        while slug in used:
            slug = f"{base}-{i}"
            i += 1
        used[slug] = True
        # grab first ~120 chars after the heading for snippet
        pos = m.end()
        snippet = ""
        rest = md_text[pos:pos + 300].strip()
        for line in rest.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("```") and not line.startswith("|"):
                snippet = line[:120]
                break
        entries.append({
            "text": text,
            "snippet": snippet,
            "id": slug,
            "page": html_file,
            "pageTitle": page_title,
        })
    return entries


def main():
    import json

    SITE.mkdir(exist_ok=True)
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "app.css").write_text(APP_CSS, encoding="utf-8")
    (ASSETS / "app.js").write_text(APP_JS, encoding="utf-8")

    # 1) Build cross-page search index from all markdown files
    all_entries = []
    texts = {}
    for src, out, title in PAGES:
        text = (HERE / src).read_text(encoding="utf-8")
        texts[src] = text
        all_entries.extend(_extract_headings(text, out, title))

    search_json = json.dumps(all_entries, ensure_ascii=False)

    # 2) Generate each HTML page
    for src, out, title in PAGES:
        text = texts[src]
        b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
        html = (PAGE_TEMPLATE
                .replace("__TITLE__", title)
                .replace("__NAVDATA__", NAV_JSON)
                .replace("__SEARCHINDEX__", search_json)
                .replace("__GAMEINDEX__", GAME_INDEX_JSON)
                .replace("__B64__", b64))
        (SITE / out).write_text(html, encoding="utf-8")
        print("wrote", (SITE / out).relative_to(HERE))

    print("\nDone. Open:", (SITE / "index.html"))


if __name__ == "__main__":
    main()
