''' Config file schema '''

from functools import partial
from schema import Schema, And, Or

from utils import (
    is_file,
    is_filetype
)
from effects import (
    SingleInputEffect,
    MultiInputEffect
)

configSchema = Schema({
    'filepath': And(str, partial(is_filetype, _type='mp4'), is_file, error='Filepath must be a valid mp4 file'),
    'outputFilePath': And(str),
    'effects': [Or(
        *[cls.opt_schema() for cls in SingleInputEffect.__subclasses__()],
        *[cls.opt_schema() for cls in MultiInputEffect.__subclasses__()]
    )]
})

def validate_config(config: dict):
    ''' Validates the passed config object against the configSchema '''
    return configSchema.validate(config)
