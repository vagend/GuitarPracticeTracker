"""Makes the Guitar Practice video series, with a natural voice.

Each video is a set of still frames (videos/<name>/frames) and the words for each frame
(videos/<name>/scenes.json). This script voices every line with Microsoft's free online neural
voices (edge-tts, the same as the check register tutorial), holds each frame for exactly as long as
its line takes to say, and writes the finished video plus files for YouTube into finished/:

    01 Overview.mp4              the video (1920x1080, 30 fps, captions you can switch on)
    01 Overview.srt              captions file to upload to YouTube
    01 Overview - YouTube.txt    title, description and chapter times to paste into YouTube
    01 Overview - thumbnail.jpg  thumbnail to upload to YouTube

Needs Python 3, ffmpeg and an internet connection.
    python make_videos.py                          all videos, voice en-US-AriaNeural
    python make_videos.py 05                       just the videos whose folder starts with 05
    python make_videos.py --voice en-US-GuyNeural  a different voice (see: edge-tts --list-voices)
    python make_videos.py --rate -5%               a little slower (+5% is faster)
Voice clips and encoded scenes are kept in cache/, so running it again only redoes what changed.
"""
import argparse, asyncio, hashlib, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEOS, OUT, CACHE = os.path.join(HERE, "videos"), os.path.join(HERE, "finished"), os.path.join(HERE, "cache")
LEAD, TAIL, LAST_TAIL, FPS = 0.4, 0.8, 2.0, 30

ap = argparse.ArgumentParser()
ap.add_argument("only", nargs="*")
ap.add_argument("--voice", default="en-US-AriaNeural")
ap.add_argument("--rate", default="+0%")
ap.add_argument("--test-voice", action="store_true", help=argparse.SUPPRESS)  # offline stand-in voice, for testing the pipeline
A = ap.parse_args()
os.makedirs(OUT, exist_ok=True); os.makedirs(CACHE, exist_ok=True)
LOG = open(os.path.join(HERE, "make_videos.log"), "w", encoding="utf-8")

def say(*a):
    print(*a); print(*a, file=LOG); LOG.flush()

def ff(*args):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], capture_output=True, text=True)
    if r.returncode:
        say("ffmpeg failed:", " ".join(args)); say(r.stderr); sys.exit(1)

def seconds(path, stream=None):
    sel = ["-select_streams", stream, "-show_entries", "stream=duration"] if stream else ["-show_entries", "format=duration"]
    out = subprocess.check_output(["ffprobe", "-v", "error", *sel, "-of", "csv=p=0", path]).decode().split()
    return float(out[0]) if out and out[0] not in ("N/A", "") else 0.0

def h(*parts):
    return hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:16]

def stamp(t, srt=True):
    ms = int(round(t * 1000)); hh, ms = divmod(ms, 3600000); mm, ms = divmod(ms, 60000); ss, ms = divmod(ms, 1000)
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}" if srt else (f"{hh}:{mm:02d}:{ss:02d}" if hh else f"{mm}:{ss:02d}")

# pick an H.264 encoder this ffmpeg has
ENC = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
if " libx264 " in ENC:
    VCODEC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-tune", "stillimage"]
elif "h264_videotoolbox" in ENC:
    VCODEC = ["-c:v", "h264_videotoolbox", "-b:v", "8M"]
else:
    VCODEC = ["-c:v", "mpeg4", "-q:v", "2"]

async def voice_clip(text, voice):
    path = os.path.join(CACHE, "voice-" + h(voice, A.rate, text, A.test_voice) + ".mp3")
    if not os.path.exists(path):
        if A.test_voice:
            tf = tempfile.mktemp(suffix=".txt"); open(tf, "w").write(text)
            ff("-f", "lavfi", "-i", f"flite=textfile={tf}:voice=slt", "-ar", "48000", path + ".tmp.mp3")
        else:
            import edge_tts
            await edge_tts.Communicate(text, voice, rate=A.rate).save(path + ".tmp.mp3")
        os.replace(path + ".tmp.mp3", path)
    return path

def scene_video(frame, dur, first, last):
    path = os.path.join(CACHE, "scene-" + h(hashlib.sha1(open(frame, "rb").read()).hexdigest(), f"{dur:.3f}", first, last, VCODEC) + ".mp4")
    if not os.path.exists(path):
        vf = f"scale=1920:1080,format=yuv420p,loop=-1:1,trim=duration={dur:.3f}"
        if first: vf += ",fade=t=in:st=0:d=0.5"
        if last: vf += f",fade=t=out:st={max(0, dur - 1.0):.3f}:d=1.0"
        ff("-framerate", str(FPS), "-i", frame, "-vf", vf, "-r", str(FPS), *VCODEC, "-pix_fmt", "yuv420p", path + ".tmp.mp4")
        os.replace(path + ".tmp.mp4", path)
    return path

def split_even(words, parts):
    """Split a list of words into `parts` runs of roughly equal character length."""
    total = sum(len(w) + 1 for w in words); out, cur, size = [], [], 0
    for w in words:
        if cur and len(out) < parts - 1 and size + len(w) / 2 > total * (len(out) + 1) / parts:
            out.append(cur); cur = []
        cur.append(w); size += len(w) + 1
    out.append(cur)
    return out

