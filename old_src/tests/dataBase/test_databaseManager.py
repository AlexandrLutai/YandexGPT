import unittest
import aiounittest
from unittest.mock import AsyncMock, patch, MagicMock
from dataBase.database import Database
import aiosqlite

class TestDatabaseManager(aiounittest.AsyncTestCase):

    def setUp(self):
        self.db_manager = Database('test.db')

    @patch('dataBase.databaseManager.async_db_ops')
    async def test_insert_data(self, mock_db_ops):
        mock_cursor = AsyncMock()
        mock_db_ops.return_value.__aenter__.return_value = mock_cursor
        data = {'id': 1, 'name': 'Test'}
        await self.db_manager.insert_data('TestTable', data)
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO TestTable (id,name) VALUES (?,?)", (1, 'Test')
        )

    @patch('dataBase.databaseManager.async_db_ops')
    async def test_insert_unique_data(self, mock_db_ops):
        mock_cursor = AsyncMock()
        mock_db_ops.return_value.__aenter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        data = {'id': 1, 'name': 'Test'}
        selected_params = {'id': 1}
        await self.db_manager.insert_unique_data('TestTable', data, selected_params)
        mock_cursor.execute.assert_any_call(
            "SELECT * FROM TestTable WHERE id = ?", (1,)
        )
        mock_cursor.execute.assert_any_call(
            "INSERT INTO TestTable (id,name) VALUES (?,?)", (1, 'Test')
        )

    @patch('dataBase.databaseManager.async_db_ops')
    async def test_clear_table(self, mock_db_ops):
        mock_cursor = AsyncMock()
        mock_db_ops.return_value.__aenter__.return_value = mock_cursor
        await self.db_manager.clear_table('TestTable')
        mock_cursor.execute.assert_called_once_with("DELETE FROM TestTable")

    @patch('dataBase.databaseManager.async_db_ops')
    async def test_select_all_data(self, mock_db_ops):
        mock_cursor = AsyncMock()
        mock_db_ops.return_value.__aenter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1, 'Test')]
        result = await self.db_manager.select_all_data('TestTable')
        mock_cursor.execute.assert_called_once_with("SELECT * FROM TestTable", ())
        self.assertEqual(result, [(1, 'Test')])

    @patch('dataBase.databaseManager.async_db_ops')
    async def test_select_one_data(self, mock_db_ops):
        mock_cursor = AsyncMock()
        mock_db_ops.return_value.__aenter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, 'Test')
        result = await self.db_manager.select_one_data('TestTable', {'id': 1})
        mock_cursor.execute.assert_called_once_with("SELECT * FROM TestTable WHERE id = ?", (1,))
        self.assertEqual(result, (1, 'Test'))

    @patch('dataBase.databaseManager.async_db_ops')
    async def test_update_data(self, mock_db_ops):
        mock_cursor = AsyncMock()
        mock_db_ops.return_value.__aenter__.return_value = mock_cursor
        data = {'name': 'Updated'}
        select_params = {'id': 1}
        await self.db_manager.update_data(data, 'TestTable', select_params)
        mock_cursor.execute.assert_called_once_with(
            "UPDATE TestTable SET name = ? WHERE id = ?", ('Updated', 1)
        )

    @patch('dataBase.databaseManager.async_db_ops')
    async def test_delete_data(self, mock_db_ops):
        mock_cursor = AsyncMock()
        mock_db_ops.return_value.__aenter__.return_value = mock_cursor
        await self.db_manager.delete_data('TestTable', {'id': 1})
        mock_cursor.execute.assert_called_once_with("DELETE FROM TestTable WHERE id = ?", (1,))

    @patch('dataBase.databaseManager.async_db_ops')
    async def test_delete_a_lot_of_data(self, mock_db_ops):
        mock_cursor = AsyncMock()
        mock_db_ops.return_value.__aenter__.return_value = mock_cursor
        data = [{'id': 1}, {'id': 2}]
        await self.db_manager.delete_a_lot_of_data('TestTable', data)
        mock_cursor.execute.assert_any_call("DELETE FROM TestTable WHERE id = ?", (1,))
        mock_cursor.execute.assert_any_call("DELETE FROM TestTable WHERE id = ?", (2,))

if __name__ == '__main__':
    unittest.main()