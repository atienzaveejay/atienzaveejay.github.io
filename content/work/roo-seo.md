---
title: Building a 130-Post Buying Guide Library, and Finding Why a Position-2.4 Ranking Got One Click
client: ROO
area: SEO and content
tags: SEO and content
order: 5
cover: /assets/roo-seo/cover.webp
role: Solo marketer for a US direct-to-consumer kitchen brand on Shopify (cutting boards and the ROO mat). I own SEO, organic social, Pinterest, the store's pages and the weekly founder report.
card: 130+ | blog posts, up from 39
metrics:
  - 39 → 130+ | blog posts live in two months
  - 0.66% → 1.22% | click-through rate after the snippet fix
  - 6 days | for new buying guides to start ranking
---
## Context

ROO sells cutting boards and a mat that sits underneath them to catch scraps. When I took over SEO the blog had 39 articles, mostly kitchen tips, and search traffic was small and flat. The founder wanted organic search to become a real channel without a big content budget.

## The diagnosis that changed the plan

Before writing anything new I went through Search Console page by page. One result didn't make sense.

The meal prep containers post had **3,278 impressions at an average position of 2.4, and one click.** The single query "meal prep containers" gave 725 impressions at position 1.09 and zero clicks. A page sitting at the top of Google should not get ignored like that.

When I looked at the result as a searcher would, the reason was obvious. The Shopify theme was auto-filling the meta description by scraping the first lines of the page, so the snippet under our title was a fragment of intro text that answered nothing. We were ranking, and then losing the click in the search result itself.

> Rankings were not the bottleneck. The snippet was.

I rewrote the descriptions across the library and worked around the theme so our own descriptions would show. Week 16 click-through rate went from **0.66% to 1.22%**.

## Building the library

### Research first

Using DataForSEO I mapped keyword clusters around what ROO actually sells. Two later batches of 20 articles targeted about 230,000 searches a month between them. A gap analysis in October found commercial terms nobody strong was competing for, such as titanium cutting boards (49,500 searches a month) and Epicurean boards (33,100), both with near-zero keyword difficulty.

### Technical groundwork

- **9 verified 301 redirects** from the old blog URLs, which protected 5,406 impressions, 52% of the site's lifetime total
- **Recipe schema** on 30 posts and product structured data on the store
- The cart page taken out of the index
- Publishing through the Shopify API, so a batch goes live in minutes instead of a day of copy-pasting

![ROO buying guides](/assets/roo-seo/index.webp)

### Guides over tips

By mid-October the blog had grown past 130 posts, 53 of them buying guides. The data split cleanly by format:

@[bars](Buying guides=102 clicks; Kitchen tips=9 clicks | Clicks from search, same period. Guides had 10.3K impressions, tips 4.4K.)

People searching "best cutting board for..." are close to buying. People searching how to clean a board are not. So the plan moved to commercial guides, and new ones started ranking within six days of publishing.

## Results

- Weekly clicks grew from 29 to 44, on 7,906 impressions in the latest week
- 243 clicks on 36,757 impressions over the trailing three months
- Click-through rate nearly doubled after the snippet fix
- A library of 130+ posts that compounds, with buying guides as the core

## What didn't work

The meal prep page itself never recovered. After the fix it slid to position 8 and stayed at zero clicks, which suggests Google had already learned that searchers skipped it. A how-to batch earned 563 impressions and one click. And the snippet fix took about seven weeks to ship because it depended on theme changes, seven weeks of traffic we didn't get back.

Search clicks have grown, but they have not yet turned into meaningful sales. That's the next problem, and it's a conversion problem on the store, not a content problem.

## Takeaway

- Look at your results the way a searcher does before writing more pages. A bad snippet can waste a top ranking.
- On a young site, domain authority caps growth more than article count does. More posts of the wrong kind won't move it.
- Write for buying intent. Guides earned 11 times the clicks of tips, and about five times the click-through rate.
