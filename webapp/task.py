

from google.cloud import datastore
import datetime


def get_client():
    return datastore.Client()


def add_task(client, task_type, video_address, comment):
    key = client.key('Task')

    task = datastore.Entity(
        key, exclude_from_indexes=['comment'])

    task.update({
        'created': datetime.datetime.utcnow(),
        'type': task_type,
        'video_address': video_address,
        'comment': comment,
        'done': False
    })

    client.put(task)

    return task.key
