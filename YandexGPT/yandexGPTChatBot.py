
import json
from dataBase.mainDataBase import DataBase
from typing import TypedDict
from crm.crmDataManagerInterface import CrmDataManagerInterface 
from YandexGPT.yandexGPTModel import YandexGPTModel
from YandexGPT.messageAnalyzer import MessageAnalyzer
from YandexGPT.chatScriptAnalyzer import ChatScriptAnalyzer
from dataBase.contextDataBase import ContextDataBase
from mTyping.dictTypes import MessageForPromptDict




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

    def _getContext(self, chatId:str) -> list[MessageForPromptDict]:
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

    def _getMessage(self, scriptKey:str, chat:str, message:dict = None) -> list[MessageForPromptDict]:
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
            "text": data['scenaries'][scriptKey]
            },
            *self._getContext(chat),  # Распаковываем словари из списка
            {
            "role": message['role'],
            "text": message['text']
            },
        ]
    
    def _getScenaries(self, message:str) -> str:
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
        
    


