''' Video effects '''

from uuid import SafeUUID
from scipy import signal
import numpy as np
import cv2
import matplotlib as mpl

from video import VideoWriter
from utils import diff_arrays, get_temp_file
from video import VideoReader, VideoWriter, open_writer_for_read
import log

# Could do some edge detection and then do something with the pixels at the edges???

class ItsFuckedError(Exception):
    pass # :) just commit your broken code its fiiiine

def frame_difference(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Applies a frame differencing effect to the passed frames '''
    new_frame = diff_arrays(frames[0], frames[-1])
    writer.write([new_frame])
    update()

def median_bound_pass(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Zero's out all pixels below the median '''
    raise ItsFuckedError
    median_pixel_color = np.median(frames[0])
    lower_bound = config['multiplier'] *  median_pixel_color
    frames[0][lower_bound > frames[0]] = 0
    writer.write([frames[0]])
    update()

def denoise(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Denoises the video using a wiener filter'''
    raise ItsFuckedError
    # https://paperswithcode.com/paper/ffdnet-toward-a-fast-and-flexible-solution
    new_frame = signal.wiener(frames[0])
    writer.write([new_frame])
    update()

def increasing(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Applies a frame differencing effect to the passed frames. but only for pixels that increased in rgb value '''
    new_frame = np.subtract(frames[1], frames[0])
    new_frame[new_frame > 0] = 0
    new_frame = np.absolute(new_frame)
    writer.write([new_frame])
    update()

def decreasing(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Applies a frame differencing effect to the passed frames, but only for pixels that decreased in rgb values '''
    new_frame = np.subtract(frames[1], frames[0])
    new_frame[new_frame < 0] = 0
    writer.write([new_frame])
    update()

def edge(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Applies an edge detection algorithm to the video, not working atm '''
    raise ItsFuckedError
    writer.write([cv2.Canny(frames[0], 100, 200)])
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
    # shit doesnt work
    std_deviation = np.std(frames[0])
    mean = np.mean(frames[0])
    percentile = 0.01

    bound = mean + (std_deviation * percentile)
    frames[0][(255 // 2) - bound > frames[0]] = 0
    frames[0][(255 // 2) + bound < frames[0]] = 0
    writer.write([frames[0]])
    update()

def saturation(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Increases the saturation of the image '''
    raise ItsFuckedError
    # often leads to pixels being maxed out, leading to massive patches of red, green or blue
    # need a way to prevent this, maybe dividing the strength by a larger value or having it be a percentage
    strength = config['strength']
    writer.write([frames[0] * strength])
    update()

def grayscale(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Makes the image grayscale according to the configured strength '''
    strength = config['strength']
    means = np.mean(frames[0], axis=(2))
    means = np.repeat(means[:, :, np.newaxis], 3, axis=2)
    frames[0] = frames[0] + (((frames[0] - means) * -1) * strength)
    writer.write([frames[0]])
    update()

def bilateral_filter(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' grayscales the image '''
    frames[0] = cv2.fastNlMeansDenoisingColored(frames[0], None, 10, 10, 7, 21)
    writer.write([frames[0]])
    update()

def light_grayscale_detector(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Increases and decreases the grayscale based on the mean amount of light in the frame '''
    raise ItsFuckedError
    new_frame = np.abs(np.subtract(frames[1], frames[0]))
    amount_of_light = np.sum(new_frame) / (writer.width * writer.height * 255 * 3)
    increase = (255 * amount_of_light)
    new_frame[new_frame > 64] = new_frame + increase
    writer.write([new_frame])
    update()

def overlay(frames_1: list, frames_2: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Takes two videos and overlays one ontop of the other '''
    if 'strength' in config:
        strength = config['strength']
    else:
        strength = 0.5
    new_frame = (frames_1[0] * (1 - strength)) + (frames_2[0] * strength)
    writer.write([new_frame])
    update()

effects = {
    'frame_difference': {
        'batch_size': 2,
        'progress_name': 'Frame differencing',
        'function': frame_difference
    },
    'pixel_range': {
        'batch_size': 1,
        'progress_name': 'Pixel range filter',
        'function': pixel_range
    },
    'std_deviation_filter': {
        'batch_size': 1,
        'progress_name': 'Standard deviation filter',
        'function': std_deviation_filter
    },
    'grayscale': {
        'batch_size': 1,
        'progress_name': 'Grayscaling',
        'function': grayscale
    },
    'bilateral_filter': {
        'batch_size': 1,
        'progress_name': 'Bilateral filtering',
        'function': bilateral_filter
    },
    'increasing': {
        'batch_size': 2,
        'progress_name': 'Increasing filter',
        'function': increasing
    },
    'decreasing': {
        'batch_size': 2,
        'progress_name': 'Decreasing filter',
        'function': decreasing
    },
    'edge': {
        'batch_size': 1,
        'progress_name': 'Edge detecting',
        'function': edge
    },
    'light_grayscale_detector': {
        'batch_size': 2,
        'progress_name': 'Light grayscale detection',
        'function': light_grayscale_detector
    },
    'denoise': {
        'batch_size': 1,
        'progress_name': 'Denoising',
        'function': denoise
    },
    'overlay': {
        'batch_size': 1,
        'progress_name': 'Overlaying',
        'function': overlay
    },
    'saturation': {
        'batch_size': 1,
        'progress_name': 'Increasing saturation',
        'function': saturation
    },
    'median_bound_pass': {
        'batch_size': 1,
        'progress_name': 'Median pass',
        'function': median_bound_pass
    }
}

def apply(video: VideoReader, effect_name: str, effect_config: dict):
    ''' Root method for applying an effect '''

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
            raise Exception('batch_size not set')
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
                effects[effect_name]['function'](batch_frames, effect_config, writer, pbar.update)
                batch_frames.pop(0)
                batch_frames = [*batch_frames, *video.read(1)]

        reader = open_writer_for_read(writer)
        writer.close()
        return reader

    def multi_input_batch_apply(video: VideoReader, effect_name: str, effect_config: dict):
        ''' Reads the passed video in batches, applies the effect and
            returns a VideoReader for the effected video
        '''
        # need to allow an arbitrary number of videos to be passed to the effect rather than 2
        # need a way to upscale or downscale videos that are combined together so you can combine different resolutions

        # got a syncing issue where if you apply a frame diff and then overlay the diff with the original,
        # the frames get out of sync so the diff ends up being far ahead of the original

        if 'batch_size' in effect_config:
            batch_size = effect_config['batch_size']
        elif 'batch_size' in effects[effect_name]:
            batch_size = effects[effect_name]['batch_size']
        else:
            raise Exception('batch_size not set')
        video_2 = VideoReader(
            effect_config['second_video']
        )
        pbar = log.progress_bar(min(video.frame_count, video_2.frame_count), effects[effect_name]['progress_name'], 'frames')

        writer = VideoWriter(
            get_temp_file(extension='mp4'),
            width=video.width,
            height=video.height,
            fps=video.fps,
            fourcc=video.fourcc
        )

        batch_frames_v1 = video.read(batch_size)
        batch_frames_v2 = video_2.read(batch_size)

        while video.frames_read < video.frame_count and video_2.frames_read < video_2.frame_count:
            if len(batch_frames_v1) > 0 and len(batch_frames_v2) > 0:
                effects[effect_name]['function'](batch_frames_v1, batch_frames_v2, effect_config, writer, pbar.update)
                batch_frames_v1.pop(0)
                batch_frames_v1 = [*batch_frames_v1, *video.read(1)]
                batch_frames_v2.pop(0)
                batch_frames_v2 = [*batch_frames_v2, *video_2.read(1)]

        reader = open_writer_for_read(writer)
        writer.close()
        return reader

    effect_methods = {
        'frame_difference': batch_apply,
        'pixel_range': batch_apply,
        'std_deviation_filter': batch_apply,
        'grayscale': batch_apply,
        'bilateral_filter': batch_apply,
        'increasing': batch_apply,
        'decreasing': batch_apply,
        'edge': batch_apply,
        'light_grayscale_detector': batch_apply,
        'denoise': batch_apply,
        'saturation': batch_apply,
        'overlay': multi_input_batch_apply,
        'median_bound_pass': batch_apply
    }

    return effect_methods[effect_name](video, effect_name, effect_config)