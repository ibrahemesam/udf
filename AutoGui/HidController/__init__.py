
from .. import os

if os.name == 'nt':
    from .win import Controller
else:
    from .unix import Controller