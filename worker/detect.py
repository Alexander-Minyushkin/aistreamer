import luigi
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

from google.cloud import pubsub

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
        return luigi.contrib.gcs.GCSTarget(self.gs_path)


class DetectVideoLabels(luigi.Task):

    task_namespace = 'detect'
    gs_path_video = luigi.Parameter()

    def requires(self):
        """
        This task's dependencies:
        * :py:class:`~.InputFileOnStorage`
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
        return luigi.LocalTarget('./DetectVideoLabels_tmp.txt')

    def run(self):
        """
        1. count the words for each of the :py:meth:`~.InputText.output`
        targets created by :py:class:`~.InputText`
        2. write the count into the :py:meth:`~.WordCount.output` target
        """

        print("DetectVideoLabels.run")

        # output data
        f = self.output().open('w')
        f.write(self.gs_path_video)
        f.close()


if __name__ == '__main__':
    luigi.run(['detect.DetectVideoLabels',
               '--gs-path-video', 'gs://amvideotest/Late_For_Work.mp4',
               '--workers', '1', '--local-scheduler'])
