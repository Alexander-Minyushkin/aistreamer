# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 23:20:41 2019

@author: alexander
"""

import luigi
from luigi.contrib.gcs import GCSTarget, GCSClient

from pytube import YouTube

# TODO: make it configurable
gs_youtube_folder = "gs://amvideotest/source/youtube/"

class UploadFileOnStorage(luigi.ExternalTask):
    """
    This class upload file to Google Storage.
    """
    task_namespace = 'detect'
    
    gs_source_path = luigi.Parameter()
    video_id = ''

    def output(self):
        """
        Returns the target output for this task.
        In this case, it expects a file to be present on Google Storage.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        if self.gs_source_path.startswith('gs://'):
            return GCSTarget(self.gs_source_path)
            
        self.video_id = self.gs_source_path.split('=')[1]        
        print(self.video_id)
        
        output_file_path = gs_youtube_folder + self.video_id +'.mp4'
        
        return GCSTarget(output_file_path)
        
    def run(self):
        if not self.gs_source_path.startswith('https://www.youtube.com/watch?v='):
            return
        
        yt = YouTube(self.gs_source_path)
        
        temp_result_file = yt.streams.filter(file_extension='mp4').first().download('../tmp', self.video_id)
        print(temp_result_file)
        
        GCSClient().put(temp_result_file, self.output().path)   

        
if __name__ == '__main__':
    luigi.run(['detect.UploadFileOnStorage',
               '--gs-source-path', 'https://www.youtube.com/watch?v=rnpxUhgz1Us',
               '--workers', '1', '--local-scheduler'])            
        