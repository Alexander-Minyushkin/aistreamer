# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
import logging

# [START imports]
from flask import Flask, render_template, request
from google.cloud import pubsub
from pytube import YouTube
# [END imports]

# [START create_app]
app = Flask(__name__)
# [END create_app]

# https://github.com/GoogleCloudPlatform/google-cloud-python/tree/master/pubsub
client = pubsub.Client()
topic = client.topic('small_jobs')
# topic.create()


@app.route('/pubsub')
def pubsub_submit():
    topic.publish('detect_labels',
                  path='gs://amvideotest/Late_For_Work.mp4',
                  attr2='value2')
    return 'Check Pub/Sub updates'

# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/pubsub/cloud-client/subscriber.py


@app.route('/pubsub_pull')
def pubsub_pull():
    subscription = topic.subscription('small_jobs')

    # Change return_immediately=False to block until messages are
    # received.
    results = subscription.pull(return_immediately=True)

    if len(results) == 0:
        return "No messages in pubsub"

    message_id, message = results[0]
    output = '* {}: {}, {}'.format(message_id,
                                   message.data,
                                   message.attributes)

    subscription.acknowledge([message_id])

    return output


@app.route('/pubsub_view')
def pubsub_view():
    subscription = topic.subscription('small_jobs')

    # Change return_immediately=False to block until messages are
    # received.
    results = subscription.pull(return_immediately=True)

    if len(results) == 0:
        return "No messages in pubsub"

    output = ""
    for ack_id, message in results:
        output = output + '\n{}, {}'.format(message.data, message.attributes)

    return output


@app.route('/')
def hello():
    return render_template('index.html')

# [START form]


@app.route('/job_list', methods=['GET'])
def job_list():
    num = request.args.get('num')
    if not num:
        num = 10
    num = int(num)
    return "get num: " + str(num)


@app.route('/new_video')
def new_video():
    return render_template('form_new_video.html')


@app.route('/new_video_check', methods=['POST'])
def new_video_check():
    site_url = request.form['site_url']
    comments = request.form['comments']

    try:
        from urllib.parse import urlparse
    except ImportError:
        from urlparse import urlparse

    o = urlparse(site_url)
    VIDEOID = o.query.split('=')[1]

    yt = YouTube(site_url)

    # [END submitted]
    # [START render_template]
    return render_template(
        'form_new_video.html',
        site_url=site_url,
        comments=comments,
        filename=yt.filename,
        VIDEOID=VIDEOID)


@app.route('/new_video_submit', methods=['POST'])
def new_video_submit():
    site_url = request.form['site_url']
    comments = request.form['comments']

    try:
        from urllib.parse import urlparse
    except ImportError:
        from urlparse import urlparse

    o = urlparse(site_url)
    VIDEOID = o.query.split('=')[1]

    yt = YouTube(site_url)

    import task

    task_type = "video_processing"
    task_key = task.add_task(task.get_client(),
                             task_type,
                             site_url,
                             comments)

    submitted = "Successfully submitted "

    # [END submitted]
    # [START render_template]
    return render_template(
        'form_new_video.html',
        site_url=site_url,
        comments=comments,
        filename=yt.filename,
        VIDEOID=VIDEOID,
        submitted=submitted,
        task_type=task_type)


@app.route('/form')
def form():
    return render_template('form.html')
# [END form]


# [START submitted]
@app.route('/submitted', methods=['POST'])
def submitted_form():
    name = request.form['name']
    email = request.form['email']
    site = request.form['site_url']
    comments = request.form['comments']

    # [END submitted]
    # [START render_template]
    return render_template(
        'submitted_form.html',
        name=name,
        email=email,
        site=site,
        comments=comments)
    # [END render_template]


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
# [END app]
