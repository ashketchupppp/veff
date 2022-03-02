''' Video effects '''

from scipy import signal
import numpy as np
import cv2
from abc import ABC, abstractclassmethod
from schema import Schema, And, Optional
from functools import partial

from utils import number_between
from video import VideoWriter
from utils import get_temp_file
from video import VideoReader, VideoWriter, open_writer_for_read
import log

# Could do some edge detection and then do something with the pixels at the edges???

class Effect(ABC):
    @abstractclassmethod
    def run(cls, video: VideoReader, effect_config: dict):
        ''' Root run method '''
        raise NotImplementedError

class SingleInputEffect(Effect):
    @classmethod
    def run(cls, video: VideoReader, effect_config: dict):
        ''' Reads the passed video in batches, applies the effect and
            returns a VideoReader for the effected video
        '''
        cls.validate_schema(effect_config)
        
        pbar = log.progress_bar(video.frame_count, cls.progress_name(), 'frames')

        if 'batch_size' in effect_config:
            batch_size = effect_config['batch_size']
        else:
            batch_size = cls.batch_size()

        # remove thsese so they don't get passed to apply
        if 'batch_size' in effect_config:
            del effect_config['batch_size']
        del effect_config['effect']


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
                frame = cls.apply(batch_frames, **effect_config)
                writer.write(frame)
                batch_frames.pop(0)
                batch_frames = [*batch_frames, *video.read(1)]
                pbar.update()

        reader = open_writer_for_read(writer)
        writer.close()
        return reader

    @classmethod
    def validate_schema(cls, config: dict):
        cls.opt_schema().validate(config)

    @classmethod
    def apply(cls):
        ''' Inner method used to apply the effect, called by run '''
        raise NotImplementedError

    @classmethod
    def batch_size(cls):
        ''' Number of frames needed for the effect to run '''
        raise NotImplementedError

    @classmethod
    def progress_name(cls):
        ''' The name used by the progress bar to tell the user what effect is running '''
        raise NotImplementedError

    @classmethod
    def opt_schema(cls):
        ''' Configuration options schema for arguments loaded from config.py '''
        raise NotImplementedError

class FrameDifference(SingleInputEffect):
    @classmethod
    def apply(cls, frames: list):
        ''' Applies a frame differencing effect to the passed frames '''
        assert len(frames) > 1
        return np.absolute(np.subtract(np.int16(frames[0]), np.int16(frames[-1])))

    @classmethod
    def opt_schema(cls):
        ''' Frame differencing options '''
        return Schema({
            'effect': cls.__name__,
            'batch_size': Optional(And(int, partial(number_between, lower_bound=1.1, upper_bound=999)))
        })

    @classmethod
    def batch_size(cls):
        ''' Number of frames needed for the effect to run '''
        return 2

    @classmethod
    def progress_name(cls):
        ''' The name used by the progress bar to tell the user what effect is running '''
        return 'Frame differencing'

class IncreasingFrameDifference(SingleInputEffect):
    @classmethod
    def apply(cls, frames: list):
        ''' Applies a frame differencing effect to the passed frames '''
        assert len(frames) > 1
        new_frame = np.subtract(frames[1], frames[0])
        new_frame[new_frame > 0] = 0
        new_frame = np.absolute(new_frame)
        return new_frame

    @classmethod
    def opt_schema(cls):
        ''' Increasing frame differencing options '''
        return Schema({
            'effect': cls.__name__,
            'batch_size': Optional(And(int, partial(number_between, lower_bound=1.1, upper_bound=999)))
        })

    @classmethod
    def batch_size(cls):
        ''' Number of frames needed for the effect to run '''
        return 2

    @classmethod
    def progress_name(cls):
        ''' The name used by the progress bar to tell the user what effect is running '''
        return 'Increasing frame differencing'

class DecreasingFrameDifference(SingleInputEffect):
    @classmethod
    def apply(cls, frames: list):
        ''' Applies a frame differencing effect to the passed frames '''
        assert len(frames) > 1
        new_frame = np.subtract(frames[1], frames[0])
        new_frame[new_frame < 0] = 0
        return new_frame

    @classmethod
    def opt_schema(cls):
        ''' Decreasing frame differencing options '''
        return Schema({
            'effect': cls.__name__,
            'batch_size': Optional(And(int, partial(number_between, lower_bound=1.1, upper_bound=999)))
        })

    @classmethod
    def batch_size(cls):
        ''' Number of frames needed for the effect to run '''
        return 2

    @classmethod
    def progress_name(cls):
        ''' The name used by the progress bar to tell the user what effect is running '''
        return 'Decreasing frame differencing'

