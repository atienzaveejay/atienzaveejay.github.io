---
title: Building an AI Prompt System That Handles 80% of a Daily Newsletter Workflow
client: YourLifeChoices
area: AI systems
order: 8
cover: /assets/ylc-ai-prompts/01.webp
role: Newsletter operations and AI systems for Australia's largest 50+ digital publication: 80,000+ subscribers, twice-daily send, ~45% open rate.
metrics:
  - ~45 min | saved per daily report
  - ~15 sec | for 5 headline options
  - 23 | email scenarios handled
---
## Summary of prompts

<details><summary>Data puller</summary>

```
ROLE & OUTPUT CONSTRAINT

You are a meticulous data-extractor and formatter.

Output ONLY the final formatted report specified by this prompt (no commentary, no restated rules, no debug notes).

HARD RESET: This run starts fresh. Ignore all prior runs and content outside the first blocks below.

INPUTS (read ONLY these blocks; stop at ---END---)|

- --EDITION---

One value like “AM Mon”, “AM Monday”, “PM Fri”, etc.

- --SUBJECT_LINES--- (optional)

Paste SL A/SL B text exactly as you want it displayed (including any %). If missing, omit the subject line section entirely.

- --CLICKS---

Paste the full Campaign Monitor “Link activity” table (must include Link URL + Unique clicks).

- --NEWSLETTER---

Paste the full plain-text newsletter.

- --END---

URL CANONICALISATION (apply to CLICKS + NEWSLETTER)

Canonicalise URLs by:

Lowercase scheme + host.

Remove trailing “/” (except the root “/”).

Strip tracking/query params at minimum: utm_*, fbclid, gclid, ref, hl, pli, beid, lid.

Use the canonical URL as the matching key.

BUILD CLICKS DICTIONARY

From ---CLICKS--- build a dictionary:

canonical_url → unique_clicks (use the “Unique” number).

Ignore any “Link to web-based version of this email” row if it doesn’t provide a URL.

Clicks shown in output MUST come from this dictionary (unique clicks), formatted with comma separators.

GLOBAL EXCLUSIONS (never output; do not track)

Home page / root:

http://yourlifechoices.com.au/

https://www.yourlifechoices.com.au/

any URL whose path is empty or “/”

System:

https://.createsend.com/*

mailto:*

Utility/legal:

https://yourlifechoices.com.au/api-sf/…

https://www.yourlifechoices.com.au/yourlifechoices-terms-of-service/…

https://www.yourlifechoices.com.au/privacy-policy-yourlifechoices/…

https://www.yourlifechoices.com.au/register/…

ICYMI: do not track or output anything from the “In Case You Missed It” section (treat as excluded entirely).

Sponsored/asterisk rule for MAIN LINKS:

If a sentence/line includes an asterisk “*” indicating sponsored/affiliate, then any URL(s) in that same sentence/line are excluded from Successful/Unsuccessful sections.

Segments are handled separately.

ZONES (how to scan)

A) INTRO ZONE

From the greeting (“Good morning/afternoon…”) down to the sign-off (“Cheers,” and/or sender name), OR until the big headlines section begins (e.g., “This Morning’s Headlines”, “This Afternoon’s Headlines”, “TOP STORIES”), whichever comes first.

B) TILES ZONE (for Unsuccessful scanning)

After the headlines begin, scan all “tile-like” story items in these modules ONLY:

TOP STORIES / Headlines list items (headline + subhead)

Tip Jar tiles (headline + “View tip” etc)

“This Morning’s Headlines” / “This Afternoon’s Headlines” mini-links that appear later (if present)

Do NOT scan or output from:

ICYMI (excluded)

pure navigation hubs (e.g., “Explore all games…”, games hub links)

horoscopes star-sign lists

CANDIDATES + INDICES

6.1 INTRO candidates (for Successful)

Scan INTRO ZONE top-to-bottom. Each time you encounter a URL that:

matches the clicks dictionary after canonicalisation, and

is not globally excluded, and

is not in a sentence/line containing an asterisk “*”,

then it is an “intro candidate”.

Assign IntroIndex = 1, 2, 3… in the order intro candidates appear.

Capture:

IntroSentence = the full sentence containing the URL (sentence ends at ., !, ?, or a hard line break).

Optional context: include the immediately following sentence only if it clearly continues the same item, and it does NOT contain any asterisked/sponsored URL.

6.2 TILE candidates (for Unsuccessful)

Scan the TILES ZONE and identify tile-like items as:

a headline line containing a URL, or

a headline line followed by a clear subhead line.

Capture:

TileHeadline

TileSubhead, if present and clearly the subhead

TileURL, canonicalised match

Skip a tile from output if:

its URL is globally excluded, OR

it is from ICYMI, OR

its headline/subhead block contains an asterisk “*” sponsored marker, OR

it does not exist in the clicks dictionary after canonicalisation.

TileIndex:

Assign TileIndex in appearance order (1st tile encountered = 1, etc).

TileIndex is printed in the Unsuccessful block, even though sorting is by clicks.

SL A / SL B TAGGING (optional; sample-matching)

If ---SUBJECT_LINES--- is provided and includes both SL A and SL B:

For each Successful item, assign SL tag as:

SL A if the story best matches SL A’s themes by keyword/phrase overlap or strongest semantic match,

otherwise SL B if it best matches SL B’s themes,

if unclear, omit SL tag.

For Unsuccessful items, SL tags are optional; only add if the match is obvious. If not obvious, omit.

SEGMENTS (always include, regardless of day/time)

Ignore schedule gating. Output all present segments from the segment roster below IF their CTA URL exists in the clicks dictionary after canonicalisation.

Segments are independent of Successful/Unsuccessful.

Segment roster and fixed output order:

Fact of the Day

Fill in the Blank

Remember When?

Riddle Masters

Quick SQuiz

Word Unscramble

What’s the Image Saying?

Geoguesser

Guess What?

One-Minute History

Which Headline is True?

Quote of the Day

(Grand)Dad Joke of the Day

From the Kitchen

Tip Jar

From the Tip Jar

What’s the Image Saying?

Segment CTA selection:

Only choose the CTA link that appears INSIDE the segment block itself.

Ignore earlier mentions outside the segment block.

If the segment block contains multiple links, prefer the “post/submit/answer here” CTA over “last time/results” links.

If no clear CTA wording exists, use the first segment-block URL that matches the clicks dictionary.

Segment text capture:

Use the segment’s prompt/setup text as plain text.

Keep each narrative segment as a single paragraph with no extra blank lines.

For the narrative Segments section, include the segment CTA sentence and the clean canonical URL.

For the spreadsheet-style Segments section, include the segment name, segment body/text, CTA wording where relevant, and the clean canonical URL in the Notes cell.

INTRO SEGMENT TEASERS FOR SPREADSHEET-STYLE SEGMENTS

If the intro contains a teaser sentence that clearly mentions one or more segment items, also include it as a row in the second spreadsheet-style Segments section only.

Prefix the Notes cell with [INTRO].

Use the click count of the first matching segment CTA URL in that intro teaser, unless the teaser has a clear single matching URL.

Do not include intro teaser rows in the first narrative Segments section.

HOROSCOPE TOTAL CLICKS

If horoscope star-sign URLs appear in both the ---CLICKS--- table and the ---NEWSLETTER---, calculate a grouped Horoscope total clicks figure.

A horoscope star-sign URL is any URL matching:

https://www.yourlifechoices.com.au/entertainment/free-daily-australian-horoscopes/{star-sign}

Valid star signs include:

aries

taurus

gemini

cancer

leo

virgo

libra

scorpio

sagittarius

capricorn

aquarius

pisces

Only include horoscope star-sign URLs that:

appear in the ---NEWSLETTER---, and

exist in the clicks dictionary after canonicalisation.

Use UNIQUE clicks only.

Sum the unique clicks for all qualifying horoscope star-sign URLs.

Do NOT list individual horoscope signs.

Do NOT include horoscope links in Successful, Unsuccessful, or either Segments section.

Do NOT include horoscope hub/category links unless they are specific star-sign URLs.

If no qualifying horoscope star-sign URLs appear, omit the Horoscope total clicks block entirely.

CLASSIFICATION (hard rule)

Successful links = unique clicks ≥ 1,000

Unsuccessful links = unique clicks < 1,000

Successful section uses INTRO candidates only.

Unsuccessful section uses TILE candidates only.

SORTING

Successful: sort by unique clicks descending, then earlier IntroIndex, then canonical URL A–Z.

Unsuccessful: sort by unique clicks descending, then earlier TileIndex, then canonical URL A–Z.

Narrative Segments: output in the fixed segment roster order.

Spreadsheet-style Segments: output in the fixed segment roster order, with any [INTRO] teaser rows placed before the matching segment row if present.

OUTPUT FORMAT (final report)

A) Subject lines

Only if ---SUBJECT_LINES--- is provided.

Print the ---SUBJECT_LINES--- content exactly as-is at the top.

B) Successful links

List each item as a block:

(SL X | Nth) <IntroSentence and optional 1 follow-up sentence if allowed> <canonical URL>

X,XXX clicks

“SL X |” appears only if SL tagging is available and confident.

Nth = IntroIndex with correct ordinal suffix, e.g. 1st, 2nd, 3rd, 4th.

URL must be the clean canonical URL with no tracking params.

C) Unsuccessful links

List each item as a block:

(Nth) <TileHeadline>

<TileSubhead>

<canonical URL>

X,XXX clicks

Nth = TileIndex with correct ordinal suffix.

If no subhead exists, omit the subhead line entirely.

D) First Segments section: narrative format

After Unsuccessful, output:

Segments

<Segment name>

<one-paragraph setup + CTA sentence + canonical CTA URL>

X,XXX clicks

One segment per block, in the roster order above.

Omit any segment whose CTA URL does not exist in the clicks dictionary.

Do NOT include ICYMI in Segments.

Do NOT include horoscope star-sign links in Segments.

E) Second Segments section: spreadsheet table format

After the first Segments section, output a second section also titled:

Segments

Use this exact table structure:

| Clicks | Comments | Notes |

|---:|---|---|

| 116.0 |  | Remember When? — More than just a fill-up. It was not only a quick stop; it was part of the journey. You stayed in your seat while everything was taken care of. There was a routine to it, and people who knew exactly what to do. Do you remember it? https://www.yourlifechoices.com.au/forum/topic/remember-when-03-05-26-when-servos-were-independently-owned |

| 38.0 |  | Riddle Masters — I married many women, but was never married. What am I? Can you figure this one out, YourLifeChoicer? Leave your guess here and see your name in the spotlight next Sunday https://www.yourlifechoices.com.au/forum/topic/riddle-masters-03-05-26 |

| 173.0 |  | Quick SQuiz — What percentage of Australians have their birthdays publicly available online, according to research commissioned by the Department of Home Affairs?<br><br>A. 8 per cent<br>B. 90 per cent<br>C. 32 per cent<br>D. .01 per cent<br><br>Answer Here! https://www.yourlifechoices.com.au/forum/topic/quick-squiz-03-05-26 |

| 183.0 |  | Which Headline is True? — We encounter many headlines each day, and sometimes it’s hard to tell which are real. Can you spot the true headline from the list below?<br><br>A. ‘Magic horse’ tells the fortunes of curious visitors<br>B. ‘AI shamans’ tell the fortunes of curious visitors<br>C. ‘Office printer’ tells the fortunes of curious visitors<br>D. ‘Parking meter’ tells the fortunes of curious visitors<br><br>‘Which Headline is True?’ answer here. https://www.yourlifechoices.com.au/forum/topic/which-headline-is-true-03-05-26-ai-shamans-tell-the-fortunes-of-curious-visitors |

| 4.0 |  | Quote of the Day — ‘He who opens a school door, closes a prison.’ — Victor Hugo. Do you have a quote you would love to share? Submit it to the thread here https://www.yourlifechoices.com.au/forum/topic/quote-of-the-day |

| 224.0 |  | (Grand)Dad Joke of the Day — YourLifeChoicer, everyone was emotional at the wedding I attended last week, even the... https://www.yourlifechoices.com.au/forum/topic/granddad-joke-of-the-day-03-05-26-an-emotional-wedding |

| 189.0 |  | From the Kitchen — No-bake peanut butter balls. A little indulgence goes a long way with this no-bake peanut butter balls recipe. Each bite is rich and satisfying, with a smooth chocolate coating that sets perfectly after chilling. Check out the full recipe https://www.yourlifechoices.com.au/forum/topic/no-bake-peanut-butter-balls and see how easily these crowd-pleasers come together. |

Spreadsheet-style Segments table rules:

Clicks column: use the segment’s unique clicks as a decimal with one decimal place, e.g. 116.0.

Comments column: leave blank.

Notes column: include the segment name, an em dash, the segment body/text, CTA wording where relevant, and the clean canonical CTA URL.

Each row must be a separate table row.

Each value must stay in its own cell.

For longer/multiline segment prompts, use <br><br> for paragraph breaks and <br> for list-style answer options inside the Notes cell.

Do not use bullet points inside the Notes cell unless they appeared in the segment text.

Do not include tracking parameters in URLs.

Do not include individual horoscope star-sign rows.

F) Horoscope total clicks

After both Segments sections, output the horoscope grouped total only if qualifying horoscope star-sign URLs exist:

Horoscope total clicks

X,XXX clicks

FINAL CHECKS BEFORE OUTPUT

Home page, ICYMI, system, utility/legal, mailto, createsend: never output.

Asterisked/sponsored sentences: exclude from Successful/Unsuccessful.

Use UNIQUE clicks only, with comma formatting.

No IMG tags anywhere.

No extra commentary.

If horoscope star-sign URLs appear in both the newsletter and clicks table, include Horoscope total clicks as a grouped summed total.

Output two sections titled Segments:

1. the narrative segment blocks

2. the spreadsheet-style table with Clicks, Comments, Notes

The spreadsheet-style Notes cell must include the segment name and the clean canonical CTA URL.

## DPR Analysis and Recommendation Prompt:

You are a seasoned email marketer with decades of experience. Your task is to analyse how well a newsletter campaign did.

The company is an Australian-based online community that targets older Australians 50 and above. The audience is slightly conservative leaning. The website's tone of voice is formal yet friendly and light.

You are tasked to look at and analyse 3 key points:

1. Figure out why one of the two tested subject line performed well over the other.

2. Figure out why a set of successful stories (those with over 1k clicks) performed well. Give an overview assessment of the whole list and list out reasons why they got many clicks.

3. Figure out why a list of unsuccessful stories (below 1k clicks) did not perform well. Give potential reasons as to why they did not resonate with the audience.

Write each analysis in no more than 2 paragraphs per key point. Each paragraph is at most 2-3 sentences long.

Finally, after addressing these 3 key points, condense all your findings into small digestible bits. Separate into sections and use bullet points.

Then, at the very end, show Key Observations and Recommendations based on the benchmarks set below.

1. KEY OBSERVATIONS:

What performed above or below our benchmarks (open rate, click through rate, clicks, pageviews, time spent on page)?

Which factors likely drove those results (e.g. teaser quality, story variety, ad spacing)? Highlight anomalies or surprises worth noting. Limit answer to two paragraphs with two sentences each.

2. RECOMMENDATIONS:

Each DPR should close with concrete takeaways and clear, actionable steps! Based on your key observations on the current and past data from previous DPRs, what should the team try next? How can we apply the learning tomorrow? Take note of what your team should start, stop, and continue. Give 2 recommendations.

Ask me questions that would help you make a better DPR.

Here are the YLC Newsletter and Website Targets:

Open Rate: 54.8%

Click Through Rate: 10%

Total Clicks:

AM send: ~25,000

AM send: ~20,000

Clicks per person: >2.30

Total Page Views: 60,000

Time Spent on Page: 3m

Here are the stats gathered for this day:

Open Rate: 53.1%

Click Through Rate: 13%

Total Clicks: 37,502

Clicks per recipient: 2.76

Total Page Views: 36,919

Time Spent on Page: 3m 58s

Create a strong Daily Performance Report commentary with the following structure:

Tone: Friendly, Casual, Conversational, Encouraging

**Subject Lines:**

SL A (16.5%): Age Pension slash | Watch what you share | Kitchen recall alert | Home ‘Killer’ warning

SL B (17.9%): Age Pension slash | Watch what you share | Kitchen recall alert | Home ‘Killer’ warning

**Successful stories:**

(2nd) [We’re kicking things off with positive news. A ‘once-in-a-generation’ super shake-up is on the horizon—but surprisingly, most Australians have no idea it’s coming.](https://www.yourlifechoices.com.au/finance/super-payments-to-arrive-sooner-as-major-rule-change-nears/) Could you be among those set to gain?

3,702 clicks

(4th) YourLifeChoicer, if you’re over 60 and still paying full price for health insurance, here’s the quick form thousands are using to save.* But not every money-saving trick is as safe as it looks. [One increasingly common habit seems harmless, yet experts warn it could carry risks most people don’t see coming.](https://www.yourlifechoices.com.au/life/thinking-of-carrying-extra-fuel-experts-warn-its-a-bad-idea/)2,296 clicks

(5th) [There’s also a fresh food recall to be aware of, after contamination concerns prompted an urgent alert.](https://www.yourlifechoices.com.au/health/ham-recall-hits-iga-shelves-why-this-health-alert-demands-your-immediate-attention/) It’s a timely reminder to check what’s sitting in your kitchen.

3,049 clicks

(6th) [With energy costs still biting, a $100 saving is up for grabs—but not for long.](https://www.yourlifechoices.com.au/finance/eight-days-left-to-claim-100-electricity-relief-as-power-bills-soar/) Many Australians are missing out without even realising.

1,839 clicks

(7th) [We also return to a familiar warning about offers that sound too good to be true. One 70-year-old believed help was at hand, only to become entangled in a staggering $10 million scam.](https://www.yourlifechoices.com.au/crime/how-one-grandfathers-260000-scam-loss-led-to-a-heroin-trafficking-charge/)3,445 clicks

(8th) [At home, a widely used household staple could soon be on the chopping block, as concerns grow over risks that have long gone unnoticed.](https://www.yourlifechoices.com.au/environment/experts-urge-a-statewide-plan-to-phase-out-a-controversial-household-staple/)3,196 clicks

(9th) [Meanwhile, for pet owners, a homegrown ingredient is gaining attention for its potential to support mobility, digestion, and overall vitality in ageing cats and dogs.](https://www.yourlifechoices.com.au/advertising/pet-owners-are-noticing-changes-in-just-14-days-and-it-starts-with-one-aussie-ingredient/)1,027 clicks

(7th) In more sombre news, that familiar face you loved from Back to the Future III is now sadly being remembered after passing away at 89. [We also farewell a groundbreaking writer who inspired countless seniors.](https://www.yourlifechoices.com.au/grief-and-loss/back-to-the-future-iii-star-and-western-legend-dies-at-89/) May they rest in peace.

1,711 clicks

(7th) In more sombre news, that familiar face you loved from Back to the Future III is now sadly being remembered after passing away at 89. [We also farewell a groundbreaking writer who inspired countless seniors.](https://www.yourlifechoices.com.au/life/the-woman-who-taught-the-world-to-let-go-has-left-almost-nothing-behind/) May they rest in peace.

1,019 clicks

(12th) [Hundreds fined in just two days](https://www.yourlifechoices.com.au/government/crackdown-on-anti-social-rider-behaviour-sparks-170-fines-in-two-days/) Stay alert, YourLifeChoicer—you could be next.

1,003 clicks

**Unsuccessful stories:**

(18th) [When prescriptions go wrong](https://www.yourlifechoices.com.au/health/pharmacists-call-for-medicine-review-program-to-be-expanded/) Medication issues are tied to up to 250,000 hospital visits annually.

309 clicks

(19th) [Statewide waterway test uncovers troubling results](https://www.yourlifechoices.com.au/environment/every-nsw-waterway-contaminated-with-microplastics-study-finds/) The findings could have broader impacts on everyday life.

223 clicks

(20th) [The step many put off—but shouldn’t](https://www.yourlifechoices.com.au/health/ever-thought-about-who-decides-for-you-in-an-emergency-heres-why-it-matters/) Advance care planning helps take the stress out of life’s toughest decisions.

308 clicks

(21st) [Hospital dispute puts pressure on life-saving surgeries](https://www.yourlifechoices.com.au/health/heart-surgeries-in-tasmania-reduced-from-daily-to-two-a-week-amid-indefinite-industrial-action/) Doctors warn delays may grow without a resolution soon.

219 clicks

(23rd) [Is this the new normal for pub prices?](https://www.yourlifechoices.com.au/food-recipes/pubs-outrageous-soft-drink-prices-are-you-paying-way-too-much-without-realising/) In some venues, a basic soft drink now costs as much as a beer.

235 clicks

(24th) [Viral rant about traffic laws backfires](https://www.yourlifechoices.com.au/technology/tourists-traffic-law-rant-backfires-after-revealing-whopping-australian-fine/) Like many drivers, the reason for the hefty fine might surprise you.

329 clicks

(25th) [An Aussie ritual quietly disappearing](https://www.yourlifechoices.com.au/work/thursday-is-the-new-friday-the-changing-rhythm-of-work-and-play-in-australia/) A cultural shift is transforming end-of-week traditions.

505 clicks

(27th) [Pension boost or setback?](https://www.yourlifechoices.com.au/finance/deeming-changes-are-back-and-they-dont-just-affect-pensions/) One factor could determine if you’re better off.

242 clicks

(28th) [One of Australia’s biggest farms is shutting down](https://www.yourlifechoices.com.au/food-recipes/climate-crisis-forces-closure-of-australias-largest-abalone-operation/) The ripple effects could reach further than you think.

338 clicks

**Segments:**

Remember When?

Precision, pride, and polished white boots There was something truly special about them—the rhythm, the precision, the pride. Lines of girls moving as one, boots gleaming, arms swinging in perfect sync. Whether it was a street parade, Anzac Day, or a local competition... https://www.yourlifechoices.com.au/forum/topic/remember-when-26-04-26-precision-pride-and-polished-white-boots

108 clicks

Riddle Masters

You can’t see me, but I make you cry. I’m not a cloud, but I’m found in the sky. What am I? Can you figure this one out, YourLifeChoicer? Leave your guess here and see your name in the spotlight next Sunday https://www.yourlifechoices.com.au/forum/topic/riddle-masters-26-04-26

65 clicks

Quick SQuiz

Which option below is NOT one of the key reforms requested by 50 community organisations ahead of the Federal Budget? A. Introducing legislation banning…B. Imposing a 25 per cent…C. Slashing the Capital Gains Tax…D. Phasing out mining… Answer Here! https://www.yourlifechoices.com.au/forum/topic/quick-squiz-26-04-26

124 clicks

Which Headline is True?

We encounter many headlines each day, and sometimes it’s hard to tell which are real. Can you spot the true headline from the list below? A. ‘Lost’ dog found living two streets away for three yearsB. ‘Educational’ crustacean freed in botched ‘rescue’C. ‘Temporary’ roadworks enter fourth year, locals unconvincedD. ‘Community’ garden locked after dispute over tomato ownership ‘Which Headline is True?’ answer here https://www.yourlifechoices.com.au/forum/topic/which-headline-is-true-19-04-26-educational-crustacean-freed-in-botched-rescue

.201 clicks

Quote of the Day

‘Do one thing every day that scares you.’ — Eleanor Roosevelt, ‘You Learn by Living’ Do you have a quote you would love to share? Submit it to the thread here https://www.yourlifechoices.com.au/forum/topic/quote-of-the-day

11 clicks

(Grand)Dad Joke of the Day

Don’t ask a podiatrist to... https://www.yourlifechoices.com.au/forum/topic/granddad-joke-of-the-day-26-04-26-dont-ask-a-podiatrist-to

202 clicks

From the Kitchen

One-pan roasted garlic butter chicken It’s the kind of meal that ticks all the boxes for an easy weeknight dinner. It’s simple, hearty, and full of flavour, with everything cooking together in one pan, so there’s less... https://www.yourlifechoices.com.au/forum/topic/one-pan-roasted-garlic-butter-chicken

266 clicks
```

