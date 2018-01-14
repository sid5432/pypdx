#!/usr/bin/python3
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os
cdir = os.path.dirname( os.path.realpath(__file__) )

sys.path.insert(0, cdir+"/..")

import pypdx

def test_module():
    
    dns = ':memory:'
    xmlfile = os.path.join(cdir,"../lib/pdx-example.xml")
    
    mypdx = pypdx.PDX(xmlfile, dns, debug=True)
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
    cur.execute("select count(*) from partsmaster")
    
    itemcount = 0
    for row in cur:
        itemcount = row[0]
        
    cur.close()
    assert(itemcount == 100)

    return

if __name__ == '__main__':
    
    test_module()
    
