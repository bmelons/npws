
import sqlite3
from enum import Enum



class TableSchema:
    def __init__(self,tableName:str,**kwargs: str):
        self.tableName = tableName
        self.columns = kwargs

class Connection:
    def __init__(self,path:str,*tables:tuple[TableSchema]):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.cur : sqlite3.Cursor = self.conn.cursor()
        self.tables : list[TableSchema] = []
        if not tables is None:
            self.tables.extend(tables)
        for i in self.tables:
            columns_def = ", ".join(f"{cname} {ctype}" for cname, ctype in i.columns.items())
            self.cur.execute(f"CREATE TABLE IF NOT EXISTS {i.tableName} ({columns_def})")
    def commit(self):
        self.conn.commit()
    def fetchAllFromTable(self,tableName):
        self.cur.execute(f"SELECT * FROM {tableName}")
        results = self.cur.fetchall()
        return results
    
    def fetchXforY(self,tableName,key,value):
        self.cur.execute(f"SELECT * FROM {tableName} WHERE {key}={value}")
        results = self.cur.fetchone()
        return results
    
    def insertInto(self,tableName,**kwargs):
        columns = ', '.join(kwargs.keys())
        values = tuple(kwargs.values())
        # print(columns,"\n-\n",values)
        statement = f"INSERT INTO {tableName} ({columns}) VALUES {values}"
        print(statement)
        self.cur.execute(statement)

class Table:
    def __init__(self,schema:TableSchema):
        self.parent : Connection = None
        self.schema : TableSchema = schema 
    # def 

if __name__=="__main__":
    guysSchema = TableSchema("guys",user_id="INTEGER PRIMARY KEY",name="TEXT",favNum="INTEGER")
    db = Connection("fart.db",guysSchema)
    db.insertInto(guysSchema.tableName,user_id=9,name="flungle",favNum=9)
    res = db.fetchAllFromTable(guysSchema.tableName)
    print(res)