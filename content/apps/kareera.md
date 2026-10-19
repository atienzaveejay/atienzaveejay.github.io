---
title: Kareera
summary: An AI interviewer for Filipino job seekers. It asks what Philippine employers actually ask, pushes back on thin answers, and scores how you came across.
stack: Next.js, Supabase, DeepSeek, Google Speech-to-Text and WaveNet, MediaPipe, PayMongo, Vercel
url: https://kareera.co
order: 1
cover: /assets/kareera/home.webp
metrics:
  - 1,880+ | real interview questions
  - 109 | Philippine companies covered
  - 4 | interview modes, from video call to typed
---
## The problem

Most Filipino corporate and BPO applicants don't fail on what they know. They fail on the spoken interview. On r/phcareers and r/BPOinPH the same pains come up again and again: blanking in English in front of a senior manager, being "fluent in writing but not live", and having no one to practise with.

Generic AI tools give generic questions. Career offices barely run mock interviews. Google's Interview Warmup shut down in April 2026. That left a gap for a practice partner built around Philippine employers.

## What I built

Kareera is my own product, registered as a business in the Philippines. I own the product calls, pricing and marketing, and I build it with Claude Code. Since July 2026 that has meant 270+ commits and 40+ merged pull requests.

@[video](/assets/kareera/what-is-kareera.mp4)

### The mock interviewer

- **Four modes.** Video call, phone call, answer out loud, or type your answers.
- **Three interviewer personas** (Mia, Paolo and Carmela), each with their own voice and an animated avatar whose mouth follows the audio.
- **It pushes back.** Thin answers get follow-up questions, and the candidate can ask the interviewer to clarify a question without it counting against them.
- **Feedback after every answer:** a communication score, a rewritten version of the answer, and up to three retries.
- **Camera checks that stay private.** Face tracking runs in the browser with MediaPipe, and only counts (like eye contact) leave the device, never video frames.

### Picking what to practise

Candidates choose a role or a company and the two filter each other, across 202 role and company pairs. If their job isn't listed they can paste the job post, and the interview is built from it. Every pasted post is saved so I can see which roles to cover next.

![Kareera question bank](/assets/kareera/questions.webp)

### SEO content that feeds the product

The question bank and company guides are free and indexable. Each question page links straight into an interview built around it, so search traffic lands one click away from the product. It's the same funnel logic I ran at Interview Query, applied to a market I know better.

## Pricing from real cost data

I didn't want to guess prices. Every speech, voice and model call writes a row to a usage table tied to one interview, and an admin page shows the average and 90th percentile cost per interview by mode. A quick voice interview came out at about ₱5 and a full one at ₱12 to ₱18.

That data moved Kareera from unlimited plans to credits: a quick interview costs one credit, a full one costs two. Plans run from a free tier to ₱1,199 for 90 days, with a ₱99 top-up.

![Kareera pricing](/assets/kareera/pricing.webp)

## Hardening it

Before marketing it properly I ran a full audit of the site and fixed all 59 findings: security, payments, interview reliability, SEO and performance. That included turning on transactional email with proper domain authentication, enforcing a content security policy, and an opt-in flow for marketing email under the Data Privacy Act.

## Where it is now

Kareera is live and pre-revenue. Marketing is focused on fresh graduates and career switchers going for corporate roles, through student organisations, Facebook groups and short-form video. I'm sharing it here as proof that I can take a product from idea to a working, priced, secure app, not as a traction story yet.
