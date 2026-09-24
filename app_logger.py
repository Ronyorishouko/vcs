import logging
from logging.handlers import RotatingFileHandler

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)s - %(message)s")

def get_file_handler(file):
	handler = RotatingFileHandler(file, maxBytes=20000000, backupCount=1)
	handler.setLevel(logging.DEBUG)
	handler.setFormatter(formatter)
	return handler

def get_stream_handler():
	handler = logging.StreamHandler()
	handler.setLevel(logging.INFO)
	handler.setFormatter(formatter)
	return handler

def get_logger(name, file):
	logger = logging.getLogger(name)
	logger.setLevel(logging.INFO)
	logger.addHandler(get_file_handler(file))
	logger.addHandler(get_stream_handler())
	return logger
