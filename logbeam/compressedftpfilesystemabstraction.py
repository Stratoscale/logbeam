from logbeam import ftpfilesystemabstraction
import contextlib
import gzip
import cStringIO


class CompressedFTPFilesystemAbstraction:
    def __init__(self):
        self._ftpFilesystemAbstration = ftpfilesystemabstraction.FTPFilesystemAbstraction()

    def close(self):
        self._ftpFilesystemAbstration.close()

    @contextlib.contextmanager
    def filesystem(self):
        with self._ftpFilesystemAbstration.filesystem() as fs:
            yield _CompressedFTPFilesystem(fs)


class _CompressedFTPFilesystem:
    def __init__(self, fs):
        self._fs = fs
        self.path = _CompressedFTPFilesystemPath(fs)

    def open(self, path, mode="r"):
        try:
            with self._fs.open(path + ".gz", mode="rb") as f:
                compressed = cStringIO.StringIO(f.read())
            return gzip.GzipFile(fileobj=compressed, mode=mode)
        except:
            return self._fs.open(path, mode)

    def listdir(self, path):
        result = self._fs.listdir(path)
        for i in xrange(len(result)):
            if result[i].endswith(".gz"):
                result[i] = result[i][: -len(".gz")]
        return result


class _CompressedFTPFilesystemPath:
    def __init__(self, fs):
        self._fs = fs
        self.isdir = fs.isdir

    def exists(self, path):
        return self._fs.path.exists(path) or self._fs.path.exists(path + ".gz")

    def isfile(self, path):
        return self._fs.path.isfile(path) or self._fs.path.isfile(path + ".gz")

    def walk(self, *args, **kwargs):
        for root, dirs, files in self._fs.walk():
            filesWithoutGZ = [
                n[: -len(".gz")] if n.endswith(".gz") else n
                for n in files]
            yield root, dirs, filesWithoutGZ
