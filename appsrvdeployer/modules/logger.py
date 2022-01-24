import logging
import logging.handlers

def create_logger(app_name, log_level=logging.DEBUG, logfile='/tmp/logger.log', address="", stdout=True, syslog=False, file=False):
    """
    create logging object with logging to syslog, file and stdout
    :param logfile log file
    :param app_name app name
    :param log_level logging log level
    :param address address of syslog
    :param stdout log to stdout
    :param syslog log to syslog
    :param file log to file
    :return: logging object
    """

    # Creazione di un logging e il set del livello di log
    logger = logging.getLogger(app_name)
    logger.setLevel(log_level)

    # Imposto il format di default per il logging
    formatter = logging.Formatter('[%(asctime)s][%(name)s][%(threadName)s] %(levelname)s: %(message)s')

    if file:
        # create file logger handler
        fh = logging.FileHandler(logfile)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    if syslog:
        # create syslog logger handler
        sh = logging.handlers.SysLogHandler(address = (address if address else "localhost",514), facility='local5', socktype=None)
        sh.setLevel(log_level)
        sf = logging.Formatter('%(message)s')
        sh.setFormatter(sf)
        logger.addHandler(sh)

    if stdout:
        # create stream logger handler
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger