from PIL.Image import frombytes
from numpy import frombuffer, uint8
from .. import os

if os.name == 'nt':
    from .win import WinCap
else:
    from .unix import WinCap