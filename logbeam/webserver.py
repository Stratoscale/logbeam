from twisted.internet import reactor
from twisted.web import resource

from twisted.web import server
from twisted.web import http

# based on http://twistedmatrix.com/pipermail/twisted-python/2003-July/005118.html


class UnauthorizedResource(resource.Resource):
    isLeaf = 1

    def __init__(self, realm):
        resource.Resource.__init__(self)
        self.realm = realm

    def render(self, request):
        request.setResponseCode(http.UNAUTHORIZED)
        request.setHeader('WWW-authenticate', 'basic realm="%s"' % self.realm)
        return 'Unauthorized'


class _HTTPBasicAuthWrapper(resource.Resource):
    realm = 'site'

    def __init__(self, resourceToWrap, username, password):
        resource.Resource.__init__(self)
        self._username = username
        self._password = password
        self._resourceToWrap = resourceToWrap

    def getChildWithDefault(self, path, request):
        if self._authenticateUser(request):
            return self._resourceToWrap.getChildWithDefault(path, request)
        else:
            return self._unauthorized()

    def render(self, request):
        if self._authenticateUser(request):
            return self._resourceToWrap.render(request)
        else:
            return self._unauthorized().render(request)

    def _authenticateUser(self, request):
        return request.getUser() == self._username and request.getPassword() == self._password

    def _unauthorized(self):
        return UnauthorizedResource(self.realm)


def listenSecured(root, port, username, password):
    rootAuth = _HTTPBasicAuthWrapper(root, username, password)
    reactor.listenTCP(port, server.Site(rootAuth))


def listenUnsecured(root, port):
    reactor.listenTCP(port, server.Site(root))
