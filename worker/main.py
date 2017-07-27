import argparse
import json
from google.cloud import pubsub

import luigi


def pubsub_pull(pubsub_topic_name='small_jobs'):
    client = pubsub.Client()
    topic = client.topic(pubsub_topic_name)
    subscription = topic.subscription('small_jobs_worker')

    # Change return_immediately=False to block until messages are
    # received.
    results = subscription.pull(return_immediately=True)

    if len(results) == 0:
        return "No messages in pubsub"

    message_id, message = results[0]
    output = '* {}: {}, {}'.format(message_id,
                                   message.data,
                                   message.attributes)

    print output

    if message.data == "detect_labels":
        if "path" in message.attributes:
            print message.attributes["path"]
            subscription.acknowledge([message_id])
            return message.data
        else:
            print "Message does'n contain required attribure 'path'"
    elif message.data == "video_full_cycle":
        if "site_url" not in message.attributes:
            print "Message does'n contain required attribure 'site_url'"
        elif "task_key" not in message.attributes:
            print "Message does'n contain required attribure 'task_key'"
        else:
            print message.attributes["site_url"]
            subscription.acknowledge([message_id])
            return message.data

    return "Unrecognized message"


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'type', help='Type action: pubsub_pull')
    # parser.add_argument(
    #    'gcs_uri', help='The Google Cloud Storage URI of the video.')
    # parser.add_argument(
    #    'path', help='File to store result.')
    args = parser.parse_args()

    if args.type == "pubsub_pull":
        pubsub_pull()
    else:
        print "Error: Type is not recognized: " + args.type
