''' Config file schema '''

from os import path
from functools import partial
from schema import Schema, And, Or, Optional

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
    median_bound_pass
)

def is_path(p: str):
    ''' Returns true if p is a valid path '''
    return path.exists(p)

def is_file(p: str):
  ''' Returns True if p is an existing file '''
  return path.isfile(p)

def is_filetype(p: str, _type: str):
    ''' Returns true if p is a valid path, is a file and has the passed filetype '''
    return p.endswith(f'.{_type}')

def number_between(num, lower_bound, upper_bound):
    ''' Returns true if num is between lower_bound and upper_bound '''
    return lower_bound <= num <= upper_bound

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
        {
            'effect': frame_difference.__name__,
            'batch_size': And(int, partial(number_between, lower_bound=1.1, upper_bound=999)),
        },
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
