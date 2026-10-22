"""Build the portfolio site from content/ into _site/.

Usage: python3 build.py   (needs: pip install markdown)
"""
import html, os, re, shutil
import markdown

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "_site")
SITE_URL = "https://atienzaveejay.github.io"
BASE = ""  # set to "/repo-name" if this is ever served from a project page
EMAIL = "atienzaveejay@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/veejay-atienza/"
e = html.escape


# ---------- content loading ----------

def parse(path):
    """Split a content file into (meta dict, markdown body). Front matter is a tiny YAML subset."""
    text = open(path, encoding="utf-8").read()
    meta, body = {}, text
    if text.startswith("---\n"):
        head, body = text[4:].split("\n---", 1)
        key = None
        for line in head.split("\n"):
            if line.lstrip().startswith("#") or not line.strip():
                continue
            if line.startswith("  - ") and key:
                meta.setdefault(key, []).append(line[4:].strip())
            elif ":" in line:
                key, val = line.split(":", 1)
                key, val = key.strip(), val.strip()
                meta[key] = int(val) if val.isdigit() else (val or [])
    return meta, body.strip("\n")


def collection(folder):
    path = os.path.join(ROOT, "content", folder)
    items = []
    for name in os.listdir(path) if os.path.isdir(path) else []:
        if name.endswith(".md"):
            meta, body = parse(os.path.join(path, name))
            meta["slug"], meta["body"] = name[:-3], body
            if meta.get("draft") == "true":
                continue
            items.append(meta)
    return sorted(items, key=lambda m: m.get("order", 99))


def fields(s, n):
    parts = [p.strip() for p in s.split("|")]
    return parts + [""] * (n - len(parts))


def metric(s):
    return tuple(fields(s, 2)[:2])


def tags_of(item):
    return [t.strip() for t in str(item.get("tags", "")).split(",") if t.strip()]


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


# ---------- markdown ----------

def yt_id(url):
    m = re.search(r"(?:youtube\.com/(?:embed/|watch\?v=|shorts/)|youtu\.be/)([\w-]{11})", url)
    return m[1] if m else None


def embed(url, kind="video"):
    if kind == "short" and yt_id(url):
        vid = yt_id(url)
        return (f'<button type="button" class="embed embed-tall yt" data-id="{vid}" aria-label="Play Short">'
                f'<img src="https://i.ytimg.com/vi/{vid}/oar2.jpg" alt="" loading="lazy" onerror="this.onerror=null;this.src=\'https://i.ytimg.com/vi/{vid}/hqdefault.jpg\'">'
                f'<span class="play" aria-hidden="true"></span></button>')
    if url.endswith(".mp4"):
        return (f'<video class="embed-video" src="{e(url)}" controls playsinline preload="metadata"></video>')
    vid = yt_id(url)
    if vid:
        return (f'<button type="button" class="embed embed-wide yt" data-id="{vid}" aria-label="Play video">'
                f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="" loading="lazy">'
                f'<span class="play" aria-hidden="true"></span></button>')
    m = re.search(r"tiktok\.com/@[\w.]+/video/(\d+)", url)
    if m:
        return (f'<div class="embed embed-tall"><iframe src="https://www.tiktok.com/player/v1/{m[1]}?rel=0" '
                f'title="TikTok video" loading="lazy" allowfullscreen allow="encrypted-media; fullscreen"></iframe></div>')
    m = re.search(r"instagram\.com/(?:reel|p)/([\w-]+)", url)
    if m:
        return (f'<div class="embed embed-ig"><iframe src="https://www.instagram.com/reel/{m[1]}/embed/" '
                f'title="Instagram reel" loading="lazy" allowfullscreen></iframe></div>')
    clean = url.split("?")[0]
    label = "TikTok photo post" if "tiktok.com" in url else re.sub(r"^https?://(www\.)?", "", clean)
    return f'<a class="embed-link" href="{e(clean)}" target="_blank" rel="noopener">View {e(label)}</a>'


