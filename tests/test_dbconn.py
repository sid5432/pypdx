#!/usr/bin/python3
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os
cdir = os.path.dirname( os.path.realpath(__file__) )

sys.path.insert(0, cdir+"/..")

from pypdx import dbconn

def test_dbconn():
    
    print("Test SQLite3:")
    dns = ':memory:'
    db = dbconn.DBconn(dns,debug=True)
    assert( db != None )
    
    print("\n")
    print("Test postgres:")
    
    dns2 = "dbname='pdx' user='pdxuser' host='localhost' port=5432"
    db2 = dbconn.DBconn(dns2,dbtype='pg',debug=True)
    assert( db2 != None )
    
    print("MAIN: all done!")
