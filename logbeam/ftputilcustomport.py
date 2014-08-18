from logbeam import config
import ftputil
import ftplib


class FTPHost(ftputil.FTPHost):
    def __init__(self, **kwargs):
        kwargs.setdefault('host', config.HOSTNAME)
        kwargs.setdefault('user', config.USERNAME)
        kwargs.setdefault('passwd', config.PASSWORD)
        kwargs.setdefault('port', config.PORT)
        kwargs.setdefault('session_factory', _Session)
        ftputil.FTPHost.__init__(self, **kwargs)


class _Session(ftplib.FTP):
    def __init__(self, host, user, passwd, port):
        ftplib.FTP.__init__(self)
        self.connect(host, port)
        self.login(user, passwd)
