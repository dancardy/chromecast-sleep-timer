#! /usr/bin/env python3

import aiy.assistant.grpc
import aiy.audio
import aiy.voicehat
import sys
import subprocess
from decimal import *
import time

sleeptime = 0

def sleep_now():
    global sleeptime
    sleeptime = 0
    print ("about to sleep")
    try:
        subprocess.call('./chromecasttakeover.sh', timeout=30, shell=True)
    except subprocess.TimeoutExpired:
        pass
    print("sleep completed")
    set_led()


def process_sleep_phrase(text):
    words = text.split(' ')
    if len(words) <= 1: # default command (e.g. "sleep")
        minutes = -1 # flag for no number given
    elif len(words) >= 3 and words[1] == "in": # "sleep in x minutes"
        minutes = word_as_num(words[2])
    elif words[1] == 'now':
        sleep_now()
        return
    else: # "sleep 15 minutes"
        minutes = word_as_num(words[1])
    set_sleep_timer(minutes)


def set_sleep_timer(minutes):
    global sleeptime
    default_minutes = 30
    if minutes <= 0:
        minutes = default_minutes
    if sys.stdout.isatty():
        print ("sleep minutes: ", minutes)
    sleeptime = time.time() + minutes*60
    announce_time_left()


def first_word_as_num(text):
    words=text.split(' ')
    if len(words) >=1:
        return word_as_num(words[0])
    else:
        return -1


textToInt = {'zero': 0, 'one': 1, 'won': 1, 'two': 2, 'to': 2, 'too': 2, 'three': 3, 'four': 4, 'for': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten':10}

def word_as_num(word):
    num = textToInt.get(word,-1)
    if word.isdecimal():
        return int(word)
    else:
        return num


def cancel_sleep_timer():
    global sleeptime
    sleeptime = 0
    aiy.audio.say('cancelled')


def announce_time_left():
    seconds = sleeptime - time.time()
    if sleeptime == 0:
        aiy.audio.say('No timer set.')
    elif seconds < 60:
        aiy.audio.say('Less than one minute.')
    else:
        minutes = str(round(seconds/60))
        aiy.audio.say('%s minutes' % minutes)


def ip_address():
    ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
    aiy.audio.say('My IP address is %s' % ip_address.decode('utf-8'))


def set_led():
    led = aiy.voicehat.get_status_ui()
    if sleeptime == 0:
        led.status('power-off')
    else:
        led.status('ready')
 

def on_button_press():
    aiy.voicehat.get_status_ui().status('listening')
    text, audio = aiy.assistant.grpc.get_assistant().recognize()
    skipGoogleAudioResponse=True
    if text:
        if sys.stdout.isatty():
            print('You said "', text, '"')
        text = text.lower()
        first_word_num = first_word_as_num(text)

        if text.startswith('sleep') or text.startswith('week') or \
           text.startswith('weak') or text.startswith('sweet'):
            process_sleep_phrase(text)
        elif first_word_num != -1:
            set_sleep_timer(first_word_num)
        elif text.startswith('cancel'):
            cancel_sleep_timer()
        elif text.startswith('time') or text.startswith('how much time'):
            announce_time_left()
        elif text == 'ip address':
            ip_address()
        else:
            skipGoogleAudioResponse=False
    else:
        set_sleep_timer(-1)
    if audio and skipGoogleAudioResponse == False:
        aiy.audio.play_audio(audio)
    set_led()


def main():
    aiy.voicehat.get_status_ui().status('power-off')

    aiy.audio.set_tts_pitch(120)
    aiy.audio.set_tts_volume(60)

    recorder = aiy.audio.get_recorder()
    recorder.__enter__()

    aiy.voicehat.get_button().on_press(on_button_press)
    
    # Check if it is time for sleep timer to turn off the chromecast
    while True:
        if sys.stdout.isatty():
            if sleeptime != 0:
                print ('sleeping in: ', sleeptime - time.time())
        if sleeptime != 0 and time.time() > sleeptime:
            sleep_now()
        time.sleep(15)
    recorder.__exit__() # we never clean up since we run forever


if __name__ == '__main__':
    main()
