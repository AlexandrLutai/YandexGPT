import requests
import json
from dataBase.DataBase import DataBase, ContextDataBase,getDateNextWeekday
from typing import TypedDict
from crm.alfaCRM import CrmDataManagerInterface 
import datetime
import numpy as np
class messageData(TypedDict):
        chat:str
        text:str
        idClient:int
        topic:str

class YandexGPTModel:

    def __init__(self, authKey, cloudBranch, temperature:float = 0.3):
        """
        Инициализирует объект модели YandexGPT.

        Args:
            authKey (str): Ключ авторизации для API.
            cloudBranch (str): Ветка облака для модели.
            temperature (float): Температура генерации текста.
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

        Args:
            messages (list): Список сообщений.

        Returns:
            dict: Заполненный запрос.
        """
        return {
            "modelUri": self._modelUrl,
            "completionOptions":self._competitions,
            'messages':messages
        }
    
    def request(self, messages:list):
        """
        Отправляет запрос к модели GPT.

        Args:
            messages (list): Список сообщений.

        Returns:
            str: Ответ модели.
        """
        prompt = self._fillGPTPrompt(messages)

        r = requests.post(url=self._url, json=prompt, headers=self._headers)
        print(r.text)
       
        if 'result' in r.text:
            return json.loads(r.text)['result']["alternatives"][0]["message"]['text']
        return r.text

class ChatScriptAnalyzer:
    def __init__(self, gpt:YandexGPTModel, instractionsPath:str):
        """
        Инициализирует объект анализатора сообщений пользователя.

        Args:
            gpt (YandexGPTModel): Экземпляр модели YandexGPT.
            instractionsPath (str): Путь к файлу инструкций.
        """
        self._gpt = gpt
        self._instractionsPath = instractionsPath
    
    def _getScenaries(self, instructionsData:dict) -> str:
        """
        Получает сценарии из данных инструкций.

        Args:
            instructionsData (dict): Данные инструкций.

        Returns:
            str: Строка с возможными сценариями.
        """
        scenaries = "Возможные сценарии: \n"
        for key in instructionsData['scenaries'].keys():
            scenaries += key + ": "+ instructionsData['scenaries'][key] + "\n"
        return scenaries

    def _getPrompt(self, message:str) -> list:
        """
        Получает запрос для модели GPT.

        Args:
            message (str): Сообщение пользователя.

        Returns:
            list: Список сообщений для отправки в модель GPT.
        """
        with open(self._instractionsPath, encoding='utf-8') as f:
            instructionData = json.load(f)
        return [
            {
            "role": "system",
            "text": instructionData['instruction']
            },
            {
            "role": "system",
            "text": self._getScenaries(instructionData)
            },
            {
                "role": "user",
                "text": message
            }
        ]

    def analyze(self, message:str) -> str:
        """
        Анализирует сообщение пользователя и отправляет его в модель GPT.

        Args:
            message (str): Сообщение пользователя.

        Returns:
            str: Ответ модели GPT.
        """
        return self._gpt.request(self._getPrompt(message))
      

