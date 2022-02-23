''' Video effects '''

from abc import ABC, abstractclassmethod
import multiprocessing as mp
from cv2 import VideoWriter
import numpy as np
from utils import diff_arrays, get_temp_file
import time
import datetime

from video import VideoReader, VideoWriter, open_writer_for_read
import log

def frame_difference(frames: list, config: dict, writer: VideoWriter, update=lambda x: None):
    ''' Applies a frame differencing effect to the passed frames '''
    previous = frames[0]
    # prev_std_deviation = np.std(previous)
    new_frames = []
    for frame in frames[1:]:
        new_frame = diff_arrays(previous, frame)
        # eliminate flashes when the scene changes
        # std_deviation = np.std(new_frame)
        # if std_deviation < 10 * prev_std_deviation:
        #    new_frames.append(new_frame)
        # prev_std_deviation = std_deviation
        new_frames.append(new_frame)
        previous = frame
        update()
    writer.write(new_frames)

def pixel_range(frames: list, config: dict, writer: VideoWriter, update=lambda x: None):
    upper_bound = 245
    lower_bound = 10
    frame = frames[0]
    frame[lower_bound > frame] = 0
    frame[upper_bound < frame] = 0
    writer.write([frame])
    update()

effects = {
    'frame_difference': {
        'batch_size': 2,
        'progress_name': 'Frame differencing',
        'method': frame_difference
    },
    'pixel_range_filter': {
        'batch_size': 1,
        'progress_name': 'Pixel range filter',
        'method': pixel_range
    }
}

def is_effect(effect_name: str):
    return effect_name in effects

def batch_apply(video: VideoReader, effect_name: str, effect_config: dict):
    ''' Reads the passed video in batches, applies the effect and
        returns a VideoReader for the effected video
    '''
    pbar = log.progress_bar(video.frame_count, effects[effect_name]['progress_name'], 'frames')

    batch_size = effects[effect_name]['batch_size']
    writer = VideoWriter(
        get_temp_file(extension='mp4'),
        width=video.width,
        height=video.height,
        fps=video.fps,
        fourcc=video.fourcc
    )

    batch_frames = video.read(batch_size)

    while video.frames_read < video.frame_count:
        if len(batch_frames) > 0:
            effects[effect_name]['method'](batch_frames, effect_config, writer, pbar.update)
        batch_frames.pop(0)
        batch_frames = [*batch_frames, *video.read(1)]

    reader = open_writer_for_read(writer)
    writer.close()
    return reader
