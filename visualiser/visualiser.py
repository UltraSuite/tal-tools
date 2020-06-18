#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TaL corpus visualiser.
Create video examples of TaL data.

Example usage: python visualiser.py -c config.ini -s 05ms -f 003_cal

Date: 2020
Author: M. Sam Ribeiro
"""

import os
import argparse

from tools import utils
from tools import vmaker
from tools import plotters
from tools import io as myio
from tools.config import Config

from ustools.transform_ultrasound import transform_ultrasound


def main(config_filename, speaker, file_id):
    config = Config(config_filename)
    basepath = os.path.join(config.tal_corpus, speaker, file_id)
    identifier = '-'.join([speaker, file_id])

    # read input data
    txt         = myio.read_text_from_file(basepath + '.txt')[0]
    wav, wav_sr = myio.read_waveform(basepath+'.wav')
    ult, params = myio.read_ultrasound_tuple(basepath, shape='3d', cast=None, truncate=None)
    vid, meta   = myio.read_video(basepath, shape='3d', cast=None)

    ult_fps = params['FramesPerSec']
    vid_fps = meta['fps']

    # trim streams to parallel data
    ult, vid, wav = utils.trim_to_parallel_streams(ult, vid, wav, params, meta, wav_sr)

    # transform ultrasound to real world coordinates
    ultrasound_background_colour = 255
    if config.dark_mode:
        ultrasound_background_colour=0

    ult = transform_ultrasound(ult, \
        spline_interpolation_order=2, background_colour=ultrasound_background_colour, \
        num_scanlines=params['scanlines'], size_scanline=params['echos'], \
        angle=params['Angle'], zero_offset=params['ZeroOffset'], pixels_per_mm=1.0)

    # bit of hacky way to trim the ultrasound
    # it works well without this box, but using this box makes it a bit nicer
    ult = ult[:, 180:-180, 120:-100]

    # downsample ultrasound and video to target fps
    ult, vid = utils.downsample(ult, vid, ult_fps, vid_fps, config.target_fps)

    # plot data frame by frame
    frame_directory = os.path.join(config.output_directory, identifier+'_frames')
    plotters.plot_video_frames(ult, vid, wav, txt, wav_sr, config.target_fps, config, \
        frame_directory)

    # make final video file from frames
    vmaker.make(frame_directory, config, wav, wav_sr, identifier)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config',  '-c', type=str, required=True, help='configuration file')
    parser.add_argument('--speaker', '-s', type=str, required=True, help='speaker or session name (e.g. 05ms')
    parser.add_argument('--file',    '-f', type=str, required=True, help='utterance identifier (e.g. 003_cal')
    args = parser.parse_args()

    main(args.config, args.speaker, args.file)
