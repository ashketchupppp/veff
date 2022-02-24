''' Video effects '''

from scipy import signal
import numpy as np
import cv2

from video import VideoWriter
from utils import diff_arrays, get_temp_file
from video import VideoReader, VideoWriter, open_writer_for_read
import log

# Could do some edge detection and then do something with the pixels at the edges???

def frame_difference(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Applies a frame differencing effect to the passed frames '''
    new_frame = diff_arrays(frames[0], frames[-1])
    current_stddev = np.std(new_frame)
    try:
        if current_stddev < 2 * frame_difference.prev_stddev:
            writer.write([new_frame])
    except AttributeError:
        pass # prev_setddev hasnt been set yet
    finally:
        frame_difference.prev_stddev = current_stddev
    update()

def denoise(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Denoises the video using a wiener filter'''
    new_frame = signal.wiener(frames[0])
    writer.write([new_frame])
    update()

def increasing(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Applies a frame differencing effect to the passed frames '''
    new_frame = np.subtract(frames[1], frames[0])
    new_frame[new_frame > 0] = 0
    new_frame = np.absolute(new_frame)
    writer.write([new_frame])
    update()

def edge(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    writer.write([cv2.Canny(frames[0], 100, 200)])
    update()

def decreasing(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Applies a frame differencing effect to the passed frames '''
    new_frame = np.subtract(frames[1], frames[0])
    new_frame[new_frame < 0] = 0
    writer.write([new_frame])
    update()

def pixel_range(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Removes all pixels above the upper bound and below the lower bound '''
    upper_bound = config['upper_bound']
    lower_bound = config['lower_bound']
    mean = np.mean(frames[0], axis=(2))
    grayscale = np.repeat(mean[:, :, np.newaxis], 3, axis=2)
    frames[0][lower_bound > grayscale] = 0
    frames[0][upper_bound < grayscale] = 0
    writer.write([frames[0]])
    update()

def std_deviation_filter(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Removes all pixels above or below the passed number of standard deviations (of pixel values) '''
    std_deviation = np.std(frames[0])
    mean = np.mean(frames[0])
    percentile = 0.01

    bound = mean + (std_deviation * percentile)
    frames[0][(255 // 2) - bound > frames[0]] = 0
    frames[0][(255 // 2) + bound < frames[0]] = 0
    writer.write([frames[0]])
    update()

def grayscale(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Grayscales the image '''
    frame_mean_pixel_colors = np.mean(frames[0], axis=(2))
    frames[0] = np.repeat(frame_mean_pixel_colors[:, :, np.newaxis], 3, axis=2)
    writer.write([frames[0]])
    update()

def bilateral_filter(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Grayscales the image '''
    frames[0] = cv2.fastNlMeansDenoisingColored(frames[0], None, 10, 10, 7, 21)
    writer.write([frames[0]])
    update()

def light_saturation_detector(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Increases and decreases the saturation based on the mean amount of light in the frame '''
    new_frame = np.abs(np.subtract(frames[1], frames[0]))
    amount_of_light = np.sum(new_frame) / (writer.width * writer.height * 255 * 3)
    increase = (255 * amount_of_light)
    new_frame[new_frame > 64] = new_frame + increase
    writer.write([new_frame])
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
    },
    'increasing': {
        'batch_size': 2,
        'progress_name': 'Increasing filter',
        'method': increasing
    },
    'decreasing': {
        'batch_size': 2,
        'progress_name': 'Decreasing filter',
        'method': decreasing
    },
    'edge': {
        'batch_size': 1,
        'progress_name': 'Edge detecting',
        'method': edge
    },
    'light_saturation_detector': {
        'batch_size': 2,
        'progress_name': 'Light saturation detection',
        'method': light_saturation_detector
    },
    'denoise': {
        'batch_size': 1,
        'progress_name': 'Denoising',
        'method': denoise
    }
}

def batch_apply(video: VideoReader, effect_name: str, effect_config: dict):
    ''' Reads the passed video in batches, applies the effect and
        returns a VideoReader for the effected video
    '''
    pbar = log.progress_bar(video.frame_count, effects[effect_name]['progress_name'], 'frames')

    if 'batch_size' in effect_config:
        batch_size = effect_config['batch_size']
    elif 'batch_size' in effects[effect_name]:
        batch_size = effects[effect_name]['batch_size']
    else:
        raise NotFoundErr('batch_size')
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
