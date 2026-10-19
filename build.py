"""Build the portfolio site from content/ into _site/.

Usage: python3 build.py   (needs: pip install markdown)
"""
import html, os, re, shutil
import markdown

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "_site")
SITE_URL = "https://atienzaveejay.github.io"
BASE = ""  # set to "/repo-name" if this is ever served from a project page


# ---------- content loading ----------

def parse(path):
    """Split a content file into (meta dict, markdown body). Front matter is a tiny YAML subset."""
    text = open(path, encoding="utf-8").read()
    meta, body = {}, text
    if text.startswith("---\n"):
        head, body = text[4:].split("\n---\n", 1)
        key = None
        for line in head.split("\n"):
            if line.startswith("  - ") and key:
                meta.setdefault(key, []).append(line[4:].strip())
            elif ":" in line:
                key, val = line.split(":", 1)
                key, val = key.strip(), val.strip()
                meta[key] = int(val) if val.isdigit() else (val or [])
    return meta, body.strip("\n")


def collection(folder):
    items = []
    for name in os.listdir(os.path.join(ROOT, "content", folder)):
        if name.endswith(".md"):
            meta, body = parse(os.path.join(ROOT, "content", folder, name))
            meta["slug"], meta["body"] = name[:-3], body
            items.append(meta)
    return sorted(items, key=lambda m: m.get("order", 99))


def metric(s):
    value, _, label = s.partition("|")
    return value.strip(), label.strip()


# ---------- markdown ----------

def embed(kind, url):
    m = re.search(r"youtube\.com/embed/([\w-]+)", url)
    if m:
        return (f'<div class="embed embed-wide"><iframe src="https://www.youtube-nocookie.com/embed/{m[1]}" '
                f'title="YouTube video" loading="lazy" allowfullscreen '
                f'allow="accelerometer; encrypted-media; gyroscope; picture-in-picture"></iframe></div>')
    m = re.search(r"tiktok\.com/@[\w.]+/video/(\d+)", url)
    if m:
        return (f'<div class="embed embed-tall"><iframe src="https://www.tiktok.com/player/v1/{m[1]}?rel=0" '
                f'title="TikTok video" loading="lazy" allowfullscreen allow="encrypted-media; fullscreen"></iframe></div>')
    m = re.search(r"instagram\.com/reel/([\w-]+)", url)
    if m:
        return (f'<div class="embed embed-ig"><iframe src="https://www.instagram.com/reel/{m[1]}/embed/" '
                f'title="Instagram reel" loading="lazy" allowfullscreen></iframe></div>')
    clean = url.split("?")[0]
    label = "TikTok photo post" if "tiktok.com" in url else clean
    return f'<a class="embed-link" href="{html.escape(clean)}">View {html.escape(label)} &rarr;</a>'


def md(text):
    text = re.sub(r"<details><summary>(.*?)</summary>", r'<details markdown="1"><summary>\1</summary>', text)
    text = re.sub(r"^@\[(\w+)\]\((.+?)\)$", lambda m: embed(m[1], m[2]), text, flags=re.M)
    out = markdown.markdown(text, extensions=["tables", "fenced_code", "md_in_html", "sane_lists"])
    out = out.replace("<img ", '<img loading="lazy" ')
    out = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', out)
    out = re.sub(r'(src|href)="/(?!/)', rf'\1="{BASE}/', out)
    return out


def u(path):
    return BASE + path


# ---------- layout ----------

NAV = [("Work", "/#work"), ("Video", "/video/"), ("Design", "/design/"), ("Writing", "/writing/"), ("About", "/#about")]
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
           "%3Crect width='64' height='64' rx='6' fill='%23b4650f'/%3E%3Ctext x='32' y='44' font-family='Georgia,serif' "
           "font-size='34' font-weight='600' fill='%23fff' text-anchor='middle'%3EVA%3C/text%3E%3C/svg%3E")


def page(title, body, desc, path, active=None, image="/assets/home/01.webp"):
    nav = "".join(
        f'<a href="{u(href)}"{" aria-current=page" if label == active else ""}>{label}</a>' for label, href in NAV)
    full_title = "Veejay Atienza" if title is None else f"{title} | Veejay Atienza"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="{SITE_URL}{u(image)}">
<meta property="og:url" content="{SITE_URL}{u(path)}">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{u('/style.css')}">
</head>
<body>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="wordmark" href="{u('/')}">Veejay Atienza</a>
    <nav>{nav}</nav>
  </div>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-inner">
    <p>Open to content, growth and marketing roles.</p>
    <p><a href="mailto:atienzaveejay@gmail.com">atienzaveejay@gmail.com</a> &middot; <a href="https://www.linkedin.com/in/veejay-atienza/" target="_blank" rel="noopener">LinkedIn</a></p>
  </div>
