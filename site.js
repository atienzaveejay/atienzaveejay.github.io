(() => {
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  // Theme toggle: remembers the choice, falls back to the system setting.
  const root = document.documentElement;
  const isDark = () => root.dataset.theme
    ? root.dataset.theme === 'dark'
    : matchMedia('(prefers-color-scheme: dark)').matches;
  const toggle = document.querySelector('.theme-toggle');
  const label = () => toggle && toggle.setAttribute('aria-label', isDark() ? 'Switch to light theme' : 'Switch to dark theme');
  label();
  toggle && toggle.addEventListener('click', () => {
    root.dataset.theme = isDark() ? 'light' : 'dark';
    try { localStorage.setItem('theme', root.dataset.theme); } catch (e) {}
    label();
  });

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
