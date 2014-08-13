import subprocess
import tempfile
import os
import time
import shutil
import signal
import logbeam
assert '/usr/' not in logbeam.__file__


class FTPServer:
    def __init__(self):
        portFile = tempfile.NamedTemporaryFile()
        self.directory = tempfile.mkdtemp()
        self._popen = subprocess.Popen([
            "coverage", "run", "--parallel-mode", "-m", "logbeam.main", "ftpserver",
            "--fileToWritePortNumberTo", portFile.name,
            "--directory", self.directory])
        self._readPort(portFile)

    def _readPort(self, portFile):
        for i in xrange(10):
            try:
                self.port = int(portFile.read().strip())
                return
            except:
                time.sleep(0.1)
        raise Exception("Port file not written")

    def cleanup(self):
        self._popen.send_signal(signal.SIGINT)
        shutil.rmtree(self.directory, ignore_errors=True)

    def fileCount(self):
        count = 0
        for root, dirs, files in os.walk(self.directory):
            count += len(files) + len(dirs)
        return count


class Null:
    def __init__(self, playground):
        self._playground = playground

    def upload(self, *paths):
        subprocess.check_call([
            "coverage", "run", "--parallel-mode", "-m", "logbeam.main", "upload"] +
            [os.path.join(self._playground, p) for p in paths])


class FTP:
    def __init__(self, playground, server, compressed, baseDir=None):
        self._playground = playground
        self._server = server
        self._compressed = compressed
        self._baseDir = baseDir

    def upload(self, *paths, **kwargs):
        subprocess.check_call([
            "coverage", "run", "--parallel-mode", "-m", "logbeam.main", "upload"] +
            [os.path.join(self._playground, p) for p in paths] +
            (["--under", kwargs['under']] if 'under' in kwargs else []),
            env=dict(
                os.environ,
                LOGBEAM_CONFIG="UPLOAD_TRANSPORT: ftp\nHOSTNAME: localhost\nUSERNAME: logs\n"
                "PASSWORD: logs\nPORT: %d\n%s\n%s\n" % (
                    self._server.port,
                    "COMPRESS: Yes" if self._compressed else "",
                    "BASE_DIRECTORY: %s" % self._baseDir if self._baseDir is not None else "")))
