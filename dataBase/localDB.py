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
            Name TEXT NOT NULL,
            date TEXT NOT NULL,
            topic TEXT NOT NULL,
            groupId INTEGER NOT NULL,
            phoneNumber TEXT NOT NULL,
            assignWorkOff INTEGER NOT NULL DEFAULT 0,
            teacher TEXT NOT NULL,
            dateNextConnection TEXT
            );
            CREATE TABLE IF NOT EXISTS GroupOccupancy(
            idsStudents TEXT,
            topic TEXT NOT NULL,
            location TEXT NOT NULL,
            teachers TEXT NOT NULL,
            day TEXT NOT NULL,
            time TEXT NOT NULL,
            assignWorkOffs INTEGER NOT NULL,
            groupId INTEGER NOT NULL,
            countStudents INTEGER NOT NULL,
            maxStudents INTEGER NOT NULL

            
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
        self._fillTeachers(cursor, data['Teachers'])
        connection.commit()
        connection.close()
    
    

    def _fillTeachers(self, cursor:sqlite3.Cursor, teachers:list):
        cursor.execute('DELETE FROM Teachers;')
        for i in teachers:
            cursor.execute('INSERT INTO Teachers (id, name) VALUES(?,?)', (i['id'], i['name']))
        
    def fillTableGroupOccupancy(self, groups:list):
        connection = sqlite3.connect(self.path)
       
        cursor = connection.cursor()
        cursor.execute('DELETE FROM GroupOccupancy;')
        for i in groups:
            cursor.execute('INSERT INTO GroupOccupancy (idsStudents,topic,location,teachers,day,time,assignWorkOffs,groupId,countStudents,maxStudents) VALUES(?,?,?,?,?,?,?,?,?,?)', (i['idsStudents'], i['topic'],i['location'], i['teachers'],i['day'],i['time'],i['assignWorkOffs'],i['groupId'],i['countStudents'],i['limit']))
            connection.commit()
        connection.close()
    def fillTableStudentAbsences(self, students:list):
        connection = sqlite3.connect(self.path)
        cursor = connection.cursor()
        for i in students:
            cursor.execute('INSERT INTO GroupOccupancy (id,Name,date,topic,groupId,phoneNumber,assignWorkOff,teacher,dateNextConnection) VALUES(?,?,?,?,?,?,?,?,?)', (i['id'], i['name'],i['date'],i['topic'], i['groupId'],i['phoneNumber'],i['teacher'],i['assignWorksOff']))
            connection.commit()
        connection.close()
            
