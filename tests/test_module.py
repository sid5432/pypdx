#!/usr/bin/python3
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os
import sqlite3
cdir = os.path.dirname( os.path.realpath(__file__) )

sys.path.insert(0, cdir+"/..")

import pypdx

def test_module():
    
    dsn = ':memory:'
    xmlfile = os.path.join(cdir,"../pypdx/data/pdx-example.xml")
    
    mypdx = pypdx.PDX(xmlfile, dsn, debug=True)
    mypdx.removeall()
    mypdx.fillparts()
    
    assert(mypdx != None)
    
    cur = mypdx.db.conn.cursor()
    cur.execute("select count(*) from bom")
    
    bomcount = 0
    for row in cur:
        bomcount = row[0]
        
    cur.close()
    assert(bomcount == 108)

    cur = mypdx.db.conn.cursor()
    cur.execute("select count(*) as rcount from partsmaster")
    
    itemcount = 0
    for row in cur:
        itemcount = row['rcount']
        
    cur.close()
    assert(itemcount == 100)
    
    cur = mypdx.db.conn.cursor()
    cur.execute("delete from partsmaster")
    cur.close()
    
    # check if bom records are removed? (foreign key support)
    cur = mypdx.db.conn.cursor()
    cur.execute("select count(*) from bom")
    
    bomcount = 0
    for row in cur:
        bomcount = row[0]
        
    cur.close()
    assert(bomcount == 0)
    
    return

if __name__ == '__main__':
    
    test_module()
    
