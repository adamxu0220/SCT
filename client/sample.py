# -*- coding: utf-8 -*-
#
# Name: Pyton Twisted binary file transfer demo (client)
# Description: Simple demo which shows how you can transfer binary files using
# the Twisted framework.
#
# Keep in mind that this is only a demo and there are many possible scenarios
# where program can break.
#
# Author: Tomaž Muraus (http://www.tomaz-muraus.info)
# License: GPL

# Requirements:
# - Python >= 2.5
# - Twisted (http://twistedmatrix.com/)

import os, gzip
import tarfile
#os.mkdir('TestCase')
#tar = tarfile.open("testcase.tar.gz")
#tar.extract("TestCase")
#tar.close()
#tar = tarfile.open("mrvl_lib.tar.gz")
#tar.extract(os.path.join(os.getcwd(), "TestCase"))
#tar.close()
tar = tarfile.open("testcase.tar.gz")
tar.extractall(path = "Test")
casename = tar.members[0].name
print casename
tar.close()

tar = tarfile.open("testcase.tar.gz", "r:gz")
for tarinfo in tar:
    print tarinfo.name, "is", tarinfo.size, "bytes in size and is",
    if tarinfo.isreg():
        print "a regular file."
    elif tarinfo.isdir():
        print "a directory."
    else:
        print "something else."
tar.close()

tar = tarfile.open("sample.tar.gz")
tar.extractall(path = "Sample")
tar.close()

