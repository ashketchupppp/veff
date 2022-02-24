
videos_to_diff = '''
 Earths roation visualised https://www.youtube.com/watch?v=1zJ9FnQXmJI
 Night sky
 Aurora borealis
 Ocean waves
 Trees swaying in the wind
 Car crash
'''

# ideally we have a recursive config
# so that if you want to combine multiple videos together you can apply effects to the other inputted videos aswell
# the whole top-level config schema would need to be replicated so an input is processed as defined
# before being used as an input for another video
CONFIG = {
    "filepath": "videos/originals/water.mp4",
    "outputFilePath": "videos/water_gabe.mp4",
    "effects": [
        {
            "effect": 'frame_difference',
            'batch_size': 2
        },
        # {
        #     'effect': 'saturation',
        #     'strength': 1.25
        # },
        {
            'effect': 'overlay',
            'second_video': 'videos/originals/water.mp4',
            'strength': 0.35
        }
    ]
}
