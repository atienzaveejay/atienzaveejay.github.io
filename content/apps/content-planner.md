---
title: Content Planner
summary: A multi-client social content calendar where drafted posts are pushed in bulk from the command line and client feedback comes back the same way.
stack: Next.js, Neon Postgres, Resend, Vercel Blob
order: 3
---
## The problem

Running social for several clients at once, the slow part was never writing the posts. It was moving them: drafts in one place, approvals in a chat thread, assets in a Drive folder, and the final copy pasted by hand into a scheduler.

## What I built

A calendar app with one workspace per client. Each client has their brand rules, CTA and hashtag snippets, and weekly post targets per platform, so drafts start on-brand.

The part I use most is the command line. I draft a month of posts in a file, preview the push, then send all of it to the calendar in one go. When the client leaves feedback, I pull it back down and revise in bulk instead of post by post.

- Email-link sign-in, with row-level security so each client only sees their own calendar
- Private file storage for images and videos attached to posts
- A full month for one client (29 posts) goes from draft to the client's review in minutes

## Stack

Next.js on Vercel, Neon Postgres with row-level security, Resend for sign-in emails, and Vercel Blob for files.