</footer>
</body>
</html>
"""


def write(path, content):
    dest = os.path.join(OUT, path.strip("/"), "index.html") if not path.endswith(".html") else os.path.join(OUT, path.strip("/"))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, "w", encoding="utf-8").write(content)


# ---------- pages ----------

def metrics_row(items, cls="metrics"):
    cells = "".join(f'<div><dt>{html.escape(v)}</dt><dd>{html.escape(l)}</dd></div>' for v, l in map(metric, items))
    return f'<dl class="{cls}">{cells}</dl>'


def build_home(home, about, work, videos, designs):
    rows = []
    for w in work:
        value, label = metric(w["metrics"][0])
        rows.append(f"""<a class="case" href="{u('/work/' + w['slug'] + '/')}">
  <div class="case-metric"><span class="num">{html.escape(value)}</span><span class="lbl">{html.escape(label)}</span></div>
  <div class="case-text"><h3>{html.escape(w['title'])}</h3><p>{html.escape(w['client'])} &middot; {html.escape(w['area'])}</p></div>
  <img class="case-thumb" src="{u(w['cover'])}" alt="" loading="lazy">
</a>""")
    video_cards = "".join(
        f'<a class="tile" href="{u("/video/#" + v["slug"])}"><img src="{u(v["cover"])}" alt="" loading="lazy">'
        f'<span class="tile-title">{html.escape(v["title"])}</span><span class="tile-sub">{html.escape(v["group"])}</span></a>'
        for v in videos)
    design_cards = "".join(
        f'<a class="tile" href="{u("/design/#" + d["slug"])}"><img src="{u(first_image(d["body"]))}" alt="" loading="lazy">'
        f'<span class="tile-title">{html.escape(d["title"])}</span><span class="tile-sub">{html.escape(d["group"])}</span></a>'
        for d in designs)
    focus = "".join(f"<li>{html.escape(f)}</li>" for f in home["focus"])
    body = f"""
<section class="hero wrap">
  <div class="hero-text">
    <h1>{html.escape(home['name'])}</h1>
    <p class="tagline">{html.escape(home['tagline'])}</p>
    <ul class="focus">{focus}</ul>
    <p class="contact"><a class="btn" href="mailto:{home['email']}">Email me</a> <a class="btn btn-quiet" href="{home['linkedin']}" target="_blank" rel="noopener">LinkedIn</a></p>
  </div>
  <img class="hero-photo" src="{u(home['photo'])}" alt="Portrait of Veejay Atienza" width="640" height="960">
</section>

<section class="wrap highlights-wrap">
  {metrics_row(home['highlights'], 'highlights')}
</section>

<section class="wrap section" id="work">
  <h2>Case studies</h2>
  <div class="cases">{''.join(rows)}</div>
</section>

<section class="wrap section">
  <div class="section-head"><h2>Video</h2><a href="{u('/video/')}">All videos &rarr;</a></div>
  <div class="tiles">{video_cards}</div>
</section>

<section class="wrap section">
  <div class="section-head"><h2>Design</h2><a href="{u('/design/')}">Full gallery &rarr;</a></div>
  <div class="tiles tiles-4">{design_cards}</div>
</section>

<section class="wrap section">
  <div class="section-head"><h2>Writing</h2><a href="{u('/writing/')}">All writing &rarr;</a></div>
  <p class="lede">LinkedIn ghostwriting that reached 120,000 impressions on a single post, B2B thought leadership, and long-form articles on job search, freelancing and self-development.</p>
</section>

<section class="wrap section about" id="about">
  <h2>More about me</h2>
  <div class="prose">{md(about)}</div>
</section>
"""
    write("/", page(None, body, home["tagline"], "/"))


def first_image(body):
    m = re.search(r"!\[[^\]]*\]\((.+?)\)", body)
    return m[1] if m else ""


def build_case(w, prev, nxt):
    nav = '<nav class="pager">'
    if prev:
        nav += f'<a href="{u("/work/" + prev["slug"] + "/")}"><span>Previous</span>{html.escape(prev["title"])}</a>'
    else:
        nav += "<span></span>"
    if nxt:
        nav += f'<a class="next" href="{u("/work/" + nxt["slug"] + "/")}"><span>Next</span>{html.escape(nxt["title"])}</a>'
    nav += "</nav>"
    body = f"""
