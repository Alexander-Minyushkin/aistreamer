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
    topic.publish('this is the message', attr1='value1', attr2='value2')
    return 'Check Pub/Sub updates'


@app.route('/pubsub_pull')
def pubsub_pull():
    pubsub_client = pubsub.Client()
    topic = pubsub_client.topic('small_jobs')
    subscription = topic.subscription('small_jobs')

    # Change return_immediately=False to block until messages are
    # received.
    results = subscription.pull(return_immediately=True)

    return str(results)


@app.route('/')
def hello():
    return render_template('index.html')

# [START form]


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
