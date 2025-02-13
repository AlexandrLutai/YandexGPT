from dataBase.database import DataBase 
from crm.AlfaCRM.alfaCRMDataManager import AlfaCRMDataManager

class AlfaCRMDBManager:
    """
    Добавляет данные из CRM в базу данных.
    """
    def __init__(self, dataBase:DataBase, alfaCRMDataManager:AlfaCRMDataManager):
        """
        Инициализирует менеджер базы данных CRM.

        Args:
            dataBase (DataBase): Экземпляр класса DataBase.
            alfaCRMDataManager (AlfaCRMDataManager): Экземпляр класса AlfaCRMDataManager.
        """
        self.db = dataBase
        self.dataManager = alfaCRMDataManager

    def synchronise_teachers(self):
        """
        Синхронизирует данные учителей с базой данных.
        """
        try:
            self.db.synchronise_teachers(self.dataManager.get_teachers())
            print('synchroniseTeachers Ok')
        except Exception as e:
            print(f"Ошибка при синхронизации учителей: {e}")

    def synchronise_regular_lessons(self):
        """
        Синхронизирует регулярные уроки с базой данных.
        """
        try:
            locations = self.db.get_all_locations()
            allLessons = []
            for location in locations:
                print(f'synchroniseRegularLessons location {location}')
                lessons = self.dataManager.get_regular_lessons_by_location_id(location['id'])
                allLessons += lessons
            self.db.synchronise_table_regular_lessons(allLessons)
            print(f'synchroniseRegularLessons done')
        except Exception as e:
            print(f"Ошибка при синхронизации регулярных уроков: {e}")

    def insert_in_student_absences(self):
        """
        Вставляет данные о пропусках студентов в базу данных.
        """
        try:
            idsGroups = self.db.get_regular_lessons_ids()
            for i in idsGroups:
                print(" insertInStudentAbsences group id ", i)
                students = self.dataManager.get_students_missed_lesson(i)
                self.db.fill_table_student_absences(students)
        except Exception as e:
            print(f"Ошибка при вставке данных о пропусках студентов: {e}")




