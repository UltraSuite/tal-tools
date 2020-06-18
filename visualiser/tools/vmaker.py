#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Make video from set of frames using ffmpeg.

Date: 2020
Author: M. Sam Ribeiro
"""

from __future__ import print_function

import os
import shutil
import subprocess

import numpy as np
import scipy.io.wavfile as wavfile



def make(frame_directory, config, audio, sample_rate, identifier):


    # video encoding parameters
    frame_rate    = config.target_fps
    vbitrate      = config.vbitrate
    vscale        = config.vscale
    vencoder      = config.vencoder
    pixel_format  = config.pixel_format

    # audio encoding parameters
    abitrate = config.abitrate
    aencoder = config.aencoder

    remove_data = config.delete_intermediate_data


    # define filenames
    tmp_audio_file = "{0}_audio.wav".format(identifier)
    tmp_video_file = "{0}_video.mp4".format(identifier)
    output_file    = "{0}.mp4".format(identifier)

    tmp_video_path = os.path.join(config.output_directory, tmp_video_file)
    tmp_audio_path = os.path.join(config.output_directory, tmp_audio_file)
    output_path    = os.path.join(config.output_directory, output_file)

    # make video from frames
    # we must use mp4 container and libx264, which can be played by html5
    # using '-y' below overwrites existing files
    # e.g. ffmpeg -hide_banner -y -r ${fps} -i ${input} -vf "scale=320:240" -b:v 1000k -c:v libx264 -pix_fmt yuv420p -f mp4 ${output}.mp4
    cmd = 'ffmpeg -hide_banner -y -r {0} -i {1} -vf \"scale={2}\" -b:v {3}k -c:v {4} -pix_fmt {5} -f mp4 {6}'.\
        format(frame_rate, frame_directory + "/%07d.jpg", vscale, vbitrate, vencoder, pixel_format, tmp_video_path)
    subprocess.call(cmd, shell=True)

    # save cropped waveform to file
    audio = np.asarray(audio, dtype=np.int16)
    wavfile.write(tmp_audio_path, sample_rate, audio)


    # merge audio and video
    # we must encode audio with ac3, which is compatible with mp4
    # using '-y' below overwrites existing files
    # e.g. ffmpeg -hide_banner -y -i input.mp4 -i input.wav -c:v copy -map 0:v:0 -map 1:a:0 -c:a ac3 -b:a 192k output.mp4
    cmd = 'ffmpeg -hide_banner -y -i {0} -i {1} -c:v copy -map 0:v:0 -map 1:a:0 -c:a {2} -b:a {3}k -strict -2 {4}'.\
        format(tmp_video_path, tmp_audio_path, aencoder, abitrate , output_path)
    subprocess.call(cmd, shell=True)


    # remove tmp data, if needed
    if remove_data:
        shutil.rmtree(frame_directory)
        os.remove(tmp_video_path)
        os.remove(tmp_audio_path)



