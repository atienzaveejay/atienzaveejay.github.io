(() => {
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  // Filters (tabs) and text search on lists; both apply together.
  const lists = new Map();
  const stateFor = id => {
    if (!lists.has(id)) lists.set(id, { tag: '', q: '' });
    return lists.get(id);
  };
  const applyList = id => {
    const list = document.getElementById(id);
    if (!list) return;
    const st = stateFor(id);
    const count = document.querySelector(`[data-count-for="${id}"]`);
    if (count && !count.dataset.noun) count.dataset.noun = count.textContent.replace(/^\d+\s*/, '');
    let shown = 0;
    Array.from(list.children).forEach(el => {
      const tagHit = !st.tag || (el.dataset.tags || '').split('|').includes(st.tag);
      const qHit = !st.q || el.textContent.toLowerCase().includes(st.q);
      el.hidden = !(tagHit && qHit);
      shown += !el.hidden;
    });
    if (count) count.textContent = `${shown} ${count.dataset.noun}`;
  };
  $$('.filters').forEach(bar => bar.addEventListener('click', ev => {
    const btn = ev.target.closest('button');
    if (!btn) return;
    $$('button', bar).forEach(b => b.setAttribute('aria-pressed', b === btn));
    stateFor(bar.dataset.target).tag = btn.dataset.filter;
    applyList(bar.dataset.target);
  }));
  $$('.list-search').forEach(inp => inp.addEventListener('input', () => {
    stateFor(inp.dataset.target).q = inp.value.trim().toLowerCase();
    applyList(inp.dataset.target);
  }));

  // Mobile menu.
  const menuBtn = document.querySelector('.menu-btn');
  menuBtn && menuBtn.addEventListener('click', () => {
    const open = menuBtn.getAttribute('aria-expanded') !== 'true';
    menuBtn.setAttribute('aria-expanded', open);
    menuBtn.textContent = open ? 'Close' : 'Menu';
    document.body.classList.toggle('menu-open', open);
  });

  // Site search (Cmd/Ctrl+K or "/").
  const finder = document.querySelector('.finder');
  if (finder) {
    const input = finder.querySelector('input');
    const out = finder.querySelector('.finder-results');
    let index = null, results = [], sel = 0;
    const load = () => index ? Promise.resolve(index)
      : fetch((window.SITE_BASE || '') + '/search.json').then(r => r.json()).then(d => (index = d));
    const esc = s => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    const render = () => {
      out.innerHTML = results.map((r, i) =>
        `<li role="option" aria-selected="${i === sel}"><a href="${esc(r.url)}"${r.ext ? ' target="_blank" rel="noopener"' : ''}>` +
        `<span class="f-kind">${esc(r.kind)}</span><span class="f-title">${esc(r.title)}</span><span class="f-sub">${esc(r.sub || '')}</span></a></li>`
      ).join('') || '<li class="f-empty">No matches</li>';
    };
    const search = () => {
      const q = input.value.trim().toLowerCase();
      const words = q.split(/\s+/).filter(Boolean);
      results = (index || []).map(it => {
        const hay = `${it.title} ${it.sub} ${it.text} ${it.kind}`.toLowerCase();
        if (!words.every(w => hay.includes(w))) return null;
        const score = (it.title.toLowerCase().includes(q) ? 3 : 0) + (it.kind === 'Case study' ? 2 : it.kind === 'App' ? 1.5 : it.kind === 'Page' ? 1 : 0);
        return [score, it];
      }).filter(Boolean).sort((a, b) => b[0] - a[0]).slice(0, q ? 12 : 8).map(x => x[1]);
      sel = 0; render();
    };
    const openFinder = () => { load().then(() => { search(); }); finder.showModal(); input.select(); };
    $$('[data-open-search]').forEach(b => b.addEventListener('click', openFinder));
    document.addEventListener('keydown', ev => {
      const typing = /input|textarea|select/i.test(document.activeElement.tagName);
      if ((ev.key === 'k' && (ev.metaKey || ev.ctrlKey)) || (ev.key === '/' && !typing)) {
        ev.preventDefault(); finder.open ? finder.close() : openFinder();
      }
    });
    input.addEventListener('input', search);
    input.addEventListener('keydown', ev => {
      if (ev.key === 'ArrowDown') { sel = Math.min(sel + 1, results.length - 1); render(); ev.preventDefault(); }
      if (ev.key === 'ArrowUp') { sel = Math.max(sel - 1, 0); render(); ev.preventDefault(); }
      if (ev.key === 'Enter' && results[sel]) {
        const r = results[sel];
        r.ext ? window.open(r.url, '_blank', 'noopener') : (location.href = r.url);
      }
    });
    finder.addEventListener('click', ev => { if (ev.target === finder) finder.close(); });
    // Show the right shortcut on non-Mac machines.
    if (!/Mac|iPhone|iPad/.test(navigator.platform)) $$('.search-btn kbd').forEach(k => (k.textContent = 'Ctrl K'));
  }

  // YouTube: show the thumbnail, load the player only on click.
  $$('.yt').forEach(btn => btn.addEventListener('click', () => {
    const f = document.createElement('iframe');
    f.src = `https://www.youtube-nocookie.com/embed/${btn.dataset.id}?autoplay=1`;
    f.title = 'YouTube video';
    f.allow = 'accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture';
    f.allowFullscreen = true;
    const wrap = document.createElement('div');
    wrap.className = btn.className.replace(/\byt\b/, '').trim();
    wrap.appendChild(f);
    btn.replaceWith(wrap);
  }));

  // Lightbox for gallery shots and case study images, with arrow-key navigation.
  const box = document.querySelector('.lightbox');
  if (box) {
    const img = box.querySelector('img');
    let set = [], idx = 0;
    const show = i => {
      idx = (i + set.length) % set.length;
      img.src = set[idx].src;
      img.alt = set[idx].alt;
      box.classList.toggle('single', set.length < 2);
    };
    const open = (items, i) => { set = items; show(i); box.showModal(); };
    $$('.shot').forEach(a => a.addEventListener('click', ev => {
      ev.preventDefault();
      const group = $$(`.shot[data-group="${a.dataset.group}"]`);
      open(group.map(g => ({ src: g.href, alt: g.querySelector('img').alt })), group.indexOf(a));
    }));
    const proseImgs = $$('.prose img');
    proseImgs.forEach((im, i) => {
      im.classList.add('zoomable');
      im.addEventListener('click', () => open(proseImgs.map(p => ({ src: p.currentSrc || p.src, alt: p.alt })), i));
    });
    box.querySelector('.lb-prev').addEventListener('click', ev => { ev.stopPropagation(); show(idx - 1); });
    box.querySelector('.lb-next').addEventListener('click', ev => { ev.stopPropagation(); show(idx + 1); });
    box.querySelector('.lb-close').addEventListener('click', () => box.close());
    box.addEventListener('click', ev => { if (ev.target === box || ev.target === img) box.close(); });
    box.addEventListener('keydown', ev => {
      if (ev.key === 'ArrowRight') show(idx + 1);
      if (ev.key === 'ArrowLeft') show(idx - 1);
    });
  }

  // Highlight the current section in the case study contents list.
  const tocLinks = $$('.toc a');
  if (tocLinks.length && 'IntersectionObserver' in window) {
    const byId = new Map(tocLinks.map(a => [decodeURIComponent(a.hash.slice(1)), a]));
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => {
        if (en.isIntersecting) {
          tocLinks.forEach(a => a.removeAttribute('aria-current'));
          const a = byId.get(en.target.id);
          a && a.setAttribute('aria-current', 'true');
        }
      });
    }, { rootMargin: '-80px 0px -70% 0px' });
    byId.forEach((_, id) => { const h = document.getElementById(id); h && io.observe(h); });
  }

})();

