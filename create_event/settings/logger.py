import os
from logging import getLogger, basicConfig, FileHandler, StreamHandler, INFO


if not os.path.exists("logs"):
    os.makedirs("logs")
relative_path = os.path.join("logs", "data.log")

logger = getLogger()

FORMAT = "%(asctime)s : %(filename)s : %(funcName)s : %(levelname)s : %(message)s"

file_handler = FileHandler(relative_path)
file_handler.setLevel(INFO)

stream = StreamHandler()
stream.setLevel(INFO)

basicConfig(level=INFO, format=FORMAT, handlers=[file_handler, stream])
