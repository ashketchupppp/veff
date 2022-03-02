from os import sep

# This is just an example configuration
# Edit this and create your own

INPUT_FILE_NAME = 'living_beings.mp4'

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

CONFIG = {
    'filepath': f'{INPUT_FILE_ROOT}{sep}{INPUT_FILE_NAME}',
    'effects': [
        {
            'effect': 'CannyEdge',
            'lower_threshold': 150,
            'upper_threshold': 200
        }
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
        # }
    ]
}

CONFIG['outputFilePath'] = f'{OUTPUT_FILE_ROOT}{sep}{OUTPUT_FILE_NAME.split()[0]}'
for effect in CONFIG['effects']:
    CONFIG['outputFilePath'] += f'_{effect["effect"]}'

CONFIG['outputFilePath'] += '.' + OUTPUT_FILE_EXT