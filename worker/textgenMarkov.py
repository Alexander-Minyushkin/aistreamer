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

from markov import Db
from markov import GenratorWithSeed
from markov import Parser
from markov import Sql
from markov import Rnd
import sys
import sqlite3

from google.cloud import storage


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

    mtg = MarkovTextGenerator('combined.db')

    print(mtg.get_text([], ['people']))