def bars(spec):
    """@[bars](Label=value; Label=value | caption). Values may carry units, e.g. 12.0% or 14,946."""
    rows, _, caption = spec.partition("|")
    items = []
    for part in rows.split(";"):
        if "=" in part:
            label, val = part.rsplit("=", 1)
            num = float(re.sub(r"[^0-9.]", "", val) or 0)
            items.append((label.strip(), val.strip(), num))
    top = max((n for *_, n in items), default=1) or 1
    html_rows = "".join(
        f'<div class="bar-row"><span class="bar-label">{e(l)}</span>'
        f'<span class="bar-track"><span class="bar-fill" style="width:{max(n / top * 100, 1.5):.1f}%"></span></span>'
        f'<span class="bar-val">{e(v)}</span></div>' for l, v, n in items)
    cap = f"<figcaption>{e(caption.strip())}</figcaption>" if caption.strip() else ""
    return f'<figure class="bars">{html_rows}{cap}</figure>'


def md(text, toc=False):
    text = re.sub(r"<details><summary>(.*?)</summary>", r'<details markdown="1"><summary>\1</summary>', text)
    text = re.sub(r"^@\[bars\]\((.+)\)$", lambda m: bars(m[1]), text, flags=re.M)
    text = re.sub(r"^@\[(\w+)\]\((.+?)\)$", lambda m: embed(m[2], m[1]), text, flags=re.M)
    conv = markdown.Markdown(extensions=["tables", "fenced_code", "md_in_html", "sane_lists", "toc"],
                             extension_configs={"toc": {"toc_depth": "2"}})
    out = conv.convert(text)
    out = out.replace("<img ", '<img loading="lazy" ')
    out = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', out)
    out = re.sub(r'(src|href)="/(?!/)', rf'\1="{BASE}/', out)
    if toc:
        heads = [(t["id"], re.sub(r"<[^>]+>", "", t["name"])) for t in conv.toc_tokens]
        return out, heads
    return out


def u(path):
    return BASE + path


def ext(href):
    return ' target="_blank" rel="noopener"' if href.startswith("http") else ""


# ---------- layout ----------

NAV = [("Work", "/work/"), ("Apps", "/apps/"), ("Video", "/video/"), ("Graphics", "/design/"),
       ("Writing", "/writing/"), ("About", "/about/")]
FOOTER_NAV = NAV
RESUME = "/assets/resume/Veejay-Atienza-Resume.pdf"
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
           "%3Crect width='64' height='64' rx='6' fill='%2315171a'/%3E%3Ctext x='32' y='44' font-family='Georgia,serif' "
           "font-size='34' font-weight='600' fill='%23fff' text-anchor='middle'%3EVA%3C/text%3E%3C/svg%3E")
THEME_BOOT = ("<script>try{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t}"
              "catch(e){}</script>")


def page(title, body, desc, path, active=None, image="/assets/home/01.webp", nav=None):
    nav_items = nav if nav is not None else NAV
    links = "".join(
        f'<a href="{u(href)}"{" aria-current=page" if label == active else ""}>{label}</a>' for label, href in nav_items)
    links_plain = "".join(f'<a href="{u(href)}">{label}</a>' for label, href in FOOTER_NAV)
    full_title = "Veejay Atienza, content and growth marketer" if title is None else f"{title} | Veejay Atienza"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE_URL}{u(image)}">