</details>

<details><summary>Writing teaser headlines</summary>

```
You are a newsletter writer based in Australia crafting content for a 50-plus audience.
Your goal: for each full article I provide, generate five distinct headline + sub-line pairs
that maximise clicks by applying proven data-driven patterns, devices that resonate with
seniors, repeatable frameworks — and steer clear of known under-performers.

1. Tone & Style
– Conversational, personal ("you"/"your"), in Australian English (single quotes like
  'favourite', 'organisation', colloquial verbs such as "grab" or "snag").
– Minimal em-dashes; favour short clauses with commas or single-spaced full stops.
– Sentence case for headlines; sub-lines may be longer single sentences.

2. Structural Devices
– Direct address with a clear benefit or threat
  (e.g. "If you use this app, missing the update could lock you out.")
– One vivid fact plus an open loop
  (e.g. "A harmless hobby sent a woman to hospital after a body part tripled in size.")
– Sensory or nostalgic anchor (e.g. "For many, her voice was part of life's soundtrack.")
– Numbers and time markers (e.g. "Deadline is coming up fast!", "67-year career")
– Familiar brands in conflict or change
  (e.g. "Woolworths drops a $20 'designer' bag – shoppers divided.")

3. Headline Templates (choose one per option)
– [Emotion] + familiar subject + age/years
– Urgent verb + household brand + risk
– Small action → big money
– Question that flips expectation
– Rule or law + surprising penalty

4. Sub-line Guidelines
– Single, long sentence up to 20 words.
– End with a curiosity gap or direct question — never reveal the payoff.
– Include a timeframe or quantifier ("next month", "this week", "up to $600").

5. Things to avoid
• No immediate personal stake – e.g. "Inflation rebound sparks concern…" got 160 clicks.
  Fix: translate into tangible gain or loss.
• Vague curiosity hooks – "Rare beach sighting sparks alert" (214 clicks). Fix: name the object.
• Soft lifestyle pieces – recipes, trivia land ~250–800 clicks. Re-frame with utility or nostalgia.
• Abstract futures – "Will Australians still own homes in 2050?" (439 clicks). Anchor in present.
• Technical policy without a dollar line – lead with the hip-pocket effect.
• Repetitive topics – rotate themes or add fresh data.
• Headlines that promise but blur the payoff – "Game-changing upgrades" (432 clicks).
  Fix: declare the change.
• Jargon or unfamiliar brands – add a known hook.

6. Red-flag checklist
– Can you add a dollar figure, deadline or danger statistic in the first 12 words?
– Does the teaser name a familiar object, brand or person?
– Is the relevance today, not years away?
– Have we run a similar topic in the last 10 days?
– Preview-pane test (80-character view): key noun + benefit visible without opening the email?

Output format for each article:
1. Headline: …  Sub-line: …
2. Headline: …  Sub-line: …
3. Headline: …  Sub-line: …
4. Headline: …  Sub-line: …
5. Headline: …  Sub-line: …

```

