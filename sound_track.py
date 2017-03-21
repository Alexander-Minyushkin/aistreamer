# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 15:21:19 2017

@author: minushkin
"""

from db import Db
from gen import Generator
from genWithSeed import GenratorWithSeed
from parse import Parser
from sql import Sql
from rnd import Rnd
import sys
import sqlite3
import codecs
import json
import pandas as pd

# Audio manipulations
from gtts import gTTS
from pydub import AudioSegment
from tempfile import TemporaryFile
from tempfile import SpooledTemporaryFile

SENTENCE_SEPARATOR = '.'
WORD_SEPARATOR = ' '

path_to_file = "data/labels/gta001_label.json"
db_name = 'tmp'

def read_json(path_to_file):
    with open(path_to_file) as json_data:
        d = json.load(json_data)
    
    headers =  ['Label','confidence','start','end']
    
    def gen_from_dict(d):
        for node in d:
            description = node['description']
            for loc in node['locations']:
                #print loc['segment']
                yield [
                        description, 
                        loc['confidence'], 
                        int(loc['segment'].get('startTimeOffset', 0)),
                        int(loc['segment'].get('endTimeOffset',   -1))
                        ]
    
    return pd.DataFrame(gen_from_dict(d), columns=headers)

def textToAudioSegment(wordsToSay):
    # Convert text to sound
    tts = gTTS(text=wordsToSay, lang='en')
        
    segmentFileName = "tmp/tmp.mp3"
    tts.save(segmentFileName) # TODO move to temporary file
                
    segment = AudioSegment.from_mp3(segmentFileName)
    
    return segment

if __name__ == '__main__':
    args = sys.argv
    usage = 'Usage: %s (db_name path_to_json)' % (args[0], )

    if (len(args) < 2):
        raise ValueError(usage)

    db_name  = args[1]
    path_to_json  = args[2]
    
    db = Db(sqlite3.connect(db_name + '.db'), Sql())
    generator = GenratorWithSeed(db_name, db, Rnd())
    
    labels = read_json(path_to_file)
    
    usedBefore = set()
    
    fullTrack = textToAudioSegment("Hello, this AI streamer. Markov process on Reddit comments")
    
    curr_time_mksec = fullTrack.duration_seconds * 1000000
    
    while (curr_time_mksec <  max(labels['end'])):
        observedBefore = set(labels[labels['start'] < curr_time_mksec]['Label'])
        candidates = list(observedBefore - usedBefore)
        
        seedWords = 'Hmmm' 
        
        if len(candidates)>0: seedWords = candidates[0]
        
        print str(curr_time_mksec ) + ' ' + seedWords
        wordsToSay = generator.generate_to_right(seedWords.split(), WORD_SEPARATOR)
        print wordsToSay 
        
        segment = textToAudioSegment(wordsToSay)
        
        print segment.duration_seconds        
        fullTrack = fullTrack + segment
        
        #print seedWords in usedBefore
        
        usedBefore = usedBefore.union(set([seedWords]))
        
        if segment.duration_seconds < 1. :
            curr_time_mksec = curr_time_mksec + 1000000
        else:
            curr_time_mksec = fullTrack.duration_seconds * 1000000
        
        
    fullTrack.export("mashup2.mp3", format="mp3")
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
