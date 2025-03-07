import unittest
import aiounittest
from unittest.mock import AsyncMock, patch, MagicMock
from crm.AlfaCRM.alfaCRM import AlfaCRM
import aiohttp

class TestAlfaCRM(aiounittest.AsyncTestCase):

    def setUp(self):
        self.crm = AlfaCRM('hostname', 'email', 'key')
        self.crm._header = {'X-ALFACRM-TOKEN': 'token', 'Content-Type': 'application/json', 'Accept': 'application/json'}
        self.crm._brunchId = 1

    @patch('aiohttp.ClientSession.post')
    async def test_get_temp_token(self, mock_post):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={'token': 'temp_token'})
        mock_post.return_value = mock_response

        token = await self.crm._get_temp_token()
        self.assertEqual(token, 'temp_token')

if __name__ == '__main__':
    unittest.main()