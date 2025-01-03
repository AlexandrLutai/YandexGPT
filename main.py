import autorizationData.authorizationData as autorization
from crm.alfaCRM import AlfaCRM, AlfaCRMDataWrapper
from dataBase.localDB import DataBase

crm = AlfaCRM(autorization.hostname,autorization.email,autorization.key)
db = DataBase()
dataWrapper = AlfaCRMDataWrapper(db,crm)


print('\n \n')
dataWrapper.fillDataBase()



# print(crm.tempToken)
# header = {'X-ALFACRM-TOKEN': crm.tempToken}
# hostname = 'kiberonestavropol.s20.online'


# #Получение информации о организации в целом
# barancPath = f"https://{hostname}/v2api/branch/index"
# #Не работает
# #locationPath = f'https://{hostname}/v2api/0/location/index'
# #locationPath = f'https://{hostname}/v2api/0/location/index'

# # costumerPath = f'https://{hostname}/v2api/0/customer/index'

# #Группы
# # groupPath =f'https://{hostname}/v2api/1/group/index'

# # r = requests.post(groupPath,data=json.dumps({"removed" : 0}),headers = header)
# # a = json.loads(r.text)

# # Данные по уроку
# # lessonPath = f'https://{hostname}/v2api/1/lesson/index'
# # r = requests.post(lessonPath,data=json.dumps({"status" : 3}),headers = header)

# costumerPath = f"https://{hostname}/v2api/1/customer/index"
# r = requests.post(barancPath,data=json.dumps({"is_active" : 1}),headers = header)
# print(r.text.replace(',', ",\n"))




# with open("p.json", "w", encoding='utf-8') as d:
#     d.write(json.dumps(r.text, indent=4, ensure_ascii=False, separators=("\n", ",")))

#print(json.loads(r.text))

# path = "https://kiberonestavropol.s20.online/v2api/auth/login"

# email = 'alex89620109009@gmail.com'
# api_key = '948f3dcb-98a2-11ec-8426-ac1f6b4782be'

# print()
# r = requests.post(path,json.dumps({'email':email, 'api_key':api_key}))

# #r = requests.post(path,json.dumps({'email':'alex89620109009@gmail.com', 'api_key':'948f3dcb-98a2-11ec-8426-ac1f6b4782be'}))
# print(json.loads(r.text)["token"])