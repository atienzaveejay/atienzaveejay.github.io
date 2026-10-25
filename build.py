"""Build the portfolio site from content/ into _site/.

Usage: python3 build.py   (needs: pip install markdown)
"""
import html, os, re, shutil, urllib.parse
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
        poster = url[:-4] + ".jpg"  # a same-name .jpg next to the video becomes its cover
        poster_attr = f' poster="{e(poster)}"' if os.path.exists(os.path.join(ROOT, poster.lstrip("/"))) else ""
        return f'<video class="embed-video" src="{e(url)}"{poster_attr} controls playsinline preload="metadata"></video>'
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


def clip(spec, kind):
    """@[short](url | caption): the embed with a caption under it; without a caption, just the embed."""
    url, _, caption = spec.partition(" | ")
    if not caption.strip():
        return embed(url.strip(), kind)
    cap = markdown.markdown(caption.strip())[3:-4]  # inline markdown, minus the <p> wrapper
    return f'<figure class="clip">{embed(url.strip(), kind)}<figcaption>{cap}</figcaption></figure>'


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
    text = re.sub(r"^@\[(\w+)\]\((.+?)\)$", lambda m: clip(m[2], m[1]), text, flags=re.M)
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

NAV = [("Video", "/video-editing/"), ("Graphics", "/graphics/"), ("Social", "/social-media/"),
       ("Growth", "/growth/"), ("About", "/about/")]
FOOTER_NAV = NAV + [("Case studies", "/work/"), ("All video", "/video/"), ("All graphics", "/design/"),
                    ("Apps", "/apps/"), ("Writing", "/writing/")]
# Every "Start a project" button opens an email with the brief questions filled in (the site is static, no form backend).
BRIEF = f"mailto:{EMAIL}?" + urllib.parse.urlencode({
    "subject": "Project enquiry",
    "body": "Hi Veejay,\n\nWhat I need:\nHow many, or how often:\nDeadline:\nBudget:\nLinks to examples I like:\n\nThanks,\n"},
    quote_via=urllib.parse.quote)
SERVICES = [
    dict(name="Video editing", path="/video-editing/", price="From USD 25 per Short",
         line="Shorts, Reels and TikToks, YouTube videos, real estate videos and ads, cut from your raw footage."),
    dict(name="Graphics", path="/graphics/", price="From USD 10 per post",
         line="Social posts, carousels, Pinterest pins and YouTube thumbnails that stay on brand."),
    dict(name="Social media", path="/social-media/", price="From USD 600 a month",
         line="Planning, posts, Shorts and scheduling across your channels, plus replies to comments and messages."),
    dict(name="Growth marketing", path="/growth/", price="From USD 1,200 a month",
         line="SEO and content, Meta and Google ads, email and the reporting that ties them to revenue."),
]
CLIENTS = ["Interview Query", "Winning Coaching", "ROO", "YourLifeChoices", "Leaders In Transition",
           "Storyseller Systems", "Kelly Technology", "PilotTV"]
STEPS = [
    ("Send the brief", "Tell me what you need, how often, your deadline and budget. Share footage or examples with a Drive, Dropbox or WeTransfer link."),
    ("Get the first version", "I confirm the timeline before I start, then send the first cut or the first designs."),
    ("Revise and publish", "Leave notes with timestamps or comments. I fix each one, and I can post it for you too."),
]
FAQ = [
    ("Where are you based?", "Manila, GMT+8. My mornings overlap with Australia, and my evenings with the US and UK workday."),
    ("How do I send footage?", "A Google Drive, Dropbox or WeTransfer link is fine, including large raw files."),
    ("How fast is turnaround?", "It depends on length and volume. Tell me your deadline and I'll confirm it before I start."),
    ("Can I try you first?", "Yes. I'm happy to do a paid test edit or design on your own material first."),
    ("What tools do you use?", "DaVinci Resolve and CapCut for video, Canva for graphics, Meta Business Suite, YouTube Studio and TikTok for posting, and GA4, Search Console, Meta Ads Manager and Google Ads for growth work."),
]


def process_block():
    steps = "".join(f'<li><h3>{e(t)}</h3><p>{e(d)}</p></li>' for t, d in STEPS)
    return f'<section class="wrap section"><h2>How it works</h2><ol class="steps">{steps}</ol></section>'


def faq_block():
    items = "".join(f'<details class="faq-item"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in FAQ)
    return f'<section class="wrap section"><h2>Questions</h2><div class="faq">{items}</div></section>'


def cta_block(title="Tell me what you need"):
    return (f'<section class="wrap"><div class="cta-band"><h2>{e(title)}</h2>'
            f'<p>Send a short brief and I\'ll reply with a plan and a price.</p>'
            f'<a class="btn" href="{BRIEF}">Start a project</a></div></section>')
RESUME = "/assets/resume/Veejay-Atienza-Resume.pdf"
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
           "%3Crect width='64' height='64' rx='6' fill='%230e0f0c'/%3E%3Ctext x='32' y='44' font-family='Georgia,serif' "
           "font-size='34' font-weight='600' fill='%23c6f432' text-anchor='middle'%3EVA%3C/text%3E%3C/svg%3E")
THEME_BOOT = ("<script>try{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t}"
              "catch(e){}</script>")


