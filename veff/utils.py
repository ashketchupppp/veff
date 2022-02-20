''' Utilities '''

import tempfile
import platform

def get_temp_file():
    ''' Opens and returns a temporary file which will be deleted when the file is closed. '''
    return tempfile.TemporaryFile()

def is_linux():
  ''' Returns True if running on Linux '''
  return 'Linux' in platform.platform()