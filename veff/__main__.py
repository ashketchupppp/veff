''' Python video processing pipeline and library.
'''

import os
import sys
import shutil

import cv2

from utils import temp_file_cleanup
from video import VideoReader
from config_schema import validate_config
import effects
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

OUTPUT_ROOT_DIR = os.path.dirname(OUTPUT_PATH)

if not os.path.exists(OUTPUT_ROOT_DIR):
    os.makedirs(OUTPUT_ROOT_DIR)

if os.path.exists(OUTPUT_PATH):
    os.remove(OUTPUT_PATH)

video = VideoReader(INPUT_PATH)
try:
    for effectConfig in CONFIGURED_EFFECTS:
        currentEffect = effectConfig['effect']
        video = effects.effects[currentEffect].run(video, effectConfig)

except Exception as err:
    log.err(f'Unexpected error occurred: {err}')
finally:
    video.close()
    # ffmpeg(video.path, OUTPUT_PATH)
    shutil.copy(video.path, OUTPUT_PATH)
    cv2.destroyAllWindows()
    temp_file_cleanup()
