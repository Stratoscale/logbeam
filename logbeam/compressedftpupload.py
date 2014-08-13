from logbeam import ftpupload
import threading
import tempfile
import gzip
import os
import concurrent.futures
import multiprocessing


class CompressedFTPUpload:
    def __init__(self):
        self._ftpPool = [ftpupload.FTPUpload()]
        self._ftpPoolLock = threading.Lock()

    def close(self):
        while len(self._ftpPool) > 0:
            ftp = self._ftpPool.pop()
            ftp.close()

    def file(self, path, destinationPath):
        temp = tempfile.NamedTemporaryFile()
        self._compress(path, temp)
        temp.flush()
        ftp = self._allocate()
        try:
            ftp.file(temp.name, destinationPath + ".gz")
        finally:
            self._free(ftp)

    def directory(self, path, destinationPath):
        with concurrent.futures.ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            todo = []
            for root, dirs, files in os.walk(path):
                for filename in files:
                    fullPath = os.path.join(root, filename)
                    relativePath = fullPath[len(path) + len(os.path.sep):]
                    destination = os.path.join(destinationPath, relativePath)
                    todo.append(executor.submit(self.file, fullPath, destination))
            for item in todo:
                item.result()

    def _compress(self, path, temp):
        gz = gzip.GzipFile(mode="wb", compresslevel=9, fileobj=temp)
        with open(path, "rb") as f:
            while True:
                data = f.read(1024 * 1024)
                if len(data) == 0:
                    break
                gz.write(data)
        gz.close()

    def _allocate(self):
        with self._ftpPoolLock:
            if len(self._ftpPool) > 0:
                return self._ftpPool.pop()
            else:
                return ftpupload.FTPUpload()

    def _free(self, ftp):
        with self._ftpPoolLock:
            self._ftpPool.append(ftp)
