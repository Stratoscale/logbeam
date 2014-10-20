from logbeam import config
from logbeam import ftputilcustomport
import os


class FTPUpload:
    def __init__(self):
        self._connection = ftputilcustomport.FTPHost()
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
        path = path.rstrip(os.path.sep)
        for root, dirs, files in os.walk(path):
            for filename in files:
                fullPath = os.path.join(root, filename)
                relativePath = fullPath[len(path) + len(os.path.sep):]
                destination = os.path.join(destinationPath, relativePath)
                self.file(fullPath, destination)
