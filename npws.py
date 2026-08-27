import sqlite3
import json
import typemap
from enum import Enum


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return dict(zip(fields, row))


class TableSchema:
    def __init__(self, tableName: str, **kwargs: str):
        self.tableName = tableName
        self.columns = kwargs


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
        if type(tableName) == TableSchema:
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
        for column in a:
            column_type = typemap.SqlTypeToPy(column["type"])
            pulled_schema[column["name"]] = column_type
        self.schema = TableSchema(self.tableName)
        self.schema.columns = pulled_schema
        # print(self.schema.columns)

    def verify_values(self, *values):  # true if invalid
        ## make this check
        return False

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
    def fetch_one(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def fetch_all(self):
        self.cursor.execute(f"SELECT * FROM {self.tableName}")
        return self.cursor.fetchall()

    def fetch_one_XforY(self, key, value):
        self.cursor.execute(f"SELECT * FROM {self.tableName} WHERE {key}={value}")
        results = self.cursor.fetchone()
        return results

    def fetch_all_XforY(self, key, value):
        self.cursor.execute(f"SELECT * FROM {self.tableName} WHERE {key}={value}")
        results = self.cursor.fetchall()
        return results
    def delete(self):
        self.cursor.execute(f"DROP TABLE {self.tableName}")

if __name__ == "__main__":
    guysSchema = TableSchema(
        "tries", user_id="INTEGER PRIMARY KEY", name="TEXT", favNum="INTEGER"
    )
    coolSchema = TableSchema(
        "bumbling_buffoons", # we have fun here
        boys_name="TEXT PRIMARY KEY",
        poop_flavor_rating="REAL",
        fav_number="INTEGER",
    )
    db = Connection("fart.db")
    the = db.getTable(coolSchema, True)
    the.insert("andrew", 0.1, 67)

    print(the)
