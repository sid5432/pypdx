#!/usr/bin/python3
from __future__ import absolute_import, print_function, unicode_literals
import os
import sys
import re

class DBconn:
    
    def __init__(self,dns,dbtype='sqlite3',debug=False):
        """
        accepted options for dbtype: sqlite3 and pg (for postgres)
        """
        self.hdr  = "DBconn: "
        self.debug = debug
        self.dbtype = dbtype
        self.noclose = False
        self.dns = dns
        self.conn = None
        
        try:
            if dbtype == 'sqlite3':
                import sqlite3 as dbmodule
                self.conn = dbmodule.connect(dns)
                self.conn.row_factory = dbmodule.Row
            elif dbtype == 'pg':
                import psycopg2 as dbmodule
                import psycopg2.extras
                self.conn = dbmodule.connect(dns, cursor_factory=psycopg2.extras.DictCursor)
            else:
                print("Unrecognized DB type %s" % dbtype);
                self.noclose = True
                sys.exit()
        except:
            print("Cannot connect to database");
            sys.exit()
        
        self.dbmodule = dbmodule
        self.debug = debug
        # hide password; not used anywhere else
        self.dns = re.sub( r"password\s*=\s*'(.*)'", "password='XXXXX'", self.dns)
        
        self.create_tables()
        
        return
    
    def create_tables(self):
        """
        create tables in database (if they don't already exist)
        """
        cdir = os.path.dirname( os.path.realpath(__file__) )
        
        # table schemas -------------------------------------
        schema = os.path.join(cdir,"data","partsmaster.sql")
        if self.debug:
            print(self.hdr,"parts master schema is ",schema)
        
        self.populate(schema)
        
        schema = os.path.join(cdir,"data","approvedmfg.sql")
        if self.debug:
            print(self.hdr,"approved mfg list schema is ",schema)
        
        self.populate(schema)
        
        schema = os.path.join(cdir,"data","attachment.sql")
        if self.debug:
            print(self.hdr,"attachment schema is ",schema)
        
        self.populate(schema)

        schema = os.path.join(cdir,"data","bom.sql")
        if self.debug:
            print(self.hdr,"bill of materials schema is ",schema)
        
        self.populate(schema)
        
        return
        
    def __enter__(self):
        return self
    
    def __del__(self):
        if self.debug:
            print(self.hdr,"closing database connection %s (auto2)" % self.dns)
        self.close()
        return
    
    def __exit__(self,exc_type,exc_value,traceback):
        if self.debug:
            print(self.hdr,"closing database connection %s (auto1)" % self.dns)
        self.close()
        return
    
    def commit(self):
        self.conn.commit()
        return
        
    def close(self):
        if not self.noclose and self.conn != None:
            self.conn.close()
        return
    
    def populate(self,schema):
        
        with open(schema) as fh:
            mstr = fh.read()
        
        # NOTE: dict cursor use
        # dict_cur = self.conn( cursor_factory=psycopg2.extras.DictCursor )
        c = self.conn.cursor()
        c.execute(mstr)
        c.close()
        self.conn.commit()
        return
    
    def removeall(self):
        c = self.conn.cursor()
        c.execute("delete from partsmaster")
        c.execute("delete from bom")
        c.execute("delete from attachment")
        c.execute("delete from approvedmfg")
        c.close()
        return
    
