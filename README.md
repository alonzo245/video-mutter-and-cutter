# Video Silence Remover

A Python script that automatically detects and removes silent parts from videos. This tool is useful for cleaning up videos by removing unnecessary pauses and silent segments.

## Features

- Detects silent segments in videos using audio analysis
- Removes silent parts while preserving video quality
- Supports various video formats (mp4, mov, etc.)
- Maintains original video quality and resolution
- Preserves audio quality

## Requirements

- Python 3.x
- FFmpeg installed on your system
- macOS (for h264_videotoolbox encoder)

## Installation

1. Clone this repository:

```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

## Usage

Basic usage:

```bash
python cut_mute_parts.py input_video.mp4
```

The script will:

1. Analyze the video for silent segments
2. Remove those segments
3. Create a new video file named `output_cut.mp4`

### Parameters

- `SILENCE_THRESHOLD`: -50 dB (adjustable in the script)
- `MIN_SILENCE_DURATION`: 0.5 seconds (adjustable in the script)

## Output

The script generates:

- `output_cut.mp4`: The final video with silent parts removed
- Temporary files (automatically cleaned up after processing)

## Notes

- The script uses FFmpeg's silencedetect filter to identify silent segments
- Video quality is preserved using the h264_videotoolbox encoder
- The script automatically cleans up temporary files after processing

## License

MIT License
