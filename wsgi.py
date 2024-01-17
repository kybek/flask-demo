import logging

logging.basicConfig(level=logging.DEBUG)

from flaskr import app

if __name__ == "__main__":
    app.run()
