import aiosqlite
from functions.functions import async_db_ops, get_date_next_weekday, get_day_name, assign_work_offs_to_text
from mTyping.dictTypes import RegularLessonDict, StudentAbsenceDict, LocationDict, GroupOccupancyDict
from dataBase.databaseManager import DatabaseManager
from dataBase.databaseDataFormatter import DatabaseDataFormatter

class DataBase:
    """
    Создаёт необходимые таблицы и предоставляет интерфейс для работы с ними.
    """
    
    def __init__(self, path: str):
        """
        Инициализирует объект базы данных.
        
        Args:
            path (str): Путь к файлу базы данных.
        """
        self._DBManager = DatabaseManager(path)
        self._DBDataFormatter = DatabaseDataFormatter()

    


    async def add_data_in_table_group_occupancy(self, synchroniseParams: list[int] | None = None) -> None:
        """
        Добавляет данные в таблицу GroupOccupancy.

        Args:
            synchroniseParams (list[int] | None): Параметры для синхронизации.
        """
        try:
            if synchroniseParams:
                await self._DBManager.delete_a_lot_of_data("GroupOccupancy", [{"idGroup": i} for i in synchroniseParams])
            regularLessons = await self._DBManager.select_all_data("RegularLessons")
            await self._DBManager.insert_a_lot_of_unique_data("GroupOccupancy", await self._DBDataFormatter.format_regulars_for_groups_occupancy_data(regularLessons), ["idGroup"])
        except aiosqlite.Error as e:
            print(f"Ошибка при добавлении данных в таблицу GroupOccupancy: {e}")

    async def synchronise_table_regular_lessons(self, groups: list[RegularLessonDict]) -> None:
        """
        Синхронизирует таблицу RegularLessons с предоставленными данными.

        Args:
            groups (list[RegularLessonDict]): Список словарей с данными о регулярных занятиях.
        """
        try:
            await self._DBManager.delete_data("RegularLessons")
            await self._DBManager.insert_a_lot_of_data("RegularLessons", groups)
        except aiosqlite.Error as e:
            print(f"Ошибка при синхронизации таблицы RegularLessons: {e}")

    async def insert_new_location(self, data: LocationDict) -> None:
        """
        Вставляет новую запись в таблицу Locations.

        Args:
            data (LocationDict): Словарь с данными о локации.
        """
        try:
            await self._DBManager.insert_unique_data("Locations", data, {"id": data['id']})
        except aiosqlite.Error as e:
            print(f"Ошибка при добавлении записи в таблицу Locations: {e}")

    async def synchronise_teachers(self, data: list[LocationDict]) -> None:
        """
        Синхронизирует таблицу Teachers с предоставленными данными.

        Args:
            data (list[LocationDict]): Список словарей с данными о преподавателях.
        """
        try:
            await self._DBManager.delete_data("Teachers")
            await self._DBManager.insert_a_lot_of_data("Teachers", data)
        except aiosqlite.Error as e:
            print(f"Ошибка при синхронизации таблицы Teachers: {e}")

    async def fill_table_student_absences(self, students: list[StudentAbsenceDict]) -> None:
        """
        Заполняет таблицу StudentAbsences данными об отсутствии студентов.

        Args:
            students (list[StudentAbsenceDict]): Список словарей с данными об отсутствии студентов.
        """
        try:
            await self._DBManager.insert_a_lot_of_unique_data("StudentAbsences", students, ["idStudent", "idLesson"])
        except aiosqlite.Error as e:
            print(f"Ошибка при заполнении таблицы StudentAbsences: {e}")

    async def get_regular_lessons_ids(self) -> list[int]:
        """
        Возвращает список идентификаторов регулярных занятий.

        Returns:
            list[int]: Список идентификаторов регулярных занятий.
        """
        try:
            groups = await self._DBManager.select_all_data("RegularLessons")
            return [group[0] for group in groups]
        except aiosqlite.Error as e:
            print(f"Ошибка при получении идентификаторов регулярных занятий: {e}")
            return []

    async def get_group_occupancy_data(self, idGroup: int) -> GroupOccupancyDict:
        """
        Возвращает данные о заполненности группы.

        Args:
            idGroup (int): Идентификатор группы.

        Returns:
            GroupOccupancyDict: Словарь с данными о заполненности группы.
        """
        try:
            group = await self._DBManager.select_one_data('GroupOccupancy', {'idGroup': idGroup})
            return await self._DBDataFormatter.format_regular_for_group_occupancy_data(group)
        except aiosqlite.Error as e:
            print(f"Ошибка при получении данных о заполненности группы: {e}")
            return {}

    async def get_available_groups(self, idGroup: int = None, idLocation: str = None) -> str:
        """
        Возвращает строку с информацией о доступных группах.

        Args:
            idGroup (int, optional): Идентификатор группы для фильтрации. Defaults to None.
            idLocation (str, optional): Идентификатор локации для фильтрации. Defaults to None.

        Returns:
            str: Строка с информацией о доступных группах.
        """
        try:
            groupsOccupancy = await self._DBDataFormatter.format_regulars_for_groups_occupancy_data(await self._DBManager.select_all_data('GroupOccupancy'))
            string = "Доступные группы:\n"
            for i in groupsOccupancy:
                regularLesson = await self._DBDataFormatter.format_regular_lesson(await self._DBManager.select_one_data('RegularLessons', {'idGroup': i['idGroup']}))
                if idGroup != regularLesson['idGroup'] and idLocation == regularLesson['location']:
                    if i['count'] < regularLesson['maxStudents']:
                        location = await self._DBDataFormatter.format_location_or_teacher(await self._DBManager.select_one_data('Locations', {'id': regularLesson['location']}))
                        teacher = await self._DBDataFormatter.format_location_or_teacher(await self._DBManager.select_one_data('Teachers', {'id': regularLesson['teacher']}))
                        string += f"""
                        id Группы: {regularLesson['idGroup']}, Основная тема: {regularLesson['topic']}, Темы отработок: {i['worksOffsTopics']}, Локация: {location['name']}, Преподаватель: {teacher['name']}, День недели: {get_day_name(regularLesson['day'])}, Время начала: {regularLesson['timeFrom']}, Время окончания: {regularLesson['timeTo']}, Назначать отработки: {assign_work_offs_to_text(regularLesson['assignWorkOffs'])}
                        """
            return string
        except aiosqlite.Error as e:
            print(f"Ошибка при получении данных о заполненности групп: {e}")
            return ""

    async def get_students_absences_information(self) -> list[StudentAbsenceDict]:
        """
        Возвращает информацию об отсутствии студентов.

        Returns:
            list[StudentAbsenceDict]: Список словарей с данными об отсутствии студентов.
        """
        try:
            studentAbsences = await self._DBDataFormatter.format_students_absences(await self._DBManager.select_all_data('StudentAbsences', {'workOffScheduled': 0}))
            students = []
            for i in studentAbsences:
                regularLesson = await self._DBDataFormatter.format_location_or_teacher(await self._DBManager.select_one_data('RegularLessons', {'idGroup': i['idGroup']}))
                teacher = await self._DBDataFormatter.format_location_or_teacher(await self._DBManager.select_one_data('Teachers', {'id': regularLesson['teacher']}))
                string = f"""
                Имя ребёнка: {i['name']}
                Тема: {i['topic']}
                Преподаватель: {teacher['name']}
                День основного занятия: {get_day_name(regularLesson['day'])}
                Время начала основного занятия: {regularLesson['timeFrom']}
                """
                students.append({'text': string, 'idGroup': int(i['idGroup']), 'location': regularLesson['location'], "phoneNumber": i['phoneNumber']})
            return students
        except aiosqlite.Error as e:
            print(f"Ошибка при получении данных об отсутствии студентов: {e}")
            return []

    async def get_regular_lessons(self, idGroup: int) -> RegularLessonDict:
        """
        Возвращает данные о регулярных занятиях для указанной группы.

        Args:
            idGroup (int): Идентификатор группы.

        Returns:
            RegularLessonDict: Словарь с данными о регулярных занятиях.
        """
        try:
            group = await self._DBManager.select_one_data('RegularLessons', {'idGroup': idGroup})
            return await self._DBDataFormatter.format_regular_lesson(group)
        except aiosqlite.Error as e:
            print(f"Ошибка при получении данных о группе: {e}")
            return {}

    async def get_student(self, phoneNumber: str) -> StudentAbsenceDict:
        """
        Возвращает данные о студенте по номеру телефона.

        Args:
            phoneNumber (str): Номер телефона студента.

        Returns:
            StudentAbsenceDict: Словарь с данными о студенте.
        """
        try:
            student = await self._DBManager.select_one_data('StudentAbsences', {'phoneNumber': phoneNumber})
            return await self._DBDataFormatter.format_student_absence(student)
        except aiosqlite.Error as e:
            print(f"Ошибка при получении данных о студенте: {e}")
            return {}

    async def get_all_locations(self) -> list[LocationDict]:
        """
        Возвращает список всех локаций.

        Returns:
            list[LocationDict]: Список словарей с данными о локациях.
        """
        try:
            locations = await self._DBManager.select_all_data('Locations')
            return await self._DBDataFormatter.format_locations_or_teachers(locations)
        except aiosqlite.Error as e:
            print(f"Ошибка при получении данных о локациях: {e}")
            return []
