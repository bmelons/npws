sql_typemap_list = {
    "NULL":None,
    "INTEGER":int,
    "REAL":float,
    "TEXT":str,
    "BLOB":bytes
}
py_typemap_list = {
    None:"NULL",
    int:"INTEGER",
    float:"REAL",
    str:"TEXT",
    bytes:"BLOB"
}


def SqlTypeToPy(t:str):
    pyType = sql_typemap_list.get(t)
    if pyType == None:
        raise ValueError("Inputted type does not seem to have a python equivalent")
    return pyType

def PyTypeToSql(t:str):
    sqlType = py_typemap_list.get(t)
    if sqlType == None:
        raise ValueError("Inputted type does not seem to have a SQL equivalent")
    return sqlType