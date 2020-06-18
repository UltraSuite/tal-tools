#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helper functons to the TaL visualiser.

Date: 2020
Author: M. Sam Ribeiro
"""

from __future__ import print_function
import skimage


def resize(data, target_frames):
    ''' resize data stream '''
    num_frames = data.shape[0]
    x, y = data.shape[1], data.shape[2]
    output_shape = (target_frames, x*y)

    data = data.reshape(num_frames, -1)

    resized = skimage.transform.resize(data, \
        output_shape=output_shape, order=1, mode='edge', \
        clip=True, preserve_range=True, anti_aliasing=True)

    resized = resized.reshape(-1, x, y)

    return resized



def downsample(ultrasound, video, ultra_fps, video_fps, target_fps):
    '''downsample ultrasound/video to target fps '''
    # resize ultrasound
    target_ult_frames = int( ultrasound.shape[0] * target_fps / ultra_fps )
    ultrasound = resize(ultrasound, target_ult_frames)
    num_ult_frames = ultrasound.shape[0]

    # resize video
    target_vid_frames = int( video.shape[0] * target_fps / video_fps )
    video = resize(video, target_vid_frames)
    num_vid_frames = video.shape[0]

    if abs(num_vid_frames - num_ult_frames) > 5:
        print('Video and ultrasound frames exceeds threshold after resizing.')
        sys.exit(1)

    num_frames = min(num_vid_frames, num_ult_frames)
    ultrasound = ultrasound[:num_frames, :, :]
    video      = video[:num_frames, :, :]

    return ultrasound, video




def trim_to_parallel_streams(ult, vid, wav, params, meta, wav_sr):
    ''' trim data to parallel streams '''

    ult_fps = params['FramesPerSec']
    vid_fps = meta['fps']

    vid_len = vid.shape[0] / vid_fps
    wav_len = wav.shape[0] / wav_sr

    # trim data streams to common start and end time stamps
    # ultrasound is always the last to start recording,
    # so we take that as out start time
    start_time = params['TimeInSecsOfFirstFrame']
    # video and audio finish recording first
    end_time   = min(vid_len, wav_len)

    # video
    frame_start = int(start_time * vid_fps)
    frame_end = int(end_time * vid_fps)
    vid = vid[frame_start:frame_end,:,:]

    # audio
    sample_start = int(start_time * wav_sr)
    sample_end   = int(end_time * wav_sr)
    wav = wav[sample_start:sample_end,]

    # ultrasound
    frame_end = int((end_time - start_time)* ult_fps)
    ult = ult[:frame_end,:,:]

    return ult, vid, wav

