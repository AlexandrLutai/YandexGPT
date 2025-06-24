import json
from dataBase.databaseManager import DataBaseManager
from typing import TypedDict
from crm.crmDataManagerInterface import CrmDataManagerInterface
from YandexGPT.yandexGPTModel import YandexGPTModel
from YandexGPT.gptMessageAnalyzer import GptMessageAnalyzer
from YandexGPT.chatScriptAnalyzer import ChatScriptAnalyzer
from dataBase.contextDataBase import ContextDataBase
from mTyping.dictTypes import MessageForPromptDict
import aiofiles

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

    def __init__(self, gpt: YandexGPTModel):
        """
        Инициализирует объект чат-бота YandexGPT.

        Args:
            gpt (YandexGPTModel): Экземпляр модели YandexGPT.
            db (DataBase): Экземпляр базы данных.
            crm (CrmDataManagerInterface): Интерфейс менеджера данных CRM.
            contextDB (ContextDataBase): Контекстная база данных.
        """
       

        
        self._currentContext:dict[str:list[dict[str:str]]] = {}
        self._groups = []
        self.students = []
        self._currentMessages = {}
        self._gpt = gpt
       

    async def get_current_context(self, chatId: str) -> dict[str:str] | None:
        context =[]
        if chatId in self._currentContext:
            context = self._currentContext[chatId]
        else:
            context = None
        return context


    async def _get_context(self, chatId: str) -> list[MessageForPromptDict]:
        """
        Получает контекст чата по идентификатору чата.

        Args:
            chatId (str): Идентификатор чата.

        Returns:
            list[dict[str:str]]: Список сообщений контекста.
        """
        if not chatId in self._currentContext:
                self._currentContext.update({chatId: {'messages':[], 'chat_script':''}})
        return self._currentContext[chatId]

    async def _del_from_current_context(self, chatId: str):
        """
        Удаляет контекст чата из текущего контекста.

        Args:
            chatId (str): Идентификатор чата.
        """
        del self._currentContext[chatId]

    async def _add_to_context(self, chat: str, role: str, message: str):
        """
        Добавляет сообщение в контекст чата.

        Args:
            chat (str): Идентификатор чата.
            role (str): Роль отправителя сообщения.
            message (str): Текст сообщения.
        """
        self._currentContext[chat].append({
            "role": role,
            "text": message
        })

    async def _get_message(self, scenariesKeys: str, chat: str, message: dict = None) -> list[MessageForPromptDict]:
        """
        Получает сообщение для отправки в модель GPT.

        Args:
            scriptKey (str): Ключ сценария.
            chat (str): Идентификатор чата.
            message (dict, optional): Сообщение для отправки. Defaults to None.

        Returns:
            list[dict[str:str]]: Список сообщений для отправки.
        """
        async with await aiofiles.open("prompts/chatBotPrompst.json", encoding='utf-8') as f: #Плохое решение, путь строго зафиксирован
            data = json.loads(await f.read())
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
                "text": data['scenaries'][scenariesKeys]
            },
            *await self._get_context(chat),  # Распаковываем словари из списка
            {
                "role": message['role'],
                "text": message['text']
            },
        ]

    async def _get_scenaries(self,chat_id: str, message: str) -> str:
        """
        Получает сценарий для обработки сообщения.

        Args:
            chat (str): Идентификатор чата.
            message (str): Текст сообщения.

        Returns:
            str: Ответ сценария.
        """
        answer = await self._chatScriptAnalyzer.analyze(message)
        scenario = None
        if answer.lower() == 'neutral':
            scenario = 'neutral'
        elif answer.lower() != 'none':
            scenario = answer
        else:
            self._currentContext[chat_id][""]
        return scenario
        

    async def send_message(self,scriptKey:str, chat_id: str, message: str) -> str:
        """
        Отправляет сообщение в модель GPT и получает ответ.

        Args:
            scriptKey (str): Ключ сценария.
            chat (str): Идентификатор чата.
            message (str): Текст сообщения.

        Returns:
            str: Ответ модели GPT.
        """
        message_from_gpt = await self._get_message(scriptKey, chat_id, message)

        
        gptMessage = await self._gpt.request(message_from_gpt)
        
        await self._add_to_context(chat_id, message['role'], message)
        await self._add_to_context(chat_id, "assistant", gptMessage.split('|')[-1]) #Получаю текст для пользователя

        return gptMessage



