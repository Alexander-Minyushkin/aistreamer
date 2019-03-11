#!/bin/bash

# Required for audio processing
apt-get install libav-tools

# Required for video processing
apt-get install ffmpeg 

# For Simplified Text Processing 
python -m textblob.download_corpora
