from dataBase.mainDataBase import DataBase 
from crm.AlfaCRM.alfaCRMDataManager import AlfaCRMDataManager
class AlfaCRMDBManager():

    def __init__(self,dataBase:DataBase, alfaCRMDataManager:AlfaCRMDataManager):
        """
        Инициализирует менеджер базы данных CRM.

        Args:
            dataBase (DataBase): Экземпляр класса DataBase.
            alfaCRMDataManager (AlfaCRMDataManager): Экземпляр класса AlfaCRMDataManager.
        """
        self.db = dataBase
        self.dataManager = alfaCRMDataManager
        pass
    
    def synchroniseTeachers(self):
        """
        Синхронизирует данные учителей с базой данных.
        """
        self.db.synchroniseTeachers(self.dataManager.getTeachers())
        print('synchroniseTeachers Ok')

    def synchroniseRegularLessons(self):
        """
        Синхронизирует регулярные уроки с базой данных.
        """
        locations = self.db.getAllLocations()
        allLessons = []
        for location in locations:
            print(f'synchroniseRegularLessons location {location}')
            lessons = self.dataManager.getRegularLessonsByLocationId(location['id'])
            allLessons+= lessons
        self.db.synchroniseTableRegularLessons(allLessons)
        print(f'synchroniseRegularLessons done')

    def insertInStudentAbsences(self):
        """
        Вставляет данные о пропусках студентов в базу данных.
        """
        idsGroups = self.db.getRegularLessonsIds()
        for i in idsGroups:
            print(" insertInStudentAbsences group id ", i )
            students = self.dataManager.getStudentsMissedLesson(i)
            self.db.fillTableStudentAbsences(students)

    


