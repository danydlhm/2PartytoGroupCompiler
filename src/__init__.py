from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO, ERROR


def __init_logger():
    logger = getLogger('2PtGC')
    c_handler = StreamHandler()
    logger.setLevel(ERROR)
    c_handler.setLevel(DEBUG)
    c_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)
    return logger


log = __init_logger()