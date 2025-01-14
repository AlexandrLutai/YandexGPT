import unittest
import os
import sqlite3
from dataBase.DataBase import DataBase, db_ops, getDateNextWeekday

class TestDataBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_db_path = "test_database.db"
        cls.db = DataBase(cls.test_db_path)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.test_db_path)

    def test_createTables(self):
        with db_ops(self.test_db_path) as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            self.assertIn(('StudentAbsences',), tables)
            self.assertIn(('GroupOccupancy',), tables)
            self.assertIn(('RegularLessons',), tables)
            self.assertIn(('Locations',), tables)
            self.assertIn(('Teachers',), tables)

    def test_addDataInTableGroupOccupancy(self):
        # Add initial data to RegularLessons
        with db_ops(self.test_db_path) as cursor:
            cursor.execute('INSERT INTO RegularLessons (idGroup, topic, idsStudents, location, teacher, day, timeFrom, timeTo, maxStudents, lastUpdate) VALUES (1, "Math", "1,2,3", 1, 1, 1, "10:00", "12:00", 30, "2023-01-01")')
        self.db.addDataInTableGroupOccupancy()
        with db_ops(self.test_db_path) as cursor:
            cursor.execute("SELECT * FROM GroupOccupancy WHERE idGroup=1")
            result = cursor.fetchone()
            self.assertIsNotNone(result)

    def test_synchroniseTableRegularLessons(self):
        groups = [
            {
                'idGroup': 1,
                'topic': 'Math',
                'idsStudents': '1,2,3',
                'location': 1,
                'teacher': 1,
                'day': 1,
                'timeFrom': '10:00',
                'timeTo': '12:00',
                'maxStudents': 30,
                'lastUpdate': '2023-01-01'
            }
        ]
        self.db.synchroniseTableRegularLessons(groups)
        with db_ops(self.test_db_path) as cursor:
            cursor.execute("SELECT * FROM RegularLessons WHERE idGroup=1")
            result = cursor.fetchone()
            self.assertIsNotNone(result)

    def test_insertNewLocation(self):
        location = {'id': 1, 'name': 'Room 101'}
        self.db.insertNewLocation(location)
        with db_ops(self.test_db_path) as cursor:
            cursor.execute("SELECT * FROM Locations WHERE id=1")
            result = cursor.fetchone()
            self.assertIsNotNone(result)

    def test_synchroniseTeachers(self):
        teachers = [{'id': 1, 'name': 'John Doe'}]
        self.db.synchroniseTeachers(teachers)
        with db_ops(self.test_db_path) as cursor:
            cursor.execute("SELECT * FROM Teachers WHERE id=1")
            result = cursor.fetchone()
            self.assertIsNotNone(result)

    def test_fillTableStudentAbsences(self):
        students = [
            {
                'idStudent': 1,
                'name': 'Alice',
                'date': '2023-01-01',
                'topic': 'Math',
                'idGroup': 1,
                'phoneNumber': '1234567890',
                'teacher': 1,
                'idLesson': 1
            }
        ]
        self.db.fillTableStudentAbsences(students)
        with db_ops(self.test_db_path) as cursor:
            cursor.execute("SELECT * FROM StudentAbsences WHERE idStudent=1 AND idLesson=1")
            result = cursor.fetchone()
            self.assertIsNotNone(result)

    def test_updateData(self):
        # Insert initial data
        with db_ops(self.test_db_path) as cursor:
            cursor.execute('INSERT INTO RegularLessons (idGroup, topic, idsStudents, location, teacher, day, timeFrom, timeTo, maxStudents, lastUpdate) VALUES (1, "Math", "1,2,3", 1, 1, 1, "10:00", "12:00", 30, "2023-01-01")')
        
        # Update data
        update_data = {'topic': 'Science', 'maxStudents': 25}
        select_params = {'idGroup': 1}
        self.db.updateData(update_data, 'RegularLessons', select_params)
        
        # Verify update
        with db_ops(self.test_db_path) as cursor:
            cursor.execute("SELECT topic, maxStudents FROM RegularLessons WHERE idGroup=1")
            result = cursor.fetchone()
            self.assertEqual(result, ('Science', 25))

    def test_getStudentAbsences(self):
        # Insert initial data
        with db_ops(self.test_db_path) as cursor:
            cursor.execute('INSERT INTO RegularLessons (idGroup, topic, idsStudents, location, teacher, day, timeFrom, timeTo, maxStudents, lastUpdate) VALUES (1, "Math", "1,2,3", 1, 1, 1, "10:00", "12:00", 30, "2023-01-01")')
            cursor.execute('INSERT INTO Locations (id, name) VALUES (1, "Room 101")')
            cursor.execute('INSERT INTO Teachers (id, name) VALUES (1, "John Doe")')
            cursor.execute('INSERT INTO StudentAbsences (idStudent, name, date, topic, idGroup, idLesson, phoneNumber, teacher, workOffScheduled) VALUES (1, "Alice", "2023-01-01", "Math", 1, 1, "1234567890", 1, 0)')
        
        # Get student absences
        absences = self.db.getStudentAbsences()
        
        # Verify absences
        self.assertEqual(len(absences), 1)
        self.assertIn('Alice', absences[0]['text'])
        self.assertIn('Math', absences[0]['text'])
        self.assertIn('Room 101', absences[0]['text'])
        self.assertIn('John Doe', absences[0]['text'])

if __name__ == '__main__':
    unittest.main()