MENU = [
    ("Growth", [("Growth marketing", "/growth/", "Strategy, reporting and the work itself"), ("SEO and content", "/growth/", "Articles and guides that rank"),
                ("Meta and Google ads", "/growth/", "Tracking, audiences and creative"), ("Email and reporting", "/growth/", "Newsletters and weekly numbers")]),
    ("Content", [("Video editing", "/video-editing/", "Shorts, YouTube, real estate, ads"), ("Graphics", "/graphics/", "Posts, carousels, pins, thumbnails"),
                 ("Social media management", "/social-media/", "Plan, post and reply")]),
    ("Design", [("Websites and UI", "/ui-design/", "Shopify stores to sales pages"), ("Pitch decks and media kits", "/decks/", "Slides, PowerPoint or PDF")]),
]


def header_html():
    cols = "".join(
        f'<div><h3 class="mono">{e(group)}</h3><ul>' + "".join(
            f'<li><a href="{u(href)}">{e(name)} <small>{e(price)}</small></a></li>' for name, href, price in items)
        + "</ul></div>" for group, items in MENU)
    return f"""<header class="site-header">
  <div class="wrap header-inner">
    <a class="wordmark" href="{u('/')}">Veejay Atienza<span>.</span></a>
    <nav class="nav" id="nav" aria-label="Main">
      <button type="button" aria-expanded="false" aria-controls="mega" id="services-btn">Services</button>
      <a href="{u('/work/')}">Work</a>
      <a href="{u('/about/')}">About</a>
      <div class="mega" id="mega">
        <div class="wrap mega-inner">
          {cols}
          <div class="mega-proof">
            <span class="mono" style="color:var(--muted)">Interview Query, SEO and content</span>
            <strong>$569K+</strong>
            <p>revenue from content</p>
            <a class="link" href="{u('/work/interview-query-seo/')}">Read the case study</a>
          </div>
        </div>
      </div>
    </nav>
    <button type="button" class="menu-toggle" aria-expanded="false" aria-controls="nav" id="menu-btn">Menu</button>
    <a class="btn btn-small" href="{BRIEF}">Start a project</a>
  </div>
</header>"""


def footer_html():
    groups = [("Services", [(n, h) for _, items in MENU for n, h, _ in items if not n.startswith(("SEO", "Meta", "Email"))]),
              ("Work", [("All work", "/work/"), ("Case studies", "/work/#growth"), ("All video", "/video/"),
                        ("All graphics", "/design/"), ("Apps", "/apps/"), ("Writing", "/writing/")]),
              ("About", [("About me", "/about/"), ("Resume (PDF)", RESUME), ("LinkedIn", LINKEDIN), (EMAIL, "mailto:" + EMAIL)])]
    cols = "".join(f'<div><h3 class="mono">{e(t)}</h3>' + "".join(
        f'<a href="{h if h.startswith(("http", "mailto")) else u(h)}"{ext(h)}>{e(n)}</a>' for n, h in links) + "</div>"
        for t, links in groups)
    return f"""<footer>
  <div class="wrap foot">
    <div class="foot-cta"><p class="foot-big">Got footage? Need <em>customers?</em></p><a class="btn" href="{BRIEF}">Start a project <span class="arrow">&rarr;</span></a></div>
    <nav class="foot-cols" aria-label="Footer">{cols}</nav>
  </div>
  <div class="wrap foot-base"><span>&copy; Veejay Atienza, Manila</span><span>Growth marketing + content creation</span></div>
</footer>"""


def page(title, body, desc, path, active=None, image="/assets/home/01.webp", nav=None, body_class=""):
    full_title = "Veejay Atienza, growth marketing and content creation" if title is None else f"{title} | Veejay Atienza"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#0e0f0c">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE_URL}{u(image)}">
<meta property="og:url" content="{SITE_URL}{u(path)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{SITE_URL}{u(path)}">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{u('/style.css')}">
<script src="{u('/site.js')}" defer></script>
</head>
<body class="{body_class}">
<a class="skip" href="#main">Skip to content</a>
{header_html()}
<main id="main">
{body}
</main>
{footer_html()}
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


def website_cards():
    """Live sites first, then the concept sites, read from the UI Design page so every list shows the same name and line."""
    src = open(os.path.join(ROOT, "content", "hire", "ui-design.md"), encoding="utf-8").read()
    out = []
    for href, img, name, desc in re.findall(
            r'<a class="concept-card" href="([^"]+)"><img src="([^"]+)"[^>]*><strong>([^<]+)</strong><span>([^<]+)</span></a>', src):
        live = href.startswith("#")
        out.append(dict(href=u("/ui-design/" + href) if live else u(href), img=img, name=html.unescape(name),
                        desc=html.unescape(desc), live=live))
    return out


def concept_card(c):
    return (f'<a class="concept-card" href="{e(c["href"])}"><img src="{e(u(c["img"]))}" alt="{e(c["name"])} homepage" loading="lazy">'
            f'<strong>{e(c["name"])}</strong><span>{e(c["desc"])}</span></a>')


