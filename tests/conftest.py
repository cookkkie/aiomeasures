# debug asyncio

import os
import os.path
import sys
import logging
import warnings
from pytest import fixture
from subprocess import Popen, PIPE
from time import sleep

os.environ['PYTHONASYNCIODEBUG'] = '1'
# logging.basicConfig(level=logging.DEBUG)
warnings.simplefilter("always")
warnings.filterwarnings('ignore', '.*sys.meta_path is empty.*')
warnings.filterwarnings('ignore', '.*deprecated.*', module='site')
