''' Config file schema '''

from os import path
from functools import partial
from schema import Schema, And, Or, Optional

from utils import (
    is_file,
    is_filetype,
    number_between
)
from effects import (
    pixel_range,
    frame_difference,
    std_deviation_filter,
    grayscale,
    bilateral_filter,
    increasing,
    decreasing,
    light_grayscale_detector,
    denoise,
    edge,
    overlay,
    saturation,
    median_bound_pass,
    FrameDifference
)

configSchema = Schema({
    'filepath': And(str, partial(is_filetype, _type='mp4'), is_file),
    'outputFilePath': And(str),
    'effects': [Or(
        {
            'effect': pixel_range.__name__,
            'upper_bound': int,
            'lower_bound': int
        },
        {
            'effect': std_deviation_filter.__name__,
            'percentile': float
        },
        FrameDifference.opt_schema(),
        {
            'effect': grayscale.__name__,
            'strength': And(float, partial(number_between, lower_bound=0, upper_bound=1))
        },
        {
            'effect': saturation.__name__,
            'strength': And(float, partial(number_between, lower_bound=0, upper_bound=999))
        },
        { 'effect': bilateral_filter.__name__ },
        { 'effect': increasing.__name__ },
        { 'effect': decreasing.__name__ },
        { 'effect': light_grayscale_detector.__name__ },
        { 'effect': denoise.__name__ },
        { 'effect': edge.__name__ },
        {
            'effect': overlay.__name__,
            'second_video': And(str, partial(is_filetype, _type='mp4'), is_file),
            'strength': float
        },
        {
            'effect': median_bound_pass.__name__,
            'multiplier': Optional(float)
        }
    )]
})

def validate_config(config: dict):
    ''' Validates the passed config object against the configSchema '''
    return configSchema.validate(config)
