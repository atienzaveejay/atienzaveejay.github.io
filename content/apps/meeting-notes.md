---
title: Meeting Notes
summary: A Mac app that records calls, transcribes them on the device, and writes structured notes with a suggested title and client.
stack: Swift, Node.js, whisper.cpp, CoreAudio, BlackHole
order: 4
---
## Why

I'm on calls with several clients a week and wanted notes I didn't have to take, without sending client conversations to a third-party recorder.

## How it works

- **Records both sides.** My mic and the call audio are captured as separate channels through a loopback device.
- **Transcribes on the Mac** with whisper.cpp's large-v3-turbo model. A "keep fully local" setting skips the AI notes step entirely.
- **Stops itself.** It watches which apps are using the microphone, and when the call app lets go, it asks whether to stop and stops after five minutes if nobody answers.
- **Cleans the transcript**, removing echo from speaker playback and the looping phrases speech models sometimes hallucinate from room noise.
- **Combines split recordings** when a call drops and restarts, and suggests a title and client for each meeting.

## What I learned

The first version produced garbage transcripts for a week, and the model wasn't the cause. It was recording the webcam mic for both sides of the call. Now each meeting stores its device choices and audio levels, so a bad transcript can be traced in a minute instead of a guess.
