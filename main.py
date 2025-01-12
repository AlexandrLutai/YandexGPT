import autorizationData.authorizationData as autorization

from crm.alfaCRM import AlfaCRM, AlfaCRMDataManager, AlfaCRMDBManager
from dataBase.DataBase import DataBase, getDateNextWeekday




db = DataBase()
crm = AlfaCRM(autorization.crmhostname, autorization.crmEmail, autorization.crmKey)
# print(crm.getData('RegularLessons', {}))
crmManager = AlfaCRMDataManager(crm,7,14)

print(db.getAllGroupsOccupancy())

# Связь между lessons и regularLessons устанавливается полем regularId
 
crmToDBManager = AlfaCRMDBManager(db, crmManager)


#Синхронизация бд и CRM
# for i in crmManager.getLocations():
#     db.insertNewLocation(i)

# crmToDBManager.synchroniseTeachers()
# crmToDBManager.synchroniseRegularLessons()
# crmToDBManager.insertInStudentAbsences()
# db.addDataInTableGroupOccupancy()

#Выполняется слишком долго, подумать над хранением данных клиентов локально
#Добавить класс для внесения изменений в AlfaCRM
#Документирование кода 
