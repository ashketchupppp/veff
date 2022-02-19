import cv2
import os
from moviepy.editor import *
import subprocess
import audio

from utils import getTempFile

class Video:
    class WrongOpenType(Exception):
        pass
    class NotOpen(Exception):
        pass

    def __init__(self, path):
        self._path = path
        self._audio = None
        self.opened_for_read = False
        self.opened_for_write = False
        self._reader = None
        self._writer = None
        self.written_frame_count = 0
        self.data = []

    def openForRead(self):
        if os.path.exists(self.path):
            self._reader = cv2.VideoCapture(self.path)
            self.opened_for_read = True
        else:
            raise FileNotFoundError

    def openForWrite(self, fourcc, fps, width, height):
        if not os.path.exists(os.path.dirname(self.path)):
            if len(os.path.dirname(self.path)) > 0:
                os.makedirs(os.path.dirname(self.path))
        self._writer = cv2.VideoWriter(
            self.path,
            fourcc,
            fps,
            (width, height)
        )

    def close(self):
        if self._reader != None:
            self._reader.release()
            self._reader = None
            self.opened_for_read = False

        if self._writer != None:
            self._writer.release()
            tempFile = getTempFile()
            if self.audio:
                subprocess.run([
                    "ffmpeg", "-y", 
                    "-i", self.path, "-i", self.audio.path, 
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-shortest", tempFile
                ], capture_output=True)
                os.remove(self.path)
                subprocess.run([
                    "ffmpeg", "-y", 
                    "-i", tempFile, "-i", self.audio.path, 
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-shortest", self.path
                ], capture_output=True)
            self._writer = None
            self.opened_for_write = False
            self.written_frame_count = 0

    def readFrame(self):
        if self.opened_for_write:
            raise Video.WrongOpenType
        return self._reader.read()

    def writeFrame(self, frame):
        if self.opened_for_read:
            raise Video.WrongOpenType
        res = self._writer.write(frame)
        self.written_frame_count += 1
        return res

    def read(self):
        success = True
        if not self.opened:
            self.openForRead()
        while self.opened and success:
            success, frame = self.readFrame()
            self.data.append(frame)
        self.close()

    @property
    def audio(self):
        return self._audio

    @audio.setter
    def audio(self, path):
        self._audio = audio.Audio(path)

    @property
    def path(self):
        return self._path

    @property
    def fps(self):
        if self.opened_for_read:
            return int(self._reader.get(cv2.CAP_PROP_FPS))
        elif self.opened_for_write:
            return int(self._writer.get(cv2.CAP_PROP_FPS))

    @property
    def fourcc(self):
        if self.opened_for_read:
            return int(self._reader.get(cv2.CAP_PROP_FOURCC))
        elif self.opened_for_write:
            return int(self._writer.get(cv2.CAP_PROP_FOURCC))

    @property
    def width(self):
        if self.opened_for_read:
            return int(self._reader.get(cv2.CAP_PROP_FRAME_WIDTH))
        elif self.opened_for_write:
            return int(self._writer.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self):
        if self.opened_for_read:
            return int(self._reader.get(cv2.CAP_PROP_FRAME_HEIGHT))
        elif self.opened_for_write:
            return int(self._writer.get(cv2.CAP_PROP_FRAME_HEIGHT))

    @property
    def framesWritten(self):
        return self.written_frame_count

    @property
    def frameCount(self):
        if self.opened_for_read:
            return int(self._reader.get(cv2.CAP_PROP_FRAME_COUNT))

    @property
    def opened(self):
        return self.opened_for_read or self.opened_for_write