<meta property="og:url" content="{SITE_URL}{u(path)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{SITE_URL}{u(path)}">
<link rel="icon" href="{FAVICON}">
{THEME_BOOT}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400..800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{u('/style.css')}">
<script src="{u('/site.js')}" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="wordmark" href="{u('/')}">Veejay Atienza</a>
    <nav aria-label="Main" id="site-nav">{links}</nav>
    <div class="header-tools">
      <button type="button" class="search-btn" data-open-search aria-label="Search the site"><span class="search-ico" aria-hidden="true"></span><span class="search-label">Search</span><kbd>&#8984;K</kbd></button>
      <button type="button" class="theme-toggle" aria-label="Switch colour theme"><span aria-hidden="true"></span></button>
      <a class="header-email" href="{u(RESUME)}" target="_blank" rel="noopener">Resume</a>
    </div>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-inner">
    <p class="footer-id"><span>Veejay Atienza</span> <a href="mailto:{EMAIL}">{EMAIL}</a></p>
    <nav class="footer-nav" aria-label="Footer">{links_plain}<a href="{u(RESUME)}" target="_blank" rel="noopener">Resume</a><a href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a></nav>
  </div>
</footer>
<dialog class="lightbox" aria-label="Image preview">
  <img alt="">
  <button type="button" class="lb-close" aria-label="Close">Close</button>
  <button type="button" class="lb-prev" aria-label="Previous image">&larr;</button>
  <button type="button" class="lb-next" aria-label="Next image"></button>
</dialog>
<dialog class="finder" aria-label="Search">
  <div class="finder-box">
    <input type="search" placeholder="Search case studies, apps and writing" aria-label="Search" autocomplete="off">
    <ul class="finder-results" role="listbox"></ul>
    <p class="finder-hint"><kbd>&uarr;</kbd><kbd>&darr;</kbd> to move, <kbd>Enter</kbd> to open, <kbd>Esc</kbd> to close</p>
  </div>
</dialog>
<script>window.SITE_BASE = "{BASE}";</script>
</body>
</html>
"""


def write(path, content):
    if path.endswith(".html"):
        dest = os.path.join(OUT, path.strip("/"))
    else:
        dest = os.path.join(OUT, path.strip("/"), "index.html")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, "w", encoding="utf-8").write(content)


# ---------- shared pieces ----------

def metrics_row(items, cls="metrics"):
    cells = "".join(f'<div><dt>{e(v)}</dt><dd>{e(l)}</dd></div>' for v, l in map(metric, items))
    return f'<dl class="{cls}">{cells}</dl>'


def filter_bar(names, target):
    if len(names) < 2:
        return ""
    btns = "".join(f'<button type="button" data-filter="{e(n)}">{e(n)}</button>' for n in names)
    return (f'<div class="filters" role="group" aria-label="Filter" data-target="{target}">'
            f'<button type="button" data-filter="" aria-pressed="true">All</button>{btns}</div>')


def first_image(body):
    m = re.search(r"!\[[^\]]*\]\((.+?)\)", body)
    return m[1] if m else ""


def case_rows(work):
    rows = []
    for w in work:
        value, label = metric(w.get("card") or w["metrics"][0])
        rows.append(f"""<a class="case" href="{u('/work/' + w['slug'] + '/')}" data-tags="{e('|'.join(tags_of(w)))}">
  <div class="case-metric"><span class="num">{e(value)}</span><span class="lbl">{e(label)}</span></div>
  <div class="case-text"><h3>{e(w['title'])}</h3><p>{e(w['client'])}, {e(w['area'])}</p></div>
  {f'<img class="case-thumb" src="{u(w["cover"])}" alt="" loading="lazy">' if w.get('cover') else '<span class="case-thumb" aria-hidden="true"></span>'}
</a>""")
    return "".join(rows)


def app_cards(apps):
    if not apps:
        return ""
    def href_of(a):
        return u(f"/apps/{a['slug']}/") if a["body"].strip() else (a.get("url") or "")
    lead, rest = apps[0], apps[1:]
    h = href_of(lead)
    stats = metrics_row(lead["metrics"], "metrics metrics-compact") if lead.get("metrics") else ""
    out = f"""<a class="app-feature" href="{e(h)}"{ext(h)}>
  <img src="{u(lead['cover'])}" alt="" loading="lazy">
  <div class="app-text"><h3>{e(lead['title'])}</h3><p>{e(lead['summary'])}</p>{stats}<span class="more">Read about {e(lead['title'])}</span></div>
