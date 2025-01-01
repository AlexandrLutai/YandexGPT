import sqlite3
import os
class tempDataBase:

    def __init__(self):
        self.path ="dataBase/dataBases/temp.db"
        self._connectToDb()
        pass

    def _connectToDb(self):
        
        if os.path.isfile(self.path):
            connection = sqlite3.connect(self.path)
        else:
            connection = sqlite3.connect(self.path)
            self._createTables(connection)
    
    def _createTables(self,connection:sqlite3.Connection):
        cursor = connection.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS StudentAbsences(
            id INTEGER PRIMARY KEY,
            lessonId INTEGER NOT NULL
            )
            '''
        )
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS GroupOccupancy(
            idStudent INTEGER NOT NULL,
            idGroup INTEGER NOT NULL,
            topic TEXT NOT NULL, 
            isRegular BLOB NOT NULL
            )
            '''
        )

        connection.commit()

            
