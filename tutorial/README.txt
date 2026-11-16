GUITAR PRACTICE VIDEOS
======================
Eight videos: an overview plus one for each part of the app. Each is a set of still frames
(videos/<name>/frames) and the words spoken over each frame (videos/<name>/scenes.json).
The voice is added on your own computer with Microsoft's free online neural voices (edge-tts),
the same as the check register tutorial, so it needs an internet connection.

MAKE THE VIDEOS
  Mac:      double-click "Make Videos (Mac).command"
            (first time: if macOS won't open it, right-click it > Open > Open)
  Windows:  double-click "Make Videos (Windows).bat"
  Needs Python 3 and ffmpeg. It takes a few minutes; when it's done the "finished" folder opens.

  Each frame is held for exactly as long as its line takes to say, so the voice always lines up.
  Running it again only redoes what changed (voice clips and scenes are kept in cache/).

WHAT YOU GET (in finished/)
  01 Overview.mp4               the video, 1920x1080, with captions you can switch on
  01 Overview.srt               captions file - upload it to YouTube (Subtitles > Upload file)
  01 Overview - YouTube.txt     title, description and chapter times to paste into YouTube
  01 Overview - thumbnail.jpg   thumbnail to upload to YouTube
  Replace "[download link]" in the YouTube.txt files with where people can get the app.

OPTIONS (from Terminal in this folder)
  bash "Make Videos (Mac).command" 05                       just video 05
  bash "Make Videos (Mac).command" --voice en-US-GuyNeural  a different voice
  bash "Make Videos (Mac).command" --rate -5%               a little slower (+5% is faster)

CHANGING THE WORDS
  Edit the "text" of a scene in videos/<name>/scenes.json and run it again.
  "chapter" marks where a YouTube chapter starts.

The screens were filmed with made-up demo practice data, not your own log.
