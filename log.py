import logging


def get_logger(name):
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s %(levelname)s %(message)s")
    return logging.getLogger(name)
