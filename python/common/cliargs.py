#!python
import argparse
from typing import Optional
from pathlib import Path
from . import log
import sys
import logging

class LogAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        #print('%r %r %r' % (namespace, value, option_string))
        value = value.upper()
        global_log = True if self.dest.startswith('global') else False
        log_level = logging.INFO
        if value.startswith('INFO'):
            log_level = logging.INFO
        elif value.startswith('WARN'):
            log_level = logging.WARN
        elif value.startswith('DEBUG'):
            log_level = logging.DEBUG
        elif value.startswith('ERROR'):
            log_level = logging.ERROR
        elif value.startswith('CRITICAL'):
            log_level = logging.CRITICAL
        else:
            raise Exception('unknown log level: [{}]'.format(value))
        
        log.setup(log_level, global_log)

class Parser(argparse.ArgumentParser):

    def __init__(self, desc, argv: Optional[str] = None) -> None:
        argv = argv or sys.argv[:]
        prog_name = Path(argv[0]).name
        super().__init__(prog=prog_name, description=desc)
        self.add_argument('--debug', dest='debug', default=False, action='store_true', help=argparse.SUPPRESS)
        self.add_argument('--global-debug', dest='global_debug', default=False, action='store_true', help=argparse.SUPPRESS)
        self.add_argument('--dump-args', dest='dump_args', default=False, action='store_true', help=argparse.SUPPRESS)

        self.add_argument('--log-level', dest='log_level', default=None, action=LogAction, help=argparse.SUPPRESS)
        self.add_argument('--global-log-level', dest='global_log', default=None, action=LogAction, help=argparse.SUPPRESS)


    def parse_args(self):
        args = super().parse_args()

        if args.dump_args:
            print('cli args = {}'.format(args))
        if args.debug:
            log.setDebug()

        if args.global_debug:
            log.setupGlobal(logging.DEBUG)

        return args


# -------- main ----------
if __name__ == '__main__' :
    p = Parser('cli parser')
    args = p.parse_args()
    logging.root.debug('This is a global DEBUG message')
    logging.root.info('This is a global INFO message')

    log.info('This is a local INFO message')
    log.debug('This is a local DEBUG message')
    