</details>

<details><summary>Data Report Analysis</summary>

```
Before answering, work through this step-by-step reasoning process silently, without showing your work:

1. **UNDERSTAND:** Identify the core question.
2. **ANALYSE:** Break down the key components and metrics in the newsletter stats.
3. **REASON:** Draw logical connections between metrics, content choices and audience behaviour.
4. **SYNTHESISE:** Prioritise the most impactful insights.
5. **CONCLUDE:** Produce the clearest, most helpful answer.

**Role:** You are an email marketing expert. Write as if these are insights being explained to the team, using a third person POV with “we”.

**Audience & style:** Australian readers aged 50+. Use Australian English, a conversational voice, and avoid em dashes. Be confident and practical.

**Inputs:** Newsletter stats will be pasted in any format (JSON, CSV, table or text). Treat missing fields conservatively.

**Output:** A single paragraph only, 90–130 words. Make it actionable with 2–4 specific next steps that the team should take now. Where helpful, reference subject line, preheader, hero, CTA placement, top/bottom links, device split, segment quality, send time/day, frequency, deliverability, unsubscribes and spam complaints.

**Goal:** Improve click-through while protecting deliverability and reducing unsubscribes for an Australian 50+ audience.

**Stats:**
```

</details>

<details><summary>Email reply</summary>

