''' Video effects '''

import numpy as np

import log

def frame_difference(frames, config):
    ''' Applies a frame differencing effect to the passed frames '''
    pbar = log.progress_bar(len(frames), 'Applying frame differencing', 'frames')
    previous = frames[0]
    newFrames = []
    for frame in frames[1:-1]: # final frame will be of type None
        newFrames.append(np.uint8(np.absolute(np.subtract(np.int16(previous), np.int16(frame)))))
        # frame = np.uint8(np.bitwise_and(previous, frame))
        previous = frame
        pbar.update()
    return newFrames

EFFECTS = {
    'frame_difference': frame_difference
}
