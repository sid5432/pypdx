#!/usr/bin/python3
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os
import xmltodict
import json
import psycopg2

from pypdx import dbconn

bomfields = [
             "revisionIdentifier",
             "isSerializationRequired",
             "globalBillOfMaterialTypeCode",
             "globalBillOfMaterialTypeCodeOther",
             "notes",
             "billOfMaterialItemIdentifier",
             "billOfMaterialItemUniqueIdentifier",
             "itemQuantity",
             "globalProductQuantityTypeCode",
             "globalProductQuantityTypeCodeOther",
             "description",
             "proprietarySequenceIdentifier",
            ]

attfields = [
             "referenceName",
             "universalResourceIdentifier",
             "fileIdentifier",
             "versionIdentifer",
             "fileSize",
             "checkSum",
             "isFileIn",
             "description",
             "globalMimeTypeQualifierCode",
             "attachmentModificationDate",
            ]

apmfields = [
             "manufacturerPartIdentifier",
             "manufacturerPartUniqueIdentifier",
             "manufacturerContactUniqueIdentifier",
             "globalManufacturerPartStatusCode",
             "globalManufacturerPartStatusCodeOther",
             "globalPreferredStatusCode",
             "description",
             "manufacturedBy",
            ]

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
    
    # ---------------------------------------------------------------------------------------
    def dump(self,outputfile):
        if self.debug:
            print(self.hdr,"dump to file ",outputfile)
        
        with open(outputfile,"w") as fh:
            print(json.dumps( self.bomtree, indent=8, separators=(',',':') ), file=fh )
        
        return
    
    # ---------------------------------------------------------------------------------------
    def removeall(self):
        self.db.removeall()
        
        return
    
    # ---------------------------------------------------------------------------------------
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
            sqltemp = "insert into partsmaster ("+(",".join(fields))+") values ("+(",".join( ['%s' for x in fields] ) )+")"
            
        # print(self.hdr,"Template: ",sqltemp)
        
        self.bomsqllist = [] # list of tuples to enter in bom table; initialize empty
        self.attsqllist = [] # list of tuples to enter in attachment table; initialize empty
        self.apmsqllist = [] # list of tuples to enter in approvedmfg table; initialize empty
        
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
            
            # .......... look for BOM ..............
            if 'BillOfMaterial' in item.keys():
                self.process_bom( item )
                
            # .......... look for Attachment ..............
            if 'Attachments' in item.keys():
                self.process_attachment( item )

            # .......... look for Approved MFG ..............
            if 'ApprovedManufacturerList' in item.keys():
                self.process_appmfg( item )

            count += 1

        cur.close()
        self.db.commit()
        
        # ------ process BOM list -----------------------------------
        cur = self.db.conn.cursor()
        if self.dbtype == 'sqlite3':
            sqltemp = "insert into bom (itemUniqueIdentifier,"+(",".join(bomfields))+") values (?,"+(",".join( ["?" for x in bomfields] ) )+")"
        else:
            # postgres/psycopg2
            # sqltemp = "insert into partsmaster ("+(",".join([('"%s"' % x) for x in fields]))+") values ("+(",".join( ['%s' for x in fields] ) )+")"
            sqltemp = "insert into bom (itemUniqueIdentifier,"+(",".join(bomfields))+") values (%s,"+(",".join( ['%s' for x in bomfields] ) )+")"
        
        for record in self.bomsqllist:
            try:
                cur.execute(sqltemp, record)
            except psycopg2.Error as e:
                print(e.pgerror)
                print(e.diag.message_detail)
                sys.exit()
                
        cur.close()
        self.db.commit()
        
        # ------ process Attachment list -----------------------------------
        cur = self.db.conn.cursor()
        if self.dbtype == 'sqlite3':
            sqltemp = "insert into attachment (itemUniqueIdentifier,"+(",".join(attfields))+") values (?,"+(",".join( ["?" for x in attfields] ) )+")"
        else:
            # postgres/psycopg2
            sqltemp = "insert into attachment (itemUniqueIdentifier,"+(",".join(attfields))+") values (%s,"+(",".join( ['%s' for x in attfields] ) )+")"
        
        for record in self.attsqllist:
            try:
                cur.execute(sqltemp, record)
            except psycopg2.Error as e:
                print(e.pgerror)
                print(e.diag.message_detail)
                sys.exit()
        
        cur.close()
        self.db.commit()
        
        # ------ process Approved MFG list -----------------------------------
        cur = self.db.conn.cursor()
        if self.dbtype == 'sqlite3':
            sqltemp = "insert into approvedmfg (itemUniqueIdentifier,"+(",".join(apmfields))+") values (?,"+(",".join( ["?" for x in apmfields] ) )+")"
        else:
            # postgres/psycopg2
            sqltemp = "insert into approvedmfg (itemUniqueIdentifier,"+(",".join(apmfields))+") values (%s,"+(",".join( ['%s' for x in apmfields] ) )+")"
        
        for record in self.apmsqllist:
            try:
                cur.execute(sqltemp, record)
            except psycopg2.Error as e:
                print(e.pgerror)
                print(e.diag.message_detail)
                sys.exit()
        
        cur.close()
        self.db.commit()

        # --------- final tally --------------------------------------
        if self.debug:
            print(self.hdr,"Total %d items" % count)
            print(self.hdr,"Total %d BOM links" % len(self.bomsqllist) )
            print(self.hdr,"Total %d Attachment items" % len(self.attsqllist) )
            print(self.hdr,"Total %d Approved MFG items" % len(self.apmsqllist) )
        
        return
    
    # =========================================================================================
    def process_bom(self, item):
        # print("item: ",item['@description'])
        parentid = item['@itemUniqueIdentifier']
        
        # sanity check
        if not ('BillOfMaterialItem' in item['BillOfMaterial'].keys()):
            print("!!!",item['@description']," missing BillOfMaterialItem")
            return
        
        xref = item['BillOfMaterial']['BillOfMaterialItem']
        if isinstance(xref,list):
            self.process_bom_list(parentid, xref)
        elif isinstance(xref,dict):
            self.process_bom_item(parentid, xref)
        else:
            print("!!!Don't know how to handle BOM ",type(xref)," type")
            return
        
        return
    
    # ---------------------------------------------------------------------------------------
    def process_bom_list(self, parentid, blist):
        for bitem in blist:
            self.process_bom_item(parentid,bitem)
        
        return
    # ---------------------------------------------------------------------------------------
    def process_bom_item(self, parentid, bitem):
        itemrecord = [parentid]
        
        for field in bomfields:
            field = '@'+field
            if field in bitem:
                val = bitem[field]
                if field[:2] == 'is':
                    if self.dbtype == 'sqlite3':
                        val = 1 if val == 'Yes' else 0
                    else:
                        val = 'True' if val == 'Yes' else 'False'
                elif field == '@itemQuantity':
                    val = float(val)
            else:
                val = None
            
            itemrecord.append( val )
        
        self.bomsqllist.append( tuple(itemrecord) )
        # print("...",tuple(itemrecord))
        return

    # =========================================================================================
    def process_attachment(self, item):
        # print("item: ",item['@description'])
        parentid = item['@itemUniqueIdentifier']
        
        # sanity check
        if not ('Attachment' in item['Attachments'].keys()):
            print("!!!",item['@description']," missing Attachment")
            return
        
        xref = item['Attachments']['Attachment']
        if isinstance(xref,list):
            self.process_att_list(parentid, xref)
        elif isinstance(xref,dict):
            self.process_att_item(parentid, xref)
        else:
            print("!!!Don't know how to handle Attachment ",type(xref)," type")
            return
        
        return
    
    # ---------------------------------------------------------------------------------------
    def process_att_list(self, parentid, blist):
        for bitem in blist:
            self.process_att_item(parentid,bitem)
        
        return
    # ---------------------------------------------------------------------------------------
    def process_att_item(self, parentid, bitem):
        itemrecord = [parentid]
        
        for field in attfields:
            field = '@'+field
            if field in bitem:
                val = bitem[field]
                if field[:2] == 'is':
                    if self.dbtype == 'sqlite3':
                        val = 1 if val == 'Yes' else 0
                    else:
                        val = 'True' if val == 'Yes' else 'False'
                elif field == '@fileSize':
                    val = int(val)
            else:
                val = None
            
            itemrecord.append( val )
        
        self.attsqllist.append( tuple(itemrecord) )
        # print("...",tuple(itemrecord))
        return
    
    # =========================================================================================
    def process_appmfg(self, item):
        # print("item: ",item['@description'])
        parentid = item['@itemUniqueIdentifier']
        
        # sanity check
        if not ('ApprovedManufacturerListItem' in item['ApprovedManufacturerList'].keys()):
            print("!!!",item['@description']," missing ApprovedManufacturerList")
            return
        
        xref = item['ApprovedManufacturerList']['ApprovedManufacturerListItem']
        if isinstance(xref,list):
            self.process_apm_list(parentid, xref)
        elif isinstance(xref,dict):
            self.process_apm_item(parentid, xref)
        else:
            print("!!!Don't know how to handle ApprovedManufacturerListItem ",type(xref)," type")
            return
        
        return
    
    # ---------------------------------------------------------------------------------------
    def process_apm_list(self, parentid, blist):
        for bitem in blist:
            self.process_apm_item(parentid,bitem)
        
        return
    # ---------------------------------------------------------------------------------------
    def process_apm_item(self, parentid, bitem):
        itemrecord = [parentid]
        
        for field in apmfields:
            field = '@'+field
            if field in bitem:
                val = bitem[field]
            else:
                val = None
            
            itemrecord.append( val )
        
        self.apmsqllist.append( tuple(itemrecord) )
        # print("...",tuple(itemrecord))
        return

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
        # dns = "dbname='pdx' user='pdxuser' host='localhost' port=5432 password='billofmaterial'"
        dns = "dbname='pdx' user='pdxuser' host='localhost' port=5432"
        mypdx = PDX(pdxfile,dns, dbtype='pg',debug=debug)
    else:
        mypdx = PDX(pdxfile,dbfile,debug=debug)
    
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

