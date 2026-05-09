
import sqlite3
from enum import Enum



class Schema:
    def __init__(self,**kwargs: str):
        self.columns = kwargs

class Connection:
    def __init__(self,path:str,schema:Schema=None):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.cur : sqlite3.Cursor = self.conn.cursor
        if schema!=None and schema is Schema:
            self.schema=schema
    def fetchAllFromList(self,tableName): # SELECT * FROM tableName
        self.cur.execute("SELECT * FROM ?",tableName)
        results = self.cur.fetchall()
        return results
    def fetchXforY(self,tableName,key,value): # SELECT * FROM tableName where key = value
        self.cur.execute("SELECT * FROM ? WHERE ?=?")
        results = self.cur.fetchone()
        return results
    def insertInto(self,tableName,**kwargs):
        providedColumnAmount = len(kwargs.keys())
        assert "Error: No arguments provided", providedColumnAmount > 0
        self.cur.execute("INSERT INTO ? VALUES (" + '?,'*providedColumnAmount-1 + "?" ")")
    

if __name__=="__main__":
    fartSchema = Schema(name="TEXT",favNum="INTEGER")
    
    db = Connection("fart.db")