#!/usr/bin/python3
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os
import xmltodict
import json
import dateutil.parser
import psycopg2

cdir = os.path.dirname( os.path.realpath(__file__) )
sys.path.insert(0, cdir+"/.")

import dbconn

# ===================================================================================
class PDX:
    def __init__(self,pdxfile, dns, dbtype='sqlite3', debug=False):
        self.hdr = "PDX: "
        self.debug = debug
        self.dns   = dns
        
        # read into string then dump into object
        with open(pdxfile,'r') as myfile:
            xmldata = myfile.read()
        
        bomtree = self.bomtree = xmltodict.parse(xmldata)
        if not 'ProductDataeXchangePackage' in bomtree:
            print(self.hdr,"!!!! ERROR: XML file does not have ProductDataeXchangePackage")
            sys.exit()
        
        self.bomroot = bomtree['ProductDataeXchangePackage']
        
        # database connection
        self.dbtype = dbtype
        self.db = dbconn.DBconn(dns, dbtype=dbtype, debug=debug)
        
        return
    
    def __del__(self):
        # self.db.close() # shouldn't need this if it doesn't crash!
        return
    
    def dump(self,outputfile):
        if self.debug:
            print(self.hdr,"dump to file ",outputfile)
        
        with open(outputfile,"w") as fh:
            print(json.dumps( self.bomtree, indent=8, separators=(',',':') ), file=fh )
        
        return
    
    def fillparts(self):
        items = self.bomroot['Items']['Item']
        
        fields = [
                  "itemIdentifier",
                  "itemUniqueIdentifier",
                  "globalLifeCyclePhaseCode",
                  "globalLifeCyclePhaseCodeOther",
                  "globalProductTypeCode",
                  "itemClassification",
                  "revisionIdentifier",
                  "versionIdentifer",
                  "proprietaryProductFamily",
                  "category",
                  "globalProductUnitOfMeasureCode",
                  "makeBuy",
                  "makeBuyOther",
                  "minimumShippableRevision",
                  "revisionReleasedDate",
                  "revisionIncorporatedDate",
                  "isSerializationRequired",
                  "isCertificationRequired",
                  "ownerName",
                  "ownerContactUniqueIdentifier",
                  "isTopLevel",
                  "description",
                  ]
        
        cur = self.db.conn.cursor()
        if self.dbtype == 'sqlite3':
            sqltemp = "insert into partsmaster ("+(",".join(fields))+") values ("+(",".join( ["?" for x in fields] ) )+")"
        else:
            # postgres/psycopg2
            sqltemp = "insert into partsmaster ("+(",".join([('"%s"' % x) for x in fields]))+") values ("+(",".join( ['%s' for x in fields] ) )+")"
        
        if self.debug:
            print(self.hdr,"Template: ",sqltemp)
        
        values = {}
        count = 0
        for item in items:
            if self.debug:
                print(self.hdr,"-",item['@description'])
            vlist = []
            for field in fields:
                if ('@'+field in item):
                    val = item['@'+field]
                    # timestamps: use the date-time string in all cases
                    
                    # boolean
                    if field[:2] == 'is':
                        if self.dbtype == 'sqlite3':
                            val = 1 if val == 'Yes' else 0
                        else:
                            val = 'True' if val == 'Yes' else 'False'
                else:
                    # val = 'NULL'
                    val = None
                vlist.append( val )
            
            # print(self.hdr," values: ",vlist)
            try:
                cur.execute(sqltemp, tuple(vlist))
            except psycopg2.Error as e:
                print(e.pgerror)
                print(e.diag.message_detail)
                sys.exit()
            
            count += 1
        
        cur.close()
        self.db.commit()
        if self.debug:
            print(self.hdr,"Total %d items" % count)
        
        return



# ==============================================================
if __name__ == '__main__':
    
    if len(sys.argv) < 3:
        print("USAGE: %s pdx-file.xml SQLite_file" % sys.argv[0])
        sys.exit()
    
    pdxfile = sys.argv[1]
    dbfile  = sys.argv[2]

    # mypdx = PDX(pdxfile,dbfile,debug=False)
    # mypdx.dump("pdx-dump.json")
    # mypdx.fillparts()
    
    dns = "dbname='coherent' user='dba' host='localhost' port=5432 password='fibrolasero'"
    mypdx2 = PDX(pdxfile,dns,dbtype='pg',debug=True)
    mypdx2.fillparts()
    
    print("MAIN: operation completed")