def build_home(home, about, work, apps, videos, designs, articles):
    """The homepage markup lives in content/home.html (sections, copy and links); the drifting reel and grids fill in from site.js."""
    body = open(os.path.join(ROOT, "content", "home.html"), encoding="utf-8").read().replace("{BRIEF}", BRIEF)
    sites = website_cards()
    picks = [c for c in sites if c["live"]][:3] + [c for c in sites if not c["live"]][:3]
    body = re.sub(r'<div class="wgrid">.*?</div>', '<div class="concept-grid">' + "".join(map(concept_card, picks)) + "</div>", body, count=1, flags=re.S)
    write("/", page(None, body, "Growth marketing and content creation by Veejay Atienza: SEO, ads, email, video editing, graphics, social media and web design.", "/", body_class="home"))


# Work library: every piece has one or more types and one or more industries; the two filters combine.
TYPES = [("content", "Content", [("short", "Short-form video"), ("long", "Long-form video"), ("video-ads", "Video ads"), ("graphics", "Graphics")]),
         ("growth", "Growth", [("seo", "SEO"), ("paid-ads", "Paid ads"), ("email", "Email"), ("social", "Social growth")]),
         ("design", "Design", [("websites", "Websites"), ("decks", "Decks")])]
INDUSTRIES = [("coaching", "Coaching"), ("careers", "Careers and recruiting"), ("real-estate", "Real estate"), ("beauty", "Beauty and wellness"),
              ("ecommerce", "E-commerce"), ("tech-b2b", "Tech and B2B"), ("media", "Media and entertainment"), ("local", "Local business")]
TYPE_LABEL = {k: v for _, _, ts in TYPES for k, v in ts}
IND_LABEL = dict(INDUSTRIES)
CASE_TAGS = {  # slug: (types, industries)
    "interview-query-seo": (["seo"], ["careers"]), "roo-seo": (["seo"], ["ecommerce"]),
    "storyseller-meta-ads": (["paid-ads"], ["tech-b2b"]), "stem-meta-ads": (["paid-ads"], ["ecommerce"]),
    "kelly-app": (["paid-ads"], ["tech-b2b"]), "fish-brand-teach-first": (["paid-ads", "social"], ["ecommerce"]),
    "ylc-newsletter": (["email"], ["media"]), "ylc-ai-prompts": (["email"], ["media"]), "outreach-audit": (["email"], ["ecommerce"]),
    "roo-tiktok-carousel": (["social"], ["ecommerce"]), "interview-query-linkedin": (["social"], ["careers"]),
    "interview-query-reddit": (["social"], ["careers"]), "interview-query-youtube": (["social"], ["careers"])}
SITE_IND = {"ROO": "ecommerce", "Winning Coaching": "coaching", "Connections Consulting Partners": "careers", "Kareera": "careers",
            "/concepts/real-estate/": "real-estate", "/concepts/saas/": "tech-b2b", "/concepts/skincare/": "ecommerce"}
DECK_IND = {"Kareera media kit": "careers", "Kareera partnership deck": "careers", "Kitchen brand Meta ads plan": "ecommerce"}


GRAPHICS = []


