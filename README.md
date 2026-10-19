# Veejay Atienza portfolio

Static site built from Markdown. Every push to `main` rebuilds and deploys it to GitHub Pages.

## Editing

You can edit any file straight on github.com (pencil icon) and the site updates a minute or two after you commit.

| What | Where |
|---|---|
| Name, tagline, headline numbers, focus areas, "More about me" | `content/home.md` |
| Case studies | `content/work/*.md` |
| Video sets | `content/video/*.md` |
| Design sets | `content/design/*.md` |
| Writing page | `content/writing.md` |
| Images and PDFs | `assets/<folder>/` |
| Colours, fonts, layout | `style.css` |

### Adding a case study

Copy an existing file in `content/work/`, rename it (the file name becomes the URL), and edit the top block:

```
---
title: Building Reddit From Zero Into a 34K-User Channel
client: Interview Query
area: Reddit
order: 5
cover: /assets/interview-query-reddit/01.webp
role: Content Marketing Manager. ...
metrics:
  - 34K+ | new users attributed
  - 20K a day | site views from one post, for two weeks
  - $0 | media spend
---
```

`order` sets the position on the homepage. The first metric is the big number shown in the list.

### Embeds

A line on its own like `@[embed](https://www.tiktok.com/@user/video/123)` becomes a player. YouTube, TikTok videos and Instagram reels are supported; anything else shows as a link.

## Building locally

```
pip install markdown
python3 build.py
cd _site && python3 -m http.server 8000
```