class PixelRange(SingleInputEffect):
    @classmethod
    def apply(cls, frames: list, lower_bound=0, upper_bound=255):
        ''' Applies a frame differencing effect to the passed frames '''
        assert len(frames) == 1
        mean = np.mean(frames[0], axis=(2))
        grayscale = np.repeat(mean[:, :, np.newaxis], 3, axis=2)
        if lower_bound > 0:
            frames[0][lower_bound > grayscale] = 0
        if upper_bound < 255:
            frames[0][upper_bound < grayscale] = 0
        return frames[0]

    @classmethod
    def opt_schema(cls):
        ''' Decreasing frame differencing options '''
        return Schema({
            'effect': cls.__name__,
            'upper_bound': Optional(int),
            'lower_bound': Optional(int)
        })

    @classmethod
    def batch_size(cls):
        ''' Number of frames needed for the effect to run '''
        return 1

    @classmethod
    def progress_name(cls):
        ''' The name used by the progress bar to tell the user what effect is running '''
        return 'Pixel range filtering'

class Grayscale(SingleInputEffect):
    @classmethod
    def apply(cls, frames: list, strength=1):
        ''' Makes the image grayscale according to the configured strength '''
        assert len(frames) == 1
        means = np.mean(frames[0], axis=(2))
        means = np.repeat(means[:, :, np.newaxis], 3, axis=2)
        frames[0] = frames[0] + (((frames[0] - means) * -1) * strength)
        return frames[0]

    @classmethod
    def opt_schema(cls):
        ''' Decreasing frame differencing options '''
        return Schema({
            'effect': cls.__name__,
            'strength': Optional(int)
        })

    @classmethod
    def batch_size(cls):
        ''' Number of frames needed for the effect to run '''
        return 1

    @classmethod
    def progress_name(cls):
        ''' The name used by the progress bar to tell the user what effect is running '''
        return 'Grayscaling'

class Filter2D(SingleInputEffect):
    @classmethod
    def apply(cls, frames: list, kernel: list):
        ''' OpenCV2 Filter 2D '''
        assert len(frames) == 1
        frames[0] = cv2.filter2D(frames[0], -1, np.array(kernel))
        return frames[0]

    @classmethod
    def opt_schema(cls):
        ''' Filter2D options '''
        return Schema({
            'effect': cls.__name__,
            'kernel': list
        })

    @classmethod
    def batch_size(cls):
        ''' Number of frames needed for the effect to run '''
        return 1

    @classmethod
    def progress_name(cls):
        ''' The name used by the progress bar to tell the user what effect is running '''
        return 'Applying Filter2D'

class CannyEdge(SingleInputEffect):
    @classmethod
    def apply(cls, frames: list, lower_threshold: int, upper_threshold: int, aperture_size = 5, l2gradient = False):
        ''' Canny edge detector '''
        assert len(frames) == 1
        frames[0] = cv2.Canny(
            frames[0],
            lower_threshold,
            upper_threshold,
            apertureSize=aperture_size, 
            L2gradient=l2gradient
        )
        frames[0] = np.repeat(frames[0][:, :, np.newaxis], 3, axis=2)
        return frames[0]

    @classmethod
    def opt_schema(cls):
        ''' Canny edge detector '''
        return Schema({
            'effect': cls.__name__,
            'lower_threshold': int,
            'upper_threshold': int,
            Optional('aperture_size'): Optional(int),
            Optional('l2gradient'): Optional(bool)
        })

    @classmethod
    def batch_size(cls):
        ''' Number of frames needed for the effect to run '''
        return 1

    @classmethod
    def progress_name(cls):
        ''' The name used by the progress bar to tell the user what effect is running '''
        return 'Edge detecting'