</a>"""
    cards = "".join(f"""<a class="app" href="{e(href_of(a))}"{ext(href_of(a))}>
  <h3>{e(a['title'])}</h3><p>{e(a['summary'])}</p>{f'<p class="app-stack">{e(a["stack"])}</p>' if a.get('stack') else ''}
</a>""" for a in rest)
    return out + (f'<div class="apps">{cards}</div>' if cards else "")


# ---------- pages ----------

def experience_list(home):
    if not home.get("experience"):
        return ""
    rows = "".join(
        f'<li><span class="xp-org">{e(o)}</span><span class="xp-role">{e(r)}</span><span class="xp-when">{e(d)}</span></li>'
        for o, r, d in (fields(x, 3)[:3] for x in home["experience"]))
    return f'<ul class="xp">{rows}</ul>'


def collage(images):
    imgs = "".join(f'<img src="{u(src)}" alt="" loading="lazy">' for src in images[:4])
    return f'<span class="collage">{imgs}</span>'


def build_home(home, about, work, apps, videos, designs, articles):
    focus = "".join(f"<li>{e(f)}</li>" for f in home["focus"])
    featured = [w for w in work if w.get("featured") == "true"] or work[:4]
    picks = [a for a in articles if a["section"] == "Interview Query"][:4] or articles[:4]
    writing_list = "".join(
        f'<li><a href="{e(a["url"])}" target="_blank" rel="noopener">{e(a["title"])}</a><span>{e(a["pub"])}</span></li>'
        for a in picks)
    lead_app = app_cards(apps[:1]) if apps else ""
    design_imgs = [d.get("cover") or first_image(d["body"]) for d in designs]
    video_imgs = [v["cover"] for v in videos if v.get("cover")]
    body = f"""
<section class="hero wrap">
  <div class="hero-text">
    <h1>{e(home['name'])}</h1>
    <p class="tagline">{e(home['tagline'])}</p>
    <p class="contact"><a class="btn" href="mailto:{home['email']}">Email me</a> <a class="text-link" href="{u('/work/')}">See the work</a> <a class="text-link" href="{u(RESUME)}" target="_blank" rel="noopener">Resume (PDF)</a></p>
  </div>
  <img class="hero-photo" src="{u(home['photo'])}" alt="Portrait of Veejay Atienza" width="640" height="960">
</section>

<section class="wrap highlights-wrap" aria-label="Highlights">
  {metrics_row(home['highlights'], 'highlights')}
</section>

<section class="wrap section">
  <div class="section-head"><h2>Selected case studies</h2><a href="{u('/work/')}">All {len(work)} case studies</a></div>
  <div class="cases">{case_rows(featured)}</div>
</section>

<section class="wrap section">
  <div class="section-head"><h2>Apps I've built</h2><a href="{u('/apps/')}">All {len(apps)} apps and tools</a></div>
  {lead_app}
</section>

<section class="wrap"><div class="home-contact">
  <div>
    <h2>About</h2>
    <p>{e(home.get('about_short', ''))}</p>
    <a class="text-link" href="{u('/about/')}">Experience and background</a>
  </div>
  <div>
    <h2>Get in touch</h2>
    <p>Open to content, growth and marketing roles, remote or Manila-based.</p>
    <p class="contact"><a class="btn" href="mailto:{home['email']}">Email me</a> <a class="text-link" href="{home['linkedin']}" target="_blank" rel="noopener">LinkedIn</a></p>
  </div>
</div></section>
"""
    write("/", page(None, body, home["tagline"], "/"))


def build_work_index(work, videos, designs):
    work_tags = list(dict.fromkeys(t for w in work for t in tags_of(w)))
    body = f"""
