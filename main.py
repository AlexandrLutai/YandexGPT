# import autorizationData.authorizationData as autorization

# # from crm.AlfaCRM.alfaCRM import AlfaCRM
# # from crm.AlfaCRM.alfaCRMDataManager import AlfaCRMDataManager
# # from crm.AlfaCRM.alfaCrmDBManager import AlfaCRMDBManager
# # from dataBase.databaseManager import DataBaseManager
# # from dataBase.contextDataBase import ContextDataBase
# # from YandexGPT.yandexGPTChatBot import YandexGPTChatBot, YandexGPTModel
# import asyncio

# from Whatsupp.webhookGetter import process_webhook





# # import datetime

# # # #Добавление урока


# # # # print(crm.createModel("Lessons", {"lesson_type_id":4,"lesson_date":"15.02.2025", "time_from":"13:30","duration":120, "subject_id":1}))







# # # # db = DataBase('dataBase\dataBases\mainDataBase.db')
# # # # contextDb = ContextDataBase("dataBase/dataBases/contextDataBase.db")
# # # # model = YandexGPTModel(autorization.yandexGPTKey,autorization.yandexCloudIdentificator, 1)
# # # # crm = AlfaCRM(autorization.crmhostname, autorization.crmEmail, autorization.crmKey)
# # # # dataManager = AlfaCRMDataManager(crm)
# # # # chatBot = YandexGPTChatBot(model, db, dataManager,contextDb)
# # # # student = db.getStudentsAbsences()
# # # # groups = db.getGroupsOccupancy(student[0]['idGroup'],student[0]["location"])
# # # # string = groups + "\n"+"Кому назначается отработка: "+student[0]['text']
# # # # print(string)
# # # # print(chatBot.sendMessage('Отработки', student[0]['phoneNumber'],{'role':"system", "text":string}))
# # # # # Связь между lessons и regularLessons устанавливается полем regularId
# # # # while(True):
# # # #     message = input()
# # # #     print(chatBot.sendMessage('Отработки', student[0]['phoneNumber'],{'role':"user", "text":message}))


# # async def main():
# #     db = DataBaseManager('dataBase/dataBases/mainDataBase.db')
#     # crm = AlfaCRM(autorization.crmhostname, autorization.crmEmail, autorization.crmKey)
#     # await crm.init()
   
#     # crmManager = AlfaCRMDataManager(crm)
#     # crmToDBManager = AlfaCRMDBManager(db, crmManager)

#     # # Синхронизация бд и CRM
#     # locations = await crmManager.get_locations()
#     # await db.synchronise_teachers_and_locations(locations)

#     # await crmToDBManager.synchronise_teachers()
#     # await crmToDBManager.synchronise_regular_lessons()
#     # await crmToDBManager.insert_in_student_absences()
#     # await db.add_data_in_table_group_occupancy()
#     # print(await db.get_lessons_event_date())
#     # # Выполняется слишком долго, подумать над хранением данных клиентов локально
#     # # Добавить класс для внесения изменений в AlfaCRM
#     # # Документирование кода

# # if __name__ == '__main__':
# #     print()
# #     asyncio.run(main())

# # # Выполняется слишком долго, подумать над хранением данных клиентов локально
# # # Добавить класс для внесения изменений в AlfaCRM
# # # Документирование кода 


# # from dataBase.database import DatabaseManager

# # db = DatabaseManager('dataBase\dataBases\mainDataBase.db')
# # db.insert_unique_data("StudentAbsences", {"idStudent":1, "name":"Иванов Иван Иванович", "date":"15.02.2025", "topic":"Тема урока", "idGroup":1, "idLesson":1, "phoneNumber":"89999999999", "teacher":1}, {"idStudent":5})

# # print("Имя", 3, "321321")


import asyncio
from Whatsupp.webhookGetter import webhook_handler

async def main():
    # Пример данных вебхука
    test_payload = {
        "messages": [
            {
                "text":"Привет, как дела?",
                "chatId": "123456789"
            }
        ]
    }

    # Убедитесь, что зависимости инициализированы
    if webhook_handler.whatsappManager is None:
        await webhook_handler._initialize_dependencies()

    # Вызов метода process_webhook
    await webhook_handler.process_webhook(test_payload)

if __name__ == "__main__":
    asyncio.run(main())