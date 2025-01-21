import unittest
from unittest.mock import patch, Mock
from YandexGPT.yandexGPT import YandexGPTModel, YandexGPTChatBot
from dataBase.DataBase import DataBase

class TestYandexGPTModel(unittest.TestCase):

    @patch('requests.post')
    def test_gptRequest(self, mock_post):
        mock_response = Mock()
        mock_response.text = '{"response": "test response"}'
        mock_post.return_value = mock_response

        model = YandexGPTModel('fake_auth_key', 'fake_cloud_branch')
        messages = [{"role": "user", "text": "Hello"}]
        response = model.request(messages)

        self.assertEqual(response, '{"response": "test response"}')
        mock_post.assert_called_once()


if __name__ == '__main__':
    unittest.main()
