import autorizationData.authorizationData as autorization

from crm.alfaCRM import AlfaCRM, AlfaCRMDataManager, AlfaCRMDBManager
from dataBase.DataBase import DataBase, ContextDataBase
from YandexGPT.yandexGPT import YandexGPTChatBot, YandexGPTModel

import json

db = DataBase('dataBase/dataBases/dataBase.db')
contextDb = ContextDataBase("dataBase/dataBases/contextDataBase.db")
crm = AlfaCRM(autorization.crmhostname, autorization.crmEmail, autorization.crmKey)
crmManager = AlfaCRMDataManager(crm,7,14)

model = YandexGPTModel(autorization.yandexGPTKey,autorization.yandexCloudIdentificator)

chatBot = YandexGPTChatBot(model, db,contextDb)
student = db.getStudentAbsences()
groups = db.getAllGroupsOccupancy(student[0]['idGroup'])
string = groups + "\n"+student[0]['text']
print(chatBot.sendRequest('worksOff', '8943543443',{'role':"system", "text":string}))
# Связь между lessons и regularLessons устанавливается полем regularId
 
while(True):
    message = input()
    print(chatBot.sendRequest('worksOff', '8943543443',{'role':"user", "text":message}))




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
