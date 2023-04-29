import datetime
import getpass
import logging
import socket
import sys
import tempfile

# loggers
_logger_declarations = [
    'core',
    'classe',
    'carte',
    'entity',
    'action'
]

# prend le plus grand nom pour le padding
_padding = max((len(n) for n in _logger_declarations))

# Format le log
_fmt_str = "%(asctime)s|%(name)-{}s|%(levelname)-8s|%(message)s" \
    .format(str(_padding))

_formatter = logging.Formatter(_fmt_str)

# propagate logger levels on top of the module
CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG
NOTSET = logging.NOTSET


_LOGGER_LEVEL_BY_NAME = {
    "critical": CRITICAL,
    "error": ERROR,
    "warning": WARNING,
    "info": INFO,
    "debug": DEBUG,
    "notset": NOTSET
}

# nom du fichier log
_now = datetime.datetime.now()
_prefix = _now.strftime("frenchstone_%Y%m%d_%Hh%Mm%S_")

# creation d'un fichier temp
_, _file_path = tempfile.mkstemp(suffix='.log', prefix=_prefix)

with open(_file_path, 'w') as _f:

    def _fmt_iter(iterable, margin=10):
        """Formats an iterable for header display purposes"""
        return ('\n'+' '*margin).join((str(i) for i in iterable))

    _user = getpass.getuser()
    _host = _fmt_iter(socket.gethostbyname_ex(socket.gethostname()), margin=6)
    _sys_argv = _fmt_iter(sys.argv, margin=6)

    _f.write("="*80 + '\n')
    _f.write("user: {_user}\n"
             "host: {_host}\n"
             "\n"
             "sys_argv: {_sys_argv}"
             "".format(**locals()))
    _f.write("="*80 + '\n')

# creation d'un file handler
_file_handler = logging.FileHandler(_file_path)
_file_handler.setFormatter(_formatter)

_loggers = {}
for name in _logger_declarations:

    # create d'un logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # connect to file handler
    logger.addHandler(_file_handler)

    # create stream handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(_formatter)
    logger.addHandler(console_handler)

    # add it to global dict
    _loggers[name] = logger

CORE = _loggers["core"]
CLASSE = _loggers["classe"]
CARTE = _loggers["carte"]
ENTITY = _loggers["entity"]
ACTION = _loggers["action"]


def set_level(level):
    """Change le level du logger en fonction du level donnée

    Args:
        level (int): level du logger
    """
    assert isinstance(level, int)
    assert level in _LOGGER_LEVEL_BY_NAME.values()
    
    for logger_ in _loggers.values():
        logger_.setLevel(level)


def get_file_path():
    """Returns the log file path"""
    return _file_path
