import pydub
import numpy as np
import os

class Audio:
    def __init__(self, path):
        if not os.path.isfile(path):
            raise FileNotFoundError
        elif "mp3" not in path:
            raise TypeError(path + " is not a supported/valid audio file type")

        self.path = path
        self.audio = np.array([])
        self.pitch = np.array([])
        self.fps = 0
        self.frame_count = 0
        self.segment = None

    def read(self, normalized=False):
        self.segment = pydub.AudioSegment.from_mp3(self.path)
        self.audio = np.array(self.segment.get_array_of_samples())
        if self.segment.channels == 2:
            self.audio = self.audio.reshape((-1, 2))
        if normalized:
            self.audio = np.float32(self.audio) / 2**15
        self.pitch = np.add.accumulate(self.audio)
        self.max = self.segment.max
        self.fps = self.segment.frame_rate

    def pitchAtFrame(self, frameNo, videofps):
        audioSampleToUse = int((frameNo * (self.fps / videofps)))
        if audioSampleToUse <= len(self.audio):
            audioSampleToUse = int((frameNo * (self.fps / videofps)))
            return self.audio[audioSampleToUse], True
        return np.array([]), False