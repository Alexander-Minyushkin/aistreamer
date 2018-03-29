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
from detect import DetectVideoLabels

import luigi
from luigi.contrib.gcs import GCSTarget, AtomicGCSFile

import json
import pandas as pd
from gtts import gTTS
from pydub import AudioSegment

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
    TextToSpeech implementation using GTTS
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
            ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)

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

    generator = DummyTextGenerator()
    tts = GCPTextToSpeech() # GTTSTextToSpeech()

    def requires(self):
        """
        This task's dependencies:
        * :py:class:`~.DetectVideoLabels`
        We need to read *.label.json file produced by this task
        :return: list of object (:py:class:`luigi.task.Task`)
        """
        return [DetectVideoLabels(self.gs_path_video)]

    def output(self):
        """
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file on
        the local filesystem.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        return GCSTarget(self.gs_path_video + '.voice.mp3')

    def json_labels_to_pd(self, d):

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

        with self.input()[0].open() as json_data:
            d = json.load(json_data)
            labels = self.json_labels_to_pd(d)

        print(labels)

        

        usedBefore = set()

        fullTrack = self.textToAudioSegment("Test")

        curr_time_mksec = fullTrack.duration_seconds * 1000000

        video_duration_mksec = max(labels['end'])
        while (curr_time_mksec < video_duration_mksec):
            observedBefore = set(labels[labels['start'] <
                                        curr_time_mksec]['Label'])
            candidates = list(observedBefore - usedBefore)

            seedWords = 'Hmmm'

            if len(candidates) > 0:
                seedWords = candidates[0]

            seedWordsToGen = seedWords.lower()
            print(str(curr_time_mksec) + ' ' + seedWordsToGen)
            wordsToSay = self.generator.get_text("TODO: full text so far",
                                            seedWordsToGen)
            print(wordsToSay)

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

        fullTrack.export("../tmp/result.mp3", format="mp3")


if __name__ == '__main__':
    luigi.run(['detect.GenVoiceFile',
               '--gs-path-video', 'gs://amvideotest/Late_For_Work.mp4',
               '--workers', '1', '--local-scheduler'])