<article class="case-page">
  <header class="wrap case-head">
    <p class="crumb"><a href="{u('/#work')}">Case studies</a> / {html.escape(w['client'])}</p>
    <h1>{html.escape(w['title'])}</h1>
    <p class="role"><strong>Role.</strong> {html.escape(w['role'])}</p>
    {metrics_row(w['metrics'])}
  </header>
  <figure class="wrap case-cover"><img src="{u(w['cover'])}" alt=""></figure>
  <div class="wrap"><div class="prose">{md(w['body'])}</div></div>
  <div class="wrap">{nav}</div>
</article>
"""
    desc = f"{w['client']}: " + "; ".join(f"{v} {l}" for v, l in map(metric, w["metrics"]))
    write(f"/work/{w['slug']}/", page(w["title"], body, desc, f"/work/{w['slug']}/", "Work", w["cover"]))


def build_video(videos):
    sections = "".join(f"""
<section class="section" id="{v['slug']}">
  <div class="section-head"><h2>{html.escape(v['title'])}</h2><span class="muted">{html.escape(v['group'])}</span></div>
  <div class="video-grid">{md(v['body'])}</div>
</section>""" for v in videos)
    body = f"""
<div class="wrap page-head"><h1>Video</h1><p class="lede">Short-form and YouTube work across tech education, consumer apps and B2B.</p></div>
<div class="wrap">{sections}</div>
"""
    write("/video/", page("Video", body, "Video portfolio: YouTube, TikTok and Instagram work by Veejay Atienza.", "/video/", "Video"))


def build_design(designs):
    sections = []
    for d in designs:
        images = re.findall(r"!\[[^\]]*\]\((.+?)\)", d["body"])
        pdfs = re.findall(r"\[PDF: ([^\]]+)\]\((.+?)\)", d["body"])
        cls = "gallery gallery-print" if pdfs else "gallery"
        figs = "".join(f'<a href="{u(src)}" class="shot"><img src="{u(src)}" alt="{html.escape(d["title"])} design" loading="lazy"></a>' for src in images)
        links = "".join(f'<a class="btn btn-quiet" href="{u(href)}" target="_blank" rel="noopener">Open the full PDF</a>' for _, href in pdfs)
        sections.append(f"""
<section class="section" id="{d['slug']}">
  <div class="section-head"><h2>{html.escape(d['title'])}</h2><span class="muted">{html.escape(d['group'])}</span></div>
  <div class="{cls}">{figs}</div>
  {f'<p>{links}</p>' if links else ''}
</section>""")
    body = f"""
<div class="wrap page-head"><h1>Design</h1><p class="lede">Social media graphics, YouTube thumbnails and print layouts. Click any image to view it larger.</p></div>
<div class="wrap">{''.join(sections)}</div>
<dialog class="lightbox" aria-label="Image preview"><button type="button" aria-label="Close">Close</button><img alt=""></dialog>
<script>
(() => {{
  const box = document.querySelector('.lightbox'), img = box.querySelector('img');
  document.querySelectorAll('.shot').forEach(a => a.addEventListener('click', e => {{
    e.preventDefault(); img.src = a.href; img.alt = a.querySelector('img').alt; box.showModal();
  }}));
  box.addEventListener('click', () => box.close());
}})();
</script>
"""
    write("/design/", page("Design", body, "Design portfolio: social media graphics, YouTube thumbnails and print by Veejay Atienza.", "/design/", "Design"))


def build_writing(text):
    body = f"""
<div class="wrap page-head"><h1>Writing</h1><p class="lede">LinkedIn ghostwriting, B2B strategy posts and blog articles.</p></div>
<div class="wrap"><div class="prose writing">{md(text)}</div></div>
"""
    write("/writing/", page("Writing", body, "Writing portfolio: LinkedIn posts, B2B copy and blog articles by Veejay Atienza.", "/writing/", "Writing"))


def build_404():
    body = f'<div class="wrap page-head"><h1>Page not found</h1><p class="lede">That page moved or never existed. <a href="{u("/")}">Back to the homepage</a>.</p></div>'
    write("404.html", page("Not found", body, "Page not found", "/404.html"))


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "assets"))
    shutil.copy(os.path.join(ROOT, "style.css"), OUT)
    open(os.path.join(OUT, ".nojekyll"), "w").close()

    home, about = parse(os.path.join(ROOT, "content", "home.md"))
    work, videos, designs = collection("work"), collection("video"), collection("design")
    _, writing = parse(os.path.join(ROOT, "content", "writing.md"))

    build_home(home, about, work, videos, designs)
    for i, w in enumerate(work):
        build_case(w, work[i - 1] if i else None, work[i + 1] if i + 1 < len(work) else None)
    build_video(videos)
    build_design(designs)
    build_writing(writing)
    build_404()
    print(f"Built {len(work)} case studies, {len(videos)} video sets, {len(designs)} design sets into _site/")


if __name__ == "__main__":
    main()
