# Add Root Dir
import sys
import os
ROOT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR + "/Utils")

from DataLoader import *

if "__main__" == __name__:
    # Parse Wikipedia

    ReadWikiDataset('a')
