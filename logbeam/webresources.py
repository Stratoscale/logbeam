from twisted.web import resource
from twisted.web import server
import os
import threading
import mimetypes
from twisted.internet import reactor


class Folder(resource.Resource):
    def __init__(self, filesystemAbstraction, path):
        self._filesystemAbstraction = filesystemAbstraction
        self._path = path
        resource.Resource.__init__(self)

    def render(self, request):
        _DirectoryListingThread(request, self._filesystemAbstraction, self._path)
        return server.NOT_DONE_YET

    def getChild(self, path, request):
        if path == "":
            return self
        relative = os.path.join(self._path, path)
        with self._filesystemAbstraction.filesystem() as fs:
            if fs.path.isdir(relative):
                return Folder(self._filesystemAbstraction, relative)
            elif fs.path.isfile(relative):
                return UncompressedFile(self._filesystemAbstraction, relative)
            elif fs.path.isfile(relative + ".gz"):
                return CompressedFile(self._filesystemAbstraction, relative)
            else:
                raise Exception("'%s' was not found" % relative)


class _DirectoryListingThread(threading.Thread):
    def __init__(self, request, filesystemAbstraction, path):
        self._request = request
        self._filesystemAbstraction = filesystemAbstraction
        self._path = path
        threading.Thread.__init__(self)
        self.daemon = True
        threading.Thread.start(self)

    def run(self):
        try:
            entries = []
            with self._filesystemAbstraction.filesystem() as fs:
                for filename in fs.listdir(self._path):
                    fullPath = os.path.join(self._path, filename)
                    fullPathUncompressed = fullPath[: -len(".gz")] if fullPath.endswith(".gz") else fullPath
                    uncompressed = filename[: -len(".gz")] if filename.endswith(".gz") else filename
                    size = "dir" if fs.path.isdir(fullPath) else fs.stat(fullPath).st_size
                    entry = _DIRECTORY_LISTING_ENTRY_TEMPLATE % dict(
                        href="/" + fullPathUncompressed, text=uncompressed, size=size)
                    entries.append(entry)
            result = _DIRECTORY_LISTING_TEMPLATE % dict(tableContent="\n".join(entries))
            reactor.callFromThread(self._request.write, result)
        finally:
            reactor.callFromThread(self._request.finish)


class UncompressedFile(resource.Resource):
    def __init__(self, filesystemAbstraction, path):
        self._filesystemAbstraction = filesystemAbstraction
        self._path = path
        resource.Resource.__init__(self)

    def render_GET(self, request):
        request.setHeader('Content-Type', mimetypes.guess_type(self._path))
        _StreamThread(request, self._filesystemAbstraction, self._path)
        return server.NOT_DONE_YET


class _StreamThread(threading.Thread):
    def __init__(self, request, filesystemAbstraction, path):
        self._request = request
        self._filesystemAbstraction = filesystemAbstraction
        self._path = path
        threading.Thread.__init__(self)
        self.daemon = True
        threading.Thread.start(self)

    def run(self):
        try:
            with self._filesystemAbstraction.filesystem() as fs:
                with fs.open(self._path, "rb") as f:
                    while True:
                        data = f.read(128 * 1024)
                        if len(data) == 0:
                            break
                        reactor.callFromThread(self._request.write, data)
        finally:
            reactor.callFromThread(self._request.finish)


class CompressedFile(resource.Resource):
    def __init__(self, filesystemAbstraction, path):
        self._filesystemAbstraction = filesystemAbstraction
        self._path = path
        self._compressedPath = path + ".gz"
        resource.Resource.__init__(self)

    def render_GET(self, request):
        request.setHeader('Content-Encoding', 'gzip')
        request.setHeader('Content-Type', mimetypes.guess_type(self._path))
        _StreamThread(request, self._filesystemAbstraction, self._compressedPath)
        return server.NOT_DONE_YET


_DIRECTORY_LISTING_TEMPLATE = """
<html>
<head>
<title>Directory Listing</title>
</head>
<table>
    <thead>
        <tr>
            <th>Filename</th>
            <th>Size</th>
        </tr>
    </thead>
    <tbody>
%(tableContent)s
    </tbody>
</table>

</body>
</html>
"""

_DIRECTORY_LISTING_ENTRY_TEMPLATE = """
<tr>
    <td><a href="%(href)s">%(text)s</a></td>
    <td>%(size)s</td>
</tr>
"""