def library_items(work, designs):
    """Everything on one wall, woven so the unfiltered view mixes growth, content and design."""
    GRAPHICS.clear()
    cases = []
    for w in work:
        value, _ = metric(w.get("card") or w["metrics"][0])
        types, inds = CASE_TAGS.get(w["slug"], (["social"], []))
        cases.append(dict(types=types, inds=inds, kind="case", href=u(f"/work/{w['slug']}/"), thumb=w.get("cover", ""),
                          title=w["title"], meta=w["client"], metric=value, ratio="r-43"))
    def yt(i, who, tall, ind):
        return dict(types=["short" if tall else "long"], inds=[ind], kind="yt",
                    href=f"https://www.youtube.com/{'shorts/' if tall else 'watch?v='}{i}",
                    thumb=f"https://i.ytimg.com/vi/{i}/{'oar2' if tall else 'hqdefault'}.jpg",
                    fallback=f"https://i.ytimg.com/vi/{i}/hqdefault.jpg", title=who,
                    meta="YouTube Short" if tall else "YouTube video", ratio="r-916" if tall else "r-169")
    def mp4(src, who, typ, ind, meta, ratio="r-916"):
        return dict(types=[typ], inds=[ind], kind="mp4", href=u(src), src=u(src), thumb=u(src[:-4] + ".jpg"),
                    title=who, meta=meta, ratio=ratio)
    def img(src, who, meta, ratio, typ, ind, href=None):
        return dict(types=[typ], inds=[ind] if ind else [], kind="img", href=href or u(src), thumb=u(src),
                    title=who, meta=meta, ratio=ratio)
    content = [
        mp4("/assets/real-estate/guess-the-price.mp4", "Guess the price", "short", "real-estate", "Real estate reel"),
        yt("bMklmLvtEqU", "Coach Edwin Soriano", True, "coaching"), yt("MJj1i-smWm8", "Interview Query", False, "careers"),
        mp4("/assets/beauty/brow-before-after.mp4", "Brow and lash before and after", "short", "beauty", "Spec Reel, stock footage"),
        mp4("/assets/roo-video/ad-three-years.mp4", "ROO", "video-ads", "ecommerce", "Meta video ad, hook: 'the smartest kitchen tool I own'"),
        img("/assets/thumbnails/02.webp", "Interview Query thumbnail", "YouTube thumbnail", "r-169", "graphics", "careers"),
        yt("eXhYwjnaA2o", "Kate Lewis", True, "careers"),
        mp4("/assets/real-estate/pov-keys.mp4", "POV: you just got the keys", "short", "real-estate", "Real estate reel"),
        img("/assets/roo-tiktok/slide-1.webp", "ROO TikTok carousel", "Carousel", "r-916", "graphics", "ecommerce"),
        mp4("/assets/beauty/skincare-ugc-ad.mp4", "Skincare UGC ad", "video-ads", "beauty", "Spec ad for a sample brand, stock footage"),
        yt("vL4Zw3YUjTY", "Coach Edwin Soriano, sales video", False, "coaching"), yt("uraRYBQaydw", "Coach Edwin Soriano", True, "coaching"),
        mp4("/assets/real-estate/listing-film.mp4", "Listing film", "long", "real-estate", "Narrated walkthrough", "r-169"),
        mp4("/assets/roo-video/ad-most-satisfying.mp4", "ROO", "video-ads", "ecommerce", "Meta video ad, hook: 'the most satisfying...'"),
        img("/assets/roo-pins/01.webp", "ROO Pinterest pin", "Pinterest pin", "r-23", "graphics", "ecommerce"),
        yt("_kA2zVr5djM", "Kate Lewis", True, "careers"),
        mp4("/assets/real-estate/just-listed.mp4", "Just listed", "short", "real-estate", "Real estate reel"),
        mp4("/assets/beauty/brow-lamination-tips.mp4", "3 things to know before a brow lamination", "short", "beauty", "Spec Reel, stock footage"),
        img("/assets/thumbnails/03.webp", "Interview Query thumbnail", "YouTube thumbnail", "r-169", "graphics", "careers"),
        yt("xC2PH0EtLI4", "Coach Edwin Soriano", True, "coaching"),
        mp4("/assets/roo-video/reel-20-second-cleanup.mp4", "ROO", "short", "ecommerce", "Organic Reel"),
        yt("0UyvI__eqmg", "Coach Edwin Soriano", False, "coaching"),
        mp4("/assets/real-estate/neighbourhood-coogee.mp4", "Neighbourhood spotlight", "short", "real-estate", "Real estate reel"),
        img("/assets/roo-pins/02.webp", "ROO Pinterest pin", "Pinterest pin", "r-23", "graphics", "ecommerce"),
        yt("nwHHkEbal_Q", "Kate Lewis", True, "careers"),
        mp4("/assets/roo-video/ad-nobody-told-me.mp4", "ROO", "video-ads", "ecommerce", "Meta video ad, hook: 'Why did nobody tell me...'"),
        img("/assets/thumbnails/05.webp", "Interview Query thumbnail", "YouTube thumbnail", "r-169", "graphics", "careers"),
        yt("cLDtFwbElTo", "Coach Edwin Soriano", True, "coaching"), yt("pmVLbOqVOYs", "Kate Lewis, Leaders In Transition", False, "careers"),
        mp4("/assets/roo-video/reel-tomato-tips.mp4", "ROO", "short", "ecommerce", "Organic Reel"),
        mp4("/assets/beauty/grwm.mp4", "Get ready with me", "short", "beauty", "Spec Reel, stock footage"),
        img("/assets/roo-tiktok/slide-3.webp", "ROO TikTok carousel", "Carousel", "r-916", "graphics", "ecommerce"),
        img("/assets/thumbnails/07.webp", "Interview Query thumbnail", "YouTube thumbnail", "r-169", "graphics", "careers"),
        img("/assets/roo-pins/03.webp", "ROO Pinterest pin", "Pinterest pin", "r-23", "graphics", "ecommerce"),
        img("/assets/thumbnails/11.webp", "Sports channel thumbnail", "YouTube thumbnail", "r-169", "graphics", "media"),
        img("/assets/thumbnails/12.webp", "Sports channel thumbnail", "YouTube thumbnail", "r-169", "graphics", "media"),
    ]
    thumb_ind = {**{n: "careers" for n in (1, 2, 3, 4, 5, 7)}, 14: "ecommerce", 15: "ecommerce"}
    graphics = [img(f"/assets/thumbnails/{n:02d}.webp", "Interview Query thumbnail" if thumb_ind.get(n) == "careers" else "YouTube thumbnail",
                    "YouTube thumbnail", "r-169", "graphics", thumb_ind.get(n, "media")) | {"gfx": "thumbnails"}
                for n in range(1, 20) if n != 10]
    graphics += [img(f"/assets/roo-tiktok/slide-{n}.webp", "ROO TikTok carousel", f"Carousel, slide {n} of 6", "r-916", "graphics", "ecommerce") | {"gfx": "carousels"} for n in range(1, 7)]
    graphics += [img(f"/assets/roo-pins/{n:02d}.webp", "ROO Pinterest pin", "Pinterest pin", "r-23", "graphics", "ecommerce") | {"gfx": "pins"} for n in range(1, 7)]
    for slug, title, ind in (("esports", "E-sports team", "media"), ("fashion", "Fashion brand", "ecommerce"),
                             ("school", "School organisation", "local"), ("accounting", "Accounting firm", "local")):
        for f in sorted(os.listdir(os.path.join(ROOT, "assets", slug)))[:3]:
            graphics.append(img(f"/assets/{slug}/{f}", title, "Social media post", "r-11", "graphics", ind) | {"gfx": "social-posts"})
    GRAPHICS.extend(graphics)
    design = []
    for c in website_cards():
        key = c["name"] if c["live"] else c["href"].replace(BASE, "")
        ind = SITE_IND.get(key, "" if c["live"] else "local")
        design.append(dict(types=["websites"], inds=[ind] if ind else [], kind="img", href=c["href"], thumb=u(c["img"]),
                           title=c["name"], meta=c["desc"], ratio="r-169", site="live" if c["live"] else "concept", card=c))
    for d in designs:
        if d.get("group") == "Decks":
            cover = d.get("cover") or first_image(d["body"])
            if cover:
                design.append(img(cover, d["title"], "Deck", "r-169", "decks", DECK_IND.get(d["title"], "tech-b2b"), u("/decks/")) | {"gfx": "decks"})
    out, ci, ki, di = [], 0, 0, 0
    while ci < len(content) or ki < len(cases) or di < len(design):
        if ki < len(cases): out.append(cases[ki]); ki += 1
        for _ in range(3):
            if ci < len(content): out.append(content[ci]); ci += 1
        if di < len(design): out.append(design[di]); di += 1
    return out


