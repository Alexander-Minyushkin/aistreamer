import time

import luigi
from luigi.contrib.gcs import GCSTarget

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

API_DISCOVERY_FILE = 'video-intelligence-service-discovery-v1beta1.json'
OPERATIONS_DISCOVERY_FILE = 'video-intelligence-operations-discovery.json'


class InputFileOnStorage(luigi.ExternalTask):
    """
    This class represents file stored on Google Storage in advance.
    """
    gs_path = luigi.Parameter()

    def output(self):
        """
        Returns the target output for this task.
        In this case, it expects a file to be present on Google Storage.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        return GCSTarget(self.gs_path)


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
        return [InputFileOnStorage(self.gs_path_video)]

    def output(self):
        """
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file on
        the local filesystem.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        return GCSTarget(self.gs_path_video + '.label.json')

    def run(self):
        """
        1. run label detection API
        2. write the result into the :py:meth:`*.label.json` target on Storage
        """

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
                'inputUri': self.gs_path_video,
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

        # output data
        f = self.output().open('w')
        f.write(lblData)
        f.close()


if __name__ == '__main__':
    luigi.run(['detect.DetectVideoLabels',
               '--gs-path-video', 'gs://amvideotest/Late_For_Work.mp4',
               '--workers', '1', '--local-scheduler'])
