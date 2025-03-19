import json
from dataBase.databaseManager import DataBaseManager
from typing import TypedDict
from crm.crmDataManagerInterface import CrmDataManagerInterface
from YandexGPT.yandexGPTModel import YandexGPTModel
from YandexGPT.messageAnalyzer import MessageAnalyzer
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

    def __init__(self, gpt: YandexGPTModel, db: DataBaseManager, crm: CrmDataManagerInterface):
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
        #self._contextDB = contextDB # Для системы с хранением контекста в БД
        self._currentContext:dict[str:list[dict[str:str]]] = {}
        self._groups = []
        self.students = []
        self._currentMessages = {}
        self.messageAnalyzer = MessageAnalyzer(ChatScriptAnalyzer(gpt, "prompts/chatBotPrompst.json"), db, crm)

    async def _get_context(self, chatId: str) -> list[MessageForPromptDict]:
        """
        Получает контекст чата по идентификатору чата.

        Args:
            chatId (str): Идентификатор чата.

        Returns:
            list[dict[str:str]]: Список сообщений контекста.
        """
        if not chatId in self._currentContext:
            # if await self._contextDB.findContext(chatId): # Для системы с хранением контекста в БД
            #     self._currentContext.update({chatId: await self._contextDB.getContext(chatId)})
            #     return self._currentContext[chatId]
            # else: 
                self._currentContext.update({chatId: []})
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

    async def _get_message(self, scriptKey: str, chat: str, message: dict = None) -> list[MessageForPromptDict]:
        """
        Получает сообщение для отправки в модель GPT.

        Args:
            scriptKey (str): Ключ сценария.
            chat (str): Идентификатор чата.
            message (dict, optional): Сообщение для отправки. Defaults to None.

        Returns:
            list[dict[str:str]]: Список сообщений для отправки.
        """
        async with await aiofiles.open("prompts/chatBotPrompst.json", encoding='utf-8') as f:
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
                "text": data['scenaries'][scriptKey]
            },
            *await self._get_context(chat),  # Распаковываем словари из списка
            {
                "role": message['role'],
                "text": message['text']
            },
        ]

    async def _get_scenaries(self, message: str) -> str:
        """
        Получает сценарий для обработки сообщения.

        Args:
            chat (str): Идентификатор чата.
            message (str): Текст сообщения.

        Returns:
            str: Ответ сценария.
        """
        answer = await self._analizer.analyze(message)
        if answer != 'None':
            return answer
        else:
            return None

    async def send_message(self, scriptKey: str, chat: str, message: str) -> str:
        """
        Отправляет сообщение в модель GPT и получает ответ.

        Args:
            scriptKey (str): Ключ сценария.
            chat (str): Идентификатор чата.
            message (str): Текст сообщения.

        Returns:
            str: Ответ модели GPT.
        """
        gptMessage = await self._gpt.request(await self._get_message(scriptKey, chat, message))
        gptMessageForUser = await self.messageAnalyzer.analyze_GPT_answer({"chatId": chat, "text": gptMessage})
        await self._add_to_context(chat, message['role'], message['text'])
        await self._add_to_context(chat, "assistant", gptMessage)

        return gptMessageForUser




