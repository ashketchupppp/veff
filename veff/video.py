import cv2
import os
from moviepy.editor import *
import subprocess
import audio
import numpy as np
import io

from utils import LimitedList
import log

class VideoFileHandler:
    def __init__(self):
        self.handle = None
        self.open = True

    def close(self):
        ''' Closes the file '''
        if bool(self.handle):
            self.handle.release()
        self.handle = None
        self.open = False

    @property
    def fps(self):
        return int(self.handle.get(cv2.CAP_PROP_FPS))

    @property
    def fourcc(self):
        return int(self.handle.get(cv2.CAP_PROP_FOURCC))

    @property
    def width(self):
        return int(self.handle.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self):
        return int(self.handle.get(cv2.CAP_PROP_FRAME_HEIGHT))

class VideoReader(VideoFileHandler):
    def __init__(self, path, num_previous_frames=2):
        super().__init__()
        self.path = path
        self.frames_read = 0
        if os.path.exists(path):
            self.handle = cv2.VideoCapture(self.path)
        else:
            raise FileNotFoundError(path)

    def set_previous_length(self, length: int):
        self.previous.set_size_limit(length)

    def read(self, num_frames_to_read=1):
        ''' Reads the passed number of frames and returns them in a list '''
        if not self.open:
            raise ValueError('I/O operation on closed file.')
        frames = []
        i = 0
        while i < num_frames_to_read:
            success, frame = self.handle.read()
            if success:
                self.frames_read += 1
                frames.append(frame)
                i += 1
            else:
                self.seek(self.curr_frame() - 1)
        return frames

    @property
    def frame_count(self):
        return int(self.handle.get(cv2.CAP_PROP_FRAME_COUNT))

    def curr_frame(self):
        return self.handle.get(cv2.CAP_PROP_POS_FRAMES)

    def seek(self, frame_num: int):
        self.handle.set(cv2.CAP_PROP_POS_FRAMES, frame_num)

    def __next__(self):
        if self.open:
            yield self.read()
        else:
            raise StopIteration

    def __iter__(self):
        if self.open:
            yield self.read()
        else:
            raise StopIteration

    def __len__(self):
        return self.frame_count

class VideoWriter(VideoFileHandler):
    def __init__(self, path, width=1280, height=720, fps=30, fourcc=cv2.VideoWriter_fourcc(*'mp4v')):
        super().__init__()
        self.path = path
        if not os.path.exists(path):
            self.handle = cv2.VideoWriter(
                self.path,
                fourcc,
                fps,
                (width, height)
            )
            self._width = width
            self._height = height
            self._fps = fps
            self._fourcc = fourcc
        else:
            self.close()
            raise FileExistsError(path)

    def write(self, frames):
        ''' Writes the passed frames '''
        if not isinstance(frames, list):
            frames = [frames]
        if len(frames) == 0:
            raise ValueError('Cannot write 0 frames to file')
        for i in range(len(frames)):
            self.handle.write(np.clip(np.uint8(frames[i]), 0, 255))
        return frames

    @property
    def fps(self):
        return self._fps

    @property
    def fourcc(self):
        return self._fourcc

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

def open_writer_for_read(writer: VideoWriter):
    path = writer.path
    writer.close()
    return VideoReader(path)

def open_reader_for_write(reader: VideoReader):
    fourcc = reader.fourcc
    width = reader.width
    height = reader.height
    fps = reader.fps
    path = reader.path
    reader.close()
    return VideoWriter(path, width, height, fps, fourcc)