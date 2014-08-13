from logbeam import config
import ftputil
import ftplib
import os


class FTPUpload:
    def __init__(self):
        self._connection = ftputil.FTPHost(
            host=config.HOSTNAME, user=config.USERNAME, passwd=config.PASSWORD,
            port=config.PORT, session_factory=_Session)
        if config.BASE_DIRECTORY:
            if not self._connection.path.isdir(config.BASE_DIRECTORY):
                self._connection.makedirs(config.BASE_DIRECTORY)
            self._connection.chdir(config.BASE_DIRECTORY)
        self._knownDirs = set()

    def close(self):
        self._connection.close()

    def file(self, path, destinationPath):
        dirname = os.path.dirname(destinationPath)
        if dirname not in self._knownDirs:
            if not self._connection.path.isdir(dirname):
                self._connection.makedirs(dirname)
            self._knownDirs.add(dirname)
        self._connection.upload(path, destinationPath)

    def directory(self, path, destinationPath):
        for root, dirs, files in os.walk(path):
            for filename in files:
                fullPath = os.path.join(root, filename)
                relativePath = fullPath[len(path) + len(os.path.sep):]
                destination = os.path.join(destinationPath, relativePath)
                self.file(fullPath, destination)


class _Session(ftplib.FTP):
    def __init__(self, host, user, passwd, port):
        ftplib.FTP.__init__(self)
        self.connect(host, port)
        self.login(user, passwd)
