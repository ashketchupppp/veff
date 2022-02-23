''' Video effects '''

import numpy as np
import cv2

from video import VideoWriter
from utils import diff_arrays, get_temp_file
from video import VideoReader, VideoWriter, open_writer_for_read
import log

def frame_difference(frames: list, config: dict, writer: VideoWriter, update=lambda x: None):
    ''' Applies a frame differencing effect to the passed frames '''
    previous = frames[0]
    # prev_std_deviation = np.std(previous)
    new_frames = []
    for frame in frames[1:]:
        new_frame = diff_arrays(previous, frame)
        new_frames.append(new_frame)
        previous = frame
        update()
    writer.write(new_frames)

def pixel_range(frames: list, config: dict, writer: VideoWriter, update=lambda x: None):
    ''' Removes all pixels above the upper bound and below the lower bound '''
    upper_bound = config['upper_bound']
    lower_bound = config['lower_bound']
    frames[0][lower_bound > frames[0]] = 0
    frames[0][upper_bound < frames[0]] = 0
    writer.write([frames[0]])
    update()

def std_deviation_filter(frames: list, config: dict, writer: VideoWriter, update=lambda x: None):
    ''' Removes all pixels above or below the passed number of standard deviations (of pixel values) '''
    num_std_devs = config['num_std_devs']
    std_deviation = np.std(frames[0])
    mean = np.mean(frames[0])
    percentile = 0.01
    bound = mean + (std_deviation * percentile)
    frames[0][(255 // 2) - bound > frames[0]] = 0
    frames[0][(255 // 2) + bound < frames[0]] = 0
    writer.write([frames[0]])
    update()

def grayscale(frames: list, config: dict, writer: VideoWriter, update=lambda x: None):
    ''' Grayscales the image '''
    frame_mean_pixel_colors = np.mean(frames[0], axis=(2))
    frames[0] = np.repeat(frame_mean_pixel_colors[:, :, np.newaxis], 3, axis=2)
    writer.write([frames[0]])
    update()

def bilateral_filter(frames: list, config: dict, writer: VideoWriter, update=lambda x: None):
    ''' Grayscales the image '''
    frames[0] = cv2.fastNlMeansDenoisingColored(frames[0], None, 10, 10, 7, 21)
    writer.write([frames[0]])
    update()

effects = {
    'frame_difference': {
        'batch_size': 2,
        'progress_name': 'Frame differencing',
        'method': frame_difference
    },
    'pixel_range': {
        'batch_size': 1,
        'progress_name': 'Pixel range filter',
        'method': pixel_range
    },
    'std_deviation_filter': {
        'batch_size': 1,
        'progress_name': 'Standard deviation filter',
        'method': std_deviation_filter
    },
    'grayscale': {
        'batch_size': 1,
        'progress_name': 'Grayscaling',
        'method': grayscale
    },
    'bilateral_filter': {
        'batch_size': 1,
        'progress_name': 'Bilateral filtering',
        'method': bilateral_filter
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
