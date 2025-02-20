import unittest
import aiounittest
from dataBase.databaseDataFormatter import DatabaseDataFormatter
from mTyping.dictTypes import RegularLessonDict, StudentAbsenceDict, LocationDict, GroupOccupancyDict
from unittest.mock import patch
import datetime

class TestDatabaseDataFormatter(aiounittest.AsyncTestCase):

    def setUp(self):
        self.formatter = DatabaseDataFormatter()

    async def test_format_group_occupancy_data(self):
        group = (1, 'Group 1', '1,2,3', '2025-02-20', '2025-02-20', 0)
        with patch('functions.functions.get_date_next_weekday', return_value=datetime.date(2023, 2, 20)):
            result = await self.formatter.format_group_occupancy_data(group)
            expected = {
                'idGroup': 1,
                'idsStudents': '1,2,3',
                'dateOfEvent': '24.02.2025',
                'count': 3,
                'lastUpdate': datetime.date.today()
            }
            self.assertEqual(result, expected)

    async def test_format_groups_occupancy_data(self):
        groups = [
            (1, 'Group 1', '1,2,3', '2025-02-20', '2025-02-20', 0),
            (2, 'Group 2', '4,5,6', '2025-02-21', '2025-02-21', 1)
        ]
        with patch('functions.functions.get_date_next_weekday', return_value=datetime.date(2023, 2, 20)):
            result = await self.formatter.format_groups_occupancy_data(groups)
            expected = [
                {
                    'idGroup': 1,
                    'idsStudents': '1,2,3',
                    'dateOfEvent': '24.02.2025',
                    'count': 3,
                    'lastUpdate': datetime.date.today()
                },
                {
                    'idGroup': 2,
                    'idsStudents': '4,5,6',
                    'dateOfEvent': '25.02.2025',
                    'count': 3,
                    'lastUpdate': datetime.date.today()
                }
            ]
            self.assertEqual(result, expected)

    async def test_format_locations_or_teachers(self):
        data = [(1, 'Location 1'), (2, 'Teacher 1')]
        result = await self.formatter.format_locations_or_teachers(data)
        expected = [{'id': 1, 'name': 'Location 1'}, {'id': 2, 'name': 'Teacher 1'}]
        self.assertEqual(result, expected)

    async def test_format_location_or_teacher(self):
        data = (1, 'Location 1')
        result = await self.formatter.format_location_or_teacher(data)
        expected = {'id': 1, 'name': 'Location 1'}
        self.assertEqual(result, expected)

    async def test_format_regular_lessons(self):
        lessons = [
            (1, 'Math', '1,2,3', 'Location 1', 'Teacher 1', 0, '09:00', '10:00', 1, 10, '2023-02-20', 1),
            (2, 'Science', '4,5,6', 'Location 2', 'Teacher 2', 1, '10:00', '11:00', 0, 15, '2023-02-21', 2)
        ]
        result = await self.formatter.format_regular_lessons(lessons)
        expected = [
            {
                'idGroup': 1,
                'topic': 'Math',
                'idsStudents': '1,2,3',
                'location': 'Location 1',
                'teacher': 'Teacher 1',
                'day': 0,
                'timeFrom': '09:00',
                'timeTo': '10:00',
                'assignWorkOffs': 1,
                'maxStudents': 10,
                'lastUpdate': '2023-02-20',
                'subjectId': 1
            },
            {
                'idGroup': 2,
                'topic': 'Science',
                'idsStudents': '4,5,6',
                'location': 'Location 2',
                'teacher': 'Teacher 2',
                'day': 1,
                'timeFrom': '10:00',
                'timeTo': '11:00',
                'assignWorkOffs': 0,
                'maxStudents': 15,
                'lastUpdate': '2023-02-21',
                'subjectId': 2
            }
        ]
        self.assertEqual(result, expected)

    async def test_format_regular_lesson(self):
        lesson = (1, 'Math', '1,2,3', 'Location 1', 'Teacher 1', 0, '09:00', '10:00', 1, 10, '2023-02-20', 1)
        result = await self.formatter.format_regular_lesson(lesson)
        expected = {
            'idGroup': 1,
            'topic': 'Math',
            'idsStudents': '1,2,3',
            'location': 'Location 1',
            'teacher': 'Teacher 1',
            'day': 0,
            'timeFrom': '09:00',
            'timeTo': '10:00',
            'assignWorkOffs': 1,
            'maxStudents': 10,
            'lastUpdate': '2023-02-20',
            'subjectId': 1
        }
        self.assertEqual(result, expected)

    async def test_format_students_absences(self):
        students = [
            (1, 'Student 1', '2023-02-20', 'Math', 1, 1, '1234567890', 'Teacher 1', 0, '2023-02-21', '2023-02-19', 1),
            (2, 'Student 2', '2023-02-21', 'Science', 2, 2, '0987654321', 'Teacher 2', 1, '2023-02-22', '2023-02-20', 2)
        ]
        result = await self.formatter.format_students_absences(students)
        expected = [
            {
                'idStudent': 1,
                'name': 'Student 1',
                'date': '2023-02-20',
                'topic': 'Math',
                'idGroup': 1,
                'idLesson': 1,
                'phoneNumber': '1234567890',
                'teacher': 'Teacher 1',
                'workOffScheduled': 0,
                'dateNextConnection': '2023-02-21',
                'dateLastConnection': '2023-02-19',
                'groupForWorkingOut': 1
            },
            {
                'idStudent': 2,
                'name': 'Student 2',
                'date': '2023-02-21',
                'topic': 'Science',
                'idGroup': 2,
                'idLesson': 2,
                'phoneNumber': '0987654321',
                'teacher': 'Teacher 2',
                'workOffScheduled': 1,
                'dateNextConnection': '2023-02-22',
                'dateLastConnection': '2023-02-20',
                'groupForWorkingOut': 2
            }
        ]
        self.assertEqual(result, expected)

    async def test_format_student_absence(self):
        student = (1, 'Student 1', '2023-02-20', 'Math', 1, 1, '1234567890', 'Teacher 1', 0, '2023-02-21', '2023-02-19', 1)
        result = await self.formatter.format_student_absence(student)
        expected = {
            'idStudent': 1,
            'name': 'Student 1',
            'date': '2023-02-20',
            'topic': 'Math',
            'idGroup': 1,
            'idLesson': 1,
            'phoneNumber': '1234567890',
            'teacher': 'Teacher 1',
            'workOffScheduled': 0,
            'dateNextConnection': '2023-02-21',
            'dateLastConnection': '2023-02-19',
            'groupForWorkingOut': 1
        }
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()