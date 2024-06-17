import os
from pathlib import Path
import sys

#Establish absolute paths for proper referencing within the module
thisdir = Path(__file__).parent.absolute()
outer_dir = thisdir.parent
sys.path.append(os.path.abspath(thisdir))