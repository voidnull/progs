import sys
import psycopg
import time
from . import log

class DB:
    def __init__(self, connstr):
        self.connstr = connstr
        self.cursor = None
        self.cxn = None

    @staticmethod
    def print_exception(err):
       # get details about the exception
        err_type, err_obj, traceback = sys.exc_info()

        # get the line number when exception occured
        line_num = traceback.tb_lineno
        # print the connect() error
        log.error("{} @line:{}".format(err, line_num))

    def connect(self, connstr = None):
        if self.cxn : return
        try:
            if connstr is None:
                connstr = self.connstr
            else:
                self.connstr = connstr
            self.cxn = psycopg.connect(connstr)
            self.cursor = self.cxn.cursor()
        except Exception as e:
            log.error('unable to connect - {}'.format(connstr))
            self.print_exception(e)

        return self.cursor

    def rollback(self, savepoint=None):
        self.connect()
        if savepoint is None:
            return self.exec('ROLLBACK')
        else:
            return self.exec('ROLLBACK TO SAVEPOINT {}'.format(savepoint))

    def commit(self):
        self.connect()
        return self.exec('COMMIT')

    def txn(self, statements):
        self.connect()
        if type(statements) != list:
            statements = [statements]
        return self.exec(['BEGIN'] + statements + ['COMMIT'] )

    def exec(self, statements, fetch=False):
        self.connect()
        if self.cxn is None:
            log.warn('not connected to the db')
            return None
        try:
            self.cursor = self.cxn.cursor()
            if type(statements) == list:
                results = []
                for s in statements:
                    self.cursor.execute(s)
                    if fetch:
                        try:
                            results.append(self.cursor.fetchall())
                        except psycopg.errors.ProgrammingError as pe:
                            self.print_exception(pe)
                return results
            else:
                self.cursor.execute(statements)
                if fetch:
                    try:
                        return self.cursor.fetchall()
                    except psycopg.errors.ProgrammingError as pe:
                        self.print_exception(pe)

        except Exception as e:
            self.print_exception(e)

        return None