import argparse

from google.cloud import videointelligence

# google.cloud.videointelligence.v1 
def analyze_labels(path):
    """ Detects labels given a GCS path. """
    video_client = videointelligence.VideoIntelligenceServiceClient()
    features = [videointelligence.enums.Feature.LABEL_DETECTION]
    operation = video_client.annotate_video(path, features=features)
    print('\nProcessing video for label annotations:\n')

    result = operation.result(timeout=900)
    print(result)
    print('\nFinished processing.')

    segment_labels = result.annotation_results[0].shot_label_annotations
    
    output_csv = ""
    for i, segment_label in enumerate(segment_labels):
        print('Video label description: {}'.format(
            segment_label.entity.description))
        for category_entity in segment_label.category_entities:
            print('\tLabel category description: {}'.format(
                category_entity.description))

            for i, segment in enumerate(segment_label.segments):
                start_time = (segment.segment.start_time_offset.seconds +
                              segment.segment.start_time_offset.nanos / 1e9)
                end_time = (segment.segment.end_time_offset.seconds +
                            segment.segment.end_time_offset.nanos / 1e9)
                positions = '{}s to {}s'.format(start_time, end_time)
                confidence = segment.confidence
                print('\tSegment {}: {}'.format(i, positions))
                print('\tConfidence: {}'.format(confidence))
                
                output_csv_line = '{},{},{},{}\n'.format(
                                segment_label.entity.description, 
                                category_entity.description,
                                start_time, 
                                end_time)
                output_csv = output_csv + output_csv_line
                print(output_csv_line)
            print('\n')
    print('\n\n-------\n')  
    print(output_csv)


if __name__ == '__main__':
    print("This script is for google.cloud.videointelligence.v1  API testing\n")
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('path', help='GCS file path for label detection.')
    args = parser.parse_args()

    analyze_labels(args.path)

