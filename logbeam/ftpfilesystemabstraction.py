from logbeam import config
from logbeam import ftputilcustomport
import threading
import contextlib


class FTPFilesystemAbstraction:
    def __init__(self):
        self._connectionPool = [self._createConnection()]
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
            self._connectionPool.pop().close()

    @contextlib.contextmanager
    def filesystem(self):
        connection = None
        with self._connectionPoolLock:
            if len(self._connectionPool) > 0:
                connection = self._connectionPool.pop()
        if connection is None:
            connection = self._createConnection()
        yield connection
        with self._connectionPoolLock:
            if len(self._connectionPool) > 5:
                connection.close()
            else:
                self._connectionPool.append(connection)
