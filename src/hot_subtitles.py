#!/usr/bin/env python3
import argparse
import os
import subprocess
import whisper

# Dependencies
# sudo apt update
# sudo apt install ffmpeg python3-pip
# pip3 install --upgrade openai-whisper

# Usage
# $ python3 hot_subtitles.py path/to/video.mp4

# Configuration
MODEL_SIZE = "small"    # options: tiny, base, small, medium, large
LANGUAGE = "en"        # options: en, ru
DEVICE = "cpu"         # options: cpu, cuda
FONT_SIZE_DEFAULT = 128   # default font size in points
MARGIN_V_DEFAULT = 1280   # default vertical margin in pixels


def get_video_resolution(input_video):
    """
    Get video resolution (width, height) using ffprobe
    """
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0:s=x",
        input_video
    ]
    output = subprocess.check_output(cmd).decode().strip()
    width, height = map(int, output.split('x'))
    return width, height


def format_timestamp_ass(seconds):
    """
    Convert seconds to ASS timestamp H:MM:SS.CS (centiseconds)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int((seconds - int(seconds)) * 100)
    return f"{hours:d}:{minutes:02d}:{secs:02d}.{centis:02d}"


def write_ass(segments, ass_path, fontsize, margin_v, video_w, video_h):
    """
    Generate ASS subtitle file with dynamic resolution
    """
    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        f"PlayResX: {video_w}\n"
        f"PlayResY: {video_h}\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,Arial,{fontsize},&H00FFFFFF,&H000000FF,0,0,3,1,0,8,10,10,{margin_v},1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Text\n"
    )
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header)
        for seg in segments:
            for w in seg["words"]:
                start = format_timestamp_ass(w["start"])
                end = format_timestamp_ass(w["end"])
                text = w["word"].replace("{", r"\{").replace("}", r"\}")
                f.write(f"Dialogue: 0,{start},{end},Default,{text}\n")


def burn_subtitles(input_video, ass_file, output_video):
    """
    Burn ASS subtitles into the video using ffmpeg
    """
    cmd = [
        "ffmpeg",
        "-i", input_video,
        "-vf", f"ass={ass_file}",
        "-c:v", "libx264",
        "-crf", "23",
        "-c:a", "copy",
        output_video
    ]
    subprocess.run(cmd, check=True)


def find_next_output(input_path):
    """
    Generate a non-colliding output filename in the same directory as input
    """
    directory = os.path.dirname(input_path) or "."
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    i = 0
    while True:
        suffix = f"{i}" if i > 0 else ""
        filename = f"{base_name}_subtitled{suffix}.mp4"
        output_path = os.path.join(directory, filename)
        if not os.path.exists(output_path):
            return output_path
        i += 1


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path to input MP4 video")
    parser.add_argument("-m", "--model", default=MODEL_SIZE,
                        choices=["tiny","base","small","medium","large"], help="Whisper model size")
    parser.add_argument("--device", choices=["cpu","cuda"], default=DEVICE, help="Device for inference")
    parser.add_argument("-s", "--size", type=int, default=FONT_SIZE_DEFAULT, help="Subtitle font size")
    parser.add_argument("-v", "--margin_v", type=int, default=MARGIN_V_DEFAULT, help="Vertical subtitle margin")
    parser.add_argument("-l", "--language", default=LANGUAGE, choices=["en","ru"], help="Transcription language")
    args = parser.parse_args()

    # Determine video resolution for correct subtitle placement
    width, height = get_video_resolution(args.input)

    # Prepare ASS file path and safe output file path
    base, _ = os.path.splitext(args.input)
    ass_path = f"{base}.ass"
    output_path = find_next_output(args.input)

    # Load Whisper model
    model = whisper.load_model(args.model, device=args.device)

    # Transcribe video with word-level timestamps
    result = model.transcribe(args.input, language=args.language, word_timestamps=True)

    # Write subtitles to ASS file
    write_ass(result["segments"], ass_path, args.size, args.margin_v, width, height)

    # Burn subtitles into video using ffmpeg
    burn_subtitles(args.input, ass_path, output_path)

    # Notify about saved output
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()

