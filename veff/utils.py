''' Utilities '''

import tempfile
import platform

def get_temp_file():
    ''' Opens and returns a temporary file which will be deleted when the file is closed. '''
    return tempfile.TemporaryFile()

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