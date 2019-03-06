import time
import json

import luigi
from luigi.contrib.gcs import GCSTarget

from upload import UploadFileOnStorage

from google.cloud import videointelligence


class DetectVideoLabels(luigi.Task):

    task_namespace = 'detect'
    gs_path_video = luigi.Parameter()

    def requires(self):
        """
        This task's dependencies:
        * :py:class:`~.InputFileOnStorage`
        We don't read this file, just make sure it exists.
        :return: list of object (:py:class:`luigi.task.Task`)
        """
        return [UploadFileOnStorage(self.gs_path_video)]

    def output(self):
        """
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file on
        the local filesystem.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        print(">>>>>\n")
        print(self.input()[0].path)
        return GCSTarget(self.input()[0].path + '.label.csv')

    def run(self):
        """
        1. run label detection API
        2. write the result into the :py:meth:`*.label.json` target on Storage
        """

        """ Detects labels given a GCS path. """
        video_client = videointelligence.VideoIntelligenceServiceClient()
        features = [videointelligence.enums.Feature.LABEL_DETECTION]
        operation = video_client.annotate_video(self.input()[0].path, 
                                                features=features)
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
        
        # output data
        f = self.output().open('w')
        f.write(output_csv)
        f.close()


if __name__ == '__main__':
    luigi.run(['detect.DetectVideoLabels',
               '--gs-path-video', 'https://www.youtube.com/watch?v=i05jta1W4Wo', #'gs://amvideotest/Late_For_Work.mp4',
               '--workers', '1', '--local-scheduler'])
