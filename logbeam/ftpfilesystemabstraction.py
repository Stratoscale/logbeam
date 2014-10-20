from logbeam import config
from logbeam import ftputilcustomport
import threading
import contextlib
import time
import collections


_Connection = collections.namedtuple("_Connection", ["connection", "lastTouch"])


class FTPFilesystemAbstraction:
    _STALE_TIMEOUT = 60

    def __init__(self):
        self._connectionPool = [_Connection(self._createConnection(), time.time())]
        self._connectionPoolLock = threading.Lock()

    def _createConnection(self):
        connection = ftputilcustomport.FTPHost()
        try:
            if config.BASE_DIRECTORY:
                if not connection.path.isdir(config.BASE_DIRECTORY):
                    connection.makedirs(config.BASE_DIRECTORY)
                connection.chdir(config.BASE_DIRECTORY)
        except:
            connection.close()
            raise
        return connection

    def close(self):
        while len(self._connectionPool) > 0:
            self._connectionPool.pop().connection.close()

    @contextlib.contextmanager
    def filesystem(self):
        connection = None
        timeout = time.time() - self._STALE_TIMEOUT
        with self._connectionPoolLock:
            while len(self._connectionPool) > 0 and self._connectionPool[0].lastTouch < timeout:
                self._connectionPool.pop(0).connection.close()
            if len(self._connectionPool) > 0:
                connection = self._connectionPool.pop().connection
        if connection is None:
            connection = self._createConnection()
        yield connection
        with self._connectionPoolLock:
            if len(self._connectionPool) > 5:
                connection.close()
            else:
                self._connectionPool.append(_Connection(connection, time.time()))
