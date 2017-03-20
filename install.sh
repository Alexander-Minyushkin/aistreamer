

git clone https://github.com/Alexander-Minyushkin/markov-text.git

export PYTHONPATH="markov-text"

# Text pre-processing. Creation of file tmp/combined.txt
bash scripts/filter1.sh

# Parsing data to prepare markov text generator
time python markov-text/markov.py parse combined 2 tmp/combined.txt

