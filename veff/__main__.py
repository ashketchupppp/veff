''' Python video processing pipeline and library.
'''

import json
import sys
import shutil

import cv2
import numpy as np

from utils import temp_file_cleanup
from video import VideoReader
from config_schema import validate_config
from effects import batch_apply
import log

from config import CONFIG

ARGS = sys.argv[1:]

try:
    config_valid = validate_config(CONFIG)
except BaseException as err:
    log.err(f'CONFIG invalid: {err}')

INPUT_PATH = CONFIG['filepath']
OUTPUT_PATH = CONFIG['outputFilePath']
CONFIGURED_EFFECTS = CONFIG['effects']

video = VideoReader(INPUT_PATH)
try:
    for effectConfig in CONFIGURED_EFFECTS:
        currentEffect = effectConfig['effect']
        video = batch_apply(video, currentEffect, effectConfig)

    video.close()
    cv2.destroyAllWindows()
    shutil.copy(video.path, OUTPUT_PATH)
except Exception as err:
    log.err(f'Unexpected error occurred: {err}')
finally:
    temp_file_cleanup()