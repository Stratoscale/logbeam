from logbeam import webresources
from logbeam import webserver
from twisted.internet import reactor
from logbeam import ftpfilesystemabstraction


class WebFrontend:
    def __init__(self, port, username=None, password=None):
        filesystemAbstraction = ftpfilesystemabstraction.FTPFilesystemAbstraction()
        root = webresources.Folder(filesystemAbstraction, "")
        if username is None:
            webserver.listenUnsecured(root, port)
        else:
            webserver.listenSecured(root, port)

    def go(self):
        reactor.run()
