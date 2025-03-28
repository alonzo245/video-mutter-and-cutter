import subprocess
from faster_whisper import WhisperModel
import re
import os

VIDEO_FILE = "Untitled_longer.mov"
AUDIO_FILE = "audio.wav"
OUTPUT_FILE = "output.mp4"
KEYWORD = "אחי"
MUTE_PADDING = 0.1  # שניות לפני ואחרי

def normalize(word: str) -> str:
    word = word.lower()
    word = re.sub(r'[^\u0590-\u05EA]', '', word)
    word = word.replace('ך', 'כ').replace('ם', 'מ').replace('ן', 'נ').replace('ף', 'פ').replace('ץ', 'צ')
    return word

print("🎧 Extracting audio...")
subprocess.run(["ffmpeg", "-y", "-i", VIDEO_FILE, "-q:a", "0", "-map", "a", AUDIO_FILE])

print("🧠 Transcribing...")
model = WhisperModel("medium", compute_type="auto")
segments, _ = model.transcribe(AUDIO_FILE, language="he", word_timestamps=True)

mute_ranges = []
for segment in segments:
    for word in segment.words:
        if normalize(word.word) == KEYWORD:
            start = max(0, word.start - MUTE_PADDING)
            end = word.end + MUTE_PADDING
            mute_ranges.append((start, end))

if not mute_ranges:
    print("✅ No 'אחי' found.")
    exit()

print(f"🔇 Found {len(mute_ranges)} 'אחי' to mute. Ranges:")
for i, (start, end) in enumerate(mute_ranges):
    print(f"  {i+1}: {start:.2f}s → {end:.2f}s")

# Create volume filter complex
volume_filter = []
for i, (start, end) in enumerate(mute_ranges):
    volume_filter.append(f"volume=0:enable='between(t,{start},{end})'")

# Combine all volume filters
volume_filter_str = ",".join(volume_filter)

print("🔊 Applying mute filters...")
subprocess.run([
    "ffmpeg", "-y",
    "-i", VIDEO_FILE,
    "-af", volume_filter_str,
    "-c:v", "copy",
    OUTPUT_FILE
])

# ניקוי
if os.path.exists(AUDIO_FILE):
    os.remove(AUDIO_FILE)

print(f"✅ Final video saved as: {OUTPUT_FILE}")
