import requests
import json
from dataBase.DataBase import DataBase, ContextDataBase,getDateNextWeekday
from typing import TypedDict
from crm.alfaCRM import CrmDataManagerInterface 
import datetime
class messageData(TypedDict):
        chat:str
        text:str
        idClient:int
        topic:str

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

    
    def _fillGPTPrompt(self, messages:list):
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
    
    def request(self, messages:list):
        """
        Отправляет запрос к модели GPT.

        :param messages: Список сообщений.
        :return: Ответ модели.
        """
        prompt = self._fillGPTPrompt(messages)

        r = requests.post(url=self._url, json=prompt, headers=self._headers)
        print(r.text)
       
        if 'result' in r.text:
            return json.loads(r.text)['result']["alternatives"][0]["message"]['text']
        return r.text
   
class YandexGPTChatBot:
    """
    _currentContext - список, следующего вида
    {
    "9629598337" : [
    {
    role:"system",
    "text":"Hello"
    },
    {
    role:"user",
    "text":"Hello"
    },
    ],
    "9756786556":[]
    }
    """
    
    
    def __init__(self, gpt:YandexGPTModel, db:DataBase, crm:CrmDataManagerInterface, contextDB:ContextDataBase):
        
        self._gpt = gpt
        self._db = db
        self._contextDB = contextDB
        self._currentContext:dict[str:list[dict[str:str]]] = {}
        self._groups = []
        self.students = []
        self._currentMessages = {}
        self._analizer = GPTTextAnalyzer(gpt,crm,db)

    def _getContext(self, chatId:str) -> list[dict[str:str]]:
        if not chatId in self._currentContext: 
            if self._contextDB.findContext(chatId):
                self._currentContext.update({chatId:self._contextDB.getContext(chatId)})
                return self._currentContext[chatId]
            else:
                self._currentContext.update({chatId :[]})
        return self._currentContext[chatId]

    def _delFromCurrentContext(self, chatId:str):
        del self._currentContext[chatId]

    def _addToContext(self, chat:str, role:str, message:str):
        self._currentContext[chat].append({
            "role" : role,
            "text": message
        })

    def _getMessage(self, skriptKey:str, chat:str, message:dict = None) -> list[dict[str:str]]:
        with open("prompts/chatBotPrompst.json", encoding='utf-8') as f:
            data = json.load(f)
        return [
            {
            "role": "system",
            "text": data['introduce']
            },
            {
            "role": "system",
            "text": data['technicalInstructions']
            },
            {
            "role": "system",
            "text": data['scenaries']['Отработки']
            },
            *self._getContext(chat),  # Распаковываем словари из списка
            {
            "role": message['role'],
            "text": message['text']
            },
        ]
    
    def _getScenaries(self,chat:str, message:str) -> str:
            answer = self._analizer.analyze(message)
            if answer != 'None':
                return answer
            else:
                return None
        
        
    def sendMessage(self, skriptKey:str, chat:str, message:str ): 
        gptMessage = self._gpt.request(self._getMessage(skriptKey,chat,message))
        self._addToContext(chat, message['role'], message['text'])
        self._addToContext(chat, "assistant", gptMessage)
        
        
        return gptMessage
        
    



class GPTTextAnalyzer:

    # class _Message(TypedDict):
    #     role:str
    #     text:str

    def __init__(self,gpt:YandexGPTModel, crm:CrmDataManagerInterface, db:DataBase):
        self._gpt = gpt
        self.db = db
        self._crm = crm
        self.scenariesKeys = []
        pass

    def _getScenaries(self):
        with open("prompts/chatBotPrompst.json", encoding='utf-8') as f:
            data = json.load(f)
        self.scenariesKeys = data['scenaries'].keys()

    async def _getMessage(self, message:list):
        with open("prompts/chatBotPrompst.json", encoding='utf-8') as f:
            data = json.load(f)
        return [
            {
            "role": "system",
            "text": data['introduce']
            },
            {
            "role": "system",
            "text": data['scenaries']['worksOff']
            },
            {
            "role": message['role'],
            "text": message['text']
            }
        ]
    
    def analyzeGPTAnswer(self, answer:messageData):
        message = answer["text"]
        if "|" in answer["text"]:
            message = self._analyzeSystemMessage(answer)
            pass
        if "help" in answer["text"].lower():
            pass
        if "пользователь" in answer["text"].lower():
            pass
        return message
   
   
    def _analyzeSystemMessage(self, answer:messageData):
        message = answer['text'].split('|')
        if "отработк" in message[0].lower():
            self._processWorkOffMessage(message, answer['chat'])
            pass
        return message[-1]
   
   
    def _processWorkOffMessage(self, message:list, chat:str):
        if message[1].lower() == 'success':
            self._addWorkOffToCRM(chat, message)
            pass
        elif message[1].lower() == 'fail':
            pass
    
    def _addWorkOffToCRM(self, chat:str, message:list):
        student = self.db.getStudent(chat)
        group = self.db.getGroup(int(message[2]))
        data = {
            "topic": student['topic'],
            "lesson_date": getDateNextWeekday(group['weekday']).strftime('%d-%m-%Y'),
            "costumer_ids": list(student['id']),
            "time_from": group['timeFrom'],
            "duration": (datetime.datetime.strptime(group['timeTo'],"%H:%M") - datetime.datetime.strptime(group['timeFrom'],"%H:%M")).total_seconds()//60,
            "subject_id": group['subjectId'],
            "teacher_id": list(group['teacherId']),
        }
        self._crm.addWorkOff(data)
        pass
    
   
    async def analyzeMessage(self, message:str):
        return self._gpt.request(await self._getMessage(message))