def caption_chunks(text, dur, start):
    """Captions: one cue per sentence (long sentences split evenly), at most two balanced lines of ~42 characters."""
    sentences = re.findall(r"[^.!?]+[.!?]*", text)
    chunks = []
    for snt in (x.strip() for x in sentences if x.strip()):
        words = snt.split(); n = max(1, -(-len(snt) // 84))
        chunks += [" ".join(c) for c in split_even(words, n)]
    total = sum(len(c) for c in chunks); t, cues = start, []
    for c in chunks:
        d = dur * len(c) / total
        lines = [" ".join(x) for x in split_even(c.split(), 2)] if len(c) > 42 else [c]
        cues.append((t, t + d, "\n".join(lines))); t += d
    return cues

async def make(folder, voice, names):
    meta = json.load(open(os.path.join(folder, "scenes.json"), encoding="utf-8"))
    name = os.path.basename(folder); num = name[:2]
    base = f"{num} {meta['short'].replace('/', '-')}"
    say(f"\n=== {base} ({len(meta['scenes'])} scenes)")
    scenes, pieces, tmp = meta["scenes"], [], tempfile.mkdtemp()
    t, cues, chapters, vlist = 0.0, [], [], []
    for i, sc in enumerate(scenes):
        first, last = i == 0, i == len(scenes) - 1
        clip = await voice_clip(sc["text"], voice)
        talk = seconds(clip)
        lead = 0.7 if first else LEAD
        dur = -(-round((lead + talk + (LAST_TAIL if last else TAIL)) * FPS * 1000) // 1000) / FPS   # whole frames, so sound and picture never drift
        vlist.append(scene_video(os.path.join(folder, sc["frame"]), dur, first, last))
        piece = os.path.join(tmp, f"{i:03d}.wav")
        ms = int(lead * 1000)
        ff("-i", clip, "-af", f"adelay={ms}|{ms},apad=whole_dur={dur:.3f}", "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", piece)
        pieces.append(piece)
        if sc.get("chapter"): chapters.append((t, sc["chapter"]))
        cues += caption_chunks(sc["text"], talk, t + lead)
        say(f"  scene {i + 1:2d}: {dur:5.1f} s  {sc['text'][:60]}")
        t += dur
    with open(os.path.join(tmp, "v.txt"), "w") as f: f.writelines(f"file '{p}'\n" for p in vlist)
    with open(os.path.join(tmp, "a.txt"), "w") as f: f.writelines(f"file '{p}'\n" for p in pieces)
    ff("-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "v.txt"), "-c", "copy", os.path.join(tmp, "video.mp4"))
    ff("-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "a.txt"), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", os.path.join(tmp, "voice.wav"))
    srt = os.path.join(OUT, base + ".srt")
    with open(srt, "w", encoding="utf-8") as f:
        for k, (a, b, txt) in enumerate(cues, 1): f.write(f"{k}\n{stamp(a)} --> {stamp(b)}\n{txt}\n\n")
    mp4 = os.path.join(OUT, base + ".mp4")
    ff("-i", os.path.join(tmp, "video.mp4"), "-i", os.path.join(tmp, "voice.wav"), "-i", srt,
       "-map", "0:v", "-map", "1:a", "-map", "2:s", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-c:s", "mov_text",
       "-metadata:s:s:0", "language=eng", "-metadata:s:s:0", "title=English", "-disposition:s:0", "-default",
       "-metadata", f"title={meta['title']}", "-t", f"{t:.3f}", "-movflags", "+faststart", mp4 + ".tmp.mp4")
    os.replace(mp4 + ".tmp.mp4", mp4)
    # YouTube chapters: first at 0:00, at least three, each at least 10 seconds long
    ch = [chapters[0]] if chapters else []
    for c in chapters[1:]:
        if c[0] - ch[-1][0] >= 10: ch.append(c)
    while len(ch) > 1 and t - ch[-1][0] < 10: ch.pop()
    others = [n for n in names if n != base]
    try: link = json.load(open(os.path.join(VIDEOS, "series.json"), encoding="utf-8")).get("link") or "[download link]"
    except Exception: link = "[download link]"
    yt = [meta["title"], "", meta["description"], "", "Get the app: " + link, ""]
    if len(ch) >= 3: yt += ["Chapters"] + [f"{stamp(a, False)} {b}" for a, b in ch] + [""]
    yt += ["More videos in this series:"] + [f"• {n[3:]}" for n in others]
    open(os.path.join(OUT, base + " - YouTube.txt"), "w", encoding="utf-8").write("\n".join(yt) + "\n")
    shutil.copy(os.path.join(folder, "thumbnail.jpg"), os.path.join(OUT, base + " - thumbnail.jpg"))
    got = seconds(mp4, "a:0")
    if got < t - 1:
        say(f"PROBLEM: {base}.mp4 has only {got:.1f} s of sound for {t:.1f} s of video"); sys.exit(1)
    say(f"  done: {base}.mp4  {int(t // 60)}:{int(t % 60):02d}")
    shutil.rmtree(tmp, ignore_errors=True)

async def main():
    say(subprocess.check_output(["ffmpeg", "-version"]).decode().splitlines()[0], "| video encoder:", VCODEC[1])
    voice = A.voice
    if not A.test_voice:
        import edge_tts
        voices = {v["ShortName"] for v in await edge_tts.list_voices()}
        if voice not in voices:
            fallback = sorted(v for v in voices if v.startswith("en-US-") and v.endswith("Neural"))[0]
            say(f"{voice} was not found, using {fallback} instead"); voice = fallback
    say("voice:", "test (offline stand-in)" if A.test_voice else voice, "rate:", A.rate)
    folders = sorted(os.path.join(VIDEOS, d) for d in os.listdir(VIDEOS) if os.path.isfile(os.path.join(VIDEOS, d, "scenes.json")))
    names = [f"{os.path.basename(f)[:2]} {json.load(open(os.path.join(f, 'scenes.json'), encoding='utf-8'))['short']}" for f in folders]
    for f in folders:
        if not A.only or any(os.path.basename(f).startswith(o) for o in A.only):
            await make(f, voice, names)
    say(f"\nAll done. The videos are in: {OUT}")

asyncio.run(main())
