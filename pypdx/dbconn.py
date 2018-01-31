#!/usr/bin/python3
from __future__ import absolute_import, print_function, unicode_literals
import os
import sys
import re

class DBconn:
    
    def __init__(self,dsn,dbtype='sqlite3',debug=False):
        """
        accepted options for dbtype: sqlite3 and pg (for postgres)
        """
        self.hdr  = "DBconn: "
        self.debug = debug
        self.dbtype = dbtype
        self.noclose = False
        self.dsn = dsn
        self.conn = None
        
        try:
            if dbtype == 'sqlite3':
                import sqlite3 as dbmodule
                self.conn = dbmodule.connect(dsn)
                self.conn.row_factory = dbmodule.Row
            elif dbtype == 'pg':
                import psycopg2 as dbmodule
                import psycopg2.extras
                self.conn = dbmodule.connect(dsn, cursor_factory=psycopg2.extras.DictCursor)
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
        self.dsn = re.sub( r"password\s*=\s*'(.*)'", "password='XXXXX'", self.dsn)
        
        # need to turn on foreign key explicitly for sqlite3!
        if dbtype == 'sqlite3':
            try:
                cur = self.conn.cursor()
                cur.execute("pragma foreign_keys = ON")
                cur.close()
            except self.dbmodule.Error as e:
                print("! Failed to turn on foreign key support!")
                
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

    """
    # remove this for now; too much trouble reconciling this with flask
    def __del__(self):
        if self.debug:
            print(self.hdr,"closing database connection %s (auto2)" % self.dsn)
            self.close()
        return
    
    def __exit__(self,exc_type,exc_value,traceback):
        if self.debug:
            print(self.hdr,"closing database connection %s (auto1)" % self.dsn)
            self.close()
        return
    """
    
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
        err = False
        try:
            c.execute("delete from partsmaster")
            c.execute("delete from bom")
            c.execute("delete from attachment")
            c.execute("delete from approvedmfg")
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
            
            c.close()
            self.conn.rollback()
            return msg
                
        self.conn.commit()
        return "ok"
    