class MultiInputEffect(Effect):
    @classmethod
    def run(cls, video: VideoReader, effect_config: dict):
        ''' Reads the passed video in batches, applies the effect and
            returns a VideoReader for the effected video
        '''
        cls.validate_schema(effect_config)
        
        pbar = log.progress_bar(video.frame_count, cls.progress_name(), 'frames')

        if 'batch_size' in effect_config:
            batch_size = effect_config['batch_size']
        else:
            batch_size = cls.batch_size()
        del effect_config['effect']

        videos = [VideoReader(path) for path in effect_config['videos']]
        del effect_config['videos']

        pbar = log.progress_bar(min(*[len(video) for video in videos]), cls.progress_name(), 'frames')

        writer = VideoWriter(
            get_temp_file(extension='mp4'),
            width=video.width,
            height=video.height,
            fps=video.fps,
            fourcc=video.fourcc
        )

        batch_frames = [video.read(batch_size) for video in videos]

        while all([video.frames_read < video.frame_count for video in videos]):
            if all([len(batch) for batch in batch_frames]):
                new_frame = cls.apply(batch_frames, **effect_config)
                writer.write(new_frame)
                for i in range(len(batch_frames)):
                    batch_frames[i].pop(0)
                    batch_frames[i] = [*batch_frames[i], *videos[i].read(1)]
                pbar.update()

        reader = open_writer_for_read(writer)
        writer.close()
        return reader
    
    @classmethod
    def validate_schema(cls, config: dict):
        cls.opt_schema().validate(config)

    @classmethod
    def apply(cls, frames: list, *args, **kwargs):
        ''' Inner method used to apply the effect, called by run '''
        raise NotImplementedError

    @classmethod
    def batch_size(cls):
        ''' Number of frames needed for the effect to run '''
        raise NotImplementedError

    @classmethod
    def progress_name(cls):
        ''' The name used by the progress bar to tell the user what effect is running '''
        raise NotImplementedError

    @classmethod
    def opt_schema(cls):
        ''' Configuration options schema for arguments loaded from config.py '''
        raise NotImplementedError

class Overlay(MultiInputEffect):
    @classmethod
    def apply(cls, batches: list):
        strength = 1 / len(batches)
        def overlay(current_frame, i = 0):
            if i < len(batches):
                return overlay(current_frame * strength + batches[i][0] * (1 - strength), i + 1)
            return current_frame
        return overlay(batches[0][0])

    @classmethod
    def batch_size(cls):
        ''' Number of frames needed for the effect to run '''
        return 1

    @classmethod
    def progress_name(cls):
        ''' The name used by the progress bar to tell the user what effect is running '''
        return 'Overlaying'

    @classmethod
    def opt_schema(cls):
        ''' Configuration options schema for arguments loaded from config.py '''

    @classmethod
    def opt_schema(cls):
        ''' Decreasing frame differencing options '''
        return Schema({
            'effect': cls.__name__,
            'videos': And(list, lambda l: all([isinstance(path, str) for path in l]))
        })

effects = {
    **dict([(cls.__name__, cls) for cls in SingleInputEffect.__subclasses__()]),
    **dict([(cls.__name__, cls) for cls in MultiInputEffect.__subclasses__()])
}

# maybe you can get these effects below to be good
class ItsFuckedError(Exception):
    pass # :) just commit your broken code its fiiiine

def std_deviation_filter(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Removes all pixels above or below the passed number of standard deviations (of pixel values) '''
    raise ItsFuckedError # this works but its crap
    std_deviation = np.std(frames[0])
    mean = np.mean(frames[0])
    percentile = 0.01

    bound = mean + (std_deviation * percentile)
    frames[0][(255 // 2) - bound > frames[0]] = 0
    frames[0][(255 // 2) + bound < frames[0]] = 0
    writer.write([frames[0]])
    update()

def bilateral_filter(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' grayscales the image '''
    raise ItsFuckedError # this is obscenely slow
    frames[0] = cv2.fastNlMeansDenoisingColored(frames[0], None, 10, 10, 7, 21)
    writer.write([frames[0]])
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

def edge(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Applies an edge detection algorithm to the video, not working atm '''
    raise ItsFuckedError
    writer.write([cv2.Canny(frames[0], 100, 200)])
    update()

def saturation(frames: list, config: dict, writer: VideoWriter, update=lambda x: None, *args, **kwargs):
    ''' Increases the saturation of the image '''
    raise ItsFuckedError
    # often leads to pixels being maxed out, leading to massive patches of red, green or blue
    # need a way to prevent this, maybe dividing the strength by a larger value or having it be a percentage
    strength = config['strength']
    writer.write([frames[0] * strength])
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
