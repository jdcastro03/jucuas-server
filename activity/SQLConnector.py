import mysql
from mysql.connector import Error
class SQLConnector:
    connection = mysql.connector
    cursor: None
    SQL_HOST = ""
    SQL_DB = ""
    SQL_PORT = ""
    SQL_USER = ""
    SQL_PASSWORD = ""

    def __init__(self, host, db, port, user, password):
        self.SQL_HOST = host
        self.SQL_DB = db
        self.SQL_PORT = port
        self.SQL_USER = user
        self.SQL_PASSWORD = password

    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.SQL_HOST,
            user=self.SQL_USER,
            password=self.SQL_PASSWORD,
            database=self.SQL_DB
        )
        self.cursor = self.connection.cursor()
    def disconnect(self):
        self.connection = None
    #JALA AL 100
    def delete(self, table, where):
        query = "DELETE FROM "+ table +" WHERE " + where
        self.cursor.execute(query)
        self.connection.commit()
        if self.cursor.rowcount >= 1:
            return 1, "Succesful delete"
        else:
            return 0, "Error while deleting values"
    #JALA AL 100
    def insert(self, table, fields, values):
        cursors = ""
        for i in values:
            if type(i) is str:
                cursors += "%s, "
            if type(i) is float:
                cursors += "%f, "
            if type(i) is int:
                cursors += "%i, "
        cursors = cursors[:-2]
        try:
            query = "INSERT INTO " + table + " (" + fields + ") VALUES (" + cursors + ")"
            print(query)
            self.cursor.execute(query, values)
            self.connection.commit()
            if self.cursor.rowcount >= 1:
                return 1, "Succesful insert"
            else:
                return 0, "Error while inserting values"
        except Error as e:
            print("Error: ", e)

    #JALA Al 100
    def update(self, table, values, where):
        sets = ""
        for i in values:
            sets += i+", "
        sets = sets[:-2]
        query = "UPDATE " + table + " SET " + sets + " WHERE "+ where
        self.cursor.execute(query)
        self.connection.commit()
        if self.cursor.rowcount >= 1:
            return 1, "Succesful update"
        else:
            return 0, "Error while updating values"

    #JALA AL 100
    def select(self, table, where):
        if(not where == ""):
            query = "SELECT * FROM "+ table +" WHERE "+where
        else:
            query = "SELECT * FROM " + table
        self.connection.commit()
        self.cursor.execute(query)
        res = self.cursor.fetchall()
        return 1, res
        #else:
        #    return 0, "Error"
    def custom_select(self, q):
        self.cursor.execute(q)
        res = self.cursor.fetchall()
        return 1, res
    #HELPERS

    def repeated(self, table, where):
        query = "SELECT COUNT(*) FROM "+ table +" WHERE "+where+""
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        row_count = result[0]
        if(row_count > 0):
            return 0, "Repeated" #REPEATED
        if(row_count == 0):
            return 1, "Not repeated" #NOT REPEATED