// ---------- Oct 2026 redesign: menu, reveals, counters, video ----------
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, r = document) => r.querySelector(s);

  // ---------- data (from _proto/content.json) ----------
  const clients = ["Interview Query", "Winning Coaching", "ROO", "YourLifeChoices", "Leaders In Transition", "Storyseller Systems", "Kelly Technology", "PilotTV"];
  const mp4 = n => ({ src: n, poster: n.replace(/\.mp4$/, '.jpg') });
  const vids = {
    justListed: mp4('/assets/real-estate/just-listed.mp4'),
    guess: mp4('/assets/real-estate/guess-the-price.mp4'),
    pov: mp4('/assets/real-estate/pov-keys.mp4'),
    coogee: mp4('/assets/real-estate/neighbourhood-coogee.mp4'),
    threeYears: mp4('/assets/roo-video/ad-three-years.mp4'),
    satisfying: mp4('/assets/roo-video/ad-most-satisfying.mp4'),
    nobody: mp4('/assets/roo-video/ad-nobody-told-me.mp4'),
    cleanup: mp4('/assets/roo-video/reel-20-second-cleanup.mp4'),
    tomato: mp4('/assets/roo-video/reel-tomato-tips.mp4'),
  };
  const short = id => ({ img: `https://i.ytimg.com/vi/${id}/oar2.jpg`, fallback: `https://i.ytimg.com/vi/${id}/hqdefault.jpg`, href: `https://www.youtube.com/shorts/${id}` });

  const isHome = !!document.getElementById('reel');
  if (isHome) {
  // ---------- hero reel: three drifting columns ----------
  const cols = [
    [vids.justListed, short('bMklmLvtEqU'), vids.cleanup, short('eXhYwjnaA2o')],
    [short('uraRYBQaydw'), vids.threeYears, short('_kA2zVr5djM'), vids.pov],
    [vids.guess, short('xC2PH0EtLI4'), vids.coogee, short('cLDtFwbElTo')],
  ];
  const tileHTML = t => t.src
    ? `<div class="tile"><video muted loop playsinline preload="none" poster="${t.poster}" data-src="/assets/previews/${t.src.split('/').pop()}"></video></div>`
    : `<div class="tile"><img src="${t.img}" alt="" loading="lazy" onerror="this.onerror=null;this.src='${t.fallback}'"></div>`;
  $('#reel').innerHTML = cols.map(c => {
    const items = c.map(tileHTML).join('');
    return `<div class="reel-col"><div class="reel-track">${items}${items}</div></div>`;
  }).join('');

  // ---------- client marquee ----------
  const mq = clients.map(c => `<span>${c}</span>`).join('');
  $('#mq').innerHTML = mq; $('#mq2').innerHTML = mq;

  // ---------- selected work ----------
  const work = [
    [vids.justListed, 'Just listed', 'Real estate reel'],
    [vids.threeYears, 'ROO', 'Meta video ad'],
    [vids.guess, 'Guess the price', 'Real estate reel'],
    [vids.cleanup, 'ROO', 'Organic Reel'],
  ];
  const shortsWork = [['bMklmLvtEqU', 'Coach Edwin Soriano', 'YouTube Short'], ['eXhYwjnaA2o', 'Kate Lewis', 'YouTube Short'],
                      ['uraRYBQaydw', 'Coach Edwin Soriano', 'YouTube Short'], ['_kA2zVr5djM', 'Kate Lewis', 'YouTube Short']];
  $('#vgrid').innerHTML =
    work.map(([v, t, s]) => `<div class="vcard" tabindex="0" data-hover><div class="tile"><video muted loop playsinline preload="none" poster="${v.poster}" data-src="${v.src}"></video><span class="play" aria-hidden="true"></span></div><p>${t}<small>${s}</small></p></div>`).join('') +
    shortsWork.map(([id, t, s]) => { const x = short(id); return `<a class="vcard" href="${x.href}" target="_blank" rel="noopener"><div class="tile"><img src="${x.img}" alt="" loading="lazy" onerror="this.onerror=null;this.src='${x.fallback}'"><span class="play" aria-hidden="true"></span></div><p>${t}<small>${s}</small></p></a>`; }).join('');

  const cases = [
    ['interview-query-seo', '$569K+', 'Turning Content Into a $569K Revenue Engine', 'Interview Query, SEO and content', '/assets/interview-query-seo/01.webp'],
    ['storyseller-meta-ads', '₱15M', 'Driving ₱15M in Contracts from Meta Ads for a Complex B2B Service', 'Storyseller Systems, Paid social', '/assets/storyseller-meta-ads/01.webp'],
    ['ylc-newsletter', '1.15M+', 'Scaling a Newsletter to 1.15M Traffic and 100K Subscribers', 'YourLifeChoices, Email', '/assets/ylc-newsletter/01.webp'],
    ['roo-tiktok-carousel', '34,527', 'A Family-Story TikTok Carousel Took Weekly Views From 1,605 to 34,527', 'ROO, TikTok', '/assets/roo-tiktok/cover.webp'],
    ['interview-query-linkedin', '8.7M+', "Scaling a Founder's LinkedIn to 8.7M Impressions", 'Interview Query, LinkedIn', '/assets/interview-query-linkedin/01.webp'],
    ['kelly-app', '23,000', 'Acquiring 23K Users in 2 Months While Reducing CAC by 40%', 'Kelly App, User acquisition', '/assets/kelly-app/01.webp'],
  ];
  $('#cgrid').innerHTML = cases.map(([slug, m, t, meta, img]) =>
    `<a class="case" href="/work/${slug}/"><img src="${img}" alt="" loading="lazy"><div class="case-body"><span class="chip">${m}</span><h3>${t}</h3><span class="meta">${meta}</span></div></a>`).join('');

  $('#ggrid').innerHTML = ['02', '03', '05', '07', '11', '12'].map(n =>
    `<a href="/graphics/"><img src="/assets/thumbnails/${n}.webp" alt="YouTube thumbnail" loading="lazy"></a>`).join('');

  }

  // ---------- videos: load and play only while visible ----------
  const load = v => { if (!v.src && v.dataset.src) v.src = v.dataset.src; };
  if (!reduce && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => es.forEach(en => {
      const v = en.target;
      if (en.isIntersecting) { load(v); v.play().catch(() => {}); } else v.pause();
    }), { rootMargin: '100px' });
    document.querySelectorAll('#reel video, video[data-autoplay]').forEach(v => io.observe(v));
  }
  // hover (or tap / focus) to play in the work grid
  document.querySelectorAll('[data-hover]').forEach(card => {
    const v = card.querySelector('video');
    const on = () => { load(v); v.play().then(() => card.classList.add('playing')).catch(() => {}); };
    const off = () => { v.pause(); card.classList.remove('playing'); };
    card.addEventListener('mouseenter', on); card.addEventListener('mouseleave', off);
    card.addEventListener('focus', on); card.addEventListener('blur', off);
    card.addEventListener('click', () => (v.paused ? on() : off()));
  });

  // ---------- tabs ----------
  const tabs = [...document.querySelectorAll('[role=tab]')];
  tabs.forEach(t => t.addEventListener('click', () => tabs.forEach(b => {
    const sel = b === t;
    b.setAttribute('aria-selected', sel);
    const p = document.getElementById(b.getAttribute('aria-controls'));
    if (p) { p.hidden = !sel; if (!sel) p.querySelectorAll('video').forEach(v => v.pause()); }
  })));

  // ---------- services menu ----------
  const sBtn = $('#services-btn'), mega = $('#mega'), nav = $('#nav'), mBtn = $('#menu-btn');
  if (sBtn && mega && nav && mBtn) {
  const setMega = open => { mega.classList.toggle('open', open); sBtn.setAttribute('aria-expanded', open); };
  sBtn.addEventListener('click', e => { e.stopPropagation(); setMega(!mega.classList.contains('open')); });
  const desktop = matchMedia('(min-width: 761px) and (hover: hover)');
  let t;
  [sBtn, mega].forEach(el => {
    el.addEventListener('mouseenter', () => { if (desktop.matches) { clearTimeout(t); setMega(true); } });
    el.addEventListener('mouseleave', () => { if (desktop.matches) t = setTimeout(() => setMega(false), 180); });
  });
  document.addEventListener('click', e => { if (!mega.contains(e.target) && e.target !== sBtn) setMega(false); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') { setMega(false); nav.classList.remove('open'); mBtn.setAttribute('aria-expanded', false); sBtn.focus(); } });
  mBtn.addEventListener('click', () => { const o = !nav.classList.contains('open'); nav.classList.toggle('open', o); mBtn.setAttribute('aria-expanded', o); });
  nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => { nav.classList.remove('open'); setMega(false); mBtn.setAttribute('aria-expanded', false); }));
  }

  // ---------- count-up stats ----------
  const countUp = el => {
    const m = el.dataset.count.match(/^([^\d]*)([\d.]+)(.*)$/);
    if (!m) return;
    const [, pre, num, post] = m, target = parseFloat(num), dec = (num.split('.')[1] || '').length, t0 = performance.now(), dur = 1400;
    const step = now => {
      const p = Math.min(1, (now - t0) / dur), eased = 1 - Math.pow(1 - p, 3);
      el.textContent = pre + (target * eased).toFixed(dec) + post;
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };
  // ---------- reveals ----------
  if (!reduce && 'IntersectionObserver' in window) {
    const ro = new IntersectionObserver(es => es.forEach(en => {
      if (!en.isIntersecting) return;
      en.target.classList.add('in');
      en.target.querySelectorAll('[data-count]').forEach(countUp);
      ro.unobserve(en.target);
    }), { threshold: .15 });
    document.querySelectorAll('.reveal').forEach(el => ro.observe(el));
  } else document.querySelectorAll('.reveal').forEach(el => el.classList.add('in'));
})();

