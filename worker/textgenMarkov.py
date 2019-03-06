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

from aistreamer import TextGenerator

from upload import InputFileOnStorage

import luigi
from luigi.contrib.gcs import GCSTarget, GCSClient

from markov import Db
from markov import GenratorWithSeed
from markov import Parser
from markov import Sql
from markov import Rnd

import sys
import re
import sqlite3

from google.cloud import storage

class MarkovTextParser(luigi.Task):

    task_namespace = 'detect'
    gs_path_txt = luigi.Parameter()
    
    temp_result_file_path = "../tmp/result.db"
    
    # https://stackoverflow.com/questions/4576077/python-split-text-on-sentences
    def split_into_sentences(self, text):
        alphabets= "([A-Za-z])"
        prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
        suffixes = "(Inc|Ltd|Jr|Sr|Co)"
        starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
        acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
        websites = "[.](com|net|org|io|gov)"
        
        text = " " + text + "  "
        text = text.replace("\n"," ")
        text = re.sub(prefixes,"\\1<prd>",text)
        text = re.sub(websites,"<prd>\\1",text)
        if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
        text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
        text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
        text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
        text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
        text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
        text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
        text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
        if "”" in text: text = text.replace(".”","”.")
        if "\"" in text: text = text.replace(".\"","\".")
        if "!" in text: text = text.replace("!\"","\"!")
        if "?" in text: text = text.replace("?\"","\"?")
        text = text.replace(".",".<stop>")
        text = text.replace("?","?<stop>")
        text = text.replace("!","!<stop>")
        text = text.replace("<prd>",".")
        sentences = text.split("<stop>")
        sentences = sentences[:-1]
        sentences = [s.strip() for s in sentences]
        return sentences    

    def requires(self):
        """
        This task's dependencies:
        * :py:class:`~.InputFileOnStorage`
        We don't read this file, just make sure it exists.
        :return: list of object (:py:class:`luigi.task.Task`)
        """
        return [InputFileOnStorage(self.gs_path_txt)]#[UploadFileOnStorage(self.gs_path_video)]

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
        return GCSTarget(self.input()[0].path + '.db')

    def run(self):
        tmp_txt_file = GCSClient().download(self.input()[0].path)
        
        text_arr = self.split_into_sentences(open(tmp_txt_file.name, "r").read())
        
        #print(text_arr)
        db = Db(sqlite3.connect(self.temp_result_file_path), Sql())
        db.setup(2)
        
        SENTENCE_SEPARATOR = '\n'
        WORD_SEPARATOR = ' '
        
        Parser("notused", db, SENTENCE_SEPARATOR, WORD_SEPARATOR).parse_array(text_arr)
        
        GCSClient().put(self.temp_result_file_path, self.output().path)  
        
        tmp_txt_file.close()

class MarkovTextGenerator(TextGenerator):
    """
    Generate text using markov process.
    """
    def download_blob(self, bucket_name, source_blob_name):
        """Downloads a blob from the bucket."""

        destination_file_name = '..\\tmp\\markov_tmp.db'

        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)

        return destination_file_name


    def __init__(self, db_path):

        self.db_local_path = self.download_blob('amvideotest', db_path)

        self.db = Db(sqlite3.connect(self.db_local_path), Sql())
        self.generator = GenratorWithSeed(self.db_local_path, self.db, Rnd())
        self.WORD_SEPARATOR = ' '
        self.SENTENCE_SEPARATOR = '\n'
		

    def words_set(self, words_list):
        pass

    def get_text(self, previous_text, word_to_use):
        return self.generator.generate_from_center(word_to_use.split(), self.WORD_SEPARATOR)


if __name__ == '__main__':
    print('MarkovTextGenerator')

    #mtg = MarkovTextGenerator('combined.db')

    #print(mtg.get_text([], ['people']))
    luigi.run(['detect.MarkovTextParser',
               '--gs-path-txt', 'gs://amvideotest/source/pg/pg345.txt',
               '--workers', '1', '--local-scheduler'])
