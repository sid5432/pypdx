pypdx
=====

*A Simple parser for PDX (Product Data eXchange) XML files*

From `the Wikipedia article on
PDX <https://en.wikipedia.org/wiki/PDX_(IPC-257X)>`__: “the PDX (Product
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
on the `IPC
website <http://www.ipc.org/4.0_Knowledge/4.1_Standards/IPC-25xx-files/2571.zip>`__.
Free PDX viewers are available, one of the most popular being PDXViewer
from `PDXplorer <http://www.pdxplorer.com/>`__.

Since the \*.pdx file is simply a ZIP file, it is easy to extract all
the attachments (documents, schematics, drawings, etc.) from the ZIP
file, and there are several ways one can view XML files. However, trying
to make sense of the assembly from a generic XML viewer is not really
feasible, and although there are specialized free (and non-free)
viewers, there are times when you might want to extract the data for
your own use. To this end I have written a simple PDX XML file parser,
pypdx (written in Python), as presented here.

The *pypdx* program can be used as a Python module, but includes a
sample program that is more or less ready to use. Be warned that it
does. It does *not* implement all the elements defined in the PDX
standard, but only the parts that happen to be of interest to *me* at
the moment, so don’t be surprised if it does not have the features you
are looking for. What it does extract are the **Item**\ s, the
**ApprovedManufacturerList**, the **BillOfMaterial**, and the
**Attachments**. The main purpose of the program is to extract this data
from the XML file, and organize them by saving them into a relational
database: in this case either a `SQLite3 <https://www.sqlite.org/>`__
database or a `PostgreSQL <https://www.postgresql.org/>`__ database.
What you do after the data is stuffed into a relational database is up
to you! The data is saved into the following tables:

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
the SQL files in the lib/ directory. A sample program (pdx-example.py)
illustrates the usage of the module. You can also dump the contents of
the PDX file into a JSON file (with the PDX.dump(filename) function).
However this merely mirrors the structure and contents of the XML file;
it may not be particularly useful unless you process the JSON
file/object further on your own.

As mentioned above, the program allows you to extract the data into a
SQLite3 database or a PostgreSQL database. The former is less trouble to
set up, as it is file-based. The program will in fact create the SQLite3
database file for you (as well as create the tables). However the
SQLite3 database does not have all the features of a full-blown
relational database such as PostgreSQL. In particular, although the
foreign key constraint is observed, the “*on delete cascade*” and “*on
update cascade*” requirements are not enforced (i.e., in PostgreSQL, if
you remove an Item, all the associated BOM links, attachments, and
approved manufacturer records will be automatically removed by the
database. This is not the case with the SQLite3 database, as of this
writing).

For using this in a PostgreSQL database, the example program
(pdx-example.py) will create the tables for you if they do not already
exist, but it assumes that the database called *pdx* already exists, and
is running on localhost (at port 5432). You can create the database with
the commands:

::

    % psql template1
    ....
    template1=# create database pdx;
    template1=# \q

or modify the *dns* specifications in the example program to suit your
needs. It should be relatively simple to modify the code to use a `MySQL
database <https://www.mysql.com/>`__, but I have not tried this.

The program depends on a few Python modules (specified in the
requirement.txt file), including the SQLite3 driver (*sqlite3*) and the
PostgreSQL driver (*psycopg2*). Run

::

    % sudo pip install -r requirement.txt

to install the modules. If you do not care for the PostgreSQL database,
you should still be able to use the program without installing the
*psycopg2* module, since it is not imported unless you specify the
PostgreSQL database option.

I have only seen a very small number of PDX files, and there does not
seem to be any sample PDX files that you can download from the Internet
(likely because the only PDX files available contain proprietary
manufacturing information!). Naturally the testing of this program has
been very limited. While I believe the implementation to be correct (if
incomplete), there is always the possibility of bugs. So use at your own
risk; you have been warned!

(*Last Revised 2018-01-11*)