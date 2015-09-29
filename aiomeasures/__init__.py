"""
    AIO Measures
    ~~~~~~~~~~~~

"""

from ._version import get_versions
from .checks import *
from .clients import *
from .events import *
from .metrics import *

__all__ = (checks.__all__
           + clients.__all__
           + events.__all__
           + metrics.__all__)

__version__ = get_versions()['version']
del get_versions