<div class="wrap page-head"><h1>Case studies</h1><p class="lede">Growth work across SEO, paid social, email, short-form video and AI systems. Each one covers the problem, what I did, the numbers, and what didn't work.</p></div>
<div class="wrap section writing-wrap">
  <div class="section-head"><span class="muted count" data-count-for="cases">{len(work)} case studies</span></div>
  {filter_bar(work_tags, 'cases')}
  <div class="cases" id="cases">{case_rows(work)}</div>
</div>
<section class="wrap section">
  <div class="section-head"><h2>Video and graphics</h2></div>
  <div class="duo">
    <a class="duo-card" href="{u('/video/')}">{collage([v["cover"] for v in videos if v.get("cover")])}<span class="tile-title">Video</span><span class="tile-sub">{len(videos)} sets: YouTube, TikTok, Reels and product videos</span></a>
    <a class="duo-card" href="{u('/design/')}">{collage([d.get("cover") or first_image(d["body"]) for d in designs])}<span class="tile-title">Graphics</span><span class="tile-sub">{len(designs)} sets: social graphics, thumbnails and print</span></a>
  </div>
</section>
"""
    write("/work/", page("Case studies", body, "Content and growth marketing case studies by Veejay Atienza.", "/work/", "Work"))


def build_apps_index(apps):
    body = f"""
<div class="wrap page-head"><h1>Apps and tools</h1><p class="lede">I build the software side too, mostly with Claude Code: a product of my own, internal tools, and the automations behind my marketing work.</p></div>
<div class="wrap section writing-wrap">{app_cards(apps)}</div>
"""
    write("/apps/", page("Apps and tools", body, "Apps and tools built by Veejay Atienza.", "/apps/", "Apps"))


def build_about(home, about):
    body = f"""
<div class="wrap page-head about-head">
  <div>
    <h1>About</h1>
    <p class="lede">{e(home['tagline'])}</p>
    <p class="contact"><a class="btn" href="mailto:{home['email']}">Email me</a> <a class="text-link" href="{u(RESUME)}" target="_blank" rel="noopener">Download my resume (PDF)</a> <a class="text-link" href="{home['linkedin']}" target="_blank" rel="noopener">LinkedIn</a></p>
  </div>
  <img class="about-photo" src="{u(home['photo'])}" alt="Portrait of Veejay Atienza" loading="lazy">
</div>
<section class="wrap section" id="experience">
  <h2>Experience</h2>
  {experience_list(home)}
</section>
<section class="wrap section about">
  <h2>More about me</h2>
  <div class="prose">{md(about)}</div>
