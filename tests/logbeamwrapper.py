import subprocess
import tempfile
import os
import time
import shutil
import signal
import requests
import socket
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


class WebFrontend:
    def __init__(self, ftpServer, secure=False):
        self._server = ftpServer
        self._secure = secure
        self.port = self._freeTCPPort()
        self._popen = subprocess.Popen([
            "coverage", "run", "--parallel-mode", "-m", "logbeam.main", "webfrontend",
            "--port", str(self.port)] +
            ([] if not secure else ["--basicAuthUser=logs", "--basicAuthPassword=logs"]),
            env=dict(
                os.environ, LOGBEAM_CONFIG="UPLOAD_TRANSPORT: ftp\nHOSTNAME: localhost\nUSERNAME: logs\n"
                "PASSWORD: logs\nPORT: %d\n" % self._server.port))

    def _freeTCPPort(self):
        sock = socket.socket()
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("", 0))
            return sock.getsockname()[1]
        finally:
            sock.close()

    def cleanup(self):
        self._popen.send_signal(signal.SIGINT)

    def fetch(self, path):
        url = 'http://localhost:%d/%s' % (self.port, path)
        if self._secure:
            request = requests.get(url, auth=('logs', 'logs'))
        else:
            request = requests.get(url)
        return request.content


class Null:
    def __init__(self, playground):
        self._playground = playground

    def upload(self, *paths):
        subprocess.check_call([
            "coverage", "run", "--parallel-mode", "-m", "logbeam.main", "upload"] +
            [os.path.join(self._playground, p) for p in paths])


class FTP:
    def __init__(self, playground, server, compressed=False, baseDir=None):
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
