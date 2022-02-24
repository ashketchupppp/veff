''' Config file schema '''

from os import path
from functools import partial
from schema import Schema, And, Or

from effects import (
    pixel_range,
    frame_difference,
    std_deviation_filter,
    grayscale,
    bilateral_filter,
    increasing,
    decreasing,
    light_saturation_detector,
    denoise,
    edge
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
        { 'effect': frame_difference.__name__, 'batch_size': int, },
        { 'effect': grayscale.__name__ },
        { 'effect': bilateral_filter.__name__ },
        { 'effect': increasing.__name__ },
        { 'effect': decreasing.__name__ },
        { 'effect': light_saturation_detector.__name__ },
        { 'effect': denoise.__name__ },
        { 'effect': edge.__name__ }
    )]
})

def validate_config(config: dict):
    ''' Validates the passed config object against the configSchema '''
    return configSchema.validate(config)