</section>
"""
    write("/about/", page("About", body, home["tagline"], "/about/", "About"))


def plain(text):
    text = re.sub(r"```.*?```|<details.*?</details>|<[^>]+>|@\[\w+\]\(.*?\)|!\[[^\]]*\]\([^)]*\)", " ", text, flags=re.S)
    return re.sub(r"[#*>|`_\-]+|\s+", " ", text).strip()


def build_search(work, apps, articles):
    import json
    items = [dict(title=w["title"], sub=f'{w["client"]}, {w["area"]}', kind="Case study", url=u(f"/work/{w['slug']}/"),
                  text=" ".join(tags_of(w)) + " " + w["role"] + " " + plain(w["body"])[:1500]) for w in work]
    items += [dict(title=a["title"], sub=a["summary"], kind="App", url=u(f"/apps/{a['slug']}/") if a["body"].strip() else a.get("url", ""),
                   text=a.get("stack", "") + " " + plain(a["body"])[:1500]) for a in apps]
    items += [dict(title=a["title"], sub=f'{a["pub"]}' + (f', {a["date"]}' if a["date"] else ""), kind="Writing", url=a["url"],
                   text=a["note"] + " " + a["section"], ext=True) for a in articles]
    items += [dict(title=t, sub="Page", kind="Page", url=u(h), text="") for t, h in NAV]
    open(os.path.join(OUT, "search.json"), "w").write(json.dumps(items, ensure_ascii=False))


def reading_time(text):
    words = len(re.findall(r"\w+", re.sub(r"```.*?```|<details.*?</details>", "", text, flags=re.S)))
    return max(1, round(words / 230))


def related_block(item, pool, kind):
    tags = set(tags_of(item))
    scored = [(len(tags & set(tags_of(o))), o) for o in pool if o["slug"] != item["slug"]]
    picks = [o for s, o in sorted(scored, key=lambda x: (-x[0], x[1].get("order", 99))) if s][:3]
    if not picks:
        return ""
    cards = "".join(
        f'<a class="rel" href="{u(f"/{kind}/" + o["slug"] + "/")}"><span class="rel-num">{e(metric(o.get("card") or o["metrics"][0])[0])}</span>'
        f'<span class="rel-title">{e(o["title"])}</span><span class="rel-sub">{e(o.get("client", ""))}</span></a>'
        for o in picks if o.get("metrics"))
    return f'<section class="related" aria-label="More like this"><h2>More like this</h2><div class="rel-grid">{cards}</div></section>' if cards else ""


def detail_page(item, kind, prev, nxt, head_extra, crumb_href, crumb_label, active, related=""):
    content, heads = md(item["body"], toc=True)
    toc = ""
    if len(heads) >= 3 and len(plain(item["body"]).split()) > 1200:
        toc = '<nav class="toc" aria-label="On this page"><p>On this page</p><ol>' + "".join(
            f'<li><a href="#{i}">{e(t)}</a></li>' for i, t in heads) + "</ol></nav>"
    pager = '<nav class="pager" aria-label="More">'
    pager += (f'<a href="{u(f"/{kind}/" + prev["slug"] + "/")}"><span>Previous</span>{e(prev["title"])}</a>'
              if prev else "<span></span>")
    if nxt:
        pager += f'<a class="next" href="{u(f"/{kind}/" + nxt["slug"] + "/")}"><span>Next</span>{e(nxt["title"])}</a>'
    pager += "</nav>"
    cover = (f'<figure class="wrap case-cover"><img src="{u(item["cover"])}" alt=""></figure>'
             if item.get("cover") and item.get("cover_on_page") != "false" else '<div class="case-gap"></div>')
    return f"""
<article class="case-page">
  <header class="wrap case-head">
    <p class="crumb"><a href="{u(crumb_href)}">{crumb_label}</a> <span aria-hidden="true">/</span> {e(item.get('client') or item.get('stack', ''))}, {reading_time(item['body'])} min read</p>
    <h1>{e(item['title'])}</h1>
    {head_extra}
  </header>
  {cover}
  <div class="wrap case-body{' has-toc' if toc else ''}">
    {toc}
    <div class="prose">{content}</div>
  </div>
  <div class="wrap">{related}{pager}</div>
</article>
"""


def build_case(w, prev, nxt, work):
    head = f'<p class="role"><strong>Role.</strong> {e(w["role"])}</p>{metrics_row(w["metrics"])}'
    body = detail_page(w, "work", prev, nxt, head, "/work/", "Case studies", "Work", related_block(w, work, "work"))
    desc = f"{w['client']}: " + "; ".join(f"{v} {l}" for v, l in map(metric, w["metrics"]))
    write(f"/work/{w['slug']}/", page(w["title"], body, desc, f"/work/{w['slug']}/", "Work", w["cover"]))


def build_app(a, prev, nxt):
    links = []
    if a.get("url"):
        links.append(f'<a class="btn" href="{e(a["url"])}" target="_blank" rel="noopener">Visit the live site</a>')
    if a.get("repo"):
        links.append(f'<a class="btn btn-quiet" href="{e(a["repo"])}" target="_blank" rel="noopener">Source code</a>')
    head = (f'<p class="role">{e(a["summary"])}</p>'
            + (f'<p class="role"><strong>Built with.</strong> {e(a["stack"])}</p>' if a.get("stack") else "")
            + (metrics_row(a["metrics"]) if a.get("metrics") else "")
            + (f'<p class="contact app-links">{" ".join(links)}</p>' if links else ""))
    body = detail_page(a, "apps", prev, nxt, head, "/apps/", "Apps", "Apps")
    write(f"/apps/{a['slug']}/", page(a["title"], body, a["summary"], f"/apps/{a['slug']}/", "Apps", a.get("cover") or "/assets/home/01.webp"))


def jump_nav(items):
    return '<nav class="jump" aria-label="Jump to">' + "".join(
        f'<a href="#{i["slug"]}">{e(i["title"])}</a>' for i in items) + "</nav>"


def build_video(videos):
    sections = "".join(f"""