class MessageAnalyzer:
    class _Message(TypedDict):
        chatId:str
        text:str
        
    def __init__(self, chatAnalyzer:ChatScriptAnalyzer, db:DataBase, crm:CrmDataManagerInterface):
        """
        Инициализирует объект анализатора сообщений.

        Args:
            chatAnalyzer (ChatScriptAnalyzer): Экземпляр анализатора сценариев.
            db (DataBase): Экземпляр базы данных.
            crm (CrmDataManagerInterface): Интерфейс менеджера данных CRM.
        """
        self._chatAnalyzer = chatAnalyzer
        self._db = db
        self._crm = crm
    

    def analyzeGPTAnswer(self, data:_Message):
        message = data['text']
        if "|" in data['text']:
           message = self._analyzeSystemMessage(data)
        return message

    def _analyzeSystemMessage(self, data:_Message):
        message = data['text'].split('|')
        if "отработк" in message[0].lower():
            self._processWorkOffMessage(data)
            pass
        return message[-1]
        pass

    def _processWorkOffMessage(self, data:_Message):
        message = data['text'].split('|')
        if 'success' in message[1].lower() :
            self._workOffSuccess(data)
            pass
        elif message[1].lower() == 'fail':
            self._workOffFail(data)
            pass
        pass

    def _workOffSuccess(self, data:_Message):
        """
        Обрабатывает успешное сообщение об отработке.

        Args:
            data (_Message): Данные сообщения, включающие идентификатор чата и текст сообщения.
        """
        try:
            idGroup = int(data['text'].split('|')[2])
            student = self._db.getStudent(data['chatId'])
            regularLesson = self._db.getRegularLessons(idGroup)
            groupOccupancy = self._db.getGroupOccupancyData(idGroup)
            dataForCRM = {
                'topic': student['topic'],
                'lesson_date': groupOccupancy['dateOfEvent'],
                'customer_ids':list([student['idStudent']]),
                'time_from': regularLesson['timeFrom'],
                'duration': getDuration(regularLesson['timeFrom'], regularLesson['timeTo']),
                'subject_id': regularLesson['subjectId'],
                'teacher_ids': list([regularLesson['teacher']])
            }

            dataForDB = {
                'worksOffsTopics': f"{groupOccupancy['worksOffsTopics']}, {student['topic']}",
                'newStudents': f"{groupOccupancy['newStudents']}, {student['idStudent']}",
                'count': groupOccupancy['count'] + 1
            }
            self._crm.addWorkOff(dataForCRM)
            self._db.updateData(dataForDB, "groupOccupancy", {'idGroup': idGroup})
        except Exception as e:
            print(f"An error occurred while processing work off success: {e}")
        

    def _workOffFail(self, data:_Message):
        dateNextConnextion = int(messageData['text'].split('|')[2])
        dataForDB = {
            'dateLastConnection' : datetime.datetime.now().strftime('%Y-%m-%d'),
            'dateNextConnection': getDateNextWeekday(datetime.datetime.now().weekday()).strftime('%Y-%m-%d')
        }
        self._db.updateData(dataForDB, "StudentAbsences", {'phoneNumber': messageData['idChat']})



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
        """
        Инициализирует объект чат-бота YandexGPT.

        Args:
            gpt (YandexGPTModel): Экземпляр модели YandexGPT.
            db (DataBase): Экземпляр базы данных.
            crm (CrmDataManagerInterface): Интерфейс менеджера данных CRM.
            contextDB (ContextDataBase): Контекстная база данных.
        """
        self._gpt = gpt
        self._db = db
        self._contextDB = contextDB
        self._currentContext:dict[str:list[dict[str:str]]] = {}
        self._groups = []
        self.students = []
        self._currentMessages = {}
        self.messageAnalyzer = MessageAnalyzer(ChatScriptAnalyzer(gpt, "prompts/chatBotPrompst.json"), db, crm)

    def _getContext(self, chatId:str) -> list[dict[str:str]]:
        """
        Получает контекст чата по идентификатору чата.

        Args:
            chatId (str): Идентификатор чата.

        Returns:
            list[dict[str:str]]: Список сообщений контекста.
        """
        if not chatId in self._currentContext: 
            if self._contextDB.findContext(chatId):
                self._currentContext.update({chatId:self._contextDB.getContext(chatId)})
                return self._currentContext[chatId]
            else:
                self._currentContext.update({chatId :[]})
        return self._currentContext[chatId]

    def _delFromCurrentContext(self, chatId:str):
        """
        Удаляет контекст чата из текущего контекста.

        Args:
            chatId (str): Идентификатор чата.
        """
        del self._currentContext[chatId]

    def _addToContext(self, chat:str, role:str, message:str):
        """
        Добавляет сообщение в контекст чата.

        Args:
            chat (str): Идентификатор чата.
            role (str): Роль отправителя сообщения.
            message (str): Текст сообщения.
        """
        self._currentContext[chat].append({
            "role" : role,
            "text": message
        })

    def _getMessage(self, skriptKey:str, chat:str, message:dict = None) -> list[dict[str:str]]:
        """
        Получает сообщение для отправки в модель GPT.

        Args:
            skriptKey (str): Ключ сценария.
            chat (str): Идентификатор чата.
            message (dict, optional): Сообщение для отправки. Defaults to None.

        Returns:
            list[dict[str:str]]: Список сообщений для отправки.
        """
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
        """
        Получает сценарий для обработки сообщения.

        Args:
            chat (str): Идентификатор чата.
            message (str): Текст сообщения.

        Returns:
            str: Ответ сценария.
        """
        answer = self._analizer.analyze(message)
        if answer != 'None':
                return answer
        else:
                return None
        
        
    def sendMessage(self, skriptKey:str, chat:str, message:str ) -> str:
        """
        Отправляет сообщение в модель GPT и получает ответ.

        Args:
            skriptKey (str): Ключ сценария.
            chat (str): Идентификатор чата.
            message (str): Текст сообщения.

        Returns:
            str: Ответ модели GPT.
        """
        gptMessage = self._gpt.request(self._getMessage(skriptKey,chat,message))
        gptMessageForUser = self.messageAnalyzer.analyzeGPTAnswer({"chatId":chat, "text":gptMessage})
        self._addToContext(chat, message['role'], message['text'])
        self._addToContext(chat, "assistant", gptMessage)
        
        
        return gptMessageForUser
        
    



