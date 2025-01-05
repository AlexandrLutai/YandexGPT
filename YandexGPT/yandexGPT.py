import requests
import json
from dataBase.localDB import DataBase
class YandexGPTModel:

    def __init__(self, authKey, cloudBranch,temperature:float = 0.3):
        self._headers ={
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {authKey}"
        } 
        self._competitions = {
            "stream": False,
            "temperature": temperature,
            "maxTokens": "1000"
        }
        self._url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self._modelUrl = f"gpt://{cloudBranch}/yandexgpt-lite"      

    def _fillGPTPrompt(self, messages:list):
        return {
            "modelUri": self._modelUrl,
            "completionOptions":self._competitions,
            'messages':messages
        }
    
    def gptRequest(self,messages:list):
        prompt = self._fillGPTPrompt(messages)
        r = requests.post(url=self._url, json=prompt, headers=self._headers)
        return r.text
   
class YandexGPTData:

    def __init__(self, gpt:YandexGPTModel, db:DataBase):
        self.gpt = gpt
        self.db = db
        self.groups = []
        self.students = []

    def _modelTraining(self):
        return self.gpt.gptRequest()

    def _getInformationAboutGroups(self):
        self.groups = self.db.getGroupOccupancyData()
        messages = [ {
            "role": "system",
            "text": "Информация по группам если понятна, отправь SERVER|SUCCESS"
        }]
        for i in self.groups:
            message = {
            "role": "system",
            "text":  f"Локация: {i['location']} Тема: {i['topic']} Преподаватель: {i['teachers']} День: {i['day']} Время: {i['time']} Id группы: {i['idGroup']} Мест в группе: {i['maxStudents'] - i['countStudents']} Можно назначать отработку: {yesOrNo(1)} " # yesOrNo(i['assignWorkOffs'])
            }
            messages.append(message)
        return messages
    
    #Сообщения о клиенте лучше передовать по одному
    def _getInformationStudentAbsences(self):
        self.students = self.db.getStudentAbsencesData()
        messages = [ {
            "role": "system",
            "text": "Информация по группам:"
        }]
        for i in self.students:
            group = findInListById(self.groups, i['idGroups'])
            message = {
            "role": "system",
            "text":  f"Напиши данному клиенту и назначь отработку: Имя : {i['name']} Телефон: {i['phoneNumber']} id Урока:{i['idLesson']} id группы:{i['idGroups']} Тема: {i['topic']} Локация:{group['location']} Преподаватель: {'teachers'} День основного урока:{group['day']} Время основного урока: {group['time']} Задача: Отработка "
            }
            messages.append(message)
        return messages
    
    #Тестовая функция, переписать
    def communicate(self):
        print(self._modelTraining())
        groupMessage = self._getInformationAboutGroups()
        print(self.gpt.gptRequest(groupMessage))
        studentMessage = self._getInformationStudentAbsences()
        for i in studentMessage:
           temp = []
           temp.append(i)
           print(self.gpt.gptRequest(temp))
           while True:
               print(self.gpt.gptRequest([{"role": 'user',
                                           "text": "CLIENT | 79624504274 | " + input('\n')
                                           }
                                           ]
                                           )
                                           )

#Костыль переписать
def findInListById(l, id):
    for i in l:
        if int(i['idGroup']) == int(id):
            return i

def yesOrNo(i:int):
    if i:
        return "Да"
    return "Не желательно"