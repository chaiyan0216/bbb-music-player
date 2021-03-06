#!/usr/bin/python3

import os
import random
import subprocess
import sys
import time

import Adafruit_BBIO.GPIO as GPIO

KEYS = ["P8_8", "P8_10", "P8_12", "P8_14", "P8_16"]
GNDK = "P8_18"
UP = KEYS[4]
DOWN = KEYS[3]
LEFT = KEYS[2]
RIGHT = KEYS[1]
MID = KEYS[0]

LEDS = ["P9_11", "P9_13", "P9_15"]
GNDL = "P9_17"
BLUE = LEDS[0]
RED = LEDS[1]
GREEN = LEDS[2]

STATES = [GPIO.HIGH, GPIO.LOW]

def _init_key():
    for key in KEYS:
        GPIO.setup(key, GPIO.IN, GPIO.PUD_UP)
        GPIO.add_event_detect(key, GPIO.FALLING)
    GPIO.setup(GNDK, GPIO.OUT)
    GPIO.output(GNDK, GPIO.LOW)
    for led in LEDS:
        GPIO.setup(led, GPIO.OUT)
    GPIO.setup(GNDL, GPIO.OUT)
    GPIO.output(GNDL, GPIO.LOW)

def _read_step(size):
    if GPIO.event_detected(LEFT):
        GPIO.output(RED, GPIO.HIGH);
        GPIO.output(GREEN, GPIO.LOW);
        GPIO.output(BLUE, GPIO.LOW);
        return -1
    elif GPIO.event_detected(RIGHT):
        GPIO.output(RED, GPIO.LOW);
        GPIO.output(GREEN, GPIO.HIGH);
        GPIO.output(BLUE, GPIO.LOW);
        return 1
    elif GPIO.event_detected(UP) or GPIO.event_detected(DOWN) or GPIO.event_detected(MID):
        GPIO.output(RED, random.choice(STATES));
        GPIO.output(GREEN, random.choice(STATES));
        GPIO.output(BLUE, random.choice(STATES));
        return random.randint(-1 * size + 1, size - 1);
    return 0

def _get_songs(path):
    songs = []
    for (root, dirs, files) in os.walk(path):
        for file in files:
            if file.endswith(".mp3"):
                songs += [os.path.abspath(os.path.join(root, file))]
    return songs

def _play_song(process, path):
    if (not process is None) and (process.poll() is None):
        process.kill()
    print(path)
    args = ["sox", path, "-t", "alsa", "plughw:1,0"]
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
    return process

def _next_song_index(index, step, size):
    print("index, step:", index, step)
    index += step
    if index >= size:
        index -= size 
    elif index < 0:
        index += size
    return index

def _loop(songs):
    if len(songs) == 0:
        return
    index = 0
    step = 0
    process = None
    while True:
        process = _play_song(process, songs[index])
        while process.poll() is None:
            step = _read_step(len(songs))
            if step != 0:
                break
            else:
                time.sleep(0.5)
        step = 1 if not step else step
        index = _next_song_index(index, step, len(songs))


if __name__ == "__main__":
    _init_key()

    path = sys.argv[1] if len(sys.argv) == 2 else "./"
    print("Path:", os.path.abspath(path))

    songs = _get_songs(path)
    print("Songs:", len(songs))

    _loop(songs)
