''' Utilities '''

from os import path
import platform
import numpy as np
import uuid
import os
import shutil

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

def is_path(p: str):
    ''' Returns true if p is a valid path '''
    return path.exists(p)

def is_file(p: str):
  ''' Returns True if p is an existing file '''
  return path.isfile(p)

def is_filetype(p: str, _type: str):
    ''' Returns true if p is a valid path, is a file and has the passed filetype '''
    return p.endswith(f'.{_type}')

def number_between(num, lower_bound, upper_bound):
    ''' Returns true if num is between lower_bound and upper_bound '''
    return lower_bound <= num <= upper_bound
