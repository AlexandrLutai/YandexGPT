import unittest
from unittest.mock import AsyncMock, patch
from YandexGPT.messageAnalyzer import MessageAnalyzer
from mTyping.dictTypes import MessageForAnalyzeDict
import datetime
import asyncio

class TestMessageAnalyzer(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.mock_db = AsyncMock()
        self.mock_crm = AsyncMock()
        self.mock_chatAnalyzer = AsyncMock()
        self.message_analyzer = MessageAnalyzer(self.mock_chatAnalyzer, self.mock_db, self.mock_crm)

    async def test_analyze_GPT_answer(self):
        data = {
            'chatId': '12345',
            'text': 'Hello'
        }
        result = await self.message_analyzer.analyze_GPT_answer(data)
        self.assertEqual(result, 'Hello')

    async def test_analyze_system_message(self):
        data = {
            'chatId': '12345',
            'text': 'отработк|success|1'
        }
        with patch.object(self.message_analyzer, '_process_work_off_message', new_callable=AsyncMock) as mock_process:
            result = await self.message_analyzer._analyze_system_message(data)
            mock_process.assert_called_once_with(data)
            self.assertEqual(result, '1')

    async def test_work_off_success(self):
        data = {
            'chatId': '12345',
            'text': 'отработк|success|1'
        }
        self.mock_db.get_student.return_value = {'idStudent': 1, 'topic': 'Math', 'idLesson': 1}
        self.mock_db.get_regular_lessons.return_value = {'timeFrom': '10:00', 'timeTo': '11:00', 'subjectId': 1, 'teacher': 1}
        self.mock_db.get_group_occupancy_data.return_value = {'dateOfEvent': '2025-02-19', 'count': 1, 'newStudents': ''}

        await self.message_analyzer._work_off_success(data)

        self.mock_db.get_student.assert_called_once_with('12345')
        self.mock_db.get_regular_lessons.assert_called_once_with(1)
        self.mock_db.get_group_occupancy_data.assert_called_once_with(1)
        self.mock_crm.add_work_off.assert_called_once()
        self.mock_db.update_data.assert_called()

    async def test_work_off_fail(self):
        data = {
            'chatId': '12345',
            'text': 'отработк|fail|1'
        }
        with patch('YandexGPT.messageAnalyzer.get_date_next_weekday', new_callable=AsyncMock) as mock_get_date:
            mock_get_date.return_value = datetime.datetime(2025, 2, 26)
            await self.message_analyzer._work_off_fail(data)

            self.mock_db.update_data.assert_called_once()

if __name__ == '__main__':
    unittest.main()