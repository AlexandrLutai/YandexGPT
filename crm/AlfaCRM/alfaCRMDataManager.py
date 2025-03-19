import enum
from datetime import date, datetime, timedelta
from crm.AlfaCRM.alfaCRM import AlfaCRM
from crm.crmDataManagerInterface import CrmDataManagerInterface
from mTyping.dictTypes import CreateLessonModelDict, StudentAbsenceDict, LocationDict, RegularLessonDict
import aiohttp
# Пересмотреть функции доступа к CRM, из-за частых обращений работает крайне долго,
# Подумать над тем, чтобы вытягивать все нужные данные одним запросом.
class AlfaCRMDataManager(CrmDataManagerInterface):
    """
    Форматирует данные при добавлении и получении информации из CRM.

    Атрибуты:
        crm (AlfaCRM): Экземпляр класса AlfaCRM.
        workOffType (AlfaCRMDataManager.WorkOffType): Тип отработки.
        updatePeriodToNextLesson (int): Период обновления до следующего урока.
        updatePeriodToPreviousLesson (int): Период обновления до предыдущего урока.
    """
    class WorkOffType(enum.Enum):
        """
        !!!На будущее!!!
        Варианты добавления отработки в CRM.
        """
        ADD_TO_CURRENT_GROUP = 0
        ADD_TO_NEW_LESSON = 1

    def __init__(self, crm: AlfaCRM, workOffType: 'AlfaCRMDataManager.WorkOffType' = WorkOffType.ADD_TO_NEW_LESSON, updatePeriotByNexLesson: int = 7, updatePeriodByPrevLesson: int = 7):
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

    async def _select_regular_lessons(self, all_lessons: list) -> list:
        """
        Асинхронно получает регулярные уроки из списка всех уроков.

        Args:
            all_lessons (list): Список всех уроков.

        Returns:
            list: Список регулярных уроков.
        """
        return [lesson for lesson in all_lessons if lesson['regular_id'] is not None]

    #Доработать
    async def _get_next_lessons_by_group_id(self, group_id:int ):
        dateNextLesson = date.today() + timedelta(self._updatePeriodToNextLesson)
        data = {'status': 1, 'date_from': date.today().strftime('%y-%m-%d'), 'date_to': dateNextLesson.strftime('%y-%m-%d'), 'page': 0, 'group_ids': [group_id]}

    async def _get_next_lessons_by_location(self, locationId: int) -> list[dict]:
        """
        Асинхронно получает запланированные уроки по идентификатору локации.

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
                temp = await self._crm.get_data("Lessons", data)
              
                if not temp:
                    break
                page += 1
                lessons.extend(await self._select_regular_lessons(temp))
            except aiohttp.ClientConnectionError as e:
                print(f"Ошибка соединения при получении следующих уроков: {e}")
                break
            except aiohttp.ClientResponseError as e:
                print(f"Ошибка ответа сервера при получении следующих уроков: {e}")
                break
            except aiohttp.ClientPayloadError as e:
                print(f"Ошибка загрузки данных при получении следующих уроков: {e}")
                break
            except RuntimeError as e:
                print(f"Ошибка выполнения при получении следующих уроков: {e}")
                break
            except Exception as e:
                print(f"Неизвестная ошибка при получении следующих уроков: {e}")
                break
        return lessons

    async def _get_previus_lesson_by_group_id(self, groupId: int) -> list[dict]:
        """
        Асинхронно получает проведённые уроки по идентификатору группы.

        Args:
            groupId (int): Идентификатор группы.

        Returns:
            list: Список предыдущих уроков.
        """
        datePreviousLesson = date.today() - timedelta(self._updatePeriodToPreviousLesson)
        data = {'status': 3, 'group_id': groupId, 'date_from': datePreviousLesson.strftime('%y-%m-%d'), 'date_to': date.today().strftime('%y-%m-%d')}
        try:
            response = await self._crm.get_data("Lessons", data)
            if response != None:
                return response
            else:
                return False
        except aiohttp.ClientConnectionError as e:
            print(f"Ошибка соединения при получении предыдущих уроков: {e}")
            return []
        except aiohttp.ClientResponseError as e:
            print(f"Ошибка ответа сервера при получении предыдущих уроков: {e}")
            return []
        except Exception as e:
            print(f"Неизвестная ошибка при получении предыдущих уроков: {e}")
            return []

    async def get_locations(self) -> list:
        """
        Асинхронно получает список локаций.

        Returns:
            list: Список локаций.
        """
        try:
            locations = await self._crm.get_data('Locations', {'is_active': 1})
            return await self._format_locations_data(locations)
        except Exception as e:
            print(f"Ошибка при получении локаций: {e}")
            return []

    async def _format_locations_data(self, locations: list) -> list[LocationDict]:
        """
        Асинхронно форматирует данные локаций.

        Args:
            locations (list): Список локаций.

        Returns:
            list: Отформатированный список локаций.
        """
        locationsList = []
        for i in locations:
            locationsList.append({'id': i['id'], 'name': i['name']})
        return locationsList
    
#!!! Переписать Next lesson вообще непонятно для чего!!!!
    async def get_regular_lessons_by_location_id(self, locationId: int) -> list[RegularLessonDict]:
        """
        Асинхронно получает регулярные уроки по идентификатору локации.

        Args:
            locationId (int): Идентификатор локации.

        Returns:
            list: Список регулярных уроков.
        """
        nextLessons = await self._get_next_lessons_by_location(locationId)
        regularLesson = []
        for nextLesson in nextLessons:
                try:
                   
                    
                    regularLesson.append(
                        await self._format_regular_lesson(nextLesson)
                    )
                except Exception as e:
                    print(f"Ошибка при получении регулярных уроков: {e}")
        return regularLesson
    
    async def _format_regular_lesson(self, nextLesson: dict):
        topic = None
        if prevLesson := (await self._get_previus_lesson_by_group_id(nextLesson['group_ids'])[0])[0]:
            topic = prevLesson['topic']
        return {
            'idGroup': nextLesson['group_ids'][0],
            'topic': topic ,
            'idsStudents': str(nextLesson['customer_ids']),
            'location': nextLesson['location_ids'][0],
            'teacher': nextLesson['teacher_ids'][0],
            'day': datetime.strptime(nextLesson['date'], '%Y-%m-%d').weekday(),
            'timeFrom': datetime.strptime(nextLesson['time_from'], '%Y-%m-%d %H:%M:%S').time().strftime('%H:%M'),
            'timeTo': datetime.strptime(nextLesson['time_to'], '%Y-%m-%d %H:%M:%S').time().strftime('%H:%M'),
            'maxStudents': (await self._get_group_by_id(nextLesson['group_ids'][0]))[0]['limit'],
            'lastUpdate': date.today().strftime('Y-%m-%d'),
            'subjectId': nextLesson['subject_id'],
            }
    

    async def _get_group_by_id(self, groupId: int) -> list:
        """
        Асинхронно получает данные группы по идентификатору группы.

        Args:
            groupId (int): Идентификатор группы.

        Returns:
            list: Данные группы.
        """
        try:
            return await self._crm.get_data("Groups", {"id": groupId})
        except Exception as e:
            print(f"Ошибка при получении данных группы: {e}")
            return []

    async def get_teachers(self) -> list[LocationDict]:
        """
        Асинхронно получает список учителей.

        Returns:
            list: Список учителей.
        """
        page = 0
        teachers = []
        while True:
            try:
                teacher = await self._crm.get_data('Teachers', {'removed': 1, 'page': page})
                if not teacher:
                    break
                teachers.append(teacher)
                page += 1
            except Exception as e:
                print(f"Ошибка при получении учителей: {e}")
                break
        return await self._format_teachers_data(teachers)

    async def _format_teachers_data(self, data: list) -> list[LocationDict]:
        """
        Асинхронно форматирует данные учителей.

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

    #Bug - если урок не был заполнен, метод выдаст ошибку, так быть не должно 
    async def get_students_missed_lesson(self, groupId: int) -> list[StudentAbsenceDict] | False:
        """
        Асинхронно получает список студентов, пропустивших урок.

        Args:
            groupId (int): Идентификатор группы.

        Returns:
            list: Список студентов, пропустивших урок.
        """
        try:
            if not (group := (await self._get_previus_lesson_by_group_id(groupId))[0]):
                return False
            skipping = []
            allStudents = await self._get_students()
            for student in group['details']:
                if not student['is_attend']:
                    studentData = await self._find_student(allStudents, 'id', student['customer_id'])
                    if studentData:
                        skipping.append(
                            {
                                'idStudent': student['customer_id'],
                                'date': group['date'],
                                'topic': group['topic'],
                                'idGroup': group['group_ids'][0],
                                'idLesson': group['id'],
                                'teacher': group['teacher_ids'][0],
                                'phoneNumber': studentData['phone'][0].replace('+', '').replace('-', '').replace('(', '').replace(')', ''),
                                'name': studentData['name']
                            }
                        )
            return skipping
        except Exception as e:
            print(f"Ошибка при получении студентов, пропустивших урок: {e}")
            return []

    async def _get_students(self) -> list[dict]:
        """
        Асинхронно получает список студентов из CRM.

        Returns:
            list: Список студентов.
        """
        page = 0
        students = []
        while True:
            try:
                onePage = await self._crm.get_data("Students", {"removed": 0, "is_study": 1, "page": page, 'withGroups': False})
                if not onePage:
                    break
                students.append(onePage)
                page += 1
            except Exception as e:
                print(f"Ошибка при получении студентов: {e}")
                break
        return students

    async def _find_student(self, table: list, key: str, value) -> list:
        """
        Асинхронно находит студента в таблице по ключу и значению.

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

    async def add_work_off(self, data: CreateLessonModelDict) -> None:
        """
        Асинхронно добавляет отработку урока.

        Args:
            data (CreateLessonModelDict): Данные урока.
        """
        if self._workOffType == self.WorkOffType.ADD_TO_CURRENT_GROUP: # Не реализовано
            pass
        elif self._workOffType == self.WorkOffType.ADD_TO_NEW_LESSON:
            data.update({'lesson_type_id': 4})
            await self._create_new_lesson(data)

    async def _create_new_lesson(self, data: CreateLessonModelDict) -> str:
        """
        Асинхронно создает новый урок.

        Args:
            data (CreateLessonModelDict): Данные урока.

        Returns:
            str: Ответ от сервера.
        """
        try:
            return await self._crm.create_model("Lessons", data)
        except Exception as e:
            print(f"Ошибка при создании нового урока: {e}")
            return ""

    #новый метод
    async def get_lesson_by_id(self, id_group:int) -> RegularLessonDict:
        return self._
        pass
    
