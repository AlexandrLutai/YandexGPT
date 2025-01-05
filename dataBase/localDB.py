import sqlite3
import enum
class GroupOccupancyFields(enum.Enum):
        idsStudents = 0
        topic = 1
        location = 2
        teachers = 3
        day = 4
        time = 5
        assignWorkOffs = 6
        idGroup = 7
        countStudents = 8 
        maxStudents = 9

class StudentAbsencesFields(enum.Enum):
        id = 0
        name = 1
        date = 2
        topic = 3
        idGroups = 4
        idLesson = 5
        phoneNumber = 6
        teacher = 7
        workOffScheduled = 7
        dateNextConnection = 8
        groupForWorkingOut = 9

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
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            topic TEXT NOT NULL,
            idGroups TEXT NOT NULL,
            idLesson INTEGER NOT NULL,
            phoneNumber TEXT NOT NULL,
            teacher TEXT NOT NULL,
            workOffScheduled INTEGER NOT NULL DEFAULT 0,
            dateNextConnection TEXT DEFAULT 0,
            groupForWorkingOut TEXT DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS GroupOccupancy(
            idsStudents TEXT,
            topic TEXT NOT NULL,
            location TEXT NOT NULL,
            teachers TEXT NOT NULL,
            day TEXT NOT NULL,
            time TEXT NOT NULL,
            assignWorkOffs INTEGER NOT NULL,
            idGroup INTEGER NOT NULL,
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
    
    def _clearTableGroupOccupancy(self,connection:sqlite3.Connection):
        cursor = connection.cursor()
        cursor.execute('DELETE FROM GroupOccupancy;')
        connection.commit()

    def _fillTeachers(self, cursor:sqlite3.Cursor, teachers:list):
        for i in teachers:
            cursor.execute('INSERT INTO Teachers (id, name) VALUES(?,?)', (i['id'], i['name']))
        
    def fillTableGroupOccupancy(self, groups:list):
        connection = sqlite3.connect(self.path)
        self._clearTableGroupOccupancy(connection)
        cursor = connection.cursor()
        for i in groups:
            cursor.execute('INSERT INTO GroupOccupancy (idsStudents,topic,location,teachers,day,time,assignWorkOffs,idGroup,countStudents,maxStudents) VALUES(?,?,?,?,?,?,?,?,?,?)', (i['idsStudents'], i['topic'],i['location'], i['teachers'],i['day'],i['time'],i['assignWorkOffs'],i['idGroup'],i['countStudents'],i['limit']))
            connection.commit()
        connection.close()
    
    def fillTableStudentAbsences(self, students:list):
        connection = sqlite3.connect(self.path)
        cursor = connection.cursor()
        for i in students:
            cursor.execute("SELECT * FROM StudentAbsences WHERE(id =? AND idLesson =?)",(i['id'], i['idLesson']))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO StudentAbsences (id,name,date,topic,idGroups,phoneNumber,teacher,idLesson) VALUES(?,?,?,?,?,?,?,?)', 
                           (i['id'], i['name'],i['date'],i['topic'], i['idGroups'],i['phoneNumber'],i['teacher'],i['idLesson']))
            connection.commit()
        connection.close()
            
    def _selectGroupOccupancyData(self):
        connection = sqlite3.connect(self.path)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM GroupOccupancy")
        c = cursor.fetchall()
        connection.close()
        return c
    
    def _selectStudentAbsences(self):
        connection = sqlite3.connect(self.path)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM StudentAbsences")
        c = cursor.fetchall()
        connection.close()
        return c
    
    def getStudentAbsencesData(self):
        temp = self._selectStudentAbsences()
        studentsList = []
        for i in temp:
              
              studentsList.append(
                   {
                        'id': i[0],
                        'name': i[1],
                        'date':i[2],
                        'topic':i[3],
                        'idGroups': i[4],
                        'idLesson': i[5],
                        'phoneNumber':i[6],
                        'topic':i[7],
                        'workOffScheduled':i[8],
                        'dateNextConnection':i[9],
                        'groupForWorkingOut':i[10]
                    }
              )
        return studentsList
    
    def getGroupOccupancyData(self):
        temp = self._selectGroupOccupancyData()
        groupList = []
        for i in temp:
            groupList.append(
            { 
                'idsStudents' : i[0],
                'topic' : i[1],
                'location': i[2],
                'teachers' : i[3],
                'day' : i[4],
                'time': i[5],
                'assignWorkOffs': i[6],
                'idGroup' : i[7],
                'countStudents' : i[8],
                'maxStudents': i[9],
            }
            )
        return groupList