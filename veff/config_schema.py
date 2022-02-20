''' Config file schema '''

from os import path
from functools import partial
from schema import Schema, And

from effects import is_effect

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
    'config': And(str, is_path),
    'filepath': And(str, partial(is_filetype, _type='mp4'), is_file),
    'outputFilePath': And(str, partial(is_filetype, _type='mp4')),
    'effects': [{
        'effect': And(str, is_effect)
    }],
    'maxBatchSize': And(int, lambda x: x > 0)
})

def validate_config(config: dict):
    ''' Validates the passed config object against the configSchema '''
    return configSchema.validate(config)
