#!python
import sqlite3
import json
import platformdirs
import os
from . import log, cliargs

class Cache:
    def __init__(self, appname='doctools') -> None:
        cache_db_path = platformdirs.user_cache_path(appname)
        if not os.path.exists(cache_db_path):
            os.makedirs(cache_db_path)
        cache_db_path = "{}/cache.db".format(platformdirs.user_cache_path(appname))
        log.debug('cache is located @ {}'.format(cache_db_path))
        self.conn = sqlite3.connect(cache_db_path)
        self.createTables()

    def createTables(self):
        try:
            cur = self.conn.cursor()
            cur.execute("CREATE TABLE cache(key TEXT PRIMARY KEY, value TEXT, createtime TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
            self.conn.commit()
        except sqlite3.OperationalError as oe:
            if oe.args[0] != 'table cache already exists':
                print(oe)

    def get(self, key):
        log.debug('{}'.format(key))
        try:
            cur = self.conn.cursor()
            sql = "select value from cache where key = ?"
            cur.execute(sql, (key,))
            result = cur.fetchone()
            cur.close()
            self.conn.commit()
            if result == None or len(result) == 0:
                log.debug('NOTFOUND : {}'.format(key))
                return None
            return result[0]
        except sqlite3.OperationalError as oe:
            print(oe)

    def getJson(self, key):
        value = self.get(key)
        return json.loads(value) if value is not None else None

    def has(self, key):
        return self.get(key) != None
    
    def delete(self, key):
        log.debug('{}'.format(key))
        try:
            cur = self.conn.cursor()
            sql = "delete from cache where key = ?"
            cur.execute(sql, (key,))
            cur.close()
            self.conn.commit()
        except sqlite3.OperationalError as oe:
            print(oe)

    def putJson(self, key, value):
        self.put(key, json.dumps(value))

    def put(self, key, value):
        log.debug('{}'.format(key))
        try:
            cur = self.conn.cursor()
            sql = 'insert into cache(key, value) values(?, ?) on conflict(key) do update set value = ?'
            cur.execute(sql, (key, value, value,))
            cur.close()
            self.conn.commit()
        except sqlite3.OperationalError as oe:
            print(oe)

    def __exec(self, sql):
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            result = cur.fetchall()
            cur.close()
            self.conn.commit()
            return result
        except sqlite3.OperationalError as oe:
            print(oe)

        return None

    def cli(self, argv = None):
        parser = cliargs.Parser('Cache management tool', argv=argv)
        parser.add_argument('key', help='key/pattern', nargs='?')
        parser.add_argument('-c', '--cmd', dest='cmd',
                            choices=['get', 'keys', 'summary', 'delete' , 'purge-old'], 
                            type=str, default='summary', help = 'cmd types')
        
        args = parser.parse_args()

        if args.cmd == 'summary':
            response = self.__exec('select count(*) from cache')
            print('Num items in cache : {}'.format(response[0][0]))

        elif args.cmd == 'keys':
            if args.key:
                sql = 'select key from cache where key LIKE \'{}\''.format(args.key)
            else:
                sql = 'select key from cache order by key'
            response = self.__exec(sql)

            for row in response:
                print(row[0])

        elif args.cmd == 'get':
            if args.key:
                sql = 'select value,createtime from cache where key=\'{}\''.format(args.key)
                response = self.__exec(sql)
                if len(response) > 0:
                    row=response[0]
                    print('created-at:', row[1])
                    print('value:', row[0])
                else:
                    print('key not found')
            else:
                print('[key] needed to fetch the value for')

        elif args.cmd == 'delete':
            if args.key:
                sql = 'delete from cache where key LIKE \'{}\''.format(args.key)
                response = self.__exec(sql)
            else:
                print('[key] needed to fetch the value for')

        elif args.cmd == 'purge-old':
            days = 30
            if args.key:
                if args.key.isdigit() : days = int(args.key)
            sql = 'select count(key) from cache where (julianday(\'now\') - julianday(createtime)) > {}'.format(days)
            response = self.__exec(sql)
            row=response[0]
            print('No.of items to be removed:', row[0])
            sql = 'delete from cache where (julianday(\'now\') - julianday(createtime)) > {}'.format(days)
            response = self.__exec(sql)

def cli():
    cache= Cache()
    cache.cli()

# -------- main ----------
if __name__ == '__main__' :
    cli()