```
‘You are replying on behalf of YourLifeChoices, a newsletter publication for over-50s in Australia.
Write a clear, polite and helpful email response using Australian English and single curly quotation marks.

Use the following rules:

Maintain a warm, respectful tone suitable for an audience aged 50+.

Keep the message concise, friendly and professional.

Address every point raised in the original email.

If the email expresses frustration, acknowledge it calmly and offer reassurance.

If the email asks a question, answer it directly and provide extra useful context if relevant.

If next steps are needed, outline them simply.

Sign off as:
The YourLifeChoices Team

Optional: I may provide a template. If I do, rewrite the reply so that it follows the structure and tone of that template while still matching the context of the email.’
```

</details>

<details><summary>Newsletter review</summary>

```
You are a YourLifeChoices copy editor reviewing a newsletter draft before it goes out.

YourLifeChoices is a newsletter publication for over-50s in Australia.

The user will paste the full raw text of a newsletter. Your job is to find specific copy
problems and suggest fixes — not to validate what already works.

## Output format

For every problem you find, output this block:

[SECTION — e.g. SL A, Headline #3, Sub-line #5, Body copy]
Problem: one sentence saying what is wrong and which rule it breaks.
previous text
->
suggested fix

Skip sections that have no problems. Do not praise what works.

At the very end, output a one-line summary:
X flags — most issues in: [section names]

---

## Rules

### Subject lines (SL A / SL B)
- Each pipe-separated fragment should be 3–5 words. Flag any fragment longer than 5 words.
- The two strongest hooks must be split across SL A and SL B.
- Each line should have a mix of: safety/recall, money shock, household bills,
  super/retirement, familiar brands, health risk, fines.
- Flag if SL B is clearly weaker or softer than SL A.
- Strip filler: "adds", "warning", possessives. Flag if any fragment is padded.

### Headlines
- Target: 5–8 words. Flag if fewer than 5 or more than 8.
- Sentence case only. Flag any title case.
- No attribution: "experts say", "study finds", "researchers warn". Flag and remove.
- Softer stories: hide the specific subject to build curiosity. "Doing this habit" not
  "Using TikTok". Exception: when the name IS the hook (e.g. John Howard, Woolworths).
- Use "us" not "Australians" or "Australians over 50" in headlines.
- Tributes: use present tense — "is being remembered" not "remembered".
- No em-dashes (—). Flag any and suggest a comma or full stop instead.

### Sub-lines
- Target: 10–13 words. Flag if under 8 or over 13.
- One sentence only. Flag if two sentences are joined with a comma, semicolon, or "and".
- No attribution at the end: never end with "experts say", "researchers found",
  "a study found", "authorities warn".
- Do not reveal the full payoff — hint and escalate, do not answer.
- Strong patterns: escalation ("and it is only getting worse"), question form,
  micro-narrative ("She thought stress explained it, but one hard lump changed everything.").
- No em-dashes (—).

### Teasers (headline + sub-line as a pair)
- The pair must answer: why should I care? If neither line makes the personal stake
  clear — money, safety, health, everyday life — flag it.
- Headline hides the subject; sub-line hints without resolving it.
- Must name or strongly imply a concrete noun, familiar brand, household habit, or dollar figure.
- "Experts say" in sub-lines: only acceptable when attribution adds legal credibility.
- Flag vague mystery with no object: "Rare sighting sparks alert", "This new trick changes
  everything", "Experts reveal surprising habit".

### General copy
- Australian English: "favourite", "organisation", "colour", "travelling". Flag American spellings.
- No em-dashes (—) anywhere. Flag every instance.
- No hype words: shocking, unbelievable, insane, game-changing, revolutionary. Flag and replace.
- No jargon without plain-English context.

### Quotes and apostrophes
- Curly single quotes: ' and ' — never straight '
- Curly double quotes: " and " — never straight "
- Curly apostrophes: ' — never straight '
- Flag any straight marks and show the corrected character.

---

## What not to flag
- Do not flag things that follow the rules.
- Do not suggest edits just to rewrite.
- Do not explain what was done correctly.
- Do not pad with section headings for sections with no issues.

```

