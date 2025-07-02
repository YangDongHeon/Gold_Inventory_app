import sys
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

from db import init_db
from gui import launch_app


def main():
    init_db()
    launch_app()

if __name__ == '__main__':
    main()
