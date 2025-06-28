import os
from TTS.api import TTS


# Dependencies:
# sudo apt update
# sudo apt install -y git python3 python3-pip ffmpeg libsndfile1 libatlas-base-dev espeak
# python3 -m venv tts_env
# source tts_env/bin/activate
# pip install --upgrade pip
# pip install TTS
# pip install torch==2.0.1+cpu torchvision==0.15.2+cpu -f https://download.pytorch.org/whl/torch_stable.html


# ====== Configuration ======
MODEL_NAME = "tts_models/en/vctk/vits"
DEFAULT_SPEAKER = "p273"
SPEAKER_DESCRIPTIONS = """
p230 - Standard male voice
p248 - Female voice
p256 - Fast male voice
p270 - Female voice on vibe
p273 - Expressive female voice
p284 - Expressive female voice
p335 - Androgynus voice on expressive vibe
p339 - Standard female voice
"""
# ==========================


def get_nonempty_text(prompt="Enter the text to synthesize: "):
	"""
	Prompt user for non-empty text input.
	"""
	while True:
		text = input(prompt).strip()
		if text:
			return text
		print("Text cannot be empty. Please enter some text.")


def choose_speaker(default=DEFAULT_SPEAKER):
	"""
	Prompt user to choose a speaker ID (e.g., p225).
	Use default if input is empty.
	"""
	print("")
	print("Choose a speaker:")
	print(SPEAKER_DESCRIPTIONS)
	val = input(f"Enter speaker ID (default: {default}): ").strip()
	return val or default


def find_output_filename(basename="output", ext=".wav"):
	"""
	Find the next available filename like output1.wav, output2.wav, ...
	"""
	i = 1
	while True:
		filename = f"{basename}{i}{ext}"
		if not os.path.exists(filename):
			return filename
		i += 1


def main():

	# Add margins
	print("")
	print("")

	# Get user inputs
	text = get_nonempty_text()
	speaker = choose_speaker()

	# Determine output filename
	out_path = find_output_filename()

	# Load TTS engine
	tts = TTS(MODEL_NAME)
	# print("Languages:", list(enumerate(tts.languages)))
	# print("Speakers:", list(enumerate(tts.speakers)))
	# return

	# Synthesize and save
	print(f"Synthesizing...")
	tts.tts_to_file(
		text=text,
		speaker=speaker,
		file_path=out_path
	)
	print(f"Audio saved to {out_path}")


if __name__ == "__main__":
    main()