def getDuration(timeFrom:str, timeTo:str) -> int:
    """
    Получает длительность урока.

    Args:
        timeFrom (str): Время начала урока.
        timeTo (str): Время окончания урока.

    Returns:
        int: Длительность урока.
    """
    return (datetime.datetime.strptime(timeTo,"%H:%M") - datetime.datetime.strptime(timeFrom,"%H:%M")).total_seconds()//60
# class GPTTextAnalyzer:

#     # class _Message(TypedDict):
#     #     role:str
#     #     text:str

#     def __init__(self,gpt:YandexGPTModel, crm:CrmDataManagerInterface, db:DataBase):
#         """
#         Инициализирует объект анализатора текста GPT.

#         Args:
#             gpt (YandexGPTModel): Экземпляр модели YandexGPT.
#             crm (CrmDataManagerInterface): Интерфейс менеджера данных CRM.
#             db (DataBase): Экземпляр базы данных.
#         """
#         self._gpt = gpt
#         self.db = db
#         self._crm = crm
#         self.scenariesKeys = []
#         pass

#     def _getScenaries(self):
#         """
#         Получает сценарии из файла конфигурации.
#         """
#         with open("prompts/chatBotPrompst.json", encoding='utf-8') as f:
#             data = json.load(f)
#         self.scenariesKeys = data['scenaries'].keys()

#     async def _getMessage(self, message:list) -> list[dict[str:str]]:
#         """
#         Получает сообщение для отправки в модель GPT.

#         Args:
#             message (list): Список сообщений.

#         Returns:
#             list[dict[str:str]]: Список сообщений для отправки.
#         """
#         with open("prompts/chatBotPrompst.json", encoding='utf-8') as f:
#             data = json.load(f)
#         return [
#             {
#             "role": "system",
#             "text": data['introduce']
#             },
#             {
#             "role": "system",
#             "text": data['scenaries']['worksOff']
#             },
#             {
#             "role": message['role'],
#             "text": message['text']
#             }
#         ]
    
#     def analyzeGPTAnswer(self, answer:messageData) -> str:
#         """
#         Анализирует ответ модели GPT.

#         Args:
#             answer (messageData): Ответ модели GPT.

#         Returns:
#             str: Проанализированный ответ.
#         """
#         message = answer["text"]
#         if "|" in answer["text"]:
#             message = self._analyzeSystemMessage(answer)
#             pass
#         if "help" in answer["text"].lower():
#             pass
#         if "пользователь" in answer["text"].lower():





#             pass
#         return message
   
   
#     def _analyzeSystemMessage(self, answer:messageData) -> str:
#         """
#         Анализирует системное сообщение.

#         Args:
#             answer (messageData): Ответ модели GPT.

#         Returns:
#             str: Проанализированное системное сообщение.
#         """
#         message = answer['text'].split('|')
#         if "отработк" in message[0].lower():
#             self._processWorkOffMessage(message, answer['chat'])
#             pass
#         return message[-1]
   
   
#     def _processWorkOffMessage(self, message:list, chat:str):
#         """
#         Обрабатывает сообщение об отработке.

#         Args:
#             message (list): Список сообщений.
#             chat (str): Идентификатор чата.
#         """
#         if message[1].lower() == 'success':
#             self._addWorkOffToCRM(chat, message)
#             pass
#         elif message[1].lower() == 'fail':
#             pass
    
#     def _addWorkOffToCRM(self, chat:str, message:list):
#         """
#         Добавляет отработку в CRM.

#         Args:
#             chat (str): Идентификатор чата.
#             message (list): Список сообщений.
#         """
#         student = self.db.getStudent(chat)
#         group = self.db.getGroup(int(message[2]))
#         data = {
#             "topic": student['topic'],
#             "lesson_date": getDateNextWeekday(group['weekday']).strftime('%d-%m-%Y'),
#             "costumer_ids": list(student['id']),
#             "time_from": group['timeFrom'],
#             "duration": (datetime.datetime.strptime(group['timeTo'],"%H:%M") - datetime.datetime.strptime(group['timeFrom'],"%H:%M")).total_seconds()//60,
#             "subject_id": group['subjectId'],
#             "teacher_id": list(group['teacherId']),
#         }
#         self._crm.addWorkOff(data)
#         pass
    
   
#     async def analyzeMessage(self, message:str) -> str:
#         """
#         Анализирует сообщение и отправляет его в модель GPT.

#         Args:
#             message (str): Текст сообщения.

#         Returns:
#             str: Ответ модели GPT.
#         """
#         return self._gpt.request(await self._getMessage(message))
