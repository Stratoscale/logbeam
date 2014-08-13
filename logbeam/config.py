import yaml
import os

HOSTNAME = None
PORT = 21
USERNAME = None
PASSWORD = None
BASE_DIRECTORY = None
UPLOAD_TRANSPORT = "null"
COMPRESS = False


def _load(filename):
    with open(filename) as f:
        data = yaml.load(f.read())
    globals().update(data)


def load():
    if os.path.exists("/etc/logbeam.config"):
        _load("/etc/logbeam.config")
    parts = os.getcwd().split(os.path.sep)
    for i in xrange(len(parts)):
        path = os.path.sep.join(parts[: i + 1])
        if os.path.exists(os.path.join(path, "logbeam.config")):
            _load(os.path.join(path, "logbeam.config"))
    if 'LOGBEAM_CONFIG' in os.environ:
        data = yaml.load(os.environ['LOGBEAM_CONFIG'])
        globals().update(data)
    if UPLOAD_TRANSPORT == "ftp":
        for mandatory in ['HOSTNAME', 'USERNAME', 'PASSWORD']:
            if globals()[mandatory] is None:
                raise Exception(
                    "When using ftp transport, Configuration file heirarchy must "
                    "include a '%s' setting" % mandatory)
