from twisted.cred.portal import Portal
from twisted.cred import checkers
from twisted.internet import reactor

from zope.interface import implements
from twisted.cred.portal import IRealm
from twisted.web.resource import IResource
from twisted.web.guard import HTTPAuthSessionWrapper, DigestCredentialFactory
from twisted.web import server


class _PublicHTMLRealm(object):
    implements(IRealm)

    def __init__(self, root):
        self._root = root

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IResource in interfaces:
            return (IResource, self._root, lambda: None)
        raise NotImplementedError()


def listenSecured(root, port, username, password):
    checker = checkers.InMemoryUsernamePasswordDatabaseDontUse(** {username: password})
    portal = Portal(_PublicHTMLRealm(root), [checker])
    credentialFactory = DigestCredentialFactory("md5", "localhost:8080")
    rootAuth = HTTPAuthSessionWrapper(portal, [credentialFactory])
    reactor.listenTCP(port, server.Site(rootAuth))


def listenUnsecured(root, port):
    reactor.listenTCP(port, server.Site(root))
