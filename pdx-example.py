#!/usr/bin/python3
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os

cdir = os.path.dirname( os.path.realpath(__file__) )
sys.path.insert(0, cdir+"/..")

import pypdx

# ==============================================================
if __name__ == '__main__':
    
    if len(sys.argv) < 3:
        print("USAGE: %s pdx-file.xml SQLite_file [dump(=1|0)] [remove_all_first(=1|0)]" % sys.argv[0])
        sys.exit()
    
    pdxfile = sys.argv[1]
    dbfile  = sys.argv[2]
    
    if len(sys.argv) >= 4:
        dodump  = True if sys.argv[3]=='1' else False
    else:
        dodump = False

    if len(sys.argv) >= 5:
        removeall = True if sys.argv[4]=='1' else False
    else:
        removeall = False
    
    debug = True
    if dbfile == 'pg':
        dns = "dbname='pdx' user='pdxuser' host='localhost' port=5432"
        mypdx = pypdx.PDX(pdxfile,dns, dbtype='pg',debug=debug)
    else:
        mypdx = pypdx.PDX(pdxfile,dbfile,debug=debug)
    
    if dodump:
        mypdx.dump("pdx-dump.json")
    
    if removeall:
        doit = input("MAIN: removing *all* records first! Are you sure? (type yes or no)")
        if doit == 'yes':
            mypdx.removeall()
        else:
            print("MAIN: not removing old records")
    
    mypdx.fillparts()
    print("MAIN: operation completed")


