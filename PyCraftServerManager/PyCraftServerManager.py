import os

from threading import Thread, Lock
from termcolor import colored

from Utilities.Utilities import *

if is_windows():
    import colorama
    colorama.init()

stopping_all = True

def init():
    """
    Starts PyCraftServerManager input thread.
    """
    pass

def input_loop_thread():
    """
    Handles accepting input from the user in a thread until an exit is met.
    """
    pass