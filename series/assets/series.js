/* The public edition of the series: flipping, the live parts of each image, and the panel of documents. */
(function () {
  'use strict';
  var d0 = document, D = JSON.parse(d0.getElementById('pd').textContent);
  var q = function (s) { return d0.querySelector(s); };
  var stage = q('#stage'), sheet = q('#sheet'), img = q('#img'), ov = q('#ov'), panel = q('#panel'), bottom = q('#bottom'),
      tip = q('#tip'), drawer = q('#drawer'), scrim = q('#scrim');
  var NS = 'http://www.w3.org/2000/svg', narrow = window.matchMedia('(max-width: 999px)'), hover = window.matchMedia('(hover: hover)');
  var homeHTML = panel.innerHTML, sel = null, selDoc = null, zoom = 1, fullOn = false, showAll = false, G = {}, partsOf = {};
  var CJKS = /[⺀-鿿＀-￯]/g;
  function zh(s) { var m = String(s || '').match(CJKS); return !!m && m.length > 0.3 * String(s).replace(/\s/g, '').length; }      // mostly Chinese: set in a Chinese face
  D.order.forEach(function (k) { D.parts[k].r.forEach(function (r) { (partsOf[r[0]] = partsOf[r[0]] || []).push(k); }); });

  function E(tag, at, kids) {
    var e = d0.createElement(tag);
    for (var k in at || {}) { if (at[k] == null) continue; if (k === 'text') e.textContent = at[k]; else e.setAttribute(k, at[k]); }
    (kids || []).forEach(function (c) { if (c != null && c !== false) e.appendChild(typeof c === 'string' ? d0.createTextNode(c) : c); });
    return e;
  }
  function S(tag, at) { var e = d0.createElementNS(NS, tag); for (var k in at) e.setAttribute(k, at[k]); return e; }
  function plural(n, one, many) { return n + ' ' + (n === 1 ? one : many); }

  // ---- the parts, drawn over the image; the smallest on top, so a click takes the part nearest the pointer
  var area = function (k) { var b = D.parts[k].b; return b ? b[2] * b[3] : 0; };
  D.order.slice().sort(function (a, b) { return area(b) - area(a); }).forEach(function (k) {
    var p = D.parts[k], g = S('g', {'class': 'pt', 'data-k': k});
    p.f.forEach(function (f) {
      var x = f[0] - 3, y = f[1] - 2.5, w = f[2] + 6, h = f[3] + 5;
      if (w < 22 && h < 22) { x -= (22 - w) / 2; y -= (22 - h) / 2; w = 22; h = 22; }
      g.appendChild(S('rect', {x: x, y: y, width: w, height: h, rx: 4}));
    });
    p.t.forEach(function (t) { var e = S(t[0], t[1]); e.setAttribute('transform', 'matrix(' + t[2].join(' ') + ')'); e.setAttribute('class', t[3] ? 'tr fl' : 'tr'); g.appendChild(e); });
    ov.appendChild(g); G[k] = g;
  });
  D.links.forEach(function (l) {
    var a = S('a', {href: l[4], 'class': 'lk', 'data-t': l[5]});
    a.appendChild(S('rect', {x: l[0] - 2, y: l[1] - 2, width: l[2] + 4, height: l[3] + 4, rx: 5})); ov.appendChild(a);
  });

  // ---- size and zoom: "fit" is the image as wide as the stage
  function fitW() { var cs = getComputedStyle(stage); return Math.max(160, stage.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight)); }
  function apply() {
    var w = fitW() * zoom; sheet.style.width = w + 'px'; sheet.style.height = (w * D.H / D.W) + 'px';
    q('#zv').textContent = zoom > 1.001 ? Math.round(zoom * 100) + '%' : 'fit';
    if (!fullOn && D.full && w * (window.devicePixelRatio || 1) > D.W * 1.3) {      // past the page image's own pixels: the full image
      fullOn = true; var im = new Image(); im.onload = function () { img.src = D.full; }; im.src = D.full;
    }
  }
  function zoomTo(z) {
    var old = sheet.clientWidth, cx = (stage.scrollLeft + stage.clientWidth / 2) / Math.max(1, old), cy = (stage.scrollTop + stage.clientHeight / 2) / Math.max(1, sheet.clientHeight);
    zoom = Math.min(8, Math.max(1, z)); apply();
    stage.scrollLeft = cx * sheet.clientWidth - stage.clientWidth / 2;
    if (!narrow.matches) stage.scrollTop = cy * sheet.clientHeight - stage.clientHeight / 2;
  }
  q('#zin').addEventListener('click', function () { zoomTo(zoom * 1.5); });
  q('#zout').addEventListener('click', function () { zoomTo(zoom / 1.5); });
  q('#zv').addEventListener('click', function () { zoomTo(1); });
  window.addEventListener('resize', apply);
  apply();
  img.addEventListener('error', function () { if (fullOn && img.src.indexOf(D.img) < 0) img.src = D.img; });

  // ---- pointing and clicking
  function keyOf(t) { var g = t && t.closest ? t.closest('g.pt') : null; return g ? g.getAttribute('data-k') : null; }
  ov.addEventListener('mousemove', function (ev) {
    if (!hover.matches) return;
    var k = keyOf(ev.target), a = ev.target.closest ? ev.target.closest('a.lk') : null;
    if (!k && !a) { tip.hidden = true; return; }
    tip.innerHTML = '';
    if (a) tip.appendChild(E('b', {text: a.getAttribute('data-t')}));
    else { var p = D.parts[k]; tip.appendChild(E('b', {text: p.l})); tip.appendChild(E('span', {text: plural(p.r.length, 'document', 'documents') + ' · click to open'})); }
    tip.hidden = false;
    var x = ev.clientX + 16, y = ev.clientY + 18; if (x + 370 > innerWidth) x = ev.clientX - 376; if (y + 90 > innerHeight) y = ev.clientY - 80;
    tip.style.left = Math.max(4, x) + 'px'; tip.style.top = Math.max(4, y) + 'px';
  });
  ov.addEventListener('mouseleave', function () { tip.hidden = true; });
  ov.addEventListener('click', function (ev) {
    if (ev.target.closest && ev.target.closest('a.lk')) return;           // the image's own links flip to another image
    var k = keyOf(ev.target); if (k) { ev.preventDefault(); showPart(k, false); }
  });
  stage.addEventListener('click', function (ev) {
    if (narrow.matches && (sel || selDoc) && !keyOf(ev.target) && !(ev.target.closest && ev.target.closest('a.lk'))) home();
  });

  // ---- the panel: this image (home), one part, one document
  function mark() {
    var on = selDoc ? (partsOf[selDoc] || []) : [];
    Object.keys(G).forEach(function (k) { G[k].classList.toggle('sel', k === sel); G[k].classList.toggle('dc', on.indexOf(k) >= 0); });
  }
  function setHash(h) { try { history.replaceState(null, '', h || location.pathname + location.search); } catch (e) {} }
  function put(node) {
    tip.hidden = true;
    if (narrow.matches) { bottom.innerHTML = ''; bottom.appendChild(node); bottom.hidden = false; bottom.scrollTop = 0; d0.body.classList.add('sheet-open'); }
    else { panel.innerHTML = ''; panel.appendChild(node); panel.scrollTop = 0; panel.removeAttribute('data-home'); }
  }
  function home() {
    sel = null; selDoc = null; mark(); bottom.hidden = true; bottom.innerHTML = ''; d0.body.classList.remove('sheet-open');
    if (!panel.hasAttribute('data-home')) { panel.innerHTML = homeHTML; panel.setAttribute('data-home', ''); var c = q('#showall'); if (c) c.checked = showAll; }
    setHash('');
  }
  function vbar(extra) {
    var b = E('div', {'class': 'vbar'}, [E('button', {'class': 'back', 'data-act': 'home', text: narrow.matches ? 'Close' : '← This image'})]);
    (extra || []).forEach(function (x) { b.appendChild(x); }); return b;
  }
  function kindLine(d) {
    return d.o === true ? 'Not on the record · ' + d.kw : d.o === false ? 'On the record · ' + d.kw : 'Kind not given';
  }
  function card(id, words, withName) {
    var d = D.docs[id], c = E('div', {'class': 'dc'});
    c.appendChild(E('div', {'class': 'kd'}, [E('i', {'class': 'dot' + (d.o === true ? ' o' : d.o === null ? ' u' : '')}), E('span', {text: kindLine(d)})]));
    if (withName) c.appendChild(E('div', {'class': 'nm' + (zh(d.n) ? ' zh' : ''), lang: zh(d.n) ? 'zh-Hans' : null, text: d.n + (d.d ? ' (' + d.d + ')' : '')}));
    if (d.a) c.appendChild(E('a', {'class': 'ad', href: d.a, target: '_blank', rel: 'noopener noreferrer', text: (d.s || 'the page') + ' ↗'}));
    else c.appendChild(E('div', {'class': 'na', text: (d.s ? d.s + ' · ' : '') + d.na}));
    if (words && words.length) {
      var qw = E('div', {'class': 'qw'}, [E('span', {text: 'In its words, on the image'})]);
      words.forEach(function (w) { qw.appendChild(E('blockquote', {'class': zh(w) ? 'zh' : null, lang: zh(w) ? 'zh-Hans' : null, text: w})); });
      c.appendChild(qw);
    }
    var n = (partsOf[id] || []).length;
    if (withName && (n > 1 || (d.also && d.also.length))) c.appendChild(E('button', {'class': 'more', 'data-act': 'doc', 'data-id': id, text: 'Where else it is used \u203a'}));
    return c;
  }
  function reveal(k) {
    var b = D.parts[k].b; if (!b) return;
    var s = sheet.clientWidth / D.W, x = sheet.offsetLeft + b[0] * s, y = b[1] * s, w = b[2] * s, h = b[3] * s;
    if (narrow.matches) {
      window.scrollTo({top: Math.max(0, sheet.getBoundingClientRect().top + window.scrollY + y - Math.max(70, innerHeight * 0.14)), behavior: 'smooth'});
      stage.scrollTo({left: Math.max(0, x + w / 2 - stage.clientWidth / 2)});
    } else stage.scrollTo({left: Math.max(0, x + w / 2 - stage.clientWidth / 2), top: Math.max(0, sheet.offsetTop + y + h / 2 - stage.clientHeight / 2), behavior: 'smooth'});
  }
  function showPart(k, scroll) {
    var p = D.parts[k]; if (!p) return; sel = k; selDoc = null; mark();
    var i = D.order.indexOf(k), extra = [];
    if (i > 0) extra.push(E('button', {'data-act': 'part', 'data-k': D.order[i - 1], text: '‹ part'}));
    if (i < D.order.length - 1) extra.push(E('button', {'data-act': 'part', 'data-k': D.order[i + 1], text: 'part ›'}));
    var box = E('div', {'class': 'pv'}, [vbar(extra), E('div', {'class': 'kick', text: 'This part of the image'}), E('h2', {text: p.l})]);
    var ac = /^A count\b\D*?(\d[\d,]*)/.exec(p.l || ''), m = /(\d+) sources?\b/.exec(p.l || ''), n = p.r.length, rc = /(\d+) (?:dated )?records\b(?:\D*?\(listed first\)[;,] (?:the other )?(\d+))?/.exec(p.l || '');
    var why = (m && +m[1] < n) ? ' The image counts sources; this list holds every saved copy behind the part, which can be more.' :      // records: both groups where the label names two ("N records ... (listed first); M are ...")
      (rc && +rc[1] + (rc[2] ? +rc[2] : 0) > n) ? ' The image counts records; this list holds each saved copy behind the part once, and one copy can carry more than one record, so the list can be shorter.' :
      (ac && +ac[1].replace(/,/g, '') !== n) ? ' The image counts what this label names; this list holds the saved copies behind it, which can be more or fewer.' : '';
    box.appendChild(E('p', {'class': 'mut', text: n === 0 ? 'No document stands behind this part; its heading says what is known and what is not held.' :
      'It rests on ' + plural(n, 'document', 'documents') + '.' + why}));
    var on = p.r.filter(function (r) { return D.docs[r[0]] && D.docs[r[0]].o === false; }), off = p.r.filter(function (r) { return D.docs[r[0]] && D.docs[r[0]].o !== false; });
    var groups = (n > 12 && on.length && off.length) ? [['On the record', on], ['Not on the record, or kind not given', off]] : [[null, p.r]];
    groups.forEach(function (g) {
      if (g[0]) box.appendChild(E('div', {'class': 'grp', text: g[0] + ' · ' + g[1].length}));
      g[1].forEach(function (r) { if (D.docs[r[0]]) box.appendChild(card(r[0], r[1], true)); });
    });
    put(box); setHash('#p-' + k); if (scroll) reveal(k);
  }
  function showDoc(id) {
    var d = D.docs[id]; if (!d) return; sel = null; selDoc = id; mark();
    var ks = partsOf[id] || [];
    var box = E('div', {'class': 'pv'}, [vbar(), E('div', {'class': 'kick', text: 'A document behind this image'}), E('h2', {'class': zh(d.n) ? 'zh' : null, lang: zh(d.n) ? 'zh-Hans' : null, text: d.n + (d.d ? ' (' + d.d + ')' : '')}), card(id, null, false)]);
    box.appendChild(E('div', {'class': 'grp', text: ks.length ? plural(ks.length, 'part of this image rests', 'parts of this image rest') + ' on it' : 'It stands behind this image as a whole'}));
    var ul = E('ul', {'class': 'lst'});
    ks.forEach(function (k) { ul.appendChild(E('li', {}, [E('button', {'data-act': 'part', 'data-k': k}, [E('span', {text: D.parts[k].l})])])); });
    box.appendChild(ul);
    if (d.also && d.also.length) {
      box.appendChild(E('div', {'class': 'grp', text: 'Other images that rest on it'}));
      var u2 = E('ul', {'class': 'sib'});
      d.also.forEach(function (a) { var pg = D.pages[a[0] - 1]; u2.appendChild(E('li', {}, [E('a', {href: pg[0] + '#doc-' + encodeURIComponent(id)}, [E('i', {text: String(a[0])}), E('span', {text: pg[1] + (a[1] ? ' · ' + plural(a[1], 'part', 'parts') : '')})])])); });
      box.appendChild(u2);
    }
    put(box); setHash('#doc-' + encodeURIComponent(id)); if (ks.length) reveal(ks[0]);
  }
  function lists(det) {
    var which = det.getAttribute('data-list'), holder = det.querySelector('.lst'), f = det.querySelector('.flt');
    function fill() {
      var t = (f.value || '').trim().toLowerCase(); holder.innerHTML = '';
      if (which === 'parts') D.order.forEach(function (k) { var p = D.parts[k];
        if (t && p.l.toLowerCase().indexOf(t) < 0) return;
        holder.appendChild(E('li', {}, [E('button', {'data-act': 'part', 'data-k': k}, [E('span', {text: p.l}), E('span', {'class': 'c', text: plural(p.r.length, 'doc.', 'docs.')})])])); });
      else Object.keys(D.docs).forEach(function (id) { var d = D.docs[id];
        if (t && (d.n + ' ' + d.d + ' ' + d.s + ' ' + d.kw).toLowerCase().indexOf(t) < 0) return;
        var n = (partsOf[id] || []).length;
        holder.appendChild(E('li', {}, [E('button', {'data-act': 'doc', 'data-id': id}, [E('i', {'class': 'dot' + (d.o === true ? ' o' : d.o === null ? ' u' : '')}), E('span', {text: d.n + (d.d ? ' (' + d.d + ')' : '')}), E('span', {'class': 'c', text: n ? plural(n, 'part', 'parts') : ''})])])); });
    }
    if (!det.hasAttribute('data-made')) { det.setAttribute('data-made', ''); f.addEventListener('input', fill); fill(); }
  }
  function act(ev) {
    var b = ev.target.closest ? ev.target.closest('[data-act]') : null; if (!b) return;
    var a = b.getAttribute('data-act');
    if (a === 'home') home();
    else if (a === 'part') showPart(b.getAttribute('data-k'), true);
    else if (a === 'doc') showDoc(b.getAttribute('data-id'));
  }
  panel.addEventListener('click', act); bottom.addEventListener('click', act);
  panel.addEventListener('toggle', function (ev) { if (ev.target.matches && ev.target.matches('details.ls') && ev.target.open) lists(ev.target); }, true);
  panel.addEventListener('change', function (ev) { if (ev.target.id === 'showall') { showAll = ev.target.checked; d0.body.classList.toggle('all', showAll); } });
  panel.setAttribute('data-home', '');

  // ---- flipping: keys, swipe, the contents drawer
  function go(t) { if (t) location.href = t[0]; }
  function openDrawer() { drawer.hidden = false; scrim.hidden = false; var c = drawer.querySelector('.cur > a') || drawer.querySelector('a'); if (c) { c.focus({preventScroll: true}); c.scrollIntoView({block: 'center'}); } }
  function closeDrawer() { drawer.hidden = true; scrim.hidden = true; }
  d0.addEventListener('keydown', function (ev) {
    var t = ev.target; if (t && /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)) { if (ev.key === 'Escape') t.blur(); return; }
    if (ev.altKey || ev.ctrlKey || ev.metaKey || ev.shiftKey) return;
    if (ev.key === 'ArrowRight') { ev.preventDefault(); go(D.next); }
    else if (ev.key === 'ArrowLeft' && D.prev) { ev.preventDefault(); go(D.prev); }
    else if (ev.key === 'Escape') { if (!drawer.hidden) closeDrawer(); else home(); }
  });
  var t0 = null;
  stage.addEventListener('touchstart', function (ev) { if (ev.touches.length !== 1) { t0 = null; return; } var t = ev.touches[0]; t0 = {x: t.clientX, y: t.clientY, t: Date.now()}; }, {passive: true});
  stage.addEventListener('touchend', function (ev) {
    if (!t0) return; var t = ev.changedTouches[0], dx = t.clientX - t0.x, dy = t.clientY - t0.y, dt = Date.now() - t0.t; t0 = null;
    if (dt > 800 || Math.abs(dx) < 60 || Math.abs(dx) < 1.6 * Math.abs(dy)) return;
    if ((window.visualViewport && window.visualViewport.scale > 1.05) || zoom > 1.001) return;     // zoomed in: a swipe pans
    go(dx < 0 ? D.next : D.prev);
  }, {passive: true});
  q('#cbtn').addEventListener('click', openDrawer); q('#pos').addEventListener('click', openDrawer);
  scrim.addEventListener('click', closeDrawer);
  drawer.addEventListener('click', function (ev) { if (ev.target.closest && ev.target.closest('[data-act=close]')) closeDrawer(); });
  var ix = q('#intro-x'); if (ix) ix.addEventListener('click', function () { q('#intro').hidden = true; apply(); });

  // ---- addresses: #p-<part>, #doc-<document>; on the first page also #<image number>
  function route() {
    var h = decodeURIComponent(location.hash || ''), m;
    if (D.pos === 1 && (m = /^#(\d{1,2})$/.exec(h))) { var n = +m[1]; if (n > 1 && n <= D.pages.length) { location.replace(D.pages[n - 1][0]); return; } }
    if ((m = /^#p-(.+)$/.exec(h)) && D.parts[m[1]]) { showPart(m[1], true); return; }
    if ((m = /^#doc-(.+)$/.exec(h)) && D.docs[m[1]]) { showDoc(m[1]); return; }
  }
  function relayout() { var s = sel, dd = selDoc; home(); apply(); if (s) showPart(s, false); else if (dd) showDoc(dd); }
  if (narrow.addEventListener) narrow.addEventListener('change', relayout); else if (narrow.addListener) narrow.addListener(relayout);
  window.addEventListener('hashchange', route);
  route();
  if (!narrow.matches) stage.focus({preventScroll: true});
})();
