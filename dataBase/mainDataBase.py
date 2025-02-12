import sqlite3
from functions.functions import db_ops, getDateNextWeekday, getNameDay, assignWorkOffsToText
import datetime
from mTyping.dictTypes import RegularLessonDict, StudentAbsenceDict, LocationDict, GroupOccupancyDict

class DataBase:
    """Создаёт необходимые таблицы и предоставляет интерфейс для работы с ними"""
    
    def __init__(self, path: str):
        """
        Инициализирует объект базы данных.
        
        Args:
            path (str): Путь к файлу базы данных.
        """
        self.path = path
        self._createTables()

    def _createTables(self):
        """
        Создаёт необходимые таблицы в базе данных.
        """
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
                    lastUpdate TEXT,
                    worksOffsTopics TEXT
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
                    lastUpdate TEXT NOT NULL,
                    subjectId INTEGER 
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
                    groupId = item[0]
                    studentIds = item[2]
                    eventDate = getDateNextWeekday(item[5]).strftime('%d.%m.%Y')
                    studentCount = len(studentIds.split(','))
                    lastUpdate = datetime.date.today()

                    cursor.execute("SELECT * FROM GroupOccupancy WHERE idGroup=?", (groupId,))
                    if not cursor.fetchone():
                        cursor.execute(
                            "INSERT INTO GroupOccupancy (idGroup, idsStudents, dateOfEvent, count, lastUpdate) VALUES (?, ?, ?, ?, ?)", 
                            (groupId, studentIds, eventDate, studentCount, lastUpdate)
                        )
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении данных в таблицу GroupOccupancy: {e}")
    
    def synchroniseTableRegularLessons(self, groups: list[RegularLessonDict]) -> None:
        """
        Синхронизирует таблицу RegularLessons с предоставленными данными.

        Args:
            groups (list[RegularLessonDict]): Список словарей с данными о регулярных занятиях.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute("DELETE FROM RegularLessons")
            with db_ops(self.path) as cursor:
                for group in groups:
                    cursor.execute('INSERT INTO RegularLessons (idGroup,topic,idsStudents,location,teacher,day,timeFrom,timeTo,maxStudents,lastUpdate,subjectId) VALUES(?,?,?,?,?,?,?,?,?,?,?)', 
                                (group['idGroup'], group['topic'],group['idsStudents'], group['location'],group['teacher'],group['day'],group['timeFrom'],group['timeTo'],group['maxStudents'],group['lastUpdate'], group['subjectId']))
        except sqlite3.Error as e:
            print(f"Ошибка при синхронизации таблицы RegularLessons: {e}")
    
    def insertNewLocation(self, data: LocationDict) -> None:
        """
        Вставляет новую запись о локации в таблицу Locations, если запись с таким ID не существует.

        Args:
            data (LocationDict): Словарь с данными о локации.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute("SELECT * FROM Locations WHERE id = ?", [int(data['id'])])
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO Locations (id, name) VALUES (?, ?)", [data['id'], data['name']])
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении записи в таблицу Locations: {e}")
    
    def synchroniseTeachers(self, data: list[LocationDict]) -> None:
        """
        Синхронизирует таблицу Teachers с предоставленными данными.

        Args:
            data (list[LocationDict]): Список словарей с данными о преподавателях.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute("DELETE FROM Teachers")
                for teacher in data:
                    cursor.execute("INSERT INTO Teachers (id, name) VALUES (?, ?)", [teacher['id'], teacher['name']])
        except sqlite3.Error as e:
            print(f"Ошибка при синхронизации таблицы Teachers: {e}")
    
    def fillTableStudentAbsences(self, students: list[StudentAbsenceDict]) -> None:
        """
        Заполняет таблицу StudentAbsences данными об отсутствии студентов.

        Args:
            students (list[StudentAbsenceDict]): Список словарей с данными об отсутствии студентов.
        """
        try:
            with db_ops(self.path) as cursor:
                for i in students:
                    cursor.execute("SELECT * FROM StudentAbsences WHERE idStudent = ? AND idLesson = ?", (i['idStudent'], i['idLesson']))
                    if not cursor.fetchone():
                        cursor.execute(
                            'INSERT INTO StudentAbsences (idStudent, name, date, topic, idGroup, phoneNumber, teacher, idLesson) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
                            (i['idStudent'], i['name'], i['date'], i['topic'], i['idGroup'], i['phoneNumber'], i['teacher'], i['idLesson'])
                        )
        except sqlite3.Error as e:
            print(f"Ошибка при заполнении таблицы StudentAbsences: {e}")
    
    def _formatLocationsOrTeachers(self, data: list[tuple]) -> list[LocationDict]:
        """
        Форматирует данные о локациях или преподавателях.

        Args:
            data (list[tuple]): Список кортежей с данными о локациях или преподавателях.

        Returns:
            list[LocationDict]: Список словарей с отформатированными данными.
        """
        try:
            dicts = []
            for i in data:
                dicts.append(self._formatLocationOrTeacher(i))
            return dicts
        except sqlite3.Error as e:
            print(f"Ошибка при форматировании данных о локациях или преподавателях: {e}")
            return []
    
    def _formatLocationOrTeacher(self, data: tuple) -> LocationDict:
        """
        Форматирует данные о локации или преподавателе.

        Args:
            data (tuple): Кортеж с данными о локации или преподавателе.

        Returns:
            LocationDict: Словарь с отформатированными данными.
        """
        return {'id': data[0], 'name': data[1]}
    
    def getRegularLessonsIds(self) -> list[int]:
        """
        Возвращает список идентификаторов всех регулярных занятий.

        Returns:
            list[int]: Список идентификаторов регулярных занятий.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute("SELECT idGroup FROM RegularLessons")
                groups = cursor.fetchall()
            return [group[0] for group in groups]
        except sqlite3.Error as e:
            print(f"Ошибка при получении идентификаторов регулярных занятий: {e}")
            return []
    
    def _formatGroupsOccupancyData(self, groups: list[tuple]) -> list[GroupOccupancyDict]:
        """
        Форматирует данные о заполненности групп.

        Args:
            groups (list[tuple]): Список кортежей с данными о заполненности групп.

        Returns:
            list[GroupOccupancyDict]: Список словарей с отформатированными данными.
        """
        allGroups = []
        for i in groups:
            allGroups.append(self._formatGroupOccupancyData(i))
        return allGroups
    
    def _selectData(self, tableName: str, field: str = None, param = None) -> list[tuple]:
        """
        Выполняет SELECT запрос к базе данных.

        Args:
            tableName (str): Название таблицы.
            field (str, optional): Поле для условия WHERE. Defaults to None.
            param (optional): Значение для условия WHERE. Defaults to None.

        Returns:
            list[tuple]: Список кортежей с результатами запроса.
        """
        try:
            sql = f"SELECT * FROM {tableName}"
            params = ()
            if param:
                sql += f" WHERE {field} = ?"
                params = (param,)
            with db_ops(self.path) as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка при выполнении SELECT запроса: {e}")
            return []
    
    def updateData(self, data: dict[str, any], tableName: str, selectPams: dict[str, any] | None) -> None:
        """
        Обновляет данные в указанной таблице.

        Args:
            data (dict[str, any]): Словарь с данными для обновления.
            tableName (str): Название таблицы.
            selectPams (dict[str, any] | None): Словарь с параметрами для условия WHERE.
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
    
    def _fromatRegularLessons(self, lessons: list[tuple]) -> list[RegularLessonDict]:
        """
        Форматирует данные о регулярных занятиях.

        Args:
            lessons (list[tuple]): Список кортежей с данными о регулярных занятиях.

        Returns:
            list[RegularLessonDict]: Список словарей с отформатированными данными о регулярных занятиях.
        """
        regularLessonsList = []
        for i in lessons:
            regularLessonsList.append(self._formatRegularLesson(i))
        return regularLessonsList
    
    def _formatStudentsAbsences(self, students: list[tuple]) -> list[StudentAbsenceDict]:
        """
        Форматирует данные об отсутствии студентов.

        Args:
            students (list[tuple]): Список кортежей с данными об отсутствии студентов.

        Returns:
            list[StudentAbsenceDict]: Список словарей с отформатированными данными об отсутствии студентов.
        """
        studentsList = []
        for i in students:
            studentsList.append(self._formatStudentAbsence(i))
        return studentsList
    
    def _formatRegularLesson(self, lesson: tuple) -> RegularLessonDict:
        """
        Форматирует данные о регулярном занятии.

        Args:
            lesson (tuple): Кортеж с данными о регулярном занятии.

        Returns:
            RegularLessonDict: Словарь с отформатированными данными о регулярном занятии.
        """
        return {
            'idGroup': lesson[0],
            'topic': lesson[1],
            'idsStudents': lesson[2],
            'location': lesson[3],
            'teacher': lesson[4],
            'day': lesson[5],
            'timeFrom': lesson[6],
            'timeTo': lesson[7],
            'assignWorkOffs': lesson[8],
            'maxStudents': lesson[9],
            'lastUpdate': lesson[10],
            'subjectId': lesson[11],
        }
    
    def _formatStudentAbsence(self, student: tuple) -> StudentAbsenceDict:
        """
        Форматирует данные об отсутствии студента.

        Args:
            student (tuple): Кортеж с данными об отсутствии студента.

        Returns:
            StudentAbsenceDict: Словарь с отформатированными данными об отсутствии студента.
        """
        return {
            'idStudent': student[0],
            'name': student[1],
            'date': student[2],
            'topic': student[3],
            'idGroup': student[4],
            'idLesson': student[5],
            'phoneNumber': student[6],
            'teacher': student[7],
            'workOffScheduled': student[8],
            'dateNextConnection': student[9],
            'dateLastConnection': student[10],
            'groupForWorkingOut': student[11]
        }
    
    def _formatGroupOccupancyData(self, group: tuple) -> GroupOccupancyDict:
        """
        Форматирует данные о заполненности групп.

        Args:
            group (tuple): Кортеж с данными о заполненности групп.

        Returns:
            GroupOccupancyDict: Словарь с отформатированными данными.
        """
        return {
            'idGroup': group[0],
            'newStudents': group[1],
            'idsStudents': group[2],
            'dateOfEvent': group[3],
            'count': group[4],
            'lastUpdate': group[5],
            'worksOffsTopics': group[6]
        }
    
    def getGroupOccupancyData(self, idGroup: int) -> GroupOccupancyDict:
        """
        Возвращает данные о заполненности группы по идентификатору.

        Args:
            idGroup (int): Идентификатор группы.

        Returns:
            GroupOccupancyDict: Словарь с данными о заполненности группы.
        """
        try:
            group = self._selectOneData('GroupOccupancy', 'idGroup', idGroup)
            return self._formatGroupOccupancyData(group)
        except sqlite3.Error as e:
            print(f"Ошибка при получении данных о заполненности группы: {e}")
            return {}
    
    def getGroupsOccupancy(self, idGroup: int = None, idLocation: str = None) -> str:
        """
        Возвращает строку с информацией о доступных группах.

        Args:
            idGroup (int, optional): Идентификатор группы для фильтрации. Defaults to None.
            idLocation (str, optional): Идентификатор локации для фильтрации. Defaults to None.

        Returns:
            str: Строка с информацией о доступных группах.
        """
        try:
            groupsOccupancy = self._formatGroupsOccupancyData(self._selectData('GroupOccupancy'))
            string = "Доступные группы:\n"
            for i in groupsOccupancy:
                regularLesson = self._formatRegularLesson(self._selectData('RegularLessons', 'idGroup', i['idGroup'])[0])
                if idGroup != regularLesson['idGroup'] and idLocation == regularLesson['location']:
                    if i['count'] < regularLesson['maxStudents']:
                        location = self._formatLocationOrTeacher(self._selectData('Locations', 'id', regularLesson['location'])[0])
                        teacher = self._formatLocationOrTeacher(self._selectData('Teachers', 'id', regularLesson['teacher'])[0])
                        string += f"""
                        id Группы: {regularLesson['idGroup']}, Основная тема: {regularLesson['topic']}, Темы отработок: {i['worksOffsTopics']}, Локация: {location['name']}, Преподаватель: {teacher['name']}, День недели: {getNameDay(regularLesson['day'])}, Время начала: {regularLesson['timeFrom']}, Время окончания: {regularLesson['timeTo']}, Назначать отработки: {assignWorkOffsToText(regularLesson['assignWorkOffs'])}
                        """
            return string
        except sqlite3.Error as e:
            print(f"Ошибка при получении данных о заполненности групп: {e}")
            return ""
    
    def getStudentsAbsences(self) -> list[StudentAbsenceDict]:
        """
        Возвращает список отсутствий студентов с подробной информацией.

        Returns:
            list[StudentAbsenceDict]: Список словарей с данными об отсутствии студентов.
        """
        try:
            studentAbsences = self._formatStudentsAbsences(self._selectData('StudentAbsences', 'workOffScheduled', 0))
            students = []
            for i in studentAbsences:
                regularLesson = self._formatRegularLesson(self._selectData('RegularLessons', 'idGroup', i['idGroup'])[0])
                location = self._formatLocationOrTeacher(self._selectData('Locations', 'id', regularLesson['location'])[0])
                teacher = self._formatLocationOrTeacher(self._selectData('Teachers', 'id', regularLesson['teacher'])[0])
                string = f"""
                Имя ребёнка: {i['name']}
                Тема: {i['topic']}
                Преподаватель: {teacher['name']}
                День основного занятия: {getNameDay(regularLesson['day'])}
                Время начала основного занятия: {regularLesson['timeFrom']}
                """
                students.append({'text': string, 'idGroup': int(i['idGroup']), 'location': regularLesson['location'], "phoneNumber": i['phoneNumber']})
            return students
        except sqlite3.Error as e:
            print(f"Ошибка при получении данных об отсутствии студентов: {e}")
            return []
    
    def deleteData(self, tableName: str, field: str, value: any) -> None:
        """
        Удаляет данные из указанной таблицы.

        Args:
            tableName (str): Название таблицы.
            field (str): Поле для условия WHERE.
            value (any): Значение для условия WHERE.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute(f"DELETE FROM {tableName} WHERE {field} = ?", [value])
        except sqlite3.Error as e:
            print(f"Ошибка при удалении данных из таблицы {tableName}: {e}")
    
    def _selectOneData(self, tableName: str, field: str, param: any) -> tuple:
        """
        Выполняет SELECT запрос к базе данных и возвращает одну запись.

        Args:
            tableName (str): Название таблицы.
            field (str): Поле для условия WHERE.
            param (any): Значение для условия WHERE.

        Returns:
            tuple: Кортеж с результатом запроса.
        """
        try:
            with db_ops(self.path) as cursor:
                cursor.execute(f"SELECT * FROM {tableName} WHERE {field} = ?", [param])
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Ошибка при выполнении SELECT запроса: {e}")
            return ()
    
    def getRegularLessons(self, idGroup: int) -> RegularLessonDict:
        """
        Возвращает данные о группе по идентификатору.

        Args:
            idGroup (int): Идентификатор группы.

        Returns:
            RegularLessonDict: Словарь с данными о группе.
        """
        try:
            group = self._selectOneData('RegularLessons', 'idGroup', idGroup)
            return self._formatRegularLesson(group)
        except sqlite3.Error as e:
            print(f"Ошибка при получении данных о группе: {e}")
            return {}
    
    def getStudent(self, phoneNumber: str) -> StudentAbsenceDict:
        """
        Возвращает данные о студенте по номеру телефона.

        Args:
            phoneNumber (str): Номер телефона студента.

        Returns:
            StudentAbsenceDict: Словарь с данными о студенте.
        """
        try:
            student = self._selectOneData('StudentAbsences', 'phoneNumber', phoneNumber)
            return self._formatStudentAbsence(student)
        except sqlite3.Error as e:
            print(f"Ошибка при получении данных о студенте: {e}")
            return {}
    
    def getAllLocations(self) -> list[LocationDict]:
        """
        Возвращает список локаций.

        Returns:
            list[LocationDict]: Список словарей с данными о локациях.
        """
        try:
            locations = self._selectData('Locations')
            return self._formatLocationsOrTeachers(locations)
        except sqlite3.Error as e:
            print(f"Ошибка при получении данных о локациях: {e}")
            return []
