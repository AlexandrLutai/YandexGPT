from datetime import date, datetime, timedelta
from crm.crmDataManagerInterface import CrmDataManagerInterface
from crm.AlfaCRM.alfaCRM import AlfaCRM
import enum
from mTyping.dictTypes import CreateLessonModelDict, StudentAbsenceDict, LocationDict, RegularLessonDict

#Пересмотреть функции доступа к CRM, из за частых обращений работает крайне долго,
#Подумать над тем, что бы вытягивать все нужные данные одним запросом.
class AlfaCRMDataManager(CrmDataManagerInterface):
    class WorkOffType(enum.Enum):
        ADD_TO_CURRENT_GROUP = 0
        ADD_TO_NEW_LESSON = 1
    
    def __init__(self, crm:AlfaCRM, workOffType: 'AlfaCRMDataManager.WorkOffType' = WorkOffType.ADD_TO_NEW_LESSON, updatePeriotByNexLesson:int = 7, updatePeriodByPrevLesson:int = 7):
        """
        Инициализирует менеджер данных CRM.

        Args:
            crm (AlfaCRM): Экземпляр класса AlfaCRM.
            workOffType (AlfaCRMDataManager.WorkOffType): Тип отработки.
            updatePeriotByNexLesson (int): Период обновления до следующего урока.
            updatePeriodByPrevLesson (int): Период обновления до предыдущего урока.
        """
        self._crm = crm
        self._workOffType = workOffType
        self._updatePeriodToNextLesson = updatePeriotByNexLesson
        self._updatePeriodToPreviousLesson = updatePeriodByPrevLesson

    def _getRegularLessons(self, allLessons:list) -> list:
        """
        Получает регулярные уроки из списка всех уроков.

        Args:
            allLessons (list): Список всех уроков.

        Returns:
            list: Список регулярных уроков.
        """
        # regularLessons = []
        # for i in allLessons:
        #     if i['regular_id'] != None:
        #         regularLessons.append(i)
        # return regularLessons
        return [lesson for lesson in allLessons if lesson['regular_id'] is not None]
    
    def _getNextLessonsByLocation(self, locationId:int) -> list[dict]:
        """
        Получает следующие уроки по идентификатору локации.

        Args:
            locationId (int): Идентификатор локации.

        Returns:
            list: Список следующих уроков.
        """
        page = 0 
        dateNextLesson = date.today() + timedelta(self._updatePeriodToNextLesson)
        data = {'status': 1, 'date_from': date.today().strftime('%y-%m-%d'), 'date_to': dateNextLesson.strftime('%y-%m-%d'), 'page': page, 'location_ids': [locationId]}
        lessons = []
        while True:
            data['page'] = page
            try:
                temp = self._crm.getItems(self._crm.getData("Lessons", data))
                if not temp:
                    break
                page += 1
                lessons.append(self._getRegularLessons(temp))
            except Exception as e:
                print(f"Ошибка при получении следующих уроков: {e}")
                break
        return lessons
    
    def _getPreviusLessonByGroupId(self, groupId:int) -> list[dict]:
        """
        Получает предыдущие уроки по идентификатору группы.

        Args:
            groupId (int): Идентификатор группы.

        Returns:
            list: Список предыдущих уроков.
        """
        datePreviousLesson = date.today() - timedelta(self._updatePeriodToPreviousLesson)
        data = {'status': 3, 'group_id': groupId, 'date_from': datePreviousLesson.strftime('%y-%m-%d'), 'date_to': date.today().strftime('%y-%m-%d')}
        try:
            return self._crm.getItems(self._crm.getData("Lessons", data))
        except Exception as e:
            print(f"Ошибка при получении предыдущих уроков: {e}")
            return []
    
    def getLocations(self) -> list:
        """
        Получает список локаций.

        Returns:
            list: Список локаций.
        """
        try:
            locations = self._crm.getItems(self._crm.getData('Locations', {'is_active': 1}))
            return self._formatLocationsData(locations)
        except Exception as e:
            print(f"Ошибка при получении локаций: {e}")
            return []
    
    def _formatLocationsData(self, locations:list) -> list[LocationDict]:
        """
        Форматирует данные локаций.

        Args:
            locations (list): Список локаций.

        Returns:
            list: Отформатированный список локаций.
        """
        locationsList = []
        for i in locations:
            locationsList.append({'id': i['id'], 'name': i['name']})
        return locationsList
    
    def getRegularLessonsByLocationId(self, locationId:int) -> list[RegularLessonDict]:
        """
        Получает регулярные уроки по идентификатору локации.

        Args:
            locationId (int): Идентификатор локации.

        Returns:
            list: Список регулярных уроков.
        """
        nextLesson = self._getNextLessonsByLocation(locationId)
        regularLesson = []
        for page in nextLesson:
            for item in page:
                try:
                    groupId = item['group_ids'][0]
                    prev = self._getPreviusLessonByGroupId(groupId)[0]
                    regularLesson.append(
                        {
                            'idGroup': groupId,
                            'topic': prev['topic'],
                            'idsStudents': str(item['customer_ids']),
                            'location': locationId,
                            'teacher': item['teacher_ids'][0],
                            'day': datetime.strptime(item['date'], '%Y-%m-%d').weekday(),
                            'timeFrom': datetime.strptime(item['time_from'], '%Y-%m-%d %H:%M:%S').time().strftime('%H:%M'),
                            'timeTo': datetime.strptime(item['time_to'], '%Y-%m-%d %H:%M:%S').time().strftime('%H:%M'),
                            'maxStudents': self._getGroupById(groupId)[0]['limit'],
                            'lastUpdate': date.today().strftime('Y-%m-%d'),
                            'subjectId': item['subject_id'],
                        }
                    )
                except Exception as e:
                    print(f"Ошибка при получении регулярных уроков: {e}")
        return regularLesson

    def _getGroupById(self, groupId:int) -> list:
        """
        Получает данные группы по идентификатору группы.

        Args:
            groupId (int): Идентификатор группы.

        Returns:
            list: Данные группы.
        """
        try:
            return self._crm.getItems(self._crm.getData("Groups", {"id": groupId}))
        except Exception as e:
            print(f"Ошибка при получении данных группы: {e}")
            return []
    
    def getTeachers(self) -> list:
        """
        Получает список учителей.

        Returns:
            list: Список учителей.
        """
        page = 0
        teachers = []
        while True:
            try:
                l = self._crm.getItems(self._crm.getData('Teachers', {'removed': 1, 'page': page}))
                if not l:
                    break
                teachers.append(l)
                page += 1
            except Exception as e:
                print(f"Ошибка при получении учителей: {e}")
                break
        return self._formatTeachersData(teachers)

    def _formatTeachersData(self, data:list) -> list:
        """
        Форматирует данные учителей.

        Args:
            data (list): Список данных учителей.

        Returns:
            list: Отформатированный список учителей.
        """
        teachers = []
        for page in data:
            for item in page:
                teachers.append({'id': item['id'], 'name': item['name']})
        return teachers
    
    def getStudentsMissedLesson(self, groupId:int) -> list[StudentAbsenceDict]:
        """
        Получает список студентов, пропустивших урок.

        Args:
            groupId (int): Идентификатор группы.

        Returns:
            list: Список студентов, пропустивших урок.
        """
        try:
            group = self._getPreviusLessonByGroupId(groupId)[0]
            skipping = []
            allStudents = self._getStudents()
            for student in group['details']:
                if not student['is_attend']:
                    studentData = self._findStudent(allStudents, 'id', student['customer_id'])
                    if studentData:
                        skipping.append(
                            {
                                'idStudent': student['customer_id'],
                                'date': group['date'],
                                'topic': group['topic'],
                                'idGroup': group['group_ids'][0],
                                'idLesson': group['id'],
                                'teacher': group['teacher_ids'][0],
                                'phoneNumber': studentData['phone'][0].replace('+()-', ''),
                                'name': studentData['name']
                            }
                        )
            return skipping
        except Exception as e:
            print(f"Ошибка при получении студентов, пропустивших урок: {e}")
            return []

    def _getStudents(self) -> list:
        """
        Получает список студентов.

        Returns:
            list: Список студентов.
        """
        page = 0
        students = []
        while True:
            try:
                onePage = self._crm.getItems(self._crm.getData("Students", {"removed": 0, "is_study": 1, "page": page, 'withGroups': False}))
                if not onePage:
                    break
                students.append(onePage)
                page += 1
            except Exception as e:
                print(f"Ошибка при получении студентов: {e}")
                break
        return students
    
    def _findStudent(self, table:list, key:str, value) -> list:
        """
        Находит студента в таблице по ключу и значению.

        Args:
            table (list): Таблица студентов.
            key (str): Ключ для поиска.
            value: Значение для поиска.

        Returns:
            dict: Данные студента.
        """
        for page in table:
            for record in page:
                if record[key] == value:
                    return record
        return []
    
    def addWorkOff(self, data:CreateLessonModelDict) -> None:
        """
        Добавляет отработку урока.

        Args:
            data (CreateLessonModelDict): Данные урока.
        """
        if self._workOffType == self.WorkOffType.ADD_TO_CURRENT_GROUP:
            pass
        elif self._workOffType == self.WorkOffType.ADD_TO_NEW_LESSON:
            data.update({'lesson_type_id': 4})
            self._createNewLesson(data)
    
    def _createNewLesson(self, data:CreateLessonModelDict) -> str:
        """
        Создает новый урок.

        Args:
            data (CreateLessonModelDict): Данные урока.

        Returns:
            str: Ответ от сервера.
        """
        try:
            return self._crm.createModel("Lessons", data)
        except Exception as e:
            print(f"Ошибка при создании нового урока: {e}")
            return ""
