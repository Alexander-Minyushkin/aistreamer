"""
Copyright 2017 Alexander Minyushkin

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
import argparse
from voice import GenVoiceFile

import luigi
from luigi.contrib.gcs import GCSTarget, GCSClient
import subprocess

class MergeVideoAndAudio(luigi.Task):
    
    task_namespace = 'detect'
    gs_path_video = luigi.Parameter()
    text_generator = luigi.Parameter()

    temp_result_file = "../tmp/result.mp4"

    def requires(self):
        """
        This task's dependencies:
        * :py:class:`~.GenVoiceFile`
        Produce file with original video an new audio cover
        :return: list of object (:py:class:`luigi.task.Task`)
        """
        return [GenVoiceFile(gs_path_video = self.gs_path_video, text_generator = 'markov')]

    def output(self):
        """
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file on
        the local GCP Storage.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """

        return GCSTarget(self.gs_path_video + '.result.mp4')

    def run(self):        
        
        tmp_video_file = GCSClient().download(self.gs_path_video)
        tmp_audio_file = GCSClient().download(self.requires()[0].output().path)

        #'ffmpeg -i Late_For_Work.mp4 -i Late_For_Work.mp4.voice.mp3 -c:v copy -map 0:v:0 -map 1:a:0 result.mp4'
        cmd = ['ffmpeg', '-y', '-i', tmp_video_file.name, 
        '-i', tmp_audio_file.name, '-c:v', 'copy', 
        '-map', '0:v:0', '-map', '1:a:0', 
        '-strict', '-2', '-y',
        self.temp_result_file]
        print(cmd)
        subprocess.check_call(cmd)

        GCSClient().put(self.temp_result_file, self.output().path)         
        
        tmp_video_file.close()
        tmp_audio_file.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('path', help='GCS file path (gs://...)')
    args = parser.parse_args()
    
    luigi.run(['detect.MergeVideoAndAudio',
               '--gs-path-video',  args.path, #'gs://amvideotest/Welcome_to_Adam_Does_Movies.mp4', # 'gs://amvideotest/battlefield1.mp4', #
               '--text-generator','markov',
               '--workers', '1', '--local-scheduler'])