</details>

---

## The Problem

YLC's newsletter team publishes 9–11 editions per week. Each edition requires:

- 7–12 article teasers (headline + sub-line pairs) written for a highly specific audience

- Daily performance reports (DPR) parsed from raw Campaign Monitor data

- Reader email replies matched to tone and policy

- Content segment generation (trivia, nostalgia, jokes, puzzles)

- Copy review before send

This was largely manual, slow, and inconsistent. The goal was to build a prompt system that a small team could run reliably without deep AI knowledge, where the prompts themselves encode all the expertise.

---

## What Was Built

A modular agentic prompt system across 6 functional areas, each prompt designed to be callable in one step with minimal input from the writer.

---

## Top Prompts

---

### 1. DPR Data Puller: The Most Technically Demanding Prompt

**File:** ylc-ai/prompts/dpr/01-data-puller.md

**The challenge:** Campaign Monitor exports raw link activity in an inconsistent format. The team needed a structured daily performance report from a paste-in data dump, with canonical URLs, click thresholds, segment tracking, horoscope aggregation, and two distinct output formats (narrative + spreadsheet table).

**What makes this prompt engineering:**

The prompt encodes a full parsing pipeline inside natural language:

`URL CANONICALISATION
- Lowercase scheme + host
- Remove trailing "/"
- Strip tracking params: utm_*, fbclid, gclid, ref, hl, pli, beid, lid`

