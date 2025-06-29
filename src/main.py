from .db import init_db
from .gui import launch_app

def main():
    init_db()
    launch_app()

if __name__ == '__main__':
    main()
