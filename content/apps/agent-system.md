---
title: My AI task and agent system
summary: A personal task app wired to background AI agents that pull in to-dos from every client tool, then draft and hand back work for my review.
stack: Next.js, Supabase, Claude Code, DeepSeek, launchd
order: 5
---
## Why

I work across several clients, and each one lives in a different tool: Notion, Slack, Gmail, a shared Google Sheet, meeting notes. Keeping one honest to-do list by hand was a job in itself.

## What I built

- **A task app** (Next.js and Supabase) with day and week views, a backlog, recurring tasks, Google Calendar sync and a chat assistant. It replaced my Notion task database.
- **A nightly sweep** that runs on my Mac at midnight, reads new to-dos from every client tool, removes duplicates and adds what's missing.
- **Agent triage.** I go through tasks one client at a time and decide who does each one: me, my assistant, or an AI agent. Agents run in the background, and their output comes back as an "In Review" task for me to approve. Nothing goes to a client without my sign-off.
- **Skills for repeat work.** Recurring jobs (a newsletter build, a performance report, a video edit) are written down as step-by-step skills with the rules each client has given me, so the agents get better with every round of feedback.

## The point

The system doesn't replace judgment. It moves my time from collecting and formatting to deciding and reviewing, which is the part clients actually pay for.
