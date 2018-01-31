pypdx
=====

*A Simple parser for PDX (Product Data eXchange) XML files*

Introduction
------------

From `the Wikipedia article on PDX <https://en.wikipedia.org/wiki/PDX_(IPC-257X)>`__: “the PDX (Product
Data eXchange) standard for manufacturing is a multi-part standard,
represented by the IPC 2570 series of specifications.”

As the name implies, it is a standard for exchanging product definition
between companies or organizations, and can include bill of material
(BOM), approved manufacturer list, drawings, documents, etc.; pretty
much anything can be included if desired.

In simple terms, a \*.pdx file (usually exported from Agile/Oracle) is
really just a ZIP file that contains all the files (“attachments”)
associated with the product (assembly), plus a special XML file called
**pdx.xml**. This XML file contains the particulars of the various Items
and their properties/attributes, the relationship between the Items,
which forms the bill-of-materials (BOM), and also information about the
various files that are inside the PDX/ZIP file.

The DTD of this XML file (identified as “DTD 2571 200111”) can be found
on the `IPC website <http://www.ipc.org/4.0_Knowledge/4.1_Standards/IPC-25xx-files/2571.zip>`__.
Free PDX viewers are available, one of the most popular being PDXViewer
from `PDXplorer <http://www.pdxplorer.com/index.html>`__.

Since the \*.pdx file is simply a ZIP file, it is easy to extract all
the attachments (documents, schematics, drawings, etc.) from the ZIP
file, and there are several ways one can view XML files. However, trying
to make sense of the assembly from a generic XML viewer is not really
feasible, and although there are specialized free (and non-free)
viewers, there are times when you might want to extract the data for
your own use. To this end I have written a simple PDX XML file parser,
pypdx (written in Python), as presented here.

The *pypdx* program can be used as a Python module, but also as a
command-line stand-alone program that is more or less ready to use. Be
warned that it does. It does *not* implement all the elements defined in
the PDX standard, but only the parts that happen to be of interest to
*me* at the moment, so don’t be surprised if it does not have the
features you are looking for. What it does extract are the **Item**\ s,
the **ApprovedManufacturerList**, the **BillOfMaterial**, and the
**Attachments**. The main purpose of the program is to extract this data
from the XML file, and organize them by saving them into a relational
database: in this case either a `SQLite3 <https://www.sqlite.org/>`__
database or a `PostgreSQL  <https://www.postgresql.org/>`__ database.
What you do after the data is stuffed into a relational database is up
to you!

Installation and Usage
----------------------

To install the module and program, run

::

    pip install pypdx

This should create an executable pypdx. The usage is as follows:

::

   USAGE: pypdx pdx-file.xml dsn [dump [remove_all_first]]
        - pdx-file.xml: this is the PDX XML file
        - dsn: can be a SQLite3 file (the program will create one if it does not exist; use the extension .sqlite3
             : or it can be the dsn connection string for a PostgreSQL database
             : if dsn is 'pg', the default database 'pdx' on localhost (port 5432) and username 'pdxuser' will be used
        - dump: 1 or 0; to dump to a JSON file pdx-dump.json (optional)
        - remove_all: 1 or 0; remove all records from the tables first (optional);
        -           : WARNING: this will delete *all* existing parts, BOM, etc., records from the database


*Examples*: for a SQLite3 database:

::

    pypdx data/pdx-example.xml testout.sqlite3 1 1

for a postgreSQL database:

::

    pypdx data/pdx-example.xml "dbname='pdx' host='localhost' user='pdxuser' password='billofmaterials' port=5432" 1 1

A sample PDX XML file (data/pdx-example.xml) is included in the
distribution. This is obviously not for a real product.

To use **pypdx** as a module, do something like this:

::

   import pypdx

   dsn = 'testout.sqlite3'
   xmlfile = 'data/pdx.xml'
   mypdx = pypdx.PDX(xmlfile, dsn, debug=True)
   
   # should return 'ok', otherwise you get the error message
   status = mypdx.removeall()
   status = mypdx.fillparts()


mypdx.removeall() removes all old records from the database tables,
mypdx.fillparts() then fills the database table with new records from
the XML file.

Database and Tables
-------------------

The data is saved into the following tables:

-  **partsmaster** is the main table that stores the Items; each Item is
   uniquely identified by a **itemUniqueIdentifier**
-  **bom** is the table the stores the BOM; each BOM record is
   essentially a “link” that points from the parent Item (identified by
   its **itemUniqueIdentifier**), to the target Item (also identified by
   its **itemUniqueIdentifier**). (Viewed as a directed graph, the
   records in the *partsmaster* are the nodes, and the records of the
   *bom* are the edges of the graph.)
-  **attachments** is the table that stores information on the
   attachment files, which should be in the ZIP file if the *isFileIn*
   field is TRUE. There can be multiple attachments to each Item, and
   these are linked to the Item through the Item’s
   *itemUniqueIdentifier*.
-  **approvedmfg** is the table that stores the information on the
   approved manufacturers for each Item. There can also be mutiple
   approved manufacturers for each Item.

The definition of (and relations between) these tables are laid out in
the SQL files in the data/ directory. A sample program (*main.py*) in the source 
code distribution illustrates the usage of the module (this is used to
form the **pypdx** program mentioned above). You can also dump the contents of
the PDX file into a JSON file (with the PDX.dump(filename) function).
However this merely mirrors the structure and contents of the XML file;
it may not be particularly useful unless you process the JSON
file/object further on your own.

As mentioned above, the program allows you to extract the data into a
SQLite3 database or a PostgreSQL database. The former is less trouble to
set up, as it is file-based. The program will in fact create the SQLite3
database file for you (as well as create the tables).

For using this in a PostgreSQL database, the program **pypdx** will
create the tables for you if they do not already exist, but it assumes
that the database called *pdx* already exists and is running on
localhost (at port 5432). You can create the database with the
commands

::

    % psql template1
    ....
    template1=# create database pdx;
    template1=# \q

or you can modify the *dsn* specifications in the example program
to suit your needs. It should be relatively simple to modify the code
to use a `MySQL database <https://www.mysql.com/>`__, but I have not
tried this.

The program depends on a few Python modules (specified in the
requirement.txt file), including the SQLite3 driver (*sqlite3*) and
the PostgreSQL driver (*psycopg2*). Run

::

    % sudo pip install -r requirement.txt

to install the modules. If you do not care for the PostgreSQL database,
you should still be able to use the program without installing the
*psycopg2* module, since it is not imported unless you specify the
PostgreSQL database option.

Closing Remarks
---------------

I have only seen a very small number of PDX files, and there does not
seem to be any sample PDX files that you can download from the Internet
(likely because the only PDX files available contain proprietary
manufacturing information!). Naturally the testing of this program has
been very limited. While I believe the implementation to be correct (if
incomplete), there is always the possibility of bugs. So use at your own
risk; you have been warned!

(*Last Revised 2018-01-19*)
