import requests
import json
from dataBase.DataBase import DataBase

class YandexGPTModel:

    def __init__(self, authKey, cloudBranch, temperature:float = 0.3):
        """
        Инициализирует объект модели YandexGPT.

        :param authKey: Ключ авторизации для API.
        :param cloudBranch: Ветка облака для модели.
        :param temperature: Температура генерации текста.
        """
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

    
    def fillGPTPrompt(self, message:dict, messages:list):
        """
        Заполняет запрос для модели GPT.

        :param message: Сообщение для модели.
        :param messages: Список сообщений.
        :return: Заполненный запрос.
        """
        return {
            "modelUri": self._modelUrl,
            "completionOptions":self._competitions,
            'messages':messages
        }
    
    def gptRequest(self, messages:list):
        """
        Отправляет запрос к модели GPT.

        :param messages: Список сообщений.
        :return: Ответ модели.
        """
        prompt = self._fillGPTPrompt(messages)
        r = requests.post(url=self._url, json=prompt, headers=self._headers)
        return r.text
   
class YandexGPTChatBot:

    def __init__(self, gpt:YandexGPTModel, db:DataBase):
        """
        Инициализирует объект чат-бота YandexGPT.

        :param gpt: Объект модели YandexGPT.
        :param db: Объект базы данных.
        """
        self.gpt = gpt
        self.db = db
        self._currentContext = {}
        self.groups = []
        self.students = []

    def _getContext(self, chatId:str) -> str:
        """
        Возвращает контекст для указанного чата.

        :param chatId: Идентификатор чата.
        :return: Контекст чата.
        """
        if not chatId in self._currentContext: 
            if self.db.findContext(chatId):
                self._currentContext.update({chatId:self.db.getContext(chatId)})
                return self._currentContext[chatId]
            else:
                self._currentContext.update({chatId : ""})
        return self._currentContext[chatId]

    def _delFromCurrentContext(self, chatId:str):
        """
        Удаляет контекст для указанного чата из текущего контекста.

        :param chatId: Идентификатор чата.
        """
        del self._currentContext[chatId]

    # def _getInformationAboutGroups(self):
    #     """
    #     Возвращает информацию о группах.

    #     :return: Список сообщений с информацией о группах.
    #     """
    #     self.groups = self.db.getAllGroupsOccupancy()
    #     text = "Информация по группам: "
    #     for i in self.groups:
    #         text +=  f"\nЛокация: {i['location']} Тема: {i['topic']} Преподаватель: {i['teachers']} День: {i['day']} Время: {i['time']} Id группы: {i['idGroup']} Мест в группе: {i['maxStudents'] - i['countStudents']} Можно назначать отработку: {yesOrNo(1)} " # yesOrNo(i['assignWorkOffs'])
            
    #     messages = [ {
    #         "role": "system",
    #         "text": text,
    #     }]
    #     return messages

    # def _getInformationStudentAbsences(self):
    #     """
    #     Возвращает информацию об отсутствиях студентов.

    #     :return: Список сообщений с информацией об отсутствиях студентов.
    #     """
    #     self.students = self.db.getStudentAbsencesData()
    #     messages = [ {
    #         "role": "system",
    #         "text": "Информация по группам:"
    #     }]
    #     for i in self.students:
    #         group = findInListById(self.groups, i['idGroups'])
    #         message = {
    #         "role": "system",
    #         "text":  f"Напиши данному клиенту и назначь отработку: Имя : {i['name']} Телефон: {i['phoneNumber']} id Урока:{i['idLesson']} id группы:{i['idGroups']} Тема: {i['topic']} Локация:{group['location']} Преподаватель: {'teachers'} День основного урока:{group['day']} Время основного урока: {group['time']} Задача: Отработка "
    #         }
    #         messages.append(message)
    #     return messages
    
#Костыль переписать
def findInListById(l, id):
    """
    Находит элемент в списке по идентификатору.

    :param l: Список элементов.
    :param id: Идентификатор элемента.
    :return: Найденный элемент.
    """
    for i in l:
        if int(i['idGroup']) == int(id):
            return i

def yesOrNo(i:int):
    """
    Возвращает "Да" или "Не желательно" в зависимости от значения.

    :param i: Целое число (1 или 0).
    :return: "Да" если i равно 1, иначе "Не желательно".
    """
    if i:
        return "Да"
    return "Не желательно"