def lib_card(it, attrs_extra, tag):
    """One library card: a playable mp4, a YouTube link, an image that opens in the lightbox, or a case study."""
    if it["kind"] == "mp4":
        media = (f'<video muted loop playsinline preload="none" poster="{e(it["thumb"])}" data-src="{e(it["src"])}"></video>'
                 '<span class="play" aria-hidden="true"></span>')
    else:
        fb = f' onerror="this.onerror=null;this.src=\'{it["fallback"]}\'"' if it.get("fallback") else ""
        media = f'<img src="{e(it["thumb"])}" alt="" loading="lazy"{fb}>' + ('<span class="play" aria-hidden="true"></span>' if it["kind"] == "yt" else "")
    top = f'<span class="metric">{e(it["metric"])}</span>' if it["kind"] == "case" else ""
    attrs = f' href="{e(it["href"])}"' + (' target="_blank" rel="noopener"' if it["kind"] == "yt" else "")
    shot = it["kind"] == "img" and it["href"] == it["thumb"]
    cls = f'item {it["ratio"]} k-{it["kind"]}' + (" shot" if shot else "")
    grp = ' data-group="library"' if shot else ""
    hover = " data-hover" if it["kind"] == "mp4" else ""
    return (f'<a class="{cls}"{attrs_extra}{attrs}{grp}{hover}><div class="media">{media}</div><div class="cap">{top}'
            f'<span class="mono">{e(tag)}</span><strong>{e(it["title"])}</strong><small>{e(it["meta"])}</small></div></a>')


def build_work_index(work, videos, designs):
    items = library_items(work, designs)
    chip = lambda axis, v, label: f'<button type="button" class="chip" data-axis="{axis}" data-v="{v}" aria-pressed="false">{e(label)} <span></span></button>'
    type_rail = chip("type", "all", "All types") + "".join(
        f'<div class="rail-sub"><span class="mono">{e(gl)}</span>{chip("type", g, "All " + gl.lower())}'
        + "".join(chip("type", k, lab) for k, lab in ts if any(k in i["types"] for i in items)) + "</div>"
        for g, gl, ts in TYPES)
    ind_rail = chip("ind", "all", "All industries") + "".join(
        chip("ind", k, lab) for k, lab in INDUSTRIES if any(k in i["inds"] for i in items))
    groups = {k: g for g, _, ts in TYPES for k, _ in ts}
    cards = []
    for it in items:
        tag = ", ".join(TYPE_LABEL[t] for t in it["types"])
        if it["inds"]:
            tag += " / " + ", ".join(IND_LABEL[i] for i in it["inds"])
        if it["kind"] == "mp4":
            media = (f'<video muted loop playsinline preload="none" poster="{e(it["thumb"])}" data-src="{e(it["src"])}"></video>'
                     '<span class="play" aria-hidden="true"></span>')
        else:
            fb = f' onerror="this.onerror=null;this.src=\'{it["fallback"]}\'"' if it.get("fallback") else ""
            media = f'<img src="{e(it["thumb"])}" alt="" loading="lazy"{fb}>' + ('<span class="play" aria-hidden="true"></span>' if it["kind"] == "yt" else "")
        top = f'<span class="metric">{e(it["metric"])}</span>' if it["kind"] == "case" else ""
        attrs = f' href="{e(it["href"])}"' + (' target="_blank" rel="noopener"' if it["kind"] == "yt" else "")
        cls = f'item {it["ratio"]} k-{it["kind"]}' + (" shot" if it["kind"] == "img" and it["href"] == it["thumb"] else "")
        grp = ' data-group="library"' if " shot" in cls else ""
        hover = " data-hover" if it["kind"] == "mp4" else ""
        tgroups = " ".join(sorted({groups[t] for t in it["types"]} | ({"video"} if set(it["types"]) & {"short", "long", "video-ads"} else set())))
        cards.append(f'<a class="{cls}" data-type="{" ".join(it["types"])} {tgroups}" data-ind="{" ".join(it["inds"])}"{attrs}{grp}{hover}>'
                     f'<div class="media">{media}</div><div class="cap">{top}<span class="mono">{e(tag)}</span>'
                     f'<strong>{e(it["title"])}</strong><small>{e(it["meta"])}</small></div></a>')
    body = f"""
<div class="wrap page-head"><span class="crumb">Work</span><h1>Everything I've made, in one place</h1>
<p class="lede">Filter by type, by industry, or both. Every filtered view has its own link you can share.</p></div>
<section class="wrap lib" id="library">
  <div class="lib-body">
    <aside class="rail" aria-label="Filter the work">
      <div class="rail-group"><span class="mono rail-title">Type</span>{type_rail}</div>
      <div class="rail-group"><span class="mono rail-title">Industry</span>{ind_rail}</div>
    </aside>
    <div><div class="lib-status"><p class="count mono" aria-live="polite">{len(items)} pieces</p><button type="button" class="clear-filters" hidden>Clear filters</button></div>
    <div class="lib-grid">{''.join(cards)}</div>
    <p class="lib-empty" hidden>Nothing in this combination yet. <a href="{BRIEF}">Ask me about it</a>.</p></div>
  </div>
</section>
"""
    write("/work/", page("Work", body, "All of Veejay Atienza's work, filterable by type (short-form, long-form, ads, graphics, websites, SEO, email) and by industry.", "/work/", "Work"))


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
{subnav([("more", "More of my work"), ("experience", "Experience"), ("about-me", "More about me")])}
<section class="wrap section" id="more">
  <h2>More of my work</h2>
  <p class="about-links"><a href="{u('/work/')}">Case studies</a> <a href="{u('/video/')}">All video</a> <a href="{u('/design/')}">All graphics</a> <a href="{u('/apps/')}">Apps I've built</a> <a href="{u('/writing/')}">Writing</a> <a href="{u(RESUME)}" target="_blank" rel="noopener">Resume (PDF)</a></p>
