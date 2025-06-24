from crm.crmDataManagerInterface import CrmDataManagerInterface
from crm.crmDBManagerInterface import CrmDBManagerInterface
from dataBase.databaseManager import DataBaseManager
from datetime import datetime

class DataSynchronizer:

    def __init__(self, crmDataManger:CrmDataManagerInterface, crmDBManager:CrmDBManagerInterface, dbManager:DataBaseManager):
        self._crmDataManager = crmDataManger
        self._crmDBManager = crmDBManager
        self._dbManager = dbManager
        self._datesOfUpdate = {}
        pass

    async def init(self):
        locations = await self._crmDataManager.get_locations()
        await self._dbManager.synchronise_teachers_and_locations(locations)
        await self._crmDBManager.synchronise_teachers()
        await self._crmDBManager.synchronise_regular_lessons()
        await self._crmDBManager.insert_in_student_absences()
        await self._dbManager.add_data_in_table_group_occupancy()

        self._datesOfUpdate = self._dbManager.get_lessons_event_date()

    async def start(self):

        pass
    
    

    async def _updateLessonsData(self):
        for lesson_id, event_date in self._datesOfUpdate.items():
            if event_date < datetime.now().date():
                
                pass
            
        