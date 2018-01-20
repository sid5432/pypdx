#!/usr/bin/python3
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os
import re

if __name__ == '__main__':
    cdir = os.path.dirname( os.path.realpath(__file__) )
    sys.path.insert(0, cdir+"/..")

import pypdx

def main():
    if len(sys.argv) < 3:
        print("USAGE: %s pdx-file.xml dsn [dump [remove_all_first]]" % sys.argv[0])
        print("     - pdx-file.xml: this is the PDX XML file")
        print("     - dsn: can be a SQLite3 file (the program will create one if it does not exist; use the extension .sqlite3")
        print("          : or it can be the dsn connection string for a PostgreSQL database")
        print("          : if dsn is 'pg', the default database 'pdx' on localhost (port 5432) and username 'pdxuser' will be used")
        print("     - dump: 1 or 0; to dump to a JSON file pdx-dump.json (optional)")
        print("     - remove_all: 1 or 0; remove all records from the tables first (optional);")
        print("     -           : WARNING: this will delete *all* existing parts, BOM, etc., records from the database")
        sys.exit()
    
    pdxfile = sys.argv[1]
    dsn     = sys.argv[2]
    
    if len(sys.argv) >= 4:
        dodump  = True if sys.argv[3]=='1' else False
    else:
        dodump = False

    if len(sys.argv) >= 5:
        removeall = True if sys.argv[4]=='1' else False
    else:
        removeall = False
    
    debug = True
    try:
        if dsn == 'pg':
            dsn = "dbname='pdx' user='pdxuser' host='localhost' port=5432"
            mypdx = pypdx.PDX(pdxfile,dsn, dbtype='pg',debug=debug)
        elif dsn[-8:] == '.sqlite3':
            mypdx = pypdx.PDX(pdxfile,dsn,debug=debug)
        elif re.match('dbname\s*=', dsn) != None:
            mypdx = pypdx.PDX(pdxfile,dsn, dbtype='pg',debug=debug)
        else:
            print("Unrecognized dsn %s" % dsn)
            sys.exit()
        
    except IOError as e:
        print("Connection Failed ",e)
        sys.exit(1)
    
    if dodump:
        mypdx.dump("pdx-dump.json")
    
    if removeall:
        if sys.version_info[0] < 3:
            doit = raw_input("MAIN: removing *all* records first! Are you sure? (type yes or no)")
        else:
            doit = input("MAIN: removing *all* records first! Are you sure? (type yes or no)")
        
        if doit == 'yes':
            mypdx.removeall()
        else:
            print("MAIN: not removing old records")
    
    status = mypdx.fillparts()
    if status == 'ok':
        print("MAIN: operation completed")
    else:
        print("MAIN: fillparts() failed")
        sys.exit(1)
    
    sys.exit(0)
    
# ==============================================
if __name__ == '__main__':
    main()

