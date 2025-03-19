from crm.crmDataManagerInterface import CrmDataManagerInterface
from crm.crmDBManagerInterface import CrmDBManagerInterface
from dataBase.databaseManager import DataBaseManager


class DataSynchronizer:

    def __init__(self, crmDataManger:CrmDataManagerInterface, crmDBManager:CrmDBManagerInterface, dbManager:DataBaseManager):
        self.crmDataManager = crmDataManger
        self.crmDBManager = crmDBManager
        self.dbManager = dbManager
        self.datesOfUpdate = {}
        pass

    async def init(self):
        locations = await self.crmManager.get_locations()
        await self.dbManager.synchronise_teachers_and_locations(locations)
        await self.crmDBManager.synchronise_teachers()
        await self.crmDBManager.synchronise_regular_lessons()
        await self.crmDBManager.insert_in_student_absences()
        await self.dbManager.add_data_in_table_group_occupancy()

        self.datesOfUpdate = self.dbManager.get_lessons_event_date()

    async def start(self):

        pass
    
    

    async def _updateLessonsData(self):

        pass