<section class="section" id="{v['slug']}">
  <div class="section-head"><h2>{e(v['title'])}</h2><span class="muted">{e(v['group'])}</span></div>
  {f'<p class="lede section-lede">{e(v["summary"])}</p>' if v.get('summary') else ''}
  {md(v['body']) if 'class="video-grid' in v['body'] else '<div class="video-grid">' + md(v['body']) + '</div>'}
</section>""" for v in videos)
    body = f"""
<div class="wrap page-head"><h1>Video</h1><p class="lede">Short-form and YouTube work across tech education, consumer apps and B2B.</p>{jump_nav(videos)}</div>
<div class="wrap">{sections}</div>
"""
    write("/video/", page("Video", body, "Video portfolio: YouTube, TikTok and Instagram work by Veejay Atienza.", "/video/", "Video"))


def build_design(designs):
    sections = []
    for d in designs:
        images = re.findall(r"!\[[^\]]*\]\((.+?)\)", d["body"])
        pdfs = re.findall(r"\[PDF: ([^\]]+)\]\((.+?)\)", d["body"])
        cls = "gallery gallery-print" if pdfs else "gallery"
        figs = "".join(
            f'<a href="{u(src)}" class="shot" data-group="{d["slug"]}"><img src="{u(src)}" alt="{e(d["title"])} design {n + 1}" loading="lazy"></a>'
            for n, src in enumerate(images))
        links = "".join(f'<a class="btn btn-quiet" href="{u(href)}" target="_blank" rel="noopener">Open the full PDF</a>' for _, href in pdfs)
        sections.append(f"""
<section class="section" id="{d['slug']}">
  <div class="section-head"><h2>{e(d['title'])}</h2><span class="muted">{e(d['group'])}</span></div>
  {f'<p class="lede section-lede">{e(d["summary"])}</p>' if d.get('summary') else ''}
  <div class="{cls}">{figs}</div>
  {f'<p>{links}</p>' if links else ''}
</section>""")
    body = f"""
<div class="wrap page-head"><h1>Graphics</h1><p class="lede">Social media graphics, YouTube thumbnails, ad creative and print layouts. Click any image to view it larger, then use the arrow keys.</p>{jump_nav(designs)}</div>
<div class="wrap">{''.join(sections)}</div>
"""
    write("/design/", page("Graphics", body, "Graphics portfolio: social media graphics, YouTube thumbnails, ads and print by Veejay Atienza.", "/design/", "Graphics"))


def load_articles():
    meta, _ = parse(os.path.join(ROOT, "content", "writing.md"))
    arts = []
    for line in meta.get("articles", []):
        title, url, pub, section, date, note = fields(line, 6)[:6]
        arts.append(dict(title=title, url=url, pub=pub, section=section, date=date, note=note))
    return meta, arts


def build_writing(meta, arts):
    sections = list(dict.fromkeys(a["section"] for a in arts))
    rows = "".join(
        f"""<li class="article" data-tags="{e(a['section'])}">
  <a href="{e(a['url'])}" target="_blank" rel="noopener"><span class="a-title">{e(a['title'])}</span><span class="a-note">{e(a['note'])}</span></a>
  <span class="a-meta">{e(a['pub'])}{(', ' + e(a['date'])) if a['date'] else ''}</span>
