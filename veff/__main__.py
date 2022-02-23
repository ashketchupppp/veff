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

ARGS = sys.argv[1:]
DEFAULT_CONFIG_PATH = 'veff.config.json'
PASSED_CONFIG_PATH = None
CONFIG_PATH = None
CONFIG = None

if len(ARGS) > 0:
    PASSED_CONFIG_PATH = ARGS[1]
    CONFIG_PATH = PASSED_CONFIG_PATH
else:
    CONFIG_PATH = DEFAULT_CONFIG_PATH

try:
    with open(CONFIG_PATH, 'r', encoding='utf8') as fh:
        contents = fh.read()
        CONFIG = json.loads(contents)
except FileNotFoundError:
    log.err(f'{CONFIG_PATH} not found')
except json.JSONDecodeError as err:
    log.err(f'Failed to decode {CONFIG_PATH} at {err.lineno},{err.colno}')

if not CONFIG:
    sys.exit(1)

try:
    config_valid = validate_config(CONFIG)
except BaseException as err:
    log.err(f'{CONFIG_PATH} invalid: {err}')

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
finally:
    temp_file_cleanup()