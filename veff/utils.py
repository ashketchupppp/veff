''' Utilities '''
import os
import uuid
import shutil
import subprocess

import platform
import numpy as np

temp_location = '.' + os.path.sep + 'temp'

def get_temp_file(extension=''):
    ''' Opens and returns a temporary file which will be deleted when the file is closed. '''
    if not os.path.exists(temp_location):
        os.mkdir(temp_location)
    return os.path.join(temp_location, str(uuid.uuid4()) + '.' + extension)

def temp_file_cleanup():
    ''' Removes all temporary directories and files at temp_location '''
    if os.path.exists(temp_location):
        shutil.rmtree(temp_location)

def needs_temp_file(func, *args, **kwargs):
    ''' Decorates function func by getting it a temporary file and passing it to func '''
    def wrapper():
        fh = get_temp_file()
        return func(*args, **kwargs, temp_file=fh)
    return wrapper

def is_linux():
  ''' Returns True if running on Linux '''
  return 'Linux' in platform.platform()

def interleave(arr1, arr2):
    ''' Inserts the values from arr2 into arr1 such that every other value will be from arr2
        Examplele: interleave([0, 2, 4], [1, 3, 5]) = [0, 1, 2, 3, 4, 5]
    '''
    i = 1
    for item in arr2:
        arr1.insert(item, i)
        i += 2
    return arr1

def diff_arrays(arr1, arr2):
    ''' Returns the difference between two numpy arrays '''
    return np.absolute(np.subtract(np.int16(arr1), np.int16(arr2)))

class LimitedList:
    def __init__(self, size_limit):
        self.values = []
        self.size_limit = size_limit

    def append(self, value):
        if len(self.values) == self.size_limit:
            self.values.pop(0)
        self.values.append(value)

    def most_recent(self):
        if len(self.values) > 0:
            return self.values[-1]

    def set_size_limit(self, new_limit: int):
        self.size_limit = new_limit

    def __iter__(self):
        for value in self.values:
            yield value

def ffmpeg(path_in, path_out):
    subprocess.run([
        'ffmpeg', '-i', path_in, path_out
    ], cwd=os.getcwd())
