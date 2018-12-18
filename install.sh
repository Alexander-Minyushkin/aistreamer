#!/bin/bash
set -euo pipefail
IFS=$'\n\t'
# https://dev.to/thiht/shell-scripts-matter


# pubsub configuration on GCP
#gcloud alpha pubsub topics create small_jobs
#gcloud alpha pubsub subscriptions create small_jobs_monitoring --topic small_jobs  --ack-deadline=60
#gcloud alpha pubsub subscriptions create small_jobs_worker --topic small_jobs  --ack-deadline=60



mkdir tmp
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
