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

from aistreamer import DummyTextGenerator
from textgenMarkov import MarkovTextGenerator, MarkovTextParser

from upload import UploadFileOnStorage
from detect import DetectVideoLabels

import luigi
from luigi.contrib.gcs import GCSTarget, GCSClient

import random
import pandas as pd
from gtts import gTTS
from pydub import AudioSegment
from textblob import TextBlob

class TextToSpeech():

    localTmpFolder = "../tmp/"

    def convertTextToSegment(self, wordsToSay):
        """
        Returns pydub.AudioSegment generated from given text .
        """
        raise NotImplementedError

class GTTSTextToSpeech(TextToSpeech):
    """
    TextToSpeech implementation using GTTS
    """

    def convertTextToSegment(self, wordsToSay):
        tts = gTTS(text=wordsToSay, lang='en')

        segmentFileName = self.localTmpFolder + "tmp.mp3"
        tts.save(segmentFileName)  # TODO move to temporary file

        segment = AudioSegment.from_mp3(segmentFileName)

        return segment       

class GCPTextToSpeech(TextToSpeech):
    """
    TextToSpeech implementation using GCP Text-to-speech
    """

    def convertTextToSegment(self, wordsToSay):        
        """
        Source taken here https://cloud.google.com/text-to-speech/docs/create-audio#text-to-speech-text-python
        """
        segmentFileName = self.localTmpFolder + "tmp.mp3"
        
        """Synthesizes speech from the input string of text."""
        from google.cloud import texttospeech
        client = texttospeech.TextToSpeechClient()

        input_text = texttospeech.types.SynthesisInput(text=wordsToSay)

        # Note: the voice can also be specified by name.
        # Names of voices can be retrieved with client.list_voices().
        voice = texttospeech.types.VoiceSelectionParams(
            language_code='en-US',
            ssml_gender=texttospeech.enums.SsmlVoiceGender.MALE)

        audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.MP3)

        response = client.synthesize_speech(input_text, voice, audio_config)

        # The response's audio_content is binary.
        with open(segmentFileName, 'wb') as out:
            out.write(response.audio_content)

        segment = AudioSegment.from_mp3(segmentFileName)

        return segment             

