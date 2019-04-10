import os

from flask import Flask, render_template, request

import luigi
from luigi.contrib.gcs import GCSTarget, GCSClient
import subprocess
from merge_video import MergeVideoAndAudio

app = Flask(__name__)

@app.route('/')
def hello_world():
    target = os.environ.get('TARGET', 'World')
    return 'Hello {}!\n'.format(target)

# http://localhost:8080/merge_video?youtube_id=asdf&text_id=pg_12
@app.route('/merge_video', methods=['GET'])
def merge_video():
    youtube_id = request.args.get('youtube_id')
    youtube_link = f'https://www.youtube.com/watch?v={youtube_id}'

    text_id = request.args.get('text_id')

    # --scheduler-url
    # https://luigi.readthedocs.io/en/latest/central_scheduler.html
    # $luigid --background --pidfile <PATH_TO_PIDFILE> --logdir <PATH_TO_LOGDIR> --state-path <PATH_TO_STATEFILE>
    scheduler_url = os.environ.get('SCHEDULER', 'http://127.0.0.1:8082')
    #if not num:

    luigi.run(['detect.MergeVideoAndAudio',
            '--gs-path-video',  youtube_link, #'gs://amvideotest/Welcome_to_Adam_Does_Movies.mp4', # 'gs://amvideotest/battlefield1.mp4', #
            '--text-generator','markov',
            '--text-generator-source', 'gs://amvideotest/source/pg/pg345.txt', #'gs://amvideotest/source/pg/pg345.txt',
            '--workers', '1', 
            '--scheduler-url', scheduler_url])


    return f'Completed youtube_link: {youtube_link}\ntext_id: {text_id}'

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))