It defines zone-based scanning rules (INTRO ZONE vs TILES ZONE), assigns indexed candidates, handles sponsored content exclusion via asterisk detection, and classifies links by a hard threshold (≥1,000 clicks = Successful). It produces two structurally different outputs from the same inputs: a narrative block for human reading, and a Markdown table pre-formatted for Airtable paste-in.

**Key prompt design choices:**

- `HARD RESET: This run starts fresh.` prevents context bleed across sessions

- `Output ONLY the final formatted report` eliminates preamble and debug commentary

- Explicit segment roster with fixed output order ensures consistency across 150+ editions

- Horoscope grouping logic: star-sign URLs summed and suppressed from other sections

This prompt replaced ~45 minutes of manual data extraction and formatting per edition.

---

### 2. Newsletter Headline Writer: Audience-Encoded Content Generation

**Files:** ylc-ai/prompts/writing/claude-writer.md + ylc-ai/prompts/writing/teasers.md

**The challenge:** Writing 5 distinct headline + sub-line pairs per article that perform for Australians aged 50–75 in a desktop email preview pane. Generic AI output fails this demographic immediately: too American, too vague, no dollar figures, no named brands.

**What makes this prompt engineering:**

The prompt encodes audience intelligence directly:

`Strong headline ingredients:
- dollar figures, deadlines, penalties
- pension, super, tax, Centrelink or bill impact
- nostalgic names or voices
- simple actions with clear consequences`

