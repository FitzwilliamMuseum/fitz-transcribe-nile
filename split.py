
#!/usr/bin/python
## Split audio files into chunks
## Daniel Pett 1/5/2020
__author__ = 'portableant'
## Tested on Python 2.7.13

import argparse
import os
import speech_recognition as sr
import csv
from csv import writer
from pydub import AudioSegment
from pydub.utils import which

AudioSegment.converter = which("ffmpeg")

from pydub.utils import make_chunks

r = sr.Recognizer()

parser = argparse.ArgumentParser(description='A script for splitting audio files into segements')
parser.add_argument('-p', '--path', help='The path to the folder to process', required=True)
# An example would be: --path '/Users/danielpett/githubProjects/fitzAudioGuide/aac'

parser.add_argument('-d', '--destination', help='The destination folder', required=True)
# An example would be: --destination '/Users/danielpett/githubProjects/fitzAudioGuide/chunked/'

parser.add_argument('-c', '--csv', help='The destination folder', required=True)
# An example would be: --csv '/Users/danielpett/githubProjects/fitzAudioGuide/csv/'

parser.add_argument('-m,', '--mp3', help='The MP3 convert folder', required=True)

parser.add_argument('-l', '--length', help='Length of chunk', required=True)
# An example would be --length 10000

# Parse arguments
args = parser.parse_args()

path = args.path
mp3 = args.mp3
destination = args.destination
length = args.length
csvfile = args.csv
chwav = '/Users/danielpett/Documents/githubProjects/aac/chunk-wav/'
chmp3 = '/Users/danielpett/Documents/githubProjects/aac/chunk-mp3/'

# Chunk mp3 files and convert to wav

# Convert aac files to MP3 for chunking
for file in os.listdir(path):
    print("File name: " + file)
    print("Now processing: " + os.path.join(path,file))
    convert = os.path.join(path,file)
    print("Conversion: " + convert)
    aac_audio = AudioSegment.from_file(convert, "aac")
    basename = file[:-4]
    print("Basename: " + basename)
    mp3FileName = basename + ".mp3"
    print("Basename: " + mp3FileName)
    mp3FileDest = os.path.join(mp3, mp3FileName)
    print(mp3FileDest)
    mp3_audio = aac_audio.export(mp3FileDest, format="mp3")

for file in os.listdir(mp3):
    print('Now processing: ' + file)
    myaudio = AudioSegment.from_file(os.path.join(mp3,file), "mp3")
    # Make chunks of length specified
    chunk_length_ms = length
    chunks = make_chunks(myaudio, int(length))
    for i, chunk in enumerate(chunks):
        processedFileName = os.path.splitext(file)[0]
        chunk_name_mp3 = processedFileName + "_Chunk{0}.mp3".format(i)
        print("Now exporting: " , chunk_name_mp3)
        print(os.path.join(chmp3,chunk_name_mp3))
        chunk.export(os.path.join(chmp3,chunk_name_mp3), format="mp3")
        chunk_name_wav = processedFileName + "_Chunk{0}.wav".format(i)
        print("Now exporting: " , chunk_name_wav)
        chunk.export(os.path.join(chwav,chunk_name_wav), format="wav")

# Create the csv file for Pybossa import

transcriptions = []
for file in os.listdir(chwav):
    print('Now processing: ' + file)
    if file.endswith('.wav'):
        #print("Source file " + file)
        sourceFile = os.path.join(chwav,file)
        audio = AudioSegment.from_file(sourceFile)
        duration =  audio.duration_seconds
        if(duration > 4):
            with sr.AudioFile(sourceFile) as source:
                # listen for the data (load audio to memory)
                audio_data = r.record(source)
                # recognize (convert from speech to text)
                text = r.recognize_google(audio_data)
                #print('Output for ' + file + ': ' + text)
                extension = '.mp3'
                basefile = os.path.splitext(file)[0] + extension
                #print(basefile)
                mp3file = os.path.join('https://fitz-audio-guide-micropasts.s3.eu-west-2.amazonaws.com/',basefile)
                transcriptions.append([mp3file,text])

#print(transcriptions)

csvOutput = '/Users/danielpett/Documents/githubProjects/aac/csv/transcriptions.csv'
file_exists = os.path.isfile(csvOutput)

with open (csvOutput, 'w') as csvfile:
    writer = csv.writer(csvfile , lineterminator='\n')
    writer.writerow(['track','currentTranscription'])
    for tup in transcriptions:
        writer.writerow(tup)

print('Good job my friend!')
