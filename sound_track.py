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

#path_to_file = "/home/alexander/Documents/video/Welcome_to_Adam_Does_Movies.mp4.label.json"
path_to_json = "data/labels/gta001_label.json"
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
                        #int(loc['segment'].get('startTimeOffset', 0)),
                        #int(loc['segment'].get('endTimeOffset',   -1))
                        int(float(loc['segment'].get('startTimeOffset', '0').replace('s',''))* 1000000),
                        int(float(loc['segment'].get('endTimeOffset',   '-1').replace('s',''))* 1000000)
                        ]    
    return pd.DataFrame(gen_from_dict(d), columns=headers)

def read_json2(path_to_file):
    with open(path_to_file) as json_data:
        d = json.load(json_data)    
    headers =  ['Label','confidence','start','end']    
    def gen_from_dict(d):
        for node in d['annotationResults'][0]['shotLabelAnnotations']:
            description = node['entity']['description']
            for loc in node['segments']:
                yield [
                        description, 
                        loc['confidence'], 
                        #int(loc['segment'].get('startTimeOffset', 0)),
                        #int(loc['segment'].get('endTimeOffset',   -1))
                        int(float(loc['segment'].get('startTimeOffset', '0').replace('s',''))* 1000000),
                        int(float(loc['segment'].get('endTimeOffset',   '-1').replace('s',''))* 1000000)
                        ]    
    return pd.DataFrame(gen_from_dict(d), columns=headers)

#for node in d['annotationResults'][0]['segmentLabelAnnotations']:
#    print(node['entity']['description'])
#    for loc in node['segments']:
#        print(loc['confidence'])
#        print(loc['segment']['startTimeOffset'])
#        print(loc['segment']['endTimeOffset'])    
#    
#    break

def textToAudioSegment(wordsToSay):
    # Convert text to sound
    tts = gTTS(text=wordsToSay, lang='en')
        
    segmentFileName = "tmp/tmp.mp3"
    tts.save(segmentFileName) # TODO move to temporary file
                
    segment = AudioSegment.from_mp3(segmentFileName)
    
    return segment

if __name__ == '__main__':
    args = sys.argv
    usage = 'Usage: %s (db_name path_to_json output_mp3_path)' % (args[0], )

    if (len(args) < 3):
        raise ValueError(usage)

    db_name  = args[1]
    path_to_json  = args[2]
    output_mp3_path = args[3]
    
    db = Db(sqlite3.connect(db_name + '.db'), Sql())
    generator = GenratorWithSeed(db_name, db, Rnd())
    
    labels = read_json(path_to_json)
    
    usedBefore = set()
    
    fullTrack = textToAudioSegment("Hello, this AI streamer. Markov process on Reddit comments")
    
    curr_time_mksec = fullTrack.duration_seconds * 1000000
    
    while (curr_time_mksec <  max(labels['end'])):
        observedBefore = set(labels[labels['start'] < curr_time_mksec]['Label'])
        candidates = list(observedBefore - usedBefore)
        
        seedWords = 'Hmmm' 
        
        if len(candidates)>0: seedWords = candidates[0]
        
        seedWordsToGen = seedWords.lower()
        print str(curr_time_mksec ) + ' ' + seedWordsToGen 
        wordsToSay = generator.generate_to_right(seedWordsToGen.split(), WORD_SEPARATOR)
        print wordsToSay 
        
        segment = textToAudioSegment(wordsToSay)
        
        print segment.duration_seconds   
        print "---------"
        fullTrack = fullTrack + segment
        
        #print seedWords in usedBefore
        
        usedBefore = usedBefore.union(set([seedWords]))
        
        if segment.duration_seconds < 1. :
            curr_time_mksec = curr_time_mksec + 1000000
        else:
            curr_time_mksec = fullTrack.duration_seconds * 1000000
        
        
    fullTrack.export(output_mp3_path, format="mp3")
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
