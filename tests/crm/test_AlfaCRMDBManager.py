import unittest
import aiounittest
from unittest.mock import AsyncMock, patch
from crm.AlfaCRM.alfaCrmDBManager import AlfaCRMDBManager
from dataBase.databaseManager import DataBaseManager
from crm.AlfaCRM.alfaCRMDataManager import AlfaCRMDataManager

class TestAlfaCRMDBManager(aiounittest.AsyncTestCase):

    def setUp(self):
        self.db = AsyncMock(spec=DataBaseManager)
        self.dataManager = AsyncMock(spec=AlfaCRMDataManager)
        self.manager = AlfaCRMDBManager(self.db, self.dataManager)

    async def test_synchronise_teachers(self):
        self.dataManager.get_teachers.return_value = []
        await self.manager.synchronise_teachers()
        self.db.synchronise_teachers.assert_called_once_with([])

    async def test_synchronise_regular_lessons(self):
        self.db.get_all_locations.return_value = [{'id': 1}, {'id': 2}]
        self.dataManager.get_regular_lessons_by_location_id.side_effect = [
            [{'id': 1, 'name': 'Lesson 1'}],
            [{'id': 2, 'name': 'Lesson 2'}]
        ]
        await self.manager.synchronise_regular_lessons()
        self.db.synchronise_table_regular_lessons.assert_called_once_with(
            [{'id': 1, 'name': 'Lesson 1'}, {'id': 2, 'name': 'Lesson 2'}]
        )

    async def test_insert_in_student_absences(self):
        self.db.get_regular_lessons_ids.return_value = [1, 2]
        self.dataManager.get_students_missed_lesson.side_effect = [
            [{'id': 1, 'name': 'Student 1'}],
            [{'id': 2, 'name': 'Student 2'}]
        ]
        await self.manager.insert_in_student_absences()
        self.db.fill_table_student_absences.assert_any_call([{'id': 1, 'name': 'Student 1'}])
        self.db.fill_table_student_absences.assert_any_call([{'id': 2, 'name': 'Student 2'}])

if __name__ == '__main__':
    unittest.main()