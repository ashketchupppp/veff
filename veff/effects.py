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

effects = {
    'frame_difference': {
        'batch_size': 2,
        'progress_name': 'Frame differencing',
        'method': frame_difference
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

    return open_writer_for_read(writer)

def multiprocess_frame_difference(frames, config):
    ''' Applies frame differencing using multiprocess.
        Don't use this, I'm just keeping it here as an example for how you would write
        a multiprocess function if I needed one in the future.
    '''
    pbar = log.progress_bar(len(frames), 'Frame differencing', 'frames')
    previous = frames[0]
    prev_std_deviation = np.std(previous)
    new_frames = []

    frame_pairs = [(frames[i], frames[i + 1]) for i in range(len(frames[:-1]))]
    assert all([len(fp) == 2 for fp in frame_pairs])
    with mp.Pool(mp.cpu_count()) as pool:
        time.clock()
        new_frames = pool.starmap(diff_arrays, frame_pairs, len(frames) // 4)
        print(time.clock())
    return new_frames

def frame_interpolation(frames, config):
    ''' Inserts new frames that are the average of each two frames '''
    interpolation_passes = 2
    pbar = log.progress_bar(len(frames), 'Slow motion interpolation', 'frames')
    new_frames = []
    i = 0
    while i < len(frames) - 2:
        current_frame = frames[i]
        next_frame = frames[i + 1]
        difference_frame = np.absolute(
            np.subtract(np.int16(current_frame), np.int16(next_frame))
        )
        interpolated_frame = current_frame + (difference_frame * (1 / interpolation_passes))
        new_frames.append(current_frame)
        new_frames.append(interpolated_frame)

        pbar.update()
        i += 1
    return new_frames