</section>
<section class="wrap section" id="experience">
  <h2>Experience</h2>
  {experience_list(home)}
</section>
<section class="wrap section about" id="about-me">
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
  {subnav(heads)}
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
    body = detail_page(w, "work", prev, nxt, head, "/work/#growth", "Case studies", "Work", related_block(w, work, "work"))
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


def subnav(links):
    """Sticky 'On this page' bar under the header; site.js highlights the section in view."""
    if len(links) < 2:
        return ""
    return ('<nav class="subnav" aria-label="On this page"><div class="wrap subnav-inner"><span class="mono">On this page</span>'
            + "".join(f'<a href="#{i}" title="{e(t)}">{e(short_label(t))}</a>' for i, t in links) + '</div></nav>')


def short_label(t):
    """'Challenge: Selling Something...' -> 'Challenge'; 'ROO, a Shopify store...' -> 'ROO'."""
    for sep in (":", ","):
        if sep in t and len(t) > 26:
            t = t.split(sep)[0]
    return t if len(t) <= 34 else t[:32].rsplit(" ", 1)[0] + "..."


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
<div class="wrap page-head"><span class="crumb"><a href="{u('/work/')}">Work</a> / All video</span><h1>Video</h1><p class="lede">Short-form and YouTube work across tech education, consumer apps and B2B.</p></div>
{subnav([(v['slug'], v['title']) for v in videos])}
<div class="wrap">{sections}</div>
"""
    write("/video/", page("Video", body, "Video portfolio: YouTube, TikTok and Instagram work by Veejay Atienza.", "/video/", "Video"))


def build_design(designs):
    sections = []
    for d in designs:
        images = re.findall(r"!\[[^\]]*\]\((.+?)\)", d["body"])
        pdfs = re.findall(r"\[PDF: ([^\]]+)\]\((.+?)\)", d["body"])
        cls = "gallery gallery-decks" if d.get("group") == "Decks" else "gallery gallery-print" if pdfs else "slides-row" if d.get("group") == "Carousels" else "gallery"
        figs = "".join(
            f'<a href="{u(src)}" class="shot" data-group="{d["slug"]}"><img src="{u(src)}" alt="{e(d["title"])} design {n + 1}" loading="lazy"></a>'
            for n, src in enumerate(images))
        links = "".join(f'<a class="btn btn-quiet" href="{u(href)}" target="_blank" rel="noopener">Open the full PDF</a>' for _, href in pdfs)
        sections.append((d.get("group", "Other"), f"""
<section class="section set" id="{d['slug']}">
  <div class="section-head"><h3>{e(d['title'])}</h3></div>
  {f'<p class="lede section-lede">{e(d["summary"])}</p>' if d.get('summary') else ''}
  <div class="{cls}">{figs}</div>
  {f'<p>{links}</p>' if links else ''}
</section>"""))
    order = ["Carousels", "Pinterest", "Social media", "Thumbnails", "Decks", "Print"]
    groups = order + sorted({g for g, _ in sections} - set(order))
    grouped = "".join(
        f'<div class="group" id="{slugify(g)}"><div class="group-head"><h2>{e(g)}</h2><span class="mono">{n} {"set" if n == 1 else "sets"}</span></div>'
        + "".join(h for gg, h in sections if gg == g) + "</div>"
        for g in groups for n in [sum(1 for gg, _ in sections if gg == g)] if n)
    body = f"""
