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

  // Filters for case studies and writing.
  $$('.filters').forEach(bar => {
    const list = document.getElementById(bar.dataset.target);
    const count = document.querySelector(`[data-count-for="${bar.dataset.target}"]`);
    const noun = count ? count.textContent.replace(/^\d+\s*/, '') : '';
    bar.addEventListener('click', ev => {
      const btn = ev.target.closest('button');
      if (!btn) return;
      $$('button', bar).forEach(b => b.setAttribute('aria-pressed', b === btn));
      const f = btn.dataset.filter;
      let shown = 0;
      Array.from(list.children).forEach(el => {
        const hit = !f || el.dataset.tags.split('|').includes(f);
        el.hidden = !hit;
        shown += hit;
      });
      if (count) count.textContent = `${shown} ${noun}`;
    });
  });

  // YouTube: show the thumbnail, load the player only on click.
  $$('.yt').forEach(btn => btn.addEventListener('click', () => {
    const f = document.createElement('iframe');
    f.src = `https://www.youtube-nocookie.com/embed/${btn.dataset.id}?autoplay=1`;
    f.title = 'YouTube video';
    f.allow = 'accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture';
    f.allowFullscreen = true;
    const wrap = document.createElement('div');
    wrap.className = 'embed embed-wide';
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
