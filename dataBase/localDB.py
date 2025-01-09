import sqlite3
from contextlib import contextmanager
import datetime


class DataBase:
    """Создаёт необходимые таблицы и предоставляет интерфейс ля работы с ними"""
    
    def __init__(self):
        self.path ="dataBase/dataBases/dataBase.db"
        self._createTables()
        pass

    def _createTables(self):
        with db_ops(self.path) as cursor:
            cursor.executescript(
                '''
                CREATE TABLE IF NOT EXISTS StudentAbsences(
                idStudent INTEGER NOT NULL, 
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                topic TEXT NOT NULL,
                idGroup TEXT NOT NULL,
                idLesson INTEGER NOT NULL,
                phoneNumber TEXT NOT NULL,
                teacher INTEGER NOT NULL,
                workOffScheduled INTEGER NOT NULL DEFAULT 0,
                dateNextConnection TEXT DEFAULT 0,
                dateLastConnection TEXT,
                groupForWorkingOut INTEGER 
                );
                CREATE TABLE IF NOT EXISTS GroupOccupancy(
                idGroup INTEGER,
                newStudents TEXT,
                idsStudents TEXT,
                dateOfEvent TEXT,
                count INTEGER DEFAULT 0,
                lastUpdate TEXT 
                );
                CREATE TABLE IF NOT EXISTS RegularLessons(
                idGroup INTEGER NOT NULL,
                topic TEXT NOT NULL,
                idsStudents TEXT,
                location INTEGER NOT NULL,
                teacher INTEGER NOT NULL,
                day INTEGER NOT NULL,
                timeFrom TEXT NOT NULL,
                timeTo TEXT NOT NULL,
                assignWorkOffs INTEGER DEFAULT 1,
                maxStudents INTEGER NOT NULL,
                lastUpdate TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS Locations(
                id INTEGER NOT NULL,
                name TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS Teachers(
                id INTEGER NOT NULL,
                name TEXT NOT NULL
                )
                '''
            )
    

    def addDataInTableGroupOccupancy(self):
        with db_ops(self.path) as cursor:
            cursor.execute("SELECT * FROM RegularLessons")
            regulars = cursor.fetchall()
            for item in regulars:
                  id= item[0]
                  idsStudents = item[2]
                  cursor.execute("SELECT * FROM GroupOccupancy WHERE(idGroup=?)",[int(item[0])])
                  if not cursor.fetchone():
                      cursor.execute("INSERT INTO GroupOccupancy (idGroup,idsStudents,dateOfEvent,count,lastUpdate) VALUES (?,?,?,?,?)", 
                                     (id, idsStudents, getDateNextWeekday(item[5]).strftime('%Y-%m-%d'), len(item[2].split(',')), datetime.date.today()  ))
    
    def synchroniseTableRegularLessons(self, groups:list):
        with db_ops(self.path) as cursor:
            cursor.execute("DELETE FROM RegularLessons")
        for i in groups:
            with db_ops(self.path) as cursor:
                cursor.execute('INSERT INTO RegularLessons (idGroup,topic,idsStudents,location,teacher,day,timeFrom,timeTo,maxStudents,lastUpdate) VALUES(?,?,?,?,?,?,?,?,?,?)', 
                               (i['idGroup'], i['topic'],i['idsStudents'], i['location'],i['teacher'],i['day'],i['timeFrom'],i['timeTo'],i['maxStudents'],i['lastUpdate']))
            
    def insertNewLocation(self, data:dict):
        with db_ops(self.path) as cursor:
            cursor.execute("SELECT * FROM Locations WHERE(id =?)",[int(data['id'])])
            if not cursor.fetchone():
                cursor.execute("INSERT INTO Locations (id,name) VALUES (?,?)",[data['id'], data['name']])

    def synchroniseTeachers(self, data:dict):
        with db_ops(self.path) as cursor:
            cursor.execute("DELETE FROM Teachers")
            for teacher in data:
                cursor.execute("INSERT INTO Teachers (id,name) VALUES (?,?)",[teacher['id'], teacher['name']])
    
    def fillTableStudentAbsences(self, students:list):
        with db_ops(self.path) as cursor:
            for i in students:
                cursor.execute("SELECT * FROM StudentAbsences WHERE(idStudent =? AND idLesson =?)",(i['idStudent'], i['idLesson']))
                if not cursor.fetchone():
                    cursor.execute('INSERT INTO StudentAbsences (idStudent,name,date,topic,idGroup,phoneNumber,teacher,idLesson) VALUES(?,?,?,?,?,?,?,?)', 
                            (i['idStudent'], i['name'],i['date'],i['topic'], i['idGroup'],i['phoneNumber'],i['teacher'],i['idLesson']))
    def getAllLocations(self):
        with db_ops(self.path) as cursor:
            cursor.execute("SELECT * FROM Locations")
            data = cursor.fetchall()
        return self._locationTupeInList(data)
    
    def _locationTupeInList(self, data:tuple):
        l = []
        for i in data:
            l.append({'id':i[0], 'name':i[1]})
        return l
    
    def getRegularLessonsIds(self) ->list:
        with db_ops(self.path) as cursor:
            cursor.execute("SELECT * FROM RegularLessons")
            groups = cursor.fetchall()
        groupsIds = []
        for i in groups:
            groupsIds.append(i[0])
        return groupsIds
    
   
    # def _selectGroupOccupancyData(self):
    #     connection = sqlite3.connect(self.path)
    #     cursor = connection.cursor()
    #     cursor.execute("SELECT * FROM GroupOccupancy")
    #     c = cursor.fetchall()
    #     connection.close()
    #     return c
    
    # def _selectStudentAbsences(self):
    #     connection = sqlite3.connect(self.path)
    #     cursor = connection.cursor()
    #     cursor.execute("SELECT * FROM StudentAbsences")
    #     c = cursor.fetchall()
    #     connection.close()
    #     return c
    
    # def getStudentAbsencesData(self):
    #     temp = self._selectStudentAbsences()
    #     studentsList = []
    #     for i in temp:
              
    #           studentsList.append(
    #                {
    #                     'id': i[0],
    #                     'name': i[1],
    #                     'date':i[2],
    #                     'topic':i[3],
    #                     'idGroups': i[4],
    #                     'idLesson': i[5],
    #                     'phoneNumber':i[6],
    #                     'topic':i[7],
    #                     'workOffScheduled':i[8],
    #                     'dateNextConnection':i[9],
    #                     'groupForWorkingOut':i[10]
    #                 }
    #           )
    #     return studentsList
    
    # def getGroupOccupancyData(self):
    #     temp = self._selectGroupOccupancyData()
    #     groupList = []
    #     for i in temp:
    #         groupList.append(
    #         { 
    #             'idsStudents' : i[0],
    #             'topic' : i[1],
    #             'location': i[2],
    #             'teachers' : i[3],
    #             'day' : i[4],
    #             'time': i[5],
    #             'assignWorkOffs': i[6],
    #             'idGroup' : i[7],
    #             'countStudents' : i[8],
    #             'maxStudents': i[9],
    #         }
    #         )
    #     return groupList



@contextmanager
def db_ops(db_name):
    conn = sqlite3.connect(db_name)
    try:
        cur = conn.cursor()
        yield cur
    except Exception as e:
        # do something with exception
        conn.rollback()
        raise e
    else:
        conn.commit()
    finally:
        conn.close()


def getDateNextWeekday(numberDay:int):
   
    d = datetime.timedelta( (7 + numberDay - datetime.date.today().weekday())%7 ).days
    return  datetime.date.today() + datetime.timedelta(d)