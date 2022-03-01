''' Config file schema '''

from functools import partial
from schema import Schema, And, Or

from utils import (
    is_file,
    is_filetype
)
from effects import (
    Overlay,
    FrameDifference,
    Grayscale,
    IncreasingFrameDifference,
    DecreasingFrameDifference,
    PixelRange
)

configSchema = Schema({
    'filepath': And(str, partial(is_filetype, _type='mp4'), is_file),
    'outputFilePath': And(str),
    'effects': [Or(
        FrameDifference.opt_schema(),
        Grayscale.opt_schema(),
        IncreasingFrameDifference.opt_schema(),
        DecreasingFrameDifference.opt_schema(),
        PixelRange.opt_schema(),
        Overlay.opt_schema()
    )]
})

def validate_config(config: dict):
    ''' Validates the passed config object against the configSchema '''
    return configSchema.validate(config)
