import sqlite3
import os
class DataBase:

    def __init__(self):
        self.path ="dataBase/dataBases/dataBase.db"
        self._createTables()
        pass

    def _createTables(self):
        connection = sqlite3.connect(self.path)
        cursor = connection.cursor()
        cursor.executescript(
            '''
            CREATE TABLE IF NOT EXISTS StudentAbsences(
            id INTEGER NOT NULL, 
            lessonId INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS GroupOccupancy(
            idStudent INTEGER NOT NULL,
            idGroup INTEGER NOT NULL,
            idTeacher INTEGER NOT NULL,
            topic TEXT NOT NULL DEFAULT Свободная, 
            isRegular INTEGER NOT NULL DEFAULT 1
            );
            
            CREATE TABLE IF NOT EXISTS Groups(
            id INTEGER PRIMARY KEY,
            location TEXT NOT NULL,
            idTeacher INTEGER NOT NULL,
            isLimit INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS Teachers(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS Students(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            idGroup INTEGER NOT NULL,
            phonenumber TEXT NOT NULL
            );
            '''
        )
        connection.commit()
        connection.close()

    #Декоратор дописать
    # def _connection(self,func):
    #     self.connction = sqlite3.connect(self.path)
    #     func(self)
    #     self.connction.close();

 
   
    
    def synchronizeDB(self, data:dict):
        connection = sqlite3.connect(self.path)
        cursor = connection.cursor()
        self._clearTables(cursor)
        self._fillTeachers(cursor, data['teachers'])
        connection.execute()
    
    def _clearTables(self,cursor:sqlite3.Cursor):
        cursor.execute('TRUNCATE Teachers, Groups, Students')

    def _fillTeachers(self, cursor:sqlite3.Cursor, teachers:list):
        for i in teachers:
            cursor.execute('INSERT INTO Teachers (id, name) VALUES(?,?)', (i['id'], i['name']))
        

    
            