// ---------- Work library: type and industry filters that combine, with live counts and shareable links ----------
(() => {
  const grid = document.querySelector('.lib-grid');
  if (!grid) return;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const chips = [...document.querySelectorAll('.rail .chip')];
  const items = [...grid.querySelectorAll('.item')];
  const count = document.querySelector('.count'), clear = document.querySelector('.clear-filters'), empty = document.querySelector('.lib-empty');
  const has = (el, axis, v) => v === 'all' || el.dataset[axis].split(' ').includes(v);
  const matches = (el, st) => has(el, 'type', st.type) && has(el, 'ind', st.ind);
  // links already in use before the two filters existed
  const LEGACY = { 'growth': { type: 'growth' }, 'content': { type: 'content' }, 'design': { type: 'design' },
    'content/shorts': { type: 'short' }, 'content/youtube': { type: 'long' }, 'content/video-ads': { type: 'video-ads' },
    'content/graphics': { type: 'graphics' }, 'content/real-estate': { ind: 'real-estate' }, 'design/web': { type: 'websites' },
    'design/decks': { type: 'decks' }, 'growth/seo': { type: 'seo' }, 'growth/ads': { type: 'paid-ads' },
    'growth/email': { type: 'email' }, 'growth/social': { type: 'social' } };
  const valid = axis => chips.filter(c => c.dataset.axis === axis).map(c => c.dataset.v).concat(axis === 'type' ? ['video'] : []);
  const fromHash = () => {
    const h = decodeURIComponent(location.hash.slice(1));
    const st = { type: 'all', ind: 'all', ...(LEGACY[h] || {}) };
    new URLSearchParams(h).forEach((v, k) => { if (k === 'type' && valid('type').includes(v)) st.type = v; if (k === 'industry' && valid('ind').includes(v)) st.ind = v; });
    return st;
  };
  const toHash = st => { const p = []; if (st.type !== 'all') p.push('type=' + st.type); if (st.ind !== 'all') p.push('industry=' + st.ind); return p.join('&'); };
  let state = fromHash();
  const apply = animate => {
    const before = new Map();
    if (animate && !reduce) items.forEach(el => { if (!el.classList.contains('hide')) before.set(el, el.getBoundingClientRect()); });
    let n = 0;
    items.forEach(el => {
      const on = matches(el, state); el.classList.toggle('hide', !on); if (on) n++;
      if (!on) { const v = el.querySelector('video'); if (v) { v.pause(); el.classList.remove('playing'); } }
    });
    chips.forEach(c => {
      const axis = c.dataset.axis, v = c.dataset.v;
      const k = items.filter(el => matches(el, { ...state, [axis]: v })).length;
      c.querySelector('span').textContent = k;
      c.setAttribute('aria-pressed', String(state[axis] === v));
      c.disabled = k === 0 && state[axis] !== v;
    });
    count.textContent = `${n} ${n === 1 ? 'piece' : 'pieces'}`;
    clear.hidden = state.type === 'all' && state.ind === 'all';
    empty.hidden = n > 0;
    if (!animate || reduce) return;
    items.forEach(el => {
      if (el.classList.contains('hide')) return;
      const a = before.get(el), b = el.getBoundingClientRect();
      if (a) { const dx = a.left - b.left, dy = a.top - b.top; if (dx || dy) el.animate([{ transform: `translate(${dx}px, ${dy}px)` }, { transform: 'none' }], { duration: 520, easing: 'cubic-bezier(.2,.7,.2,1)' }); }
      else el.animate([{ opacity: 0, transform: 'scale(.94)' }, { opacity: 1, transform: 'none' }], { duration: 380, easing: 'cubic-bezier(.2,.7,.2,1)' });
    });
  };
  const set = st => { state = st; const h = toHash(st); history.replaceState(null, '', h ? '#' + h : location.pathname); apply(true); };
  chips.forEach(c => c.addEventListener('click', () => set({ ...state, [c.dataset.axis]: c.dataset.v })));
  clear.addEventListener('click', () => set({ type: 'all', ind: 'all' }));
  addEventListener('hashchange', () => { state = fromHash(); apply(false); });
  apply(false);
})();

