''' Utilities '''

import tempfile

def getTempFile():
    ''' Opens and returns a temporary file which will be deleted when the file is closed. '''
    return tempfile.TemporaryFile()
