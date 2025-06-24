import unittest
from unittest.mock import patch, AsyncMock
from YandexGPT.yandexGPTModel import YandexGPTModel
from mTyping.dictTypes import MessageForPromptDict
import json

class TestYandexGPTModel(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.authKey = "test_auth_key"
        self.cloudBranch = "test_cloud_branch"
        self.temperature = 0.3
        self.model = YandexGPTModel(self.authKey, self.cloudBranch, self.temperature)
        self.messages = [
            {"role": "user", "text": "Hello, how are you?"},
            {"role": "assistant", "text": "I'm fine, thank you!"}
        ]

    async def test_fill_GPT_prompt(self):
        expected_prompt = {
            "modelUri": f"gpt://{self.cloudBranch}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": self.temperature,
                "maxTokens": "1000"
            },
            'messages': self.messages
        }
        result = await self.model._fill_GPT_prompt(self.messages)
        self.assertEqual(result, expected_prompt)

    @patch('aiohttp.ClientSession.post')
    async def test_request_success(self, mock_post):
        mock_response = AsyncMock()
        mock_response.text = AsyncMock(return_value=json.dumps({
            "result": {
                "alternatives": [
                    {"message": {"text": "I'm fine, thank you!"}}
                ]
            }
        }))
        mock_post.return_value.__aenter__.return_value = mock_response

        result = await self.model.request(self.messages)
        self.assertEqual(result, "I'm fine, thank you!")

    @patch('aiohttp.ClientSession.post')
    async def test_request_failure(self, mock_post):
        mock_response = AsyncMock()
        mock_response.text = AsyncMock(return_value=json.dumps({
            "error": "Some error occurred"
        }))
        mock_post.return_value.__aenter__.return_value = mock_response

        result = await self.model.request(self.messages)
        self.assertIn("error", result)

if __name__ == '__main__':
    unittest.main()