<div class="wrap page-head"><span class="crumb"><a href="{u('/work/')}">Work</a> / All graphics</span><h1>Graphics</h1><p class="lede">Social media graphics, YouTube thumbnails, pitch decks and media kits, ad creative and print layouts. Click any image to view it larger, then use the arrow keys.</p></div>
{subnav([(slugify(g), g) for g in ["Carousels", "Pinterest", "Social media", "Thumbnails", "Decks", "Print"] if any(d.get("group") == g for d in designs)])}
<div class="wrap">{grouped}</div>
"""
    write("/design/", page("Graphics", body, "Graphics portfolio: social media graphics, YouTube thumbnails, pitch decks, media kits, ads and print by Veejay Atienza.", "/design/", "Graphics"))


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


VIDEO_T, GROWTH_T = ("short", "long", "video-ads"), ("seo", "paid-ads", "email", "social")
SVC_LIB = {  # page: (hash key, filter label, facets, which facets an item belongs to)
    "/video-editing/": ("format", "Format", [("short", "Short-form"), ("long", "Long-form"), ("video-ads", "Video ads")],
                        lambda i: [t for t in i["types"] if t in VIDEO_T]),
    "/growth/": ("type", "Type", [("seo", "SEO"), ("paid-ads", "Paid ads"), ("email", "Email"), ("social", "Social growth")],
                 lambda i: [t for t in i["types"] if t in GROWTH_T] if i["kind"] == "case" else []),
    "/graphics/": ("format", "Format", [("thumbnails", "Thumbnails"), ("carousels", "Carousels"), ("pins", "Pinterest pins"),
                                        ("social-posts", "Social posts"), ("decks", "Decks")],
                   lambda i: [i["gfx"]] if i.get("gfx") else []),
    "/social-media/": ("format", "Format", [("results", "Growth results"), ("carousels", "Carousels"), ("pins", "Pinterest pins"),
                                            ("short", "Short-form video")],
                       lambda i: (["results"] if i["kind"] == "case" and "social" in i["types"] else
                                  [i["gfx"]] if i.get("gfx") in ("carousels", "pins") else
                                  ["short"] if "short" in i["types"] and "real-estate" not in i["inds"] else [])),
    "/ui-design/": ("type", "Type", [("live", "Live sites"), ("concept", "Concept sites")], lambda i: [i["site"]] if i.get("site") else []),
}


def service_gallery(path):
    """'The work' on a service page: only that service's pieces, with its own format filter and an industry filter."""
    key, label, facets, pick = SVC_LIB[path]
    pool = [(i, pick(i)) for i in LIBRARY + GRAPHICS]
    pool = [(i, f) for i, f in pool if f]
    seen, uniq = set(), []
    for i, f in pool:  # graphics also sit in the main library; keep one copy of each image
        k = (i["thumb"], i["title"])
        if k not in seen: seen.add(k); uniq.append((i, f))
    fl = dict(facets)
    chip = lambda axis, v, lab: f'<button type="button" class="chip" data-axis="{axis}" data-v="{v}" aria-pressed="false">{e(lab)} <span></span></button>'
    frow = chip("f", "all", "All") + "".join(chip("f", k, l) for k, l in facets if any(k in f for _, f in uniq))
    irow = chip("ind", "all", "All") + "".join(chip("ind", k, l) for k, l in INDUSTRIES if any(k in i["inds"] for i, _ in uniq))
    cards = []
    for i, f in uniq:
        tag = ", ".join(fl[x] for x in f) + (" / " + ", ".join(IND_LABEL[x] for x in i["inds"]) if i["inds"] else "")
        data = f' data-f="{" ".join(f)}" data-ind="{" ".join(i["inds"])}"'
        if i.get("card"):
            c = i["card"]
            cards.append(f'<a class="concept-card item-card"{data} href="{e(c["href"])}"><img src="{e(u(c["img"]))}" alt="{e(c["name"])} homepage" loading="lazy">'
                         f'<span class="mono">{e(tag)}</span><strong>{e(c["name"])}</strong><span>{e(c["desc"])}</span></a>')
        else:
            cards.append(lib_card(i, data, tag))
    grid = (f'<div class="concept-grid svc-grid">{"".join(cards)}</div>' if path == "/ui-design/"
            else f'<div class="lib-grid svc-grid">{"".join(cards)}</div>')
    return f"""<section class="wrap section svc-lib" id="work" data-key="{key}">
  <h2>The work</h2>
  <div class="svc-filters">
    <div class="filter-row"><span class="mono">{e(label)}</span>{frow}</div>
    <div class="filter-row"><span class="mono">Industry</span>{irow}</div>
  </div>
  <div class="lib-status"><p class="count mono" aria-live="polite">{len(uniq)} pieces</p><button type="button" class="clear-filters" hidden>Clear filters</button></div>
  {grid}
  <p class="lib-empty" hidden>Nothing in this combination yet. <a href="{BRIEF}">Ask me about it</a>.</p>
</section>"""


SERVICE_TYPE = {"/video-editing/": "video", "/graphics/": "graphics", "/social-media/": "social", "/growth/": "growth",
                "/ui-design/": "websites", "/decks/": "decks"}