// ---------- in-page navigation: highlight the section in view, keep its chip visible, back to top ----------
(() => {
  const bar = document.querySelector('.subnav');
  if (bar) {
    const links = [...bar.querySelectorAll('a[href^="#"]')];
    const targets = links.map(a => document.getElementById(decodeURIComponent(a.hash.slice(1)))).filter(Boolean);
    const mark = id => links.forEach(a => {
      const on = a.hash.slice(1) === id;
      a.toggleAttribute('aria-current', on); if (on) a.setAttribute('aria-current', 'true');
      if (on) { const r = a.getBoundingClientRect(), p = a.parentElement.getBoundingClientRect(); if (r.left < p.left || r.right > p.right) a.parentElement.scrollBy({ left: r.left - p.left - 40, behavior: 'smooth' }); }
    });
    const onScroll = () => {
      let cur = targets[0];
      for (const t of targets) if (t.getBoundingClientRect().top < 180) cur = t;
      if (cur) mark(cur.id);
    };
    addEventListener('scroll', onScroll, { passive: true }); onScroll();
  }
  const btn = document.createElement('button');
  btn.type = 'button'; btn.className = 'to-top'; btn.setAttribute('aria-label', 'Back to top'); btn.textContent = '↑';
  btn.addEventListener('click', () => scrollTo({ top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' }));
  document.body.appendChild(btn);
  addEventListener('scroll', () => btn.classList.toggle('show', scrollY > 900), { passive: true });
})();

// ---------- service page galleries: a format (or type) filter and an industry filter, linkable as #format=short&industry=real-estate ----------
(() => {
  const root = document.querySelector('.svc-lib');
  if (!root) return;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const key = root.dataset.key;
  const chips = [...root.querySelectorAll('.chip')];
  const items = [...root.querySelectorAll('.svc-grid > a')];
  const count = root.querySelector('.count'), clear = root.querySelector('.clear-filters'), empty = root.querySelector('.lib-empty');
  const has = (el, axis, v) => v === 'all' || (el.dataset[axis] || '').split(' ').includes(v);
  const matches = (el, st) => has(el, 'f', st.f) && has(el, 'ind', st.ind);
  const valid = axis => chips.filter(c => c.dataset.axis === axis).map(c => c.dataset.v);
  const fromHash = () => {
    const st = { f: 'all', ind: 'all' };
    new URLSearchParams(decodeURIComponent(location.hash.slice(1))).forEach((v, k) => {
      if (k === key && valid('f').includes(v)) st.f = v;
      if (k === 'industry' && valid('ind').includes(v)) st.ind = v;
    });
    return st;
  };
  const toHash = st => [st.f !== 'all' && `${key}=${st.f}`, st.ind !== 'all' && `industry=${st.ind}`].filter(Boolean).join('&');
  let state = fromHash();
  const apply = animate => {
    const before = new Map();
    if (animate && !reduce) items.forEach(el => { if (!el.classList.contains('hide')) before.set(el, el.getBoundingClientRect()); });
    let n = 0;
    items.forEach(el => {
      const on = matches(el, state); el.classList.toggle('hide', !on); if (on) n++;
      if (!on) { const v = el.querySelector('video'); if (v) { v.pause(); el.classList.remove('playing'); } }
    });
    chips.forEach(c => {
      const axis = c.dataset.axis, v = c.dataset.v;
      const k = items.filter(el => matches(el, { ...state, [axis]: v })).length;
      c.querySelector('span').textContent = k;
      c.setAttribute('aria-pressed', String(state[axis] === v));
      c.disabled = k === 0 && state[axis] !== v;
    });
    count.textContent = `${n} ${n === 1 ? 'piece' : 'pieces'}`;
    clear.hidden = state.f === 'all' && state.ind === 'all';
    empty.hidden = n > 0;
    if (!animate || reduce) return;
    items.forEach(el => {
      if (el.classList.contains('hide')) return;
      const a = before.get(el), b = el.getBoundingClientRect();
      if (a) { const dx = a.left - b.left, dy = a.top - b.top; if (dx || dy) el.animate([{ transform: `translate(${dx}px, ${dy}px)` }, { transform: 'none' }], { duration: 520, easing: 'cubic-bezier(.2,.7,.2,1)' }); }
      else el.animate([{ opacity: 0, transform: 'scale(.94)' }, { opacity: 1, transform: 'none' }], { duration: 380, easing: 'cubic-bezier(.2,.7,.2,1)' });
    });
  };
  const set = st => { state = st; const h = toHash(st); history.replaceState(null, '', h ? '#' + h : location.pathname); apply(true); };
  chips.forEach(c => c.addEventListener('click', () => set({ ...state, [c.dataset.axis]: c.dataset.v })));
  clear.addEventListener('click', () => set({ f: 'all', ind: 'all' }));
  addEventListener('hashchange', () => { const st = fromHash(); if (st.f !== state.f || st.ind !== state.ind) { state = st; apply(false); } });
  apply(false);
  if (state.f !== 'all' || state.ind !== 'all') root.scrollIntoView();  // a shared filtered link lands on the work
})();
