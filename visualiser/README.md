# TaL Tools Visualiser
This directory contains a module to help with the visualisation of the TaL corpus.



#### Requirements

Please make sure the following Python libraries and their dependencies are available.

- numpy
- scipy
- skimage
- imageio
- matplotlib

Additionally, we use [ffmpeg](https://ffmpeg.org) to create the video files. Please make sure this is available on your system.


#### Usage

Most of the configurable parameters are defined in `config.ini`.
In the configuration file, please replace `<PATH-TO-TAL-CORPUS>` with the absolute path to the location of the TaL corpus on your system. Replace also `<OUTPUT-DIRECTORY>` with the location of where the output video files should be placed.

To create a video, you can run something like:

`python visualiser.py -config config.ini -speaker 05ms -file 003_cal`

Or

`python visualiser.py -c config.ini -s 05ms -f 003_cal`

This command will make a video using utterance 003_cal from speaker 05ms.


#### Examples

TODO

