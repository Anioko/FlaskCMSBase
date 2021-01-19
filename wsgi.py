#!/usr/bin/python3.6

activate_this = '/home/ubuntu/flaskapp/venv/bin/activate_this.py'
with open(activate_this) as f:
 exec(f.read(), dict(__file__=activate_this))

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/home/ubuntu/flaskapp/flaskapp/")

from manage import app as application

if __name__ == "__main__":
    application.run()
