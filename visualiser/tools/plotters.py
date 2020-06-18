#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Plot individual video frames.

Date: 2020
Author: M. Sam Ribeiro
"""

import os
from textwrap import wrap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec



def set_dark_mode():
    ''' set global variables for matplotlib's dark mode'''

    # a simple way is to use:
    # plt.style.use('dark_background')

    # but we want more control so we use parameters adapted from here:
    # https://stackoverflow.com/questions/48391568/matplotlib-creating-plot-for-black-background-presentation-slides
    plt.rcParams.update({
        "lines.color": "white",
        "patch.edgecolor": "black",
        "text.color": "black",
        "axes.facecolor": "white",
        "axes.edgecolor": "black",
        "axes.labelcolor": "white",
        "xtick.color": "white",
        "ytick.color": "white",
        "grid.color": "black",
        "figure.facecolor": "black",
        "figure.edgecolor": "black",
        "savefig.facecolor": "black",
        "savefig.edgecolor": "black"}
        )




def plot_video_frames(ult, vid, wav, txt, \
    sample_rate, frame_rate, config, frame_directory):
    """ Writes ultrasound, speech, and spectrogram as images to a directory. """

    width_ratios = [1, 0.8]

    # standard parameters from configuration file
    plot_spectrogram = config.make_spectrogram
    plot_waveform    = config.make_waveform
    plot_text        = config.make_prompt_text

    dark_mode = config.dark_mode

    spectrogram_frame_size  = config.spectrogram_frame_size
    spectrogram_frame_shift = config.spectrogram_frame_shift
    spectrogram_color_map   = config.spectrogram_color_map

    text_font_size  = config.text_font_size
    text_wrap_width = config.text_wrap_width

    dpi = config.dpi
    size = config.figure_size
    fig_size = (size[0]/float(dpi), size[1]/float(dpi))


    if dark_mode:
        set_dark_mode()


    if not os.path.exists(frame_directory):
        os.makedirs(frame_directory)


    plt.figure(dpi=dpi, frameon=False, figsize=fig_size)
    fig = plt.gcf()

    # set grid with relevant axes
    if plot_waveform and plot_spectrogram:
        gs = gridspec.GridSpec(4, 2, width_ratios=width_ratios, figure=fig)
        wav_ax  = fig.add_subplot(gs[0,:])
        spec_ax = fig.add_subplot(gs[1,:])
        ult_ax  = fig.add_subplot(gs[2:,0])
        vid_ax  = fig.add_subplot(gs[2:,1])

    elif plot_waveform:
        gs = gridspec.GridSpec(3, 2, width_ratios=width_ratios, figure=fig)
        wav_ax = fig.add_subplot(gs[0,:])
        ult_ax = fig.add_subplot(gs[1:,0])
        vid_ax = fig.add_subplot(gs[1:,1])

    elif plot_spectrogram:
        gs = gridspec.GridSpec(3, 2, width_ratios=width_ratios, figure=fig)
        spec_ax = fig.add_subplot(gs[0,:])
        ult_ax = fig.add_subplot(gs[1:,0])
        vid_ax = fig.add_subplot(gs[1:,1])

    else:
        gs = gridspec.GridSpec(1, 2, width_ratios=width_ratios, figure=fig)
        ult_ax = plt.subplot(gs[0])
        vid_ax = plt.subplot(gs[1])

    gs.update(wspace=0.0, hspace=0.0)

    # plot waveform
    if plot_waveform:
        total_samples = wav.shape[0]

        # # if we want a full dark theme on the waveform axis (dark background)
        # wav_ax.plot(wav, color='white', linewidth=0.2)
        # wav_ax.axis("off")

        # here, we use a light background, even if using a dark theme.
        wav_ax.plot(wav, color='black', linewidth=0.2)

        wav_ax.set_xlim([0, total_samples])
        wav_ax.set_xticks([])
        wav_ax.set_yticks([])
        max_wav_x  = wav.shape[0]


    # plot spectrogram
    if plot_spectrogram:

        nfft    = int(sample_rate * (spectrogram_frame_size/1000.))
        overlap = int(sample_rate * (spectrogram_frame_shift/1000.))

        # spectrogram with matplotlib: 
        # https://matplotlib.org/api/_as_gen/matplotlib.pyplot.specgram.html
        spectrum, freqs, bins, spec_im = spec_ax.specgram(wav.reshape(-1,),\
            NFFT=nfft, Fs=sample_rate, noverlap=overlap, cmap=spectrogram_color_map)

        spec_im.set_interpolation('bilinear')

        spec_ax.set_xticks([])
        spec_ax.set_yticks([])
        xlim = spec_ax.get_xlim()
        spec_ax.set_xlim([0, xlim[1]])
        max_spec_x = xlim[-1]

    # prompt text
    if plot_text:
        color = 'white' if dark_mode else 'black'
        txt = "\n".join(wrap(txt, text_wrap_width))
        fig.suptitle(txt, fontsize=text_font_size, color=color)

    # plot ultrasound and video frame-by-frame
    num_frames = ult.shape[0]

    ult_im = ult_ax.imshow(ult[0].T, aspect='equal', origin='lower', cmap='gray')
    vid_im = vid_ax.imshow(vid[0],   aspect='equal', origin='upper', cmap='gray')

    for i in range(0, num_frames):
        u = ult[i]
        v = vid[i]

        if plot_waveform:
            wav_x = int( (1/frame_rate) * i * sample_rate)
            wav_x = min(wav_x, max_wav_x)
            ln1 = wav_ax.axvline(x=wav_x, color='red')

        if plot_spectrogram:
            spec_x = (1/frame_rate) * i
            spec_x = min(spec_x, max_spec_x)
            ln2 = spec_ax.axvline(x=spec_x, color='red')

        ult_im.set_data(u.T)
        vid_im.set_data(v)

        ult_ax.axis("off")
        vid_ax.axis("off")

        plt.savefig(frame_directory + "/%07d.jpg" % i, bbox_inches='tight', pad_inches=0.1, dpi=dpi)

        if plot_waveform:    ln1.remove()
        if plot_spectrogram: ln2.remove()

    plt.close()