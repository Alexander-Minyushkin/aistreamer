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

from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers

from functools import reduce


if __name__ == '__main__':
    author = "Sheckley_Robert"
    book_id = [33854, 9055, 29446, 29458, 29876, 32040, 29487, 29445, 32346, 29525, 51833, 32041, 50844, 51768, 20919, 51545, 29509, 29548, 29579 ]

    author = "Best_books"
    book_id = [1342,219,844,84,2542,5200,76,98,11,345,2701,2591,74,6130,1080,43,1400,174,158,1232,1661]

    all_texts = reduce((lambda x, y: x + y), [ strip_headers(load_etext(id)).strip() for id in book_id])

    f = open("../data/pg/" + author + ".txt", 'w')
    f.write(all_texts)
    f.close()

