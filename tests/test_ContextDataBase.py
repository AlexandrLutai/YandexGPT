import unittest
import os
import sqlite3
from dataBase.DataBase import ContextDataBase, db_ops

class TestContextDataBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_db_path = "test_context_database.db"
        cls.db = ContextDataBase(cls.test_db_path)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.test_db_path)

    def test_createTables(self):
        with db_ops(self.test_db_path) as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            self.assertIn(('Context',), tables)

    def test_insertContext(self):
        self.db.insertContext('chat1', 'context1')
        with db_ops(self.test_db_path) as cursor:
            cursor.execute("SELECT context FROM Context WHERE chat='chat1'")
            result = cursor.fetchone()
            self.assertIsNotNone(result)
            self.assertEqual(result[0], 'context1')

    def test_updateContext(self):
        self.db.insertContext('chat2', 'context2')
        self.db.updateContext('chat2', 'new_context2')
        with db_ops(self.test_db_path) as cursor:
            cursor.execute("SELECT context FROM Context WHERE chat='chat2'")
            result = cursor.fetchone()
            self.assertIsNotNone(result)
            self.assertEqual(result[0], 'new_context2')

    def test_getContext(self):
        self.db.insertContext('chat3', 'context3')
        context = self.db.getContext('chat3')
        self.assertEqual(context, 'context3')

    def test_findContext(self):
        self.db.insertContext('chat4', 'context4')
        exists = self.db.findContext('chat4')
        self.assertTrue(exists)
        not_exists = self.db.findContext('chat5')
        self.assertFalse(not_exists)

if __name__ == '__main__':
    unittest.main()
