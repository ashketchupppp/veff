''' Logging utils '''

import datetime
from colorama import Fore, Back, Style, init

init()

# TODO: Fix colors

def info(msg):
    ''' Logs an info message '''
    print(Fore.WHITE + Back.BLUE + 'INFO' + Style.RESET_ALL + f' {datetime.datetime.now()}: {msg}')

def err(msg):
    ''' Logs an error message '''
    print(Fore.BLACK + Back.RED + 'ERR' + Style.RESET_ALL + f' {datetime.datetime.now()}: {msg}')
