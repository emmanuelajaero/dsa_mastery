(function(){
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
