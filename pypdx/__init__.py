"""
This program takes a PDX XML file and extracts the information into
a relational database (choice of SQLite3 or PostgreSQL).
"""
from .parser import PDX
from .main import main
__version__ = "0.0.1b3"
