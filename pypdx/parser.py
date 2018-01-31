#!/usr/bin/python3
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os
import xmltodict
import json

from . import dbconn

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
    def __init__(self,pdxfile, dsn, dbtype='sqlite3', debug=False):
        self.hdr = "PDX: "
        self.debug = debug
        self.dsn   = dsn
        
        # read into string then dump into object
        with open(pdxfile,'r') as myfile:
            xmldata = myfile.read()
        
        bomtree = self.bomtree = xmltodict.parse(xmldata)
        if not 'ProductDataeXchangePackage' in bomtree:
            print(self.hdr,"!!!! ERROR: XML file does not have ProductDataeXchangePackage")
            self.db = None
            return
        
        self.bomroot = bomtree['ProductDataeXchangePackage']
        
        # database connection
        self.dbtype = dbtype
        self.db = dbconn.DBconn(dsn, dbtype=dbtype, debug=debug)
        
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
        status = self.db.removeall()
        
        return status
    
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
            err = False
            try:
                cur.execute(sqltemp, tuple(vlist))
            except self.db.dbmodule.Error as e:
                err = True
                errmsg = e
            
            if err:
                if self.dbtype == 'sqlite3':
                    print("ERROR: ",errmsg)
                    msg = errmsg
                else:
                    print(errmsg.pgerror)
                    print(errmsg.diag.message_detail)
                    msg = errmsg.pgerror + "; " + errmsg.diag.message_detail
                
                cur.close()
                self.db.conn.rollback()
                return msg
            
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
            err = False
            try:
                cur.execute(sqltemp, record)
            except self.db.dbmodule.Error as e:
                err = True
                errmsg = e
            
            if err:
                if self.dbtype == 'sqlite3':
                    print("ERROR: ",errmsg)
                    msg = errmsg
                else:
                    print(errmsg.pgerror)
                    print(errmsg.diag.message_detail)
                    msg = errmsg.pgerror + "; " + errmsg.diag.message_detail
                
                cur.close()
                self.db.conn.rollback()
                return msg
        
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
            err = False
            try:
                cur.execute(sqltemp, record)
            except self.db.dbmodule.Error as e:
                err = True
                errmsg = e
            
            if err:
                if self.dbtype == 'sqlite3':
                    print("ERROR: ",errmsg)
                    msg = errmsg
                else:
                    print(errmsg.pgerror)
                    print(errmsg.diag.message_detail)
                    msg = errmsg.pgerror + "; " + errmsg.diag.message_detail
                
                cur.close()
                self.db.conn.rollback()
                return msg
        
        
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
            err = False
            try:
                cur.execute(sqltemp, record)
            except self.db.dbmodule.Error as e:
                err = True
                errmsg = e
            
            if err:
                if self.dbtype == 'sqlite3':
                    print("ERROR: ",errmsg)
                    msg = errmsg
                else:
                    print(errmsg.pgerror)
                    print(errmsg.diag.message_detail)
                    msg = errmsg.pgerror + "; " + errmsg.diag.message_detail
                
                cur.close()
                self.db.conn.rollback()
                return msg
        
        cur.close()
        self.db.commit()

        # --------- final tally --------------------------------------
        if self.debug:
            print(self.hdr,"Total %d items" % count)
            print(self.hdr,"Total %d BOM links" % len(self.bomsqllist) )
            print(self.hdr,"Total %d Attachment items" % len(self.attsqllist) )
            print(self.hdr,"Total %d Approved MFG items" % len(self.apmsqllist) )
        
        return 'ok'
    
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

