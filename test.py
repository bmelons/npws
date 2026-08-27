import sqlite3

db = sqlite3.connect("sqlite3test.db")
cursor = db.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS catalog (row_id INTEGER PRIMARY_KEY, name TEXT NOT NULL, quantity INTEGER)")
db.commit()
# cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='catalog';")
cursor.execute()
# schema = cursor.fetchone()
# if not schema:
#     quit()
# schema=schema[0]




db.close()