import logging
import inspect

setup_done = False

def setup(level=logging.INFO, root=False):
    global setup_done

    # remove all handlers
    for h in logging.root.handlers[:]:
        logging.root.removeHandler(h)
        h.close()

    datefmt="%b/%d %H:%M:%S"
    logformat="%(asctime)s | %(levelname)s | %(loc)s : %(message)s"

    fmt = logging.Formatter(fmt=logformat, datefmt=datefmt, defaults={'loc' : ''})
    handler = logging.StreamHandler()
    handler.setFormatter(fmt)
    logging.root.addHandler(handler)

    if root:
        logging.root.setLevel(level)

    logging.getLogger('log').setLevel(level)
    setup_done = True

def setupGlobal(level=logging.INFO):
    setup(level, True)

def setLevel(level=logging.INFO):
    if not setup_done : setup()
    logging.getLogger('log').setLevel(level)

def setDebug(): setLevel(logging.DEBUG)
def setInfo(): setLevel(logging.INFO)
def setWarn(): setLevel(logging.WARNING)

def critical(msg, *args, **kwargs):
    if not setup_done : setup()
    logging.getLogger('log').critical(msg, extra=__loc(), *args, **kwargs)

def error(msg, *args, **kwargs):
    if not setup_done : setup()
    logging.getLogger('log').error(msg, extra=__loc(), *args, **kwargs)

def warn(msg, *args, **kwargs):
    if not setup_done : setup()
    logging.getLogger('log').warning(msg, extra=__loc(), *args, **kwargs)

def info(msg, *args, **kwargs):
    if not setup_done : setup()
    logging.getLogger('log').info(msg, extra=__loc(), *args, **kwargs)

def debug(msg, *args, **kwargs):
    if not setup_done : setup()
    logging.getLogger('log').debug(msg, extra=__loc(), *args, **kwargs)

def __loc():
    try:
        stack = inspect.stack()
        return {'loc' : stack[2][0].f_code.co_qualname }
    except Exception as e:
        #print(e)
        pass
    return {'loc': ''}


