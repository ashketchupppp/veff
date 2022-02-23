''' Config file schema '''

from os import path
from functools import partial
from schema import Schema, And, Or

from effects import is_effect, pixel_range, frame_difference

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
    'outputFilePath': And(str, partial(is_filetype, _type='mp4')),
    'effects': [Or(
        {
            'effect': pixel_range.__name__,
            'upper_bound': int,
            'lower_bound': int
        },
        {
            'effect': frame_difference.__name__
        }
    )]
})

def validate_config(config: dict):
    ''' Validates the passed config object against the configSchema '''
    return configSchema.validate(config)