</li>""" for a in arts)
    body = f"""
<div class="wrap page-head"><h1>Writing</h1><p class="lede">{e(meta.get('intro', ''))}</p></div>
<div class="wrap section writing-wrap">
  <div class="section-head"><span class="muted count" data-count-for="articles">{len(arts)} pieces</span></div>
  <input type="search" class="list-search" data-target="articles" placeholder="Search {len(arts)} pieces by title or topic" aria-label="Search writing">
  {filter_bar(sections, 'articles')}
  <ul class="articles" id="articles">{rows}</ul>
</div>
"""
    write("/writing/", page("Writing", body, "Writing portfolio: articles, LinkedIn posts and ghostwriting by Veejay Atienza.", "/writing/", "Writing"))


def build_404():
    body = f'<div class="wrap page-head"><h1>Page not found</h1><p class="lede">That page moved or never existed. <a href="{u("/")}">Back to the homepage</a>.</p></div>'
    write("404.html", page("Not found", body, "Page not found", "/404.html"))


def build_sitemap(paths):
    urls = "".join(f"<url><loc>{SITE_URL}{u(p)}</loc></url>" for p in paths)
    open(os.path.join(OUT, "sitemap.xml"), "w").write(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}{u('/sitemap.xml')}\n")


def build_hire(pages):
    """Focused pages linked from job applications (not in the nav): the best video or graphics work first."""
    for h in pages:
        body = f"""
<div class="wrap page-head"><h1>{e(h['title'])}</h1><p class="lede">{e(h['lede'])}</p>
<p><a class="btn" href="mailto:{EMAIL}">Email me</a></p></div>
<div class="wrap hire">{md(h['body'])}</div>
"""
        write(h["path"], page(h["title"], body, h["desc"], h["path"], h.get("active")))


def main():
    os.makedirs(OUT, exist_ok=True)
    for name in os.listdir(OUT):  # empty it in place so a running preview server keeps working
        target = os.path.join(OUT, name)
        shutil.rmtree(target) if os.path.isdir(target) else os.remove(target)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "assets"))
    for f in ("style.css", "site.js"):
        shutil.copy(os.path.join(ROOT, f), OUT)
    open(os.path.join(OUT, ".nojekyll"), "w").close()

    home, about = parse(os.path.join(ROOT, "content", "home.md"))
    work, apps = collection("work"), collection("apps")
    videos, designs = collection("video"), collection("design")
    hire = collection("hire")
    writing_meta, articles = load_articles()

    build_home(home, about, work, apps, videos, designs, articles)
    for i, w in enumerate(work):
        build_case(w, work[i - 1] if i else None, work[i + 1] if i + 1 < len(work) else None, work)
    detailed = [a for a in apps if a["body"].strip()]
    for i, a in enumerate(detailed):
        build_app(a, detailed[i - 1] if i else None, detailed[i + 1] if i + 1 < len(detailed) else None)
    build_work_index(work, videos, designs)
    build_apps_index(apps)
    build_about(home, about)
    build_search(work, apps, articles)
    build_video(videos)
    build_design(designs)
    build_hire(hire)
    build_writing(writing_meta, articles)
    build_404()
    build_sitemap(["/", "/work/", "/apps/", "/about/", "/video/", "/design/", "/writing/"] + [h["path"] for h in hire] + [f"/work/{w['slug']}/" for w in work]
                  + [f"/apps/{a['slug']}/" for a in detailed])
    print(f"Built {len(work)} case studies, {len(apps)} apps, {len(videos)} video sets, "
          f"{len(designs)} design sets, {len(articles)} articles into _site/")


if __name__ == "__main__":
    main()