It enforces five distinct structural frameworks per output (never two of the same type), applies a hard 7-word reading-glasses test for preview panes, and includes a data-backed anti-pattern library:

`"Inflation rebound sparks concern" → 160 clicks (fail)
Fix: "Rising prices could add $412 a year to your grocery bill"

"Rare beach sighting sparks alert" → 214 clicks (fail)  
Fix: "Blue-ringed octopus spotted on Qld beaches – what to do if you see one"`

The anti-patterns are pulled from real click data, not guesses, which makes the prompt a living document of audience behaviour.

**Result:** Consistent 5-option output per article, structured for A/B testing, in ~15 seconds.

---

### 3. DPR Analysis: Chain-of-Thought Structured Reasoning

**File:** ylc-ai/prompts/dpr/02-analysis.md

**The challenge:** Turn raw newsletter stats into a 90–130 word actionable paragraph that a non-analyst newsletter writer can use immediately.

**What makes this prompt engineering:**

This prompt uses an explicit internal reasoning scaffold that runs silently before output:

`1. UNDERSTAND: Identify the core question
2. ANALYSE: Break down key components and metrics
3. REASON: Draw connections between metrics, content, and behaviour
4. SYNTHESISE: Prioritise the most impactful insights
5. CONCLUDE: Produce the clearest, most helpful answer`

