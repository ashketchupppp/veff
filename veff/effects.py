''' Video effects '''

from audioop import mul
from multiprocessing import Process, Queue
import numpy as np
from utils import interleave

import log

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

def frame_difference(frames, config):
    ''' Applies a frame differencing effect to the passed frames '''
    pbar = log.progress_bar(len(frames), 'Frame differencing', 'frames')
    previous = frames[0]
    prev_std_deviation = np.std(previous)
    new_frames = []
    for frame in frames[1:-1]: # final frame will be of type None
        new_frame = np.absolute(np.subtract(np.int16(previous), np.int16(frame)))
        # eliminate flashes when the scene changes
        std_deviation = np.std(new_frame)
        if std_deviation < 2 * prev_std_deviation:
            new_frames.append(new_frame)
        prev_std_deviation = std_deviation
        previous = frame
        pbar.update()
    return new_frames

EFFECTS = {
    'frame_difference': frame_difference,
    'frame_interpolation': frame_interpolation
}
