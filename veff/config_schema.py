''' Config file schema '''

from os import path
from functools import partial
from schema import Schema, And

from effects import EFFECTS

def is_path(p: str):
    ''' Returns true if p is a valid path '''
    return path.exists(p)

def is_filetype(p: str, _type: str):
    ''' Returns true if p is a valid path, is a file and has the passed filetype '''
    return is_path(p) and path.isfile(p) and p.endswith(f'.{_type}')

def is_effect(effect_name: str):
    ''' Returns true if effect_name is a valid video effect '''
    return effect_name in EFFECTS

configSchema = Schema({
    'config': And(str, is_path),
    'file': And(str, partial(is_filetype, _type='mp4')),
    'effects': [{
        'effect': And(str, is_effect)
    }]
})

def validate_config(config: dict):
    ''' Validates the passed config object against the configSchema '''
    return configSchema.validate(config)
