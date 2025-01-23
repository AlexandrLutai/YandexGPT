import sqlite3
from contextlib import contextmanager
import datetime


from contextlib import contextmanager
import datetime


class DataBase:
    """Создаёт необходимые таблицы и предоставляет интерфейс ля работы с ними"""
    
    
    def __init__(self,path: str ):
        """
        Инициализирует объект базы данных.
        
        :param path: Путь к файлу базы данных.
        """
        self.path = path
        self._createTables()
        pass

    def _createTables(self):
        try:
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
        except sqlite3.Error as e:
            print(f"Ошибка при создании таблиц: {e}")
    

    def addDataInTableGroupOccupancy(self) -> None:
        """
        Добавляет данные в таблицу GroupOccupancy на основе данных из таблицы RegularLessons.
        """
        try:
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
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении данных в таблицу GroupOccupancy: {e}")
   
   
    def synchroniseTableRegularLessons(self, groups:list[dict[str:any]]) -> None:
        """
        Синхронизирует таблицу RegularLessons с предоставленными данными.

        :param groups: Список словарей с данными о регулярных занятиях.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute("DELETE FROM RegularLessons")
            for i in groups:
                with db_ops(self.path) as cursor:
                    cursor.execute('INSERT INTO RegularLessons (idGroup,topic,idsStudents,location,teacher,day,timeFrom,timeTo,maxStudents,lastUpdate) VALUES(?,?,?,?,?,?,?,?,?,?)', 
                                (i['idGroup'], i['topic'],i['idsStudents'], i['location'],i['teacher'],i['day'],i['timeFrom'],i['timeTo'],i['maxStudents'],i['lastUpdate']))
        except sqlite3.Error as e:
            print(f"Ошибка при синхронизации таблицы Teachers: {e}")      
   
   
    def insertNewLocation(self, data:dict) -> None:
        """
        Вставляет новую запись о локации в таблицу Locations, если запись с таким ID не существует.

        :param data: Словарь с данными о локации.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute("SELECT * FROM Locations WHERE(id =?)",[int(data['id'])])
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO Locations (id,name) VALUES (?,?)",[data['id'], data['name']])
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении записи в таблицу location: {e}")      
   
    def synchroniseTeachers(self, data:dict)->None:
        """
        Вставляет новую запись о локации в таблицу Locations, если запись с таким ID не существует.

        :param data: Словарь с данными о локации.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute("DELETE FROM Teachers")
                for teacher in data:
                    cursor.execute("INSERT INTO Teachers (id,name) VALUES (?,?)",[teacher['id'], teacher['name']])
        except sqlite3.Error as e:
            print(f"Ошибка при синхронизации таблицы Teachers: {e}")
    
    
    def fillTableStudentAbsences(self, students:list) -> None:
        """
        Заполняет таблицу StudentAbsences данными об отсутствии студентов.

        :param students: Список словарей с данными об отсутствии студентов.
        """
        try:
            with db_ops(self.path) as cursor:
                for i in students:
                    cursor.execute("SELECT * FROM StudentAbsences WHERE(idStudent =? AND idLesson =?)",(i['idStudent'], i['idLesson']))
                    if not cursor.fetchone():
                        cursor.execute('INSERT INTO StudentAbsences (idStudent,name,date,topic,idGroup,phoneNumber,teacher,idLesson) VALUES(?,?,?,?,?,?,?,?)', 
                                (i['idStudent'], i['name'],i['date'],i['topic'], i['idGroup'],i['phoneNumber'],i['teacher'],i['idLesson']))
        except sqlite3.Error as e:
            print(f"Ошибка при заполнении таблицы StudentAbsences: {e}")   

    def _formatLocationsOrTeachers(self, data:list[tuple]) -> dict[str:any]:
        """
        Форматирует данные о локациях или преподавателях.

        :param data: Список кортежей с данными о локациях или преподавателях.
        :return: Список словарей с отформатированными данными.
        """
        try:
            dicts = []
            for i in data:
                dicts.append(self._formatLocationOrTeacher(i))
            return dicts
        except sqlite3.Error as e:
            print(f"Ошибка при форматировании данных о локациях или преподавателях: {e}")
    
    def _formatLocationOrTeacher(self, data:tuple) -> list[dict[str:any]]:
        """
        Форматирует данные о локации или преподавателе.

        :param data: Кортеж с данными о локации или преподавателе.
        :return: Словарь с отформатированными данными.
        """
        return {'id':data[0], 'name':data[1]}
    
    def getRegularLessonsIds(self) ->list[int]:
        """
        Возвращает список идентификаторов всех регулярных занятий.

        :return: Список идентификаторов регулярных занятий.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute("SELECT * FROM RegularLessons")
                groups = cursor.fetchall()
            groupsIds = []
            for i in groups:
                groupsIds.append(i[0])
        except sqlite3.Error as e:
            print(f"Ошибка при получении идентификаторов регулярных занятий: {e}")
        return groupsIds
    
    def _formatGroupsOccupancyData(self, groups:list) -> list[dict[str:any]]:
        """
        Форматирует данные о заполненности групп.

        :param groups: Список кортежей с данными о заполненности групп.
        :return: Список словарей с отформатированными данными.
        """
        allGroups = []
        for i in groups:
            allGroups.append(self._formatGroupOccupancyData(i))
        return allGroups
    
    
    def _selectData(self, tableName:str, field:str = None, param = None) -> list[tuple]:
        """
        Выполняет SELECT запрос к базе данных.

        :param tableName: Название таблицы.
        :param field: Поле для условия WHERE.
        :param param: Значение для условия WHERE.
        :return: Список кортежей с результатами запроса.
        """
        try:
            sql = f"SELECT * FROM {tableName}"
            params = ()
            if param:
                sql += f" WHERE {field} = ?"
                params = (param,) 
            with db_ops(self.path) as cursor:
                cursor.execute(sql, params)
                groups = cursor.fetchall()
            return groups
        except sqlite3.Error as e:
            print(f"Ошибка при выполнении SELECT запроса: {e}")       
    
    def updateData(self, data:dict[str:any],  tableName:str, selectPams:dict[str:any] = None) -> None:
        """
        Обновляет данные в указанной таблице.

        :param data: Словарь с данными для обновления.
        :param tableName: Название таблицы.
        :param selectPams: Словарь с параметрами для условия WHERE.
        """
        try:
            set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
            params = list(data.values())

            if selectPams:
                where_clause = " AND ".join([f"{key} = ?" for key in selectPams.keys()])
                params.extend(selectPams.values())
                sql = f"UPDATE {tableName} SET {set_clause} WHERE {where_clause}"
            else:
                sql = f"UPDATE {tableName} SET {set_clause}"

            with db_ops(self.path) as cursor:
                cursor.execute(sql, params)
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении данных в таблице {tableName}: {e}")
      
       

       
    def _fromatRegularLessons(self, lessons:list[tuple]) -> list[dict]:
        """
        Форматирует данные о регулярных занятиях.

        :param lessons: Список кортежей с данными о регулярных занятиях.
        :return: Список словарей с отформатированными данными о регулярных занятиях.
        """
        regularLessonsList = []
        for i in lessons:
           regularLessonsList.append(self._formatRegularLesson(i))
        return regularLessonsList

    
    
    def _selectData(self, tableName:str, field:str = None, param = None) -> list[tuple]:
        """
        Выполняет SELECT запрос к базе данных.

        :param tableName: Название таблицы.
        :param field: Поле для условия WHERE.
        :param param: Значение для условия WHERE.
        :return: Список кортежей с результатами запроса.
        """
        try:
            sql = f"SELECT * FROM {tableName}"
            if param:
                sql += f" WHERE({field} = {param})"
            with db_ops(self.path) as cursor:
                cursor.execute(sql)
                groups = cursor.fetchall()
            return groups
        except sqlite3.Error as e:
            print(f"Ошибка при выполнении SELECT запроса: {e}")
    
    def _fromatRegularLessons(self, lessons:list[tuple]) -> list[dict]:
        """
        Форматирует данные о регулярном занятии.

        :param lesson: Кортеж с данными о регулярном занятии.
        :return: Словарь с отформатированными данными о регулярном занятии.
        """
        regularLessonsList = []
        for i in lessons:
           regularLessonsList.append(self._formatRegularLesson(i))
        return regularLessonsList

    def _formatStudentsAbsences(self, students:list[tuple]) -> list[dict[str:any]]:
        """
        Форматирует данные об отсутствии студентов.

        :param students: Список кортежей с данными об отсутствии студентов.
        :return: Список словарей с отформатированными данными об отсутствии студентов.
        """
        studentsList =[]
        for i in students:
            studentsList.append(self._formatStudentAbsence(i))
        return studentsList
    
    def _formatRegularLesson(self, lesson:tuple) -> dict[str:any]:
        """
        Форматирует данные о регулярном занятии.

        :param lesson: Кортеж с данными о регулярном занятии.
        :return: Словарь с отформатированными данными о регулярном занятии.
        """
        return {
            'idGroup' : lesson[0],
            'topic' : lesson[1],
            'idsStudents' : lesson[2],
            'location' : lesson[3],
            'teacher' : lesson[4],
            'day' : lesson[5],
            'timeFrom' : lesson[6],
            'timeTo' : lesson[7],
            'assignWorkOffs' : lesson[8],
            'maxStudents' : lesson[9],
            'lastUpdate' : lesson[10]
        }
    
    def _formatStudentAbsence(self, student:tuple) -> dict[str:any]:
        """
        Форматирует данные об отсутствии студента.

        :param student: Кортеж с данными об отсутствии студента.
        :return: Словарь с отформатированными данными об отсутствии студента.
        """
        return {
            'idStudent': student[0],
            'name' : student[1],
            'date' : student[2],
            'topic' : student[3],
            'idGroup' : student[4],
            'idLesson' : student[5],
            'phoneNumber' : student[6],
            'teacher': student[7],
            'workOffScheduled' : student[8],
            'dateNextConnection':student[9],
            'dateLastConnection':student[10],
            'groupForWorkingOut': student[11]

        }
    def _formatGroupOccupancyData(self, group:tuple) -> dict:
        """
    Форматирует данные о заполненности групп.

    :param data: Список кортежей с данными о заполненности групп.
    :return: Список словарей с отформатированными данными.
    """
        return{
            'idGroup': group[0],
            'newStudents': group[1],
            'idsStudents' : group[2],
            'dateOfEvent' : group[3],
            'count' : group[4],
            'lastUpdate': group[5]
        }
    
    def getAllGroupsOccupancy(self, idGroup: int = None) -> str:
        """
        Возвращает строку с информацией о доступных группах.
        Параметры:
        idGroup (bool): Идентификатор группы для фильтрации (по умолчанию None).
        Возвращает:
        str: Строка с информацией о доступных группах, включая тему, локацию, преподавателя, день недели и время занятий.
        """
        groupsOccupancy = self._formatGroupsOccupancyData(self._selectData('GroupOccupancy'))
        string = "Доступные группы:\n"
        for i in groupsOccupancy:
            regularLesson = self._formatRegularLesson(self._selectData('RegularLessons', 'idGroup', i['idGroup'])[0])
            if idGroup != regularLesson['idGroup']:
                if i['count'] < regularLesson['maxStudents']:
                    location =self._formatLocationOrTeacher(self._selectData('Locations', 'id', regularLesson['location'])[0])
                    teacher =self._formatLocationOrTeacher(self._selectData('Teachers', 'id', regularLesson['teacher'])[0])

                    string += f"""
                    Тема : {regularLesson['topic']}, Локация : {location['name']}, Преподаватель: {teacher['name']}, День недели: {getNameDay(regularLesson['day'])},Время начала: {regularLesson['timeFrom']},Время окончания: {regularLesson['timeTo']},Назначать отработки: {assignWorkOffsToText(regularLesson['assignWorkOffs'])}
                    """
        return string
   

    def getStudentAbsences(self) -> list[dict[str:any]]:
        """
        Возвращает список отсутствий студентов с подробной информацией.
        Метод извлекает данные об отсутствиях студентов, форматирует их и добавляет
        информацию о регулярных занятиях, местоположении и преподавателе.
        Returns:
            list[dict[str:any]]: Список словарей, содержащих текстовую информацию об отсутствии
            студентов и идентификатор группы. Каждый словарь имеет следующие ключи:
                - 'text' (str): Текстовая информация об отсутствии студента.
                - 'idGroup' (any): Идентификатор группы студента.
        """
        
        studentAbsences = self._formatStudentsAbsences(self._selectData('StudentAbsences', 'workOffScheduled', 0)) 
        students = []
        for i in studentAbsences:
                regularLesson = self._formatRegularLesson(self._selectData('RegularLessons', 'idGroup', i['idGroup'])[0])
                location =self._formatLocationOrTeacher(self._selectData('Locations', 'id', regularLesson['location'])[0])
                teacher =self._formatLocationOrTeacher(self._selectData('Teachers', 'id', regularLesson['teacher'])[0])
                string = f"""
                Имя ребёнка: {i['name']}
                Тема: {i['topic']}
                Локация: {location['name']}
                Преподаватель: {teacher['name']}
                Дата: {i['date']}
                Телефон: {i['phoneNumber']}
                """
                students.append({'text':string, 'idGroup': int(i['idGroup'])})
        return students
    
    def deleteData(self, tableName:str, field:str, param) -> None:
        """
        Удаляет данные из указанной таблицы.

        :param tableName: Название таблицы.
        :param field: Поле для условия WHERE.
        :param param: Значение для условия WHERE.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute(f"DELETE FROM {tableName} WHERE {field} = ?", [param])
        except sqlite3.Error as e:
            print(f"Ошибка при удалении данных из таблицы {tableName}: {e}")
    
class ContextDataBase:
    def __init__(self, path:str):
        """
        Инициализирует объект базы данных контекста.

        :param path: Путь к файлу базы данных.
        """
        self.path = path
        self._createTables()
    
    def _createTables(self):
        """
        Создает таблицу Context, если она не существует.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS Context(
                    chat TEXT PRIMARY KEY,
                    context TEXT NOT NULL
                    )
                    '''
                    )
        except sqlite3.Error as e:
            print(f"Ошибка при создании таблиц: {e}")
    

    def updateContext(self, chat:str, context:str) -> None:
        """
        Обновляет контекст для указанного чата.

        :param chat: Идентификатор чата.
        :param context: Новый контекст.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute("UPDATE Context SET context = ? WHERE chat = ?", [context, chat])
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении контекста: {e}")
    
    def getContext(self, chat:str) -> str:
        """
        Возвращает контекст для указанного чата.

        :param chat: Идентификатор чата.
        :return: Контекст чата.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute("SELECT context FROM Context WHERE chat = ?", [chat])
                context = cursor.fetchone()
                if context:
                    return list(context[0])
                else:
                    return None
        except sqlite3.Error as e:
            print(f"Ошибка при получении контекста: {e}")

    def findContext(self, chat:str) -> bool:
        """
        Проверяет, существует ли контекст для указанного чата.

        :param chat: Идентификатор чата.
        :return: True, если контекст существует, иначе False.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute("SELECT * FROM Context WHERE chat = ?", [chat])
                context = cursor.fetchone()
                if context:
                    return True
                else:
                    return False
        except sqlite3.Error as e:
            print(f"Ошибка при поиске контекста: {e}")

    def insertContext(self, chat:str, context:str) -> None:
        """
        Вставляет новый контекст для указанного чата.

        :param chat: Идентификатор чата.
        :param context: Контекст чата.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute("INSERT INTO Context (chat, context) VALUES (?,?)", [chat, context])
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении контекста: {e}")

    def __enter__(self):
        """
        Возвращает объект базы данных при входе в контекстный менеджер.
        """
        return DataBase(self.path)
    


    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Выполняет действия при выходе из контекстного менеджера.
        """
        pass
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

def getNameDay(day:int) ->str:
    match(day):
        case 0:
            return 'Понедельник'
        case 1:
            return 'Вторник'
        case 2:
            return 'Среда'
        case 3:
            return 'Четверг'
        case 4:
            return 'Пятница'
        case 5:
            return 'Суббота'
        case 6:
            return 'Воскресенье'
def assignWorkOffsToText(assignWorkOffs:int) -> str:
    match assignWorkOffs:
        case 0:
            return "Не желательно"
        case 1: 
            return "Можно"
        