LIBRARY = []


def build_hire(pages, work):
    """Service pages: breadcrumb, quick facts, an 'On this page' bar, then numbered sections."""
    W = {w["slug"]: w for w in work}
    services = [(n, h) for _, items in MENU for n, h, _ in items if not n.startswith(("SEO", "Meta", "Email"))]
    group_of = {h: g for g, items in MENU for _, h, _ in items}
    for h in pages:
        content, heads = md(h["body"], toc=True)
        gallery = service_gallery(h["path"]) if h["path"] in SVC_LIB else ""
        if gallery and h["path"] == "/ui-design/":  # the gallery replaces the two card grids written into the page
            content = re.sub(r'<h2 id="live-sites">.*?(?=<h2 id="(?!concept-sites)[^"]*">)', "", content, count=1, flags=re.S)
            heads = [(i, t) for i, t in heads if i not in ("live-sites", "concept-sites")]
        links = ([("work", "The work")] if gallery else []) + list(heads)
        extra = []
        cases = [] if gallery else [W[c.strip()] for c in h.get("cases", "").split(",") if c.strip() in W]
        if cases:
            links.append(("results", h.get("cases_title", "Results")))
            extra.append(f'<section class="wrap section" id="results"><h2>{e(h.get("cases_title", "Results"))}</h2>'
                         f'<div class="cases">{case_rows(cases)}</div></section>')
        prices = "".join(f'<li><span>{e(a)}</span><span class="price">{e(b)}</span></li>'
                         for a, b in (fields(x, 2)[:2] for x in h.get("prices", [])))
        if prices:
            links.append(("prices", "Prices"))
            extra.append(f'<section class="wrap section" id="prices"><h2>Prices</h2><ul class="price-list">{prices}</ul>'
                         f'<p class="note">Starting prices. The final quote depends on length, volume and turnaround.</p></section>')
        stype = SERVICE_TYPE.get(h["path"])
        if stype and not gallery:
            pool = [i for i in LIBRARY if stype in i["types"] or (stype == "video" and set(i["types"]) & {"short", "long", "video-ads"})
                    or (stype == "growth" and set(i["types"]) & {"seo", "paid-ads", "email", "social"})]
            chips = "".join(f'<a href="{u("/work/")}#type={stype}&amp;industry={k}">{e(lab)} <span>{n}</span></a>'
                            for k, lab in INDUSTRIES for n in [sum(1 for i in pool if k in i["inds"])] if n)
            if chips:
                links.append(("industries", "By industry"))
                extra.append(f'<section class="wrap section" id="industries"><h2>Browse by industry</h2>'
                             f'<p class="note">Open the work library filtered to this service and one industry.</p>'
                             f'<div class="next-service by-industry">{chips}<a href="{u("/work/")}#type={stype}">All {len(pool)} pieces</a></div></section>')
        links.append(("how", "How it works"))
        extra.append(process_block().replace('<section class="wrap section">', '<section class="wrap section" id="how">', 1))
        others = "".join(f'<a href="{u(href)}">{e(n)}</a>' for n, href in services if href != h["path"])
        links.append(("other", "Other services"))
        extra.append(f'<section class="wrap section" id="other"><h2>Other services</h2><div class="next-service">{others}</div></section>')
        facts = "".join(f'<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>' for a, b in (fields(x, 2)[:2] for x in h.get("facts", [])))
        group = group_of.get(h["path"])
        crumb = f'<span class="crumb">Services{" / " + e(group) if group else ""} / {e(h["title"])}</span>'
        body = f"""
<div class="wrap page-head">{crumb}<h1>{e(h['title'])}</h1><p class="lede">{e(h['lede'])}</p>
<p><a class="btn" href="{BRIEF}">Start a project <span class="arrow">&rarr;</span></a></p>
{f'<dl class="facts">{facts}</dl>' if facts else ''}</div>
{subnav(links)}
<div class="svc-page">{gallery}<div class="wrap hire">{content}</div>
{''.join(extra)}</div>
"""
        write(h["path"], page(h["title"], body, h["desc"], h["path"], h.get("active")))


def main():
    os.makedirs(OUT, exist_ok=True)
    for name in os.listdir(OUT):  # empty it in place so a running preview server keeps working
        target = os.path.join(OUT, name)
        shutil.rmtree(target) if os.path.isdir(target) else os.remove(target)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "assets"))
    shutil.copytree(os.path.join(ROOT, "concepts"), os.path.join(OUT, "concepts"),
                    ignore=shutil.ignore_patterns("_tools", "_work"))  # standalone concept sites, served as-is
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
    LIBRARY.extend(library_items(work, designs))
    build_hire(hire, work)
    build_writing(writing_meta, articles)
    build_404()
    build_sitemap(["/", "/work/", "/apps/", "/about/", "/video/", "/design/", "/writing/"] + [h["path"] for h in hire] + [f"/work/{w['slug']}/" for w in work]
                  + [f"/apps/{a['slug']}/" for a in detailed])
    print(f"Built {len(work)} case studies, {len(apps)} apps, {len(videos)} video sets, "
          f"{len(designs)} design sets, {len(articles)} articles into _site/")


if __name__ == "__main__":
    main()
