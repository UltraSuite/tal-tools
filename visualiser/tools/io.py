
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Everything related to reading and writing of files.

Date: 2020
Author: M. Sam Ribeiro
"""

from __future__ import print_function

import imageio
import numpy as np
import scipy.io.wavfile as wavfile



def read_text_from_file(filename):
    ''' reader for text files '''
    with open(filename) as fid:
        lines = fid.readlines()
    return [l.rstrip() for l in lines]


def read_waveform(filename):
    ''' read waveform '''
    sr, wav = wavfile.read(filename)
    wav = wav.reshape(-1, 1)
    return wav, sr


def read_ultrasound_param(filename):
    ''' read ultrasound parameters from file'''
    params = {}
    with open(filename) as param_id:
        for line in param_id:
            name, var = line.partition("=")[::2]
            params[name.strip()] = float(var)

    scanlines = int(params['NumVectors'])
    echos     = int(params['PixPerVector'])
    frame_size = int( scanlines * echos )

    params['frame_size'] = frame_size
    params['scanlines'] = scanlines
    params['echos'] = echos

    return params


def read_ultrasound_data(filename):
    ''' read ultrasound data from file '''
    fid = open(filename, "r")
    ultrasound = np.fromfile(fid, dtype=np.uint8)
    fid.close()
    return ultrasound


def read_ultrasound_tuple(path, shape='2d', cast=None, truncate=None):
    '''
        read ultrasound data and parameters
        shape '2d': (frames, frame_size)
              '3d': (frames, scanlines, echos)
              anything else defaults to '1d' (single vector)
        cast: (str) ultrasound is uint8, cast to a different data type
        truncate: (int) truncate ultrasound to first N frames
    '''

    params      = read_ultrasound_param(path + '.param')
    ultrasound  = read_ultrasound_data(path + '.ult')

    if cast:
        ultrasound = ultrasound.astype(cast)

    n_frames =  int( ultrasound.size / params['frame_size'] )

    if shape == '2d':
        ultrasound = ultrasound.reshape((n_frames, params['frame_size']))
    elif shape == '3d':
        ultrasound = ultrasound.reshape((n_frames, params['scanlines'], params['echos']))

    if truncate:
        if truncate < n_frames:
            ultrasound = ultrasound[:truncate]

    return ultrasound, params


def read_video(path, shape='3d', cast=None):
    '''
        read video data and parameters
        shape '2d': (frames, frame_size)
              anything else defaults to '3d' (frames, width, height)
    '''
    filename   = path + '.mp4'
    reader = imageio.get_reader(filename,  'ffmpeg')

    # we can get some metadata for the video file
    # things like: fps, size, codec, duration, plugin, pix_fmt
    metadata = reader.get_meta_data()

    # this method estimates the number of frames using ffmpeg
    # might be longer for big files
    number_frames = reader.count_frames()

    frames = []
    for i in range(number_frames):
        image = reader.get_data(i)
        # convert frame to numpy array
        # shape will be (X,Y,3), where X,Y are image dimensions and 3 is YUV channels

        # we can sum all three channels
        frame = image.sum(axis=2)

        # # or we take only the Y channel
        # frame = np.asarray(image)[:,:,0]

        frames.append(frame)

    frames = np.stack(frames, axis=0)

    if cast:
        frames = frames.astype(cast)

    if shape == '2d':
        size = metadata['size']
        frames = frames.reshape((number_frames, size[0]*size[1]))

    return frames, metadata

