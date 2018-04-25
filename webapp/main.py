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

# [START imports]
import logging
import functools

from flask import Flask, render_template, request

from pytube import YouTube
# [END imports]

# [START create_app]
app = Flask(__name__)
# [END create_app]


@app.route('/task_view')
def task_view():

    from task import Task
    results = [(t.task_type, t.video_address, t.comment, t.created, t.pulled, t.is_completed)
               for t in Task.latest()]

    return render_template('task_view.html',
                           results=results,
                           res_len=len(results))


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
    
    yt = YouTube(site_url)
    VIDEOID = yt.video_id

    # [END submitted]
    # [START render_template]
    return render_template(
        'form_new_video.html',
        site_url=site_url,
        comments=comments,
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

    yt = YouTube(site_url)
    VIDEOID = yt.video_id

    from task import Task

    task_type = "video_full_cycle"
    task_key = Task(task_type=task_type,
                    video_address=site_url,
                    is_completed = False,
                    comment=comments).put().urlsafe()

    #topic.publish(task_type,
    #              task_key=task_key,
    #              site_url=site_url)

    submitted = "Successfully submitted "

    # [END submitted]
    # [START render_template]
    return render_template(
        'form_new_video.html',
        site_url=site_url,
        comments=comments,
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
