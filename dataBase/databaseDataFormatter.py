from mTyping.dictTypes import RegularLessonDict, StudentAbsenceDict, LocationDict, GroupOccupancyDict
import aiosqlite
import datetime
from functions.functions import get_date_next_weekday

class DatabaseDataFormatter:
    """
    Класс для форматирования данных из базы данных.
    """

    async def format_group_occupancy_data(self, group: tuple) -> GroupOccupancyDict:
        """
        Асинхронно форматирует данные о заполненности группы.

        Args:
            group (tuple): Кортеж с данными о заполненности группы.

        Returns:
            GroupOccupancyDict: Словарь с отформатированными данными о заполненности группы.
        """
        return {
            'idGroup': group[0],
            'idsStudents': group[2],
            'dateOfEvent': (await get_date_next_weekday(group[5])).strftime('%d.%m.%Y'),
            'count': len(group[2].split(',')),
            'lastUpdate': datetime.date.today()
        }

    async def format_groups_occupancy_data(self, groups: list[tuple]) -> list[GroupOccupancyDict]:
        """
        Асинхронно форматирует данные о заполненности групп.

        Args:
            groups (list[tuple]): Список кортежей с данными о заполненности групп.

        Returns:
            list[GroupOccupancyDict]: Список словарей с отформатированными данными о заполненности групп.
        """
        allGroups = []
        for i in groups:
            allGroups.append(await self.format_group_occupancy_data(i))
        return allGroups

    async def format_locations_or_teachers(self, data: list[tuple]) -> list[LocationDict]:
        """
        Асинхронно форматирует данные о локациях или преподавателях.

        Args:
            data (list[tuple]): Список кортежей с данными о локациях или преподавателях.

        Returns:
            list[LocationDict]: Список словарей с отформатированными данными.
        """
        try:
            dicts = []
            for i in data:
                dicts.append(await self.format_location_or_teacher(i))
            return dicts
        except aiosqlite.Error as e:
            print(f"Ошибка при форматировании данных о локациях или преподавателях: {e}")
            return []

    async def format_location_or_teacher(self, data: tuple) -> LocationDict:
        """
        Асинхронно форматирует данные о локации или преподавателе.

        Args:
            data (tuple): Кортеж с данными о локации или преподавателе.

        Returns:
            LocationDict: Словарь с отформатированными данными.
        """
        return {'id': data[0], 'name': data[1]}

    async def format_regular_lessons(self, lessons: list[tuple]) -> list[RegularLessonDict]:
        """
        Асинхронно форматирует данные о регулярных занятиях.

        Args:
            lessons (list[tuple]): Список кортежей с данными о регулярных занятиях.

        Returns:
            list[RegularLessonDict]: Список словарей с отформатированными данными о регулярных занятиях.
        """
        regularLessonsList = []
        for i in lessons:
            regularLessonsList.append(await self.format_regular_lesson(i))
        return regularLessonsList

    async def format_regular_lesson(self, lesson: tuple) -> RegularLessonDict:
        """
        Асинхронно форматирует данные о регулярном занятии.

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

    async def format_students_absences(self, students: list[tuple]) -> list[StudentAbsenceDict]:
        """
        Асинхронно форматирует данные об отсутствии студентов.

        Args:
            students (list[tuple]): Список кортежей с данными об отсутствии студентов.

        Returns:
            list[StudentAbsenceDict]: Список словарей с отформатированными данными об отсутствии студентов.
        """
        studentsList = []
        for i in students:
            studentsList.append(await self.format_student_absence(i))
        return studentsList

    async def format_student_absence(self, student: tuple) -> StudentAbsenceDict:
        """
        Асинхронно форматирует данные об отсутствии студента.

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