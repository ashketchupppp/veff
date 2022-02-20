''' Python video processing pipeline and library.
'''

import json
import sys

import cv2

import utils
import log
import video
from config_schema import validate_config
from effects import EFFECTS

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

inputVideo = video.Video(INPUT_PATH)
inputVideo.openForRead()
inputVideo.read()
frames = inputVideo.data

for effectConfig in CONFIGURED_EFFECTS:
    currentEffect = effectConfig['effect']
    frames = EFFECTS[currentEffect](frames, effectConfig)

# TOOD: Support more filetypes than mp4
if utils.is_linux():
  fourcc = cv2.VideoWriter_fourcc(*'mp4v')
else:
  fourcc = inputVideo.fourcc

outputVideo = video.Video(OUTPUT_PATH)
outputVideo.openForWrite(fourcc, inputVideo.fps, inputVideo.width, inputVideo.height)
pbar = log.progress_bar(len(frames), f'Writing to {OUTPUT_PATH}', 'frames')
for frame in frames:
    outputVideo.writeFrame(frame)
    pbar.update()

outputVideo.close()