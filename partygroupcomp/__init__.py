from logging import getLogger, StreamHandler, FileHandler, Formatter, DEBUG, INFO, ERROR


def __init_logger():
    logger = getLogger('2PtGC')
    c_handler = StreamHandler()
    logger.setLevel(DEBUG)
    c_handler.setLevel(DEBUG)
    c_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)
    try:
        f_handler = FileHandler('.//extras//2PGC.log', )
        f_handler.setLevel(DEBUG)
        f_handler.setFormatter(c_format)
        logger.addHandler(f_handler)
    except Exception as e:
        logger.warning('File logger not initialized')
    return logger


log = __init_logger()