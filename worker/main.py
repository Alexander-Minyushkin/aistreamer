import argparse
import time
import json

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

from google.cloud import pubsub

API_DISCOVERY_FILE = 'video-intelligence-service-discovery-v1beta1.json'
OPERATIONS_DISCOVERY_FILE = 'video-intelligence-operations-discovery.json'


def main(gcs_uri):

    credentials = GoogleCredentials.get_application_default()

    with open(API_DISCOVERY_FILE, 'r') as f:
        doc = f.read()
    video_service = discovery.build_from_document(
        doc, credentials=credentials)

    with open(OPERATIONS_DISCOVERY_FILE, 'r') as f:
        op_doc = f.read()
    op_service = discovery.build_from_document(
        op_doc, credentials=credentials)

    video_service_request = video_service.videos().annotate(
        body={
            'inputUri': gcs_uri,
            'features': ['LABEL_DETECTION']
        })

    response = video_service_request.execute()
    name = response['name']

    op_service_request = op_service.operations().get(name=name)
    response = op_service_request.execute()
    op_start_time = str(
        response['metadata']['annotationProgress'][0]['startTime']
    )
    print('Operation {} started: {}'.format(name, op_start_time))

    while True:
        response = op_service_request.execute()
        time.sleep(30)
        if 'done' in response and response['done'] is True:
            break
        else:
            print('Operation processing ...')
    print('The video has been successfully processed.')

    lblData = response['response']['annotationResults'][0]['labelAnnotations']

    return lblData


def pubsub_pull(pubsub_topic_name='small_jobs'):
    client = pubsub.Client()
    topic = client.topic(pubsub_topic_name)
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

    print output

    if message.data == "detect_labels":
        if "path" in message.attributes:
            print message.attributes["path"]
            subscription.acknowledge([message_id])
        else:
            print "Message does'n contain required attribure 'path'"

    return "Unrecognized message"


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'type', help='Type of video analysis: label, face or shot')
    parser.add_argument(
        'gcs_uri', help='The Google Cloud Storage URI of the video.')
    parser.add_argument(
        'path', help='File to store result.')
    args = parser.parse_args()
    if args.type == 'label':
        res = main(args.gcs_uri)
    else:
        print "Error: Type is not recognized: " + args.type
        res = ['Error: Wrong type']

    with open(args.path, 'w') as outfile:
        json.dump(res, outfile)
