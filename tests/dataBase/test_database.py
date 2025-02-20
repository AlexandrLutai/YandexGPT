import unittest
import aiounittest
from unittest.mock import AsyncMock, patch
from dataBase.database import DataBase
from mTyping.dictTypes import RegularLessonDict, StudentAbsenceDict, LocationDict, GroupOccupancyDict

class TestDataBase(aiounittest.AsyncTestCase):

    def setUp(self):
        self.db = DataBase('test.db')
        self.db._DBManager = AsyncMock()
        self.db._DBDataFormatter = AsyncMock()

    async def test_add_data_in_table_group_occupancy(self):
        self.db._DBManager.select_all_data.return_value = []
        self.db._DBDataFormatter.format_groups_occupancy_data.return_value = []
        await self.db.add_data_in_table_group_occupancy()
        self.db._DBManager.select_all_data.assert_called_once_with("RegularLessons")
        self.db._DBManager.insert_a_lot_of_unique_data.assert_called_once()

    async def test_synchronise_table_regular_lessons(self):
        groups = []
        await self.db.synchronise_table_regular_lessons(groups)
        self.db._DBManager.delete_data.assert_called_once_with("RegularLessons")
        self.db._DBManager.insert_a_lot_of_data.assert_called_once_with("RegularLessons", groups)

    async def test_insert_new_location(self):
        data = {'id': 1, 'name': 'Test Location'}
        await self.db.insert_new_location(data)
        self.db._DBManager.insert_unique_data.assert_called_once_with("Locations", data, {"id": data['id']})

    async def test_synchronise_teachers(self):
        data = []
        await self.db.synchronise_teachers(data)
        self.db._DBManager.delete_data.assert_called_once_with("Teachers")
        self.db._DBManager.insert_a_lot_of_data.assert_called_once_with("Teachers", data)

    async def test_fill_table_student_absences(self):
        students = []
        await self.db.fill_table_student_absences(students)
        self.db._DBManager.insert_a_lot_of_unique_data.assert_called_once_with("StudentAbsences", students, ["idStudent", "idLesson"])

    async def test_get_regular_lessons_ids(self):
        self.db._DBManager.select_all_data.return_value = [(1,), (2,)]
        result = await self.db.get_regular_lessons_ids()
        self.assertEqual(result, [1, 2])

    async def test_get_group_occupancy_data(self):
        self.db._DBManager.select_one_data.return_value = {}
        self.db._DBDataFormatter.format_group_occupancy_data.return_value = {}
        result = await self.db.get_group_occupancy_data(1)
        self.assertEqual(result, {})
        self.db._DBManager.select_one_data.assert_called_once_with('GroupOccupancy', {'idGroup': 1})

    async def test_get_all_locations(self):
        self.db._DBManager.select_all_data.return_value = []
        self.db._DBDataFormatter.format_locations_or_teachers.return_value = []
        result = await self.db.get_all_locations()
        self.assertEqual(result, [])
        self.db._DBManager.select_all_data.assert_called_once_with('Locations')

if __name__ == '__main__':
    unittest.main()