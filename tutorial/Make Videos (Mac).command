#!/bin/bash
# Double-click to make the Guitar Practice videos with the natural voice.
# Sets up a private Python environment next to this file the first time and installs edge-tts into it.
# Needs an internet connection while it runs. Optional, from Terminal:
#   bash "Make Videos (Mac).command" 05                    just video 05
#   bash "Make Videos (Mac).command" --voice en-US-GuyNeural --rate -5%
cd "$(dirname "$0")" || exit 1
if ! command -v ffmpeg >/dev/null 2>&1; then
  for p in /opt/homebrew/bin /usr/local/bin; do [ -x "$p/ffmpeg" ] && export PATH="$p:$PATH"; done
fi
command -v ffmpeg >/dev/null 2>&1 || { echo "ffmpeg wasn't found. Install it (for example: brew install ffmpeg) and try again."; read -r -p "Press Return to close."; exit 1; }
[ -d .venv ] || python3 -m venv .venv || { echo "Could not create the environment. Install Python 3 from python.org and try again."; read -r -p "Press Return to close."; exit 1; }
.venv/bin/python -m pip install -q edge-tts || { echo "Could not install edge-tts (is the internet connected?)"; read -r -p "Press Return to close."; exit 1; }
.venv/bin/python make_videos.py "$@" && open finished
read -r -p "Press Return to close."
