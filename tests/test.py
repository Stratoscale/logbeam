import unittest
import tempfile
import shutil
import os
import gzip
from tests import logbeamwrapper


class Test(unittest.TestCase):
    def setUp(self):
        self.playground = tempfile.mkdtemp()
        self.server = logbeamwrapper.FTPServer()
        self.frontend = logbeamwrapper.WebFrontend(self.server)

    def tearDown(self):
        self.frontend.cleanup()
        self.server.cleanup()
        shutil.rmtree(self.playground, ignore_errors=True)

    def writeFile(self, path, contents):
        fullPath = os.path.join(self.playground, path)
        if not os.path.isdir(os.path.dirname(fullPath)):
            os.makedirs(os.path.dirname(fullPath))
        with open(fullPath, "wb") as f:
            f.write(contents)

    def assertFileAtServer(self, path, expectedContents):
        fullPath = os.path.join(self.server.directory, path)
        with open(fullPath, "rb") as f:
            contents = f.read()
        self.assertEquals(contents, expectedContents)

    def assertFileCompressedAtServer(self, path, expectedContents):
        fullPath = os.path.join(self.server.directory, path)
        with gzip.open(fullPath + ".gz", "rb") as f:
            contents = f.read()
        self.assertEquals(contents, expectedContents)

    def test_NullUploadADirectory(self):
        self.writeFile("var/log/dmesg", "something")
        self.writeFile("var/log/myself.log", "something else")
        client = logbeamwrapper.Null(self.playground)
        client.upload("var/log")
        self.assertEquals(self.server.fileCount(), 0)

    def test_NullUploadAFile(self):
        self.writeFile("var/log/dmesg", "something")
        client = logbeamwrapper.Null(self.playground)
        client.upload("var/log/dmesg")
        self.assertEquals(self.server.fileCount(), 0)

    def test_UploadADirectory(self):
        self.writeFile("var/log/dmesg", "something")
        self.writeFile("var/log/myself.log", "something else")
        client = logbeamwrapper.FTP(self.playground, self.server, compressed=False)
        client.upload("var/log", under="var_log")
        self.assertEquals(self.server.fileCount(), 3)
        self.assertFileAtServer("var_log/dmesg", "something")
        self.assertFileAtServer("var_log/myself.log", "something else")

    def test_UploadACompressedDirectory(self):
        self.writeFile("var/log/dmesg", "something")
        self.writeFile("var/log/myself.log", "something else")
        client = logbeamwrapper.FTP(self.playground, self.server, compressed=True)
        client.upload("var/log", under="var_log")
        self.assertEquals(self.server.fileCount(), 3)
        self.assertFileCompressedAtServer("var_log/dmesg", "something")
        self.assertFileCompressedAtServer("var_log/myself.log", "something else")

    def test_UploadACompressedDirectory_With100Files(self):
        for i in xrange(100):
            self.writeFile("var/log/file%d" % i, "something")
        client = logbeamwrapper.FTP(self.playground, self.server, compressed=True)
        client.upload("var/log")
        self.assertEquals(self.server.fileCount(), 100)
        for i in xrange(100):
            self.assertFileCompressedAtServer("file%d" % i, "something")

    def test_UploadACompressedDirectory_HasBaseDirectory(self):
        self.writeFile("var/log/dmesg", "something")
        client = logbeamwrapper.FTP(
            self.playground, self.server, compressed=True, baseDir="project/hash/build")
        client.upload("var/log", under="var_log")
        self.assertEquals(self.server.fileCount(), 5)
        self.assertFileCompressedAtServer("project/hash/build/var_log/dmesg", "something")

    def test_UploadAFile_WithUnder(self):
        self.writeFile("var/log/dmesg", "something")
        client = logbeamwrapper.FTP(
            self.playground, self.server, compressed=True, baseDir="project/hash/build")
        client.upload("var/log/dmesg", under="var_log")
        self.assertEquals(self.server.fileCount(), 5)
        self.assertFileCompressedAtServer("project/hash/build/var_log/dmesg", "something")

    def test_WebFrontend_FetchNonCompressedFile(self):
        self.writeFile("var/log/dmesg", "something")
        client = logbeamwrapper.FTP(self.playground, self.server)
        client.upload("var/log/dmesg")
        self.assertEquals(self.server.fileCount(), 1)
        self.assertFileAtServer("dmesg", "something")
        self.assertEquals(self.frontend.fetch("dmesg"), "something")
        self.assertIn(">dmesg<", self.frontend.fetch(""))
        self.frontend.fetch("")

    def test_WebFrontend_FetchCompressedFile(self):
        self.writeFile("var/log/dmesg", "something")
        client = logbeamwrapper.FTP(self.playground, self.server, compressed=True)
        client.upload("var/log/dmesg")
        self.assertEquals(self.server.fileCount(), 1)
        self.assertFileCompressedAtServer("dmesg", "something")
        self.assertEquals(self.frontend.fetch("dmesg"), "something")
        self.assertIn(">dmesg<", self.frontend.fetch(""))


if __name__ == '__main__':
    unittest.main()
