
# Markov process tool for text generation
git clone https://github.com/Alexander-Minyushkin/markov-text.git
export PYTHONPATH="markov-text"

# Create an mp3 file from spoken text via the Google TTS (Text-to-Speech) API
pip install gTTS

# Manipulate audio
pip install pydub

# Text pre-processing. Creation of file tmp/combined.txt
bash scripts/filter1.sh

# Parsing data to prepare markov text generator
time python markov-text/markov.py parse combined 2 tmp/combined.txt

