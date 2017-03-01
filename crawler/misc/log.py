import logging
# from logging.config import fileConfig

# fileConfig('logging_config.ini')
logger = logging.getLogger(__name__)
# handler = logging.StreamHandler()
handler = logging.FileHandler('hello.log')
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
