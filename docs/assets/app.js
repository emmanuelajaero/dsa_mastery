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
})();
