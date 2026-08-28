#!/opt/homebrew/Caskroom/miniforge/base/bin/python
from __future__ import annotations
import sqlite3
import typemap

auto_commit = False

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return dict(zip(fields, row))

class TableSchema:
    def __init__(self, tableName: str, **kwargs: None|int|float|str|bytes):
        self.tableName = tableName
        self.columns = kwargs
        self.primary_key = None


class Connection:
    def __init__(self, path: str):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = dict_factory
        self.cur: sqlite3.Cursor = self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def getTable(self, table: str | TableSchema, createIfNotExists: bool):
        tableName = table
        if isinstance(tableName,TableSchema):
            tableName = table.tableName
            if createIfNotExists:
                columns_def = ", ".join(
                    f"{cname} {ctype}" for cname, ctype in table.columns.items()
                )
                self.cur.execute(
                    f"CREATE TABLE IF NOT EXISTS {table.tableName} ({columns_def})"
                )
        elif createIfNotExists:
            raise TypeError(
                "Non-schema object was passed to getTable with intent to create"
            )
        newTable = Table(self, tableName)
        return newTable

    def createTable(self, schema: TableSchema):
        columns_def = ", ".join(
            f"{cname} {ctype}" for cname, ctype in schema.columns.items()
        )
        self.cur.execute(
            f"CREATE TABLE IF NOT EXISTS {schema.tableName} ({columns_def})"
        )
        return self.getTable(schema.tableName)

    def insertInto(self, tableName, **kwargs):
        columns = ", ".join(kwargs.keys())
        values = tuple(kwargs.values())
        # print(columns,"\n-\n",values)
        statement = f"INSERT INTO {tableName} ({columns}) VALUES {values}"
        print(statement)
        self.cur.execute(statement)


class Table:
    def __init__(self, parent: Connection, tableName: str):
        self.parent: Connection = parent
        self.cursor: sqlite3.Cursor = self.parent.cur
        self.tableName: str = tableName
        self.schema: TableSchema = None
        self.setSchema()
    def setSchema(self):
        self.cursor.execute(f"PRAGMA table_info({self.tableName});")
        a = self.cursor.fetchall()
        pulled_schema = {}
        self.schema = TableSchema(self.tableName)
        for column in a:
            column_type = typemap.SqlTypeToPy(column["type"])
            is_primary_key = column["pk"]==1
            pulled_schema[column["name"]] = column_type
            self.schema.primary_key = column["name"]
        self.schema.columns = pulled_schema
        # print(self.schema.columns)

    def verify_values(self, *values):  # true if invalid
        ## make this check
        return False
    ## TODO: Implement TableItem orm component into the insert function(s)
    ## TODO: insert many function
    def insert(self, *values, replace_if_exists=False):
        insertedValues = ", ".join(["?"] * len(values))
        if self.verify_values(*values):
            raise TypeError("Values are not valid for this table")
            return
        secondary_action = "IGNORE"
        if replace_if_exists:
            secondary_action = "REPLACE"
        query = f"INSERT OR {secondary_action} INTO {self.tableName} VALUES ({insertedValues})"
        self.cursor.execute(query, tuple(values))
        self.parent.commit()

    def insert_columns_values(self, columns: tuple, values: tuple):
        pass
    # selections/fetches
    ## TODO: Implement TableItem orm component into the fetch functions
    def get_item_one(self, key:str, value:str) -> TableItem: #do not give a user provided key, why would you ever ever ever want that
        pass
        if key not in self.schema.columns:
            raise ValueError(f"Invalid column name: {key}")
        self.cursor.execute(f"SELECT * FROM {self.tableName} WHERE {key}=?",(value,))
        results = self.cursor.fetchone()
        item = TableItem(self,results)
        return item
    def get_items(self):
        self.cursor.execute(f"SELECT * FROM {self.tableName}")
        rows = self.cursor.fetchall()
        items = []
        for row in rows:
            items.append(TableItem(self,row))
        return items
    def fetch_one(self, query) -> dict:
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def fetch_all(self) -> list[any]:
        self.cursor.execute(f"SELECT * FROM {self.tableName}")
        return self.cursor.fetchall()

    def fetch_one_XforY(self, key:str, value:str): #do not give a user provided key, why would you ever ever ever want that
        if key not in self.schema.columns:
            raise ValueError(f"Invalid column name: {key}")
        self.cursor.execute(f"SELECT * FROM {self.tableName} WHERE {key}=?",(value,))
        results = self.cursor.fetchone()
        return results

    def fetch_all_XforY(self, key, value):
        self.cursor.execute(f"SELECT * FROM {self.tableName} WHERE {key}=?",(value,))
        results = self.cursor.fetchall()
        return results
    # rethinking adding a function to drop a table, super dangerous!
    # def delete(self):
    #     self.cursor.execute(f"DROP TABLE {self.tableName}")

class TableItem: #Do not instantiate, intended to only to be spawned by Table
    def __init__(self,parent : Table, values: dict[str,any]):
        self.values : dict[str,any] = values
        self.parent : Table = parent
        self.validate()
    def validate(self):
        global validate_values_against_schema
        if self.parent == None or self.values == None:
            raise ValueError("Cannot validate, one or more attributes are None")
        result = validate_values_against_schema(self.values,self.parent.schema)
        if not result:
            raise TypeError("Values of tableitem do not properly map to the schema")
        return result
    def get_primary_key(self) -> str:
        return self.values.get(self.parent.schema.primary_key)
    def update(self,column:str,value:any):
        self.parent.cursor.execute(f"UPDATE {self.parent.tableName} SET {column} = (?) WHERE {self.parent.schema.primary_key} = {self.get_primary_key()}",(value,))
        self.values[column] = self.values 

def typify(dictionary:dict): # maps a dictionary to store its old value's types instead of the values themselves
    dictionary=dictionary.copy()
    for key in dictionary.keys():
        dictionary[key] = type(dictionary[key])
    return dictionary
def validate_values_against_schema(values,schema:dict|TableSchema):
    # TableSchema degrades into just its columns value
    if isinstance(schema,TableSchema):
        schema = schema.columns
    if not isinstance(schema,dict):
        raise TypeError("Passed value is not dict")
    typed_values = typify(values)
    return typed_values == schema

if __name__ == "__main__":
    print("Running NPWS main tests")
    guysSchema = TableSchema(
        "tries", user_id="INTEGER PRIMARY KEY", name="TEXT", favNum="INTEGER"
    )
    coolSchema = TableSchema(
        "bumbling_buffoons", # we have fun here
        boys_name="TEXT PRIMARY KEY",
        star_rating="REAL",
        fav_number="INTEGER",
    )
    db = Connection("test_database.db")
    the = db.getTable(coolSchema, True)
    the.insert("andrew", 0.1, 67)
    item = the.get_item_one("fav_number",67)
    item.update("star_rating",4.4)
    db.commit()

