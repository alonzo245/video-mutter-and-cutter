import subprocess
import os
import sys
import tempfile

VIDEO_FILE = sys.argv[1] if len(sys.argv) > 1 else "output.mp4"
OUTPUT_FILE = "output_cut.mp4"
TEMP_LIST = "segments.txt"
SILENCE_THRESHOLD = -50  # dB
MIN_SILENCE_DURATION = 0.1  # seconds

def get_silent_regions(video_path):
    """ Use ffmpeg to detect silent parts """
    cmd = [
        "ffmpeg", "-i", video_path,
        "-af", f"silencedetect=noise={SILENCE_THRESHOLD}dB:d={MIN_SILENCE_DURATION}",
        "-f", "null", "-"
    ]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
    lines = result.stderr.splitlines()
    silent_regions = []
    start_time = None
    for line in lines:
        if "silence_start" in line:
            start_time = float(line.strip().split("silence_start: ")[-1])
        elif "silence_end" in line and start_time is not None:
            end_time = float(line.strip().split("silence_end: ")[-1].split(" ")[0])
            silent_regions.append((start_time, end_time))
            start_time = None
    return silent_regions

def get_video_duration(video_path):
    result = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", video_path
    ])
    return float(result.decode().strip())

def invert_ranges(silent_ranges, duration):
    """ Return non-silent (keep) ranges """
    if not silent_ranges:
        return [(0, duration)]
    ranges = []
    last_end = 0
    for start, end in silent_ranges:
        if start > last_end:
            ranges.append((last_end, start))
        last_end = max(last_end, end)
    if last_end < duration:
        ranges.append((last_end, duration))
    return ranges

def extract_segments(video_path, ranges):
    segment_files = []
    for i, (start, end) in enumerate(ranges):
        temp_file = f"part_{i}.mp4"
        duration = end - start
        subprocess.run([
            "ffmpeg", "-y",
            "-ss", str(start), "-t", str(duration),
            "-i", video_path,
            "-c:v", "h264_videotoolbox", "-c:a", "aac",
            "-movflags", "+faststart",
            temp_file
        ])
        segment_files.append(temp_file)
    return segment_files

def concatenate_segments(segment_files, output_path):
    with open(TEMP_LIST, "w") as f:
        for file in segment_files:
            f.write(f"file '{os.path.abspath(file)}'\n")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", TEMP_LIST, "-c", "copy", output_path
    ])

def clean_temp_files(files):
    for f in files + [TEMP_LIST]:
        if os.path.exists(f):
            os.remove(f)

# === RUN ===

print(f"🔍 Detecting silence in {VIDEO_FILE}...")
silent_regions = get_silent_regions(VIDEO_FILE)
print(f"Found {len(silent_regions)} silent parts.")

duration = get_video_duration(VIDEO_FILE)
keep_ranges = invert_ranges(silent_regions, duration)

print(f"✂️ Extracting {len(keep_ranges)} segments...")
segment_files = extract_segments(VIDEO_FILE, keep_ranges)

print("🧩 Concatenating final video...")
concatenate_segments(segment_files, OUTPUT_FILE)

clean_temp_files(segment_files)
print(f"✅ Done. Saved to: {OUTPUT_FILE}")
