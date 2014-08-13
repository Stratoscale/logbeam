from logbeam import config
from logbeam import ftpupload
from logbeam import compressedftpupload
from logbeam import nullupload
import os


class Upload:
    def __init__(self):
        if config.UPLOAD_TRANSPORT == "ftp":
            if config.COMPRESS:
                self._transport = compressedftpupload.CompressedFTPUpload()
            else:
                self._transport = ftpupload.FTPUpload()
        elif config.UPLOAD_TRANSPORT == "null":
            self._transport = nullupload.NullUpload()
        else:
            raise AssertionError("Unknown upload transport %s" % config.UPLOAD_TRANSPORT)

    def upload(self, paths, under=None):
        for path in paths:
            if os.path.isdir(path):
                destination = "" if under is None else under
                self._transport.directory(path, destination)
            else:
                if under is None:
                    destination = os.path.basename(path)
                else:
                    destination = os.path.join(under, os.path.basename(path))
                self._transport.file(path, destination)

    def close(self):
        self._transport.close()
