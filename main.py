import autorizationData.authorizationData as autorization

from crm.AlfaCRM.alfaCRM import AlfaCRM
from crm.AlfaCRM.alfaCRMDataManager import AlfaCRMDataManager
from crm.AlfaCRM.alfaCrmDBManager import AlfaCRMDBManager
from dataBase.mainDataBase import DataBase
from dataBase.contextDataBase import ContextDataBase
from YandexGPT.yandexGPTChatBot import YandexGPTChatBot, YandexGPTModel

import datetime

#Добавление урока


# print(crm.createModel("Lessons", {"lesson_type_id":4,"lesson_date":"15.02.2025", "time_from":"13:30","duration":120, "subject_id":1}))







db = DataBase('dataBase\dataBases\mainDataBase.db')
# contextDb = ContextDataBase("dataBase/dataBases/contextDataBase.db")
# model = YandexGPTModel(autorization.yandexGPTKey,autorization.yandexCloudIdentificator, 1)
crm = AlfaCRM(autorization.crmhostname, autorization.crmEmail, autorization.crmKey)
# dataManager = AlfaCRMDataManager(crm)
# chatBot = YandexGPTChatBot(model, db, dataManager,contextDb)
# student = db.getStudentsAbsences()
# groups = db.getGroupsOccupancy(student[0]['idGroup'],student[0]["location"])
# string = groups + "\n"+"Кому назначается отработка: "+student[0]['text']
# print(string)
# print(chatBot.sendMessage('Отработки', student[0]['phoneNumber'],{'role':"system", "text":string}))
# # Связь между lessons и regularLessons устанавливается полем regularId
# while(True):
#     message = input()
#     print(chatBot.sendMessage('Отработки', student[0]['phoneNumber'],{'role':"user", "text":message}))



crmManager = AlfaCRMDataManager(crm)
crmToDBManager = AlfaCRMDBManager(db,crmManager)
# Синхронизация бд и CRM
for i in crmManager.getLocations():
    db.insertNewLocation(i)

crmToDBManager.synchroniseTeachers()
crmToDBManager.synchroniseRegularLessons()
crmToDBManager.insertInStudentAbsences()
db.addDataInTableGroupOccupancy()

# Выполняется слишком долго, подумать над хранением данных клиентов локально
# Добавить класс для внесения изменений в AlfaCRM
# Документирование кода 