class GenVoiceFile(luigi.Task):
    
    task_namespace = 'detect'
    gs_path_video = luigi.Parameter()
    text_generator = luigi.Parameter()
    text_generator_source = luigi.Parameter()
    random_seed  = luigi.IntParameter(default=123)

    generator = DummyTextGenerator()
    tts = GCPTextToSpeech() # GTTSTextToSpeech()
    temp_result_file = "../tmp/result.mp3"

    def requires(self):
        """
        This task's dependencies:
        * :py:class:`~.DetectVideoLabels`
        We need to read *.label.json file produced by this task
        :return: list of object (:py:class:`luigi.task.Task`)
        """
        return {'labels_csv': DetectVideoLabels(self.gs_path_video),
                'video': UploadFileOnStorage(self.gs_path_video),
                'markov_db': MarkovTextParser(self.text_generator_source)}

    def output(self):
        """
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file on
        the local filesystem.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """

        return GCSTarget(self.input()['video'].path + "_" + str(self.random_seed) + '.mp3')

    def json_labels_to_pd(self, d):

        headers = ['Label', 'confidence', 'start', 'end']

        def gen_from_dict(d):
            for node in d['annotationResults'][0]['shotLabelAnnotations']:
                description = node['entity']['description']
                for loc in node['segments']:
                    yield [
                        description, 
                        loc['confidence'], 
                        int(float(loc['segment'].get('startTimeOffset', '0').replace('s',''))* 1000000),
                        int(float(loc['segment'].get('endTimeOffset',   '-1').replace('s',''))* 1000000)
                        ] 

        return pd.DataFrame(gen_from_dict(d), columns=headers)
    
    def json_labels_to_pd_old(self, d):

        headers = ['Label', 'confidence', 'start', 'end']

        def gen_from_dict(d):
            for node in d:
                description = node['description']
                for loc in node['locations']:
                    # print loc['segment']
                    yield [
                        description,
                        loc['confidence'],
                        int(loc['segment'].get('startTimeOffset', 0)),
                        int(loc['segment'].get('endTimeOffset',   -1))
                    ]

        return pd.DataFrame(gen_from_dict(d), columns=headers)    

    def textToAudioSegment(self, wordsToSay):
        # Convert text to sound
        return self.tts.convertTextToSegment(wordsToSay)

    def run(self):
        print(">>>> Run GenVoiceFile")
        
        random.seed(self.random_seed)

        #with self.input()[0].open() as json_data:
        #    d = json.load(json_data)
        #    labels = self.json_labels_to_pd(d)

        labels = pd.read_csv(self.input()['labels_csv'].open(), 
                             header=None,
                             names = ['Label', 'category', 'start', 'end'])
        print(labels)

        if self.text_generator == 'markov':
            tmp_file_db = GCSClient().download(self.input()['markov_db'].path)
            print("GenVoiceFile.run markov_db tmp file path: ", tmp_file_db.name)
            self.generator = MarkovTextGenerator(tmp_file_db.name) #'combined.db')            

        usedBefore = set()

        fullTrack = self.textToAudioSegment("")

        curr_time_mksec = fullTrack.duration_seconds * 1000000

        video_duration_mksec = max(labels['end']) * 1000000
        print('video_duration_mksec:' + str(video_duration_mksec))
        while (curr_time_mksec < video_duration_mksec):
            observedBefore = set(labels[labels['start'] * 1000000 <
                                        curr_time_mksec]['Label'])
            candidates = list(observedBefore - usedBefore)

            seedWords = 'Hmmm'

            if len(candidates) > 0:
                seedWords = candidates[0]
            elif len(usedBefore)>0:
                # Need to do this if list of detected words is too small
                seedWords = random.sample(usedBefore, 1)[0]
                print("RANDOM seed word!")

            seedWordsToGen = seedWords.lower()
            print('curr_time_mksec:' + str(curr_time_mksec) + ' ' + seedWordsToGen)
            wordsToSay = self.generator.get_text("TODO: full text so far",
                                            seedWordsToGen)
                                            
            for _ in range(5):
                if len(wordsToSay) < 100:
                    break
                wordsToSay = self.generator.get_text("TODO: full text so far",
                                            seedWordsToGen)
                                            
            print(wordsToSay)
            wordsToSay_corrected = str(TextBlob(wordsToSay).correct())
            if wordsToSay_corrected  != wordsToSay:
                wordsToSay = wordsToSay_corrected
                print("CORRECTED to: "+ wordsToSay)
                

            print(len(wordsToSay))

            segment = self.textToAudioSegment(wordsToSay)

            print(segment.duration_seconds)
            print(fullTrack.duration_seconds)
            print("---------")

            if (segment.duration_seconds + fullTrack.duration_seconds) * 1000000 > video_duration_mksec:
                break
            fullTrack = fullTrack + segment

            # print seedWords in usedBefore

            usedBefore = usedBefore.union(set([seedWords]))

            curr_time_mksec = fullTrack.duration_seconds * 1000000

        fullTrack.export(self.temp_result_file, format="mp3")

        GCSClient().put(self.temp_result_file, self.output().path)   
    


if __name__ == '__main__':
    luigi.run(['detect.GenVoiceFile',
               '--gs-path-video', 'gs://amvideotest/Late_For_Work.mp4', #'https://www.youtube.com/watch?v=i05jta1W4Wo',# 'gs://amvideotest/Late_For_Work.mp4', # 'gs://amvideotest/battlefront1.mp4', #
               '--text-generator','markov',
               '--text-generator-source', 'gs://amvideotest/source/pg/pg345.txt', 
               '--random-seed', "1111", 
               '--workers', '1', '--local-scheduler'])
