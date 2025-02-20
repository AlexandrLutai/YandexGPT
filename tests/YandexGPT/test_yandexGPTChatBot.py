import unittest
from unittest.mock import AsyncMock, patch
from YandexGPT.yandexGPTChatBot import YandexGPTChatBot
from YandexGPT.yandexGPTModel import YandexGPTModel
from dataBase.database import DataBase
from crm.crmDataManagerInterface import CrmDataManagerInterface
from dataBase.contextDataBase import ContextDataBase
from YandexGPT.messageAnalyzer import MessageAnalyzer
from YandexGPT.chatScriptAnalyzer import ChatScriptAnalyzer
from mTyping.dictTypes import MessageForPromptDict

class TestYandexGPTChatBot(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.mock_gpt = AsyncMock(YandexGPTModel)
        self.mock_db = AsyncMock(DataBase)
        self.mock_crm = AsyncMock(CrmDataManagerInterface)
        self.chatBot = YandexGPTChatBot(self.mock_gpt, self.mock_db, self.mock_crm)

    async def test_get_context(self):
        chatId = "12345"
        self.chatBot._currentContext = {}
        context = await self.chatBot._get_context(chatId)
        self.assertEqual(context, [])
        self.assertIn(chatId, self.chatBot._currentContext)

    async def test_add_to_context(self):
        chat = "12345"
        role = "user"
        message = "Hello"
        self.chatBot._currentContext = {chat: []}
        await self.chatBot._add_to_context(chat, role, message)
        self.assertEqual(self.chatBot._currentContext[chat], [{"role": role, "text": message}])

    async def test_get_message(self):
        scriptKey = "testScript"
        chat = "12345"
        message = {"role": "user", "text": "Hello"}
        self.chatBot._currentContext = {chat: [{"role": "system", "text": "Hello"}]}
        with patch("aiofiles.open", new_callable=AsyncMock) as mock_open:
            mock_open.return_value.__aenter__.return_value.read.return_value = '{"introduce": "Hello", "technicalInstructions": "Follow the rules", "scenaries": {"testScript": "Test scenario"}}'
            result = await self.chatBot._get_message(scriptKey, chat, message)
            self.assertEqual(result, [
                {"role": "system", "text": "Hello"},
                {"role": "system", "text": "Follow the rules"},
                {"role": "system", "text": "Test scenario"},
                {"role": "system", "text": "Hello"},
                {"role": "user", "text": "Hello"}
            ])

    async def test_send_message(self):
        scriptKey = "testScript"
        chat = "12345"
        message = {"role": "user", "text": "Hello"}
        self.chatBot._currentContext = {chat: []}
        self.mock_gpt.request.return_value = "GPT response"
        self.chatBot.messageAnalyzer = AsyncMock(MessageAnalyzer)
        self.chatBot.messageAnalyzer.analyze_GPT_answer.return_value = "Analyzed response"
        with patch("aiofiles.open", new_callable=AsyncMock) as mock_open:
            mock_open.return_value.__aenter__.return_value.read.return_value = '{"introduce": "Hello", "technicalInstructions": "Follow the rules", "scenaries": {"testScript": "Test scenario"}}'
            response = await self.chatBot.send_message(scriptKey, chat, message)
            self.assertEqual(response, "Analyzed response")
            self.assertEqual(self.chatBot._currentContext[chat], [
                {"role": "user", "text": "Hello"},
                {"role": "assistant", "text": "GPT response"}
            ])

if __name__ == '__main__':
    unittest.main()