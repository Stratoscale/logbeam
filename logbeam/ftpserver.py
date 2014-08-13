import threading
import pyftpdlib.authorizers
import pyftpdlib.handlers
import pyftpdlib.servers


class FTPServer(threading.Thread):
    def __init__(self, directory, username, password, port, fileToWritePortNumberTo=None):
        autherizer = pyftpdlib.authorizers.DummyAuthorizer()
        autherizer.add_user(username, password, directory, perm="elradfmw")
        handler = pyftpdlib.handlers.FTPHandler
        handler.authorizer = autherizer
        self._server = pyftpdlib.servers.FTPServer(("", port), handler)
        actualPort = self._server.socket.getsockname()[1]
        if fileToWritePortNumberTo is not None:
            with open(fileToWritePortNumberTo, "w") as f:
                f.write(str(actualPort))
        threading.Thread.__init__(self)
        self.daemon = True
        threading.Thread.start(self)

    def run(self):
        self._server.serve_forever()
