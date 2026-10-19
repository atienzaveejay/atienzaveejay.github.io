---
title: Programmatic video editing in DaVinci Resolve
summary: A pipeline that edits talking-head videos through Resolve's Python API: cuts from the transcript, graphics timed to speech, music, and word-timed captions.
stack: Python, DaVinci Resolve Studio API, whisper.cpp, ffmpeg, Remotion
order: 2
cover: /assets/video-pipeline/cover.webp
metrics:
  - 15 | versions of a sales video, each a re-render not a re-edit
  - 20 | YouTube Shorts cut from two long-form videos in one pass
  - 1 | script per video, so every edit is repeatable
---
## Why I built it

Clients kept sending me hours of raw talking-head footage: teleprompter takes, webinar recordings, interviews. Editing by hand meant every round of feedback ("cut that stutter", "the music is too loud", "use the other take") cost an afternoon. I wanted feedback to cost a re-render instead.

## How it works

DaVinci Resolve Studio ships a Python scripting API. I drive it from scripts I write with Claude Code:

1. **Transcribe** the raw takes with whisper.cpp, with word-level timings.
2. **Cut from the transcript.** The edit is a list of phrase ranges in a script, so swapping a take or trimming a sentence is a one-line change.
3. **Time the graphics to the words.** Motion graphics (built in Remotion or rendered as overlays) appear on the exact word they illustrate.
4. **Mix the audio** to a target loudness, with a music bed that ducks under speech and sound effects on the graphics.
5. **Burn in captions** word by word, styled for each brand.
6. **Render and check.** I re-transcribe the render to confirm every cut landed where the script says it should.

## What it has produced

- A long-form sales video for a business coach, taken through 15 rounds of review notes.
- Long-form YouTube videos and 20 Shorts for an executive career coach, cut from two masters in one pass and scheduled straight to YouTube.
- Product reels for [Kareera](/apps/kareera/).

## What I learned

Most of the work was in the edge cases the API doesn't document. Timeline frames are absolute, not relative to the start. Re-imported audio can play a cached old version. Keyframes can't be set by script at all. I wrote each one down as a rule, so the next video starts from everything the last one taught me.
