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
    subprocess.call('./chromecasttakeover.sh', shell=True)


textToInt = {'zero': 0, 'one': 1, 'won': 1, 'two': 2, 'to': 2, 'too': 2, 'three': 3, 'four': 4, 'for': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten':10}

def set_sleep_timer(text):
    global sleeptime
    default_minutes = 30
    words = text.split(' ')
    if len(words) <= 1: # default command (e.g. "sleep")
        minutes = str(default_minutes)
    elif len(words) >= 3 and words[1] == "in": # "sleep in x minutes"
        minutes = words[2]
    else: # "sleep 15 minutes"
        minutes = words[1]

    if not minutes.isdecimal():
        minutes = textToInt.get(minutes,default_minutes) 
    if sys.stdout.isatty():
        print ("sleep minutes: ", minutes)
    sleeptime = time.time() + int(minutes)*60
    announce_time_left()


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
        print('You said "', text, '"')
        text = text.lower()
        if text.startswith('sleep') or text.startswith('week') or \
           text.startswith('weak') or text.startswith('sweet'):
            set_sleep_timer(text)
        elif text.startswith('cancel'):
            cancel_sleep_timer()
        elif text.startswith('time') or text.startswith('how much time'):
            announce_time_left()
        elif text == 'ip address':
            ip_address()
        else:
            skipGoogleAudioResponse=False
    else:
        set_sleep_timer("sleep")
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
            set_led()
        time.sleep(15)
    recorder.__exit__() # we never clean up since we run forever


if __name__ == '__main__':
    main()
