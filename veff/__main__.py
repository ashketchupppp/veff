''' Python video processing pipeline and library.
'''

import os
import sys
import shutil
import uuid
from pathlib import Path, PurePath

import cv2

from utils import temp_file_cleanup, ffmpeg
from video import VideoReader
from config_schema import validate_config
from effects import apply
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

if os.path.exists(OUTPUT_PATH):
    os.remove(OUTPUT_PATH)
    # OLD_OUTPUT_PATH = OUTPUT_PATH
    # path_split = [*PurePath(OLD_OUTPUT_PATH).parts]
    # path_split[-1] = str(uuid.uuid4())[0:4] + '-' + path_split[-1]
    # OUTPUT_PATH = str(os.path.sep.join(path_split))
    # log.info(f'{OLD_OUTPUT_PATH} already exists! Using {OUTPUT_PATH} instead')
    # make this a toggle-able option in the config

video = VideoReader(INPUT_PATH)
try:
    for effectConfig in CONFIGURED_EFFECTS:
        currentEffect = effectConfig['effect']
        video = apply(video, currentEffect, effectConfig)

except Exception as err:
    log.err(f'Unexpected error occurred: {err}')
finally:
    video.close()
    # ffmpeg(video.path, OUTPUT_PATH)
    shutil.copy(video.path, OUTPUT_PATH)
    cv2.destroyAllWindows()
    temp_file_cleanup()
