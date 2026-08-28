import sqlite3
import npws
import json
import random

# nf = 
names = json.load("")

db = npws.Connection("test_database.db")
doofs = db.getTable("bumbling_buffoons")
for i in range(1,50):
    doofs.insert()
