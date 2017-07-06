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


class TextGenerator():

    def words_set(self, words_list):
        """
        Input list of words wich will be presumably used later
        to produce text.
        Can be used for topic or sentimet detection for example.
        """
        raise NotImplementedError

    def get_text(self, previous_text, word_to_use):
        """
        Returns text to continue previous_text which includes word_to_use.
        """
        raise NotImplementedError


class DummyTextGenerator(TextGenerator):
    def words_set(self, words_list):
        pass

    def get_text(self, previous_text, word_to_use):
        return word_to_use


tg = DummyTextGenerator()

print(tg.get_text("", "Ha-Ha!"))
