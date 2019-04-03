import os
import sqlite3
from pickle import loads, dumps
from threading import get_ident
from time import sleep
from tess.utils import Singleton
from tinydb import TinyDB, Query
from tempfile import mkstemp


class TinyDBQueue(object, metaclass=Singleton):

    DEFAULT_TABLE = '_default'

    def __init__(self, path=None, table=DEFAULT_TABLE):
        if path is None:
            path = mkstemp()
        self.path = os.path.abspath(path)
        self.db = TinyDB(self.path)
        self.table = self.db.table(table)

    def append(self, obj):
        return self.table.insert(obj)

    def get(self, id):
        return self.table.get(doc_id=id)

    def get_new(self):
        query = Query()
        return self.table.search(query['status'] == 'NEW')

    def update(self, doc_id, doc):
        self.table.update(doc, doc_ids=[doc_id])

    def __iter__(self):
        for entry in self.table:
            yield entry

    def __len__(self):
        return len(self.db)


class SqliteQueue(object, metaclass=Singleton):
    _create = (
        'CREATE TABLE IF NOT EXISTS queue '
        '('
        '  id INTEGER PRIMARY KEY AUTOINCREMENT,'
        '  item BLOB'
        ')'
    )
    _count = 'SELECT COUNT(*) FROM queue'
    _iterate = 'SELECT id, item FROM queue'
    _append = 'INSERT INTO queue (item) VALUES (?)'
    _write_lock = 'BEGIN IMMEDIATE'
    _popleft_get = (
        'SELECT id, item FROM queue '
        'ORDER BY id LIMIT 1'
    )
    _popleft_del = 'DELETE FROM queue WHERE id = ?'
    _peek = (
        'SELECT item FROM queue '
        'ORDER BY id LIMIT 1'
    )

    def __init__(self, path=None):
        self.path = os.path.abspath(path)
        self._connection_cache = {}
        with self._get_conn() as conn:
            conn.execute(self._create)

    def __len__(self):
        with self._get_conn() as conn:
            l = conn.execute(self._count).next()[0]
        return l

    def __iter__(self):
        with self._get_conn() as conn:
            for id, obj_buffer in conn.execute(self._iterate):
                yield loads(str(obj_buffer))

    def _get_conn(self):
        id = get_ident()
        if id not in self._connection_cache:
            self._connection_cache[id] = sqlite3.Connection(self.path,
                                                            timeout=60)
        return self._connection_cache[id]

    def append(self, obj):
        obj_buffer = memoryview(dumps(obj, 2))
        with self._get_conn() as conn:
            conn.execute(self._append, (obj_buffer,))
            return conn.cursor().lastrowid

    def popleft(self, sleep_wait=True):
        keep_pooling = True
        wait = 0.1
        max_wait = 2
        tries = 0
        with self._get_conn() as conn:
            id = None
            while keep_pooling:
                conn.execute(self._write_lock)
                cursor = conn.execute(self._popleft_get)
                try:
                    id, obj_buffer = cursor.next()
                    keep_pooling = False
                except StopIteration:
                    conn.commit()  # unlock the database
                    if not sleep_wait:
                        keep_pooling = False
                        continue
                    tries += 1
                    sleep(wait)
                    wait = min(max_wait, tries / 10 + wait)
            if id:
                conn.execute(self._popleft_del, (id,))
                return loads(str(obj_buffer))
        return None

    def peek(self):
        with self._get_conn() as conn:
            cursor = conn.execute(self._peek)
            try:
                return loads(str(cursor.next()[0]))
            except StopIteration:
                return None
