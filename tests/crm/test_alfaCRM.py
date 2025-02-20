import unittest
from unittest.mock import AsyncMock, patch
from crm.AlfaCRM.alfaCRM import AlfaCRM
import aiohttp
import asyncio

class TestAlfaCRM(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.alfa_crm = AlfaCRM("hostname", "email@example.com", "api_key")
        with patch('aiohttp.ClientSession.post', new_callable=AsyncMock) as mock_post:
            mock_response = AsyncMock()
            mock_response.json.return_value = {"token": "test_token"}
            mock_post.return_value.__aenter__.return_value = mock_response
            await self.alfa_crm.init()
    
    async def test_get_temp_token_success(self):
        with patch('aiohttp.ClientSession.post', new_callable=AsyncMock) as mock_post:
            mock_response = AsyncMock()
            mock_response.json.return_value = {"token": "test_token"}
            mock_post.return_value.__aenter__.return_value = mock_response

            token = await self.alfa_crm._get_temp_token()
            self.assertEqual(token, "test_token")

    async def test_get_temp_token_failure(self):
        with patch('aiohttp.ClientSession.post', new_callable=AsyncMock) as mock_post:
            mock_response = AsyncMock()
            mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(
                request_info=None, history=None, status=401, message="Unauthorized", headers=None
            )
            mock_post.return_value.__aenter__.return_value = mock_response

            token = await self.alfa_crm._get_temp_token()
            self.assertEqual(token, "")

if __name__ == '__main__':
    unittest.main()