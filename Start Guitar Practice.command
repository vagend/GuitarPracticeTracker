#!/bin/bash
# Starts the Guitar Practice app on this Mac and opens it in your browser.
# Only needed the first time (to install it) and after you replace the files with a new version.
# Once installed, the app opens from your Dock/Launchpad without this running.
cd "$(dirname "$0")" || exit 1
PORT=8642
URL="http://localhost:$PORT/index.html"

open_app() {
  if [ -d "/Applications/Google Chrome.app" ]; then open -a "Google Chrome" "$URL"
  elif [ -d "/Applications/Microsoft Edge.app" ]; then open -a "Microsoft Edge" "$URL"
  else open "$URL"; fi
}

if curl -s -o /dev/null "http://localhost:$PORT/index.html"; then
  echo "Guitar Practice is already running."; open_app; exit 0
fi

echo "Starting Guitar Practice at $URL"
echo "Leave this window open while you use or install the app. Close it (or press Ctrl+C) to stop."
(sleep 1; open_app) &
if command -v python3 >/dev/null 2>&1 && python3 -c "import http.server" >/dev/null 2>&1; then
  exec python3 -m http.server "$PORT" --bind 127.0.0.1
elif command -v ruby >/dev/null 2>&1; then
  exec ruby -run -e httpd . -p "$PORT" -b 127.0.0.1
else
  echo "Couldn't find python3 on this Mac. Install Apple's command line tools by running:  xcode-select --install"
  read -r -p "Press Return to close."
fi
