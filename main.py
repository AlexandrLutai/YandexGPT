import autorizationData.authorizationData as autorization
from crm.alfaCRM import AlfaCRM, AlfaCRMDataManager, AlfaCRMDBManager
from dataBase.localDB import DataBase, getDateNextWeekday
db = DataBase()
crm = AlfaCRM(autorization.crmhostname, autorization.crmEmail, autorization.crmKey)

crmManager = AlfaCRMDataManager(crm,7,14)

crmToDBManager = AlfaCRMDBManager(db, crmManager)

for i in crmManager.getLocations():
    db.insertNewLocation(i)

crmToDBManager.synchroniseTeachers()
crmToDBManager.synchroniseRegularLessons()
crmToDBManager.insertInStudentAbsences()
db.addDataInTableGroupOccupancy()

#Выполняется слишком долго, подумать над хранением данных клиентов локально
#Добавить класс для внесения изменений в AlfaCRM
#Документирование кода 
