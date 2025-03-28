import json
import subprocess

# קובץ הפלט של whisper
with open("audio.json", encoding="utf-8") as f:
    data = json.load(f)

mute_segments = []

# חיפוש כל המופעים של המילה "אחי"
for segment in data["segments"]:
    text = segment["text"]
    if "אחי" in text:
        start = segment["start"]
        end = segment["end"]
        mute_segments.append((start, end))

# מייצר פילטרים שמנמיכים את הווליום ל-0
volume_filters = [
    f"volume=enable='between(t,{start},{end})':volume=0"
    for start, end in mute_segments
]

filter_str = ",".join(volume_filters)

# הרצת ffmpeg עם הפילטרים
cmd = [
    "ffmpeg", "-i", "Untitled.mov", "-af", filter_str, "-c:v", "copy", "output.mp4"
]

subprocess.run(cmd)
