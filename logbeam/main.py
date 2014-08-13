import argparse
import logging
import time
import os
from logbeam import upload
from logbeam import config
from logbeam import ftpserver

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="cmd")
uploadCmd = subparsers.add_parser(
    "upload",
    help="upload logs")
uploadCmd.add_argument(
    "paths", nargs="+",
    help="directories or files to beam")
uploadCmd.add_argument("--username", help="override username from config file")
uploadCmd.add_argument("--password", help="override password from config file")
uploadCmd.add_argument("--hostname", help="override hostname from config file")
uploadCmd.add_argument("--under", help="put under a directory")
ftpserverCmd = subparsers.add_parser(
    'ftpserver',
    help="Start a ftp server endpoint for beaming in logs")
ftpserverCmd.add_argument("--username", default="logs")
ftpserverCmd.add_argument("--password", default="logs")
ftpserverCmd.add_argument("--port", type=int, default=0)
ftpserverCmd.add_argument("--fileToWritePortNumberTo")
ftpserverCmd.add_argument("--directory", required=True)
webfrontendCmd = subparsers.add_parser(
    'webfrontend',
    help="Start a frontend webserver with a ftp backend "
    "that shows an uncompressed files, but send them GZIPped "
    "encoded")
webfrontendCmd.add_argument("--port", type=int, required=True)
webfrontendCmd.add_argument("--basicAuthPassword")
args = parser.parse_args()

config.load()

if args.cmd == "upload":
    instance = upload.Upload()
    instance.upload(args.paths, under=args.under)
    instance.close()
elif args.cmd == "ftpserver":
    server = ftpserver.FTPServer(
        directory=args.directory,
        username=args.username, password=args.password,
        port=args.port, fileToWritePortNumberTo=args.fileToWritePortNumberTo)
    while True:
        time.sleep(10000000)
elif args.cmd == "webfrontend":
    raise AssertionError("Not implemented")
else:
    assert False, "command mismatch"
