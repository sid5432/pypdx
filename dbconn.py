#!/usr/bin/python3
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
        
        try:
            if dbtype == 'sqlite3':
                import sqlite3
                self.conn = sqlite3.connect(dns)
            elif dbtype == 'pg':
                import psycopg2
                import psycopg2.extras
                self.conn = psycopg2.connect(dns, cursor_factory=psycopg2.extras.DictCursor)
            else:
                print("Unrecognized DB type %s" % dbtype);
                self.noclose = True
                sys.exit()
        except:
            print("Cannot connect to database");
            sys.exit()

        self.debug = debug
        # hide password; not used anywhere else
        self.dns = re.sub( r"password\s*=\s*'(.*)'", "password='XXXXX'", self.dns)
        
        cdir = os.path.dirname( os.path.realpath(__file__) )
        
        # table schemas -------------------------------------
        schema1 = os.path.join(cdir,"lib","parts.sql")
        if debug:
            print(self.hdr,"parts master schema is ",schema1)
            print(self.hdr,"create partsmaster table")
        
        self.populate(schema1)
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
        if not self.noclose:
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
    
    def clearall(self):
        c = self.conn.cursor()
        c.execute("delete * from partsmaster")
        c.close()
        return
    
# -----------------------------------------
if __name__ == '__main__':
    
    # with DBconn(filename) as dbconn:
    #    dbconn.populate()
    
    print("Test SQLite3:")
    dns = "mypdx.db3"
    dbconn = DBconn(dns,debug=True)
    
    print("\n")
    print("Test postgres:")
    
    dns2 = "dbname='coherent' user='dba' host='localhost' port=5432 password='fibrolasero'"
    dbconn2 = DBconn(dns2,dbtype='pg',debug=True)
        
    print("MAIN: all done!")