The output constraint is precise: one paragraph, 90–130 words, 2–4 specific next steps, written in third-person "we" as if briefing the team. The persona is `email marketing expert` with a domain-specific scope list:

`subject line, preheader, hero, CTA placement, top/bottom links, 
device split, segment quality, send time/day, frequency, 
deliverability, unsubscribes and spam complaints`

This prevents the model from drifting into generic marketing advice. The reasoning stays grounded in the metrics that actually drive newsletter performance.

---

### 4. Email Reply Agent: Template Matching at Scale

**File:** .claude/commands/ylc-email-reply.md

**The challenge:** YLC receives hundreds of reader emails across 23+ distinct scenarios: press releases, unsubscribe requests, game complaints, login issues, forum help, horoscope location, advertising inquiries. Replies had to be consistent with the brand's voice and legally defensible (e.g. unsubscribes).

**What makes this prompt engineering:**

This is a classification + retrieval agent encoded entirely in a prompt. The model:

1. Reads the incoming email

1. Matches it to one of 23 named scenarios with explicit `Use when:` conditions

1. Outputs the exact template, word-for-word, with only bracketed placeholders filled in

The critical constraint:

`CRITICAL: Copy the matching template below word for word, character for character.
The ONLY changes allowed are:
- Substitute [Name] with sender's first name
- Substitute any other [bracketed placeholder] with the relevant detail
- Do NOT rephrase, reword, shorten, expand, or improve the template in any way`

This is deliberate. The brand team approved those exact words. AI helpfulness that "improves" the wording breaks the guarantee. The prompt also handles edge cases: hostile unsubscribers get Version B (direct link, no soft pitch), irate complainers get a different tone path, travel press releases get a different sign-off with the Seniors' Travel Club redirect.

**Result:** Any team member can handle 20+ email types in under 30 seconds with zero judgment calls required.

---

### 5. Newsletter Copy Review: Rule-Based Diff Agent

**File:** .claude/commands/ylc-newsletter-review.md

**The challenge:** Newsletter drafts go out with inconsistent quote marks, em-dashes, American spellings, subject line fragments that are too long, and sub-lines that reveal the full story before the click.

**What makes this prompt engineering:**

This prompt turns a style guide into a structured linting agent. Every rule has an explicit violation condition:

`Headlines: target 5–8 words. Flag if fewer than 5 or more than 8.
Sub-lines: No attribution at the end — never end with "experts say", 
           "researchers found", "a study found"
No em-dashes (—) anywhere. Flag every instance.
Curly quotes only: ' and ' — never straight '`

The output format is a diff-style block per flag:

`[SECTION — e.g. SL A, Headline #3]
Problem: one sentence saying what is wrong and which rule it breaks.
previous text
->
suggested fix`

And critically, a rule for what NOT to output:

`Skip sections that have no problems. Do not praise what works.
Do not suggest edits just to rewrite — only flag genuine violations.`

This keeps the output tight and actionable, not a wall of compliments with one real flag buried at the bottom.

---

## System Design Principles Applied

| Principle | How it shows up in YLC prompts |
|---|---|
| **Encode expertise, not instructions** | Anti-pattern libraries from real click data; audience motivators ranked by engagement |
| **Constrain the output format exactly** | Word counts, diff blocks, fixed table schemas, roster order |
| **Separate reasoning from output** | Silent chain-of-thought in DPR analysis; `HARD RESET` in data puller |
| **Make failure explicit** | `If URL cannot be accessed, say: "Could not access this URL"` |
| **Match output to the next tool in the workflow** | Spreadsheet table pre-formatted for Airtable paste; narrative blocks for Google Doc insert |
| **Prevent AI helpfulness from breaking guarantees** | Template agent locked to exact wording; no rephrasing allowed |

---

## Impact

- ~45 min saved per DPR (Daily Performance Report): data puller + analysis run in under 2 minutes

- 5 headline options per article in ~15 seconds, vs. 10–20 min manual writing

- 23 email scenarios handled without judgment calls, with consistent voice, zero rewrites

- Pre-send copy review in ~30 seconds, catching curly quote issues, em-dashes, attribution phrases that reduce click-through

The system runs inside Claude Code, with skills triggered by slash commands (`/ylc-email-reply`, `/ylc-newsletter-review`), giving the team one-word access to the full prompt stack.
