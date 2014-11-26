import threading
import pyftpdlib.authorizers
import pyftpdlib.handlers
import pyftpdlib.servers
from logbeam import firewallpuncture


class FTPServer(threading.Thread):
    def __init__(self, directory, username, password, port, fileToWritePortNumberTo=None):
        autherizer = pyftpdlib.authorizers.DummyAuthorizer()
        autherizer.add_user(username, password, directory, perm="elradfmw")
        handler = pyftpdlib.handlers.FTPHandler
        handler.passive_ports = (20000, 22000)
        handler.authorizer = autherizer
        self._server = pyftpdlib.servers.FTPServer(("", port), handler)
        self._actualPort = self._server.socket.getsockname()[1]
        self._puncture = firewallpuncture.FirewallPuncture(self._actualPort, handler.passive_ports)
        if fileToWritePortNumberTo is not None:
            with open(fileToWritePortNumberTo, "w") as f:
                f.write(str(self._actualPort))
        threading.Thread.__init__(self)
        self.daemon = True
        threading.Thread.start(self)

    def run(self):
        self._server.serve_forever()

    def actualPort(self):
        return self._actualPort
