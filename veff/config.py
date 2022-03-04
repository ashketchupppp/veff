from os import sep
import numpy as np

from utils import smoothstep

# This is just an example configuration
# Edit this and create your own

INPUT_FILE_NAME = 'test_video.mp4'

INPUT_FILE_ROOT = 'videos/originals'
INPUT_FILE_PATH = INPUT_FILE_ROOT + sep + INPUT_FILE_NAME
OUTPUT_FILE_ROOT = f'videos/{INPUT_FILE_NAME.split(".")[0]}'
OUTPUT_FILE_NAME = INPUT_FILE_NAME
OUTPUT_FILE_EXT = 'mp4'

# ideally we have a recursive config
# so that if you want to combine multiple videos together you can apply effects to 
# the other inputted videos aswell
# the whole top-level config schema would need to be replicated so an input is processed as defined
# before being used as an input for another video

def func_multiplier(width, height, fps, frameNo):
    Y, X = np.ogrid[:height, :width]
    if not 'dist' in func_multiplier.__dict__:
        func_multiplier.dist = np.sqrt((X - width // 2)**2 + (Y - height // 2)**2)

    # frequency = 0.25 # per second
    middle_radius = (frameNo % (fps)) * (width / fps)

    # this creates a gradient
    # this is the distance relative to middle_radius rather than from the center
    relative_dist = 1 - np.abs(func_multiplier.dist - middle_radius)
    mask = np.repeat(relative_dist[:, :, np.newaxis], 3, axis=2)

    # this creates a solid ring that expands
    # inner_radius = middle_radius - 50
    # outer_radius = middle_radius + 50
    # outer_mask = func_multiplier.dist > outer_radius
    # inner_mask = func_multiplier.dist < inner_radius
    # mask = inner_mask + outer_mask
    # mask ^= True
    return mask

CONFIG = {
    'filepath': f'{INPUT_FILE_ROOT}{sep}{INPUT_FILE_NAME}',
    'effects': [
        #{
        #    'effect': 'CannyEdge',
        #    'lower_threshold': 150,
        #    'upper_threshold': 200
        #}
        # {
        #     'effect': 'Filter2D',
        #     'kernel': [
        #         [-1, -1, -1],
        #         [-1, 8, -1],
        #         [-1, -1, -1]
        #     ]
        # }# ,
        # {
        #     'effect': 'FrameDifference',
        #     'batch_size': 2
        # },
        {
            'effect': 'FunctionMultiplier',
            'func_multiplier': func_multiplier
        }
    ]
}

CONFIG['outputFilePath'] = f'{OUTPUT_FILE_ROOT}{sep}{OUTPUT_FILE_NAME.split()[0]}'
for effect in CONFIG['effects']:
    CONFIG['outputFilePath'] += f'_{effect["effect"]}'

CONFIG['outputFilePath'] += '.' + OUTPUT_FILE_EXT