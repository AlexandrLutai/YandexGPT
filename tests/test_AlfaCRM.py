import unittest
from unittest.mock import patch, MagicMock
from crm.alfaCRM import AlfaCRM
import json

class TestAlfaCRM(unittest.TestCase):

    @patch('crm.alfaCRM.requests.post')
    def setUp(self, mock_post):
        self.mock_post = mock_post
        self.mock_post.return_value.text = json.dumps({"token": "test_token"})
        self.crm = AlfaCRM("hostname", "email", "key")

    def test_getTempToken(self):
        token = self.crm._getTempToken()
        self.assertEqual(token, "test_token")

    @patch('crm.alfaCRM.requests.post')
    def test_fillHeader(self, mock_post):
        mock_post.return_value.text = json.dumps({"token": "test_token"})
        self.crm._fillHeader()
        self.assertEqual(self.crm._header, {'X-ALFACRM-TOKEN': 'test_token'})

    @patch('crm.alfaCRM.requests.post')
    def test_getBrunches(self, mock_post):
        mock_post.return_value.text = json.dumps({"items": [{"id": 1}]})
        brunch_id = self.crm._getBrunches()
        self.assertEqual(brunch_id, 1)

    @patch('crm.alfaCRM.requests.post')
    def test_getData(self, mock_post):
        mock_post.return_value.text = json.dumps({"items": [{"id": 1, "name": "Test"}]})
        data = self.crm.getData("Teachers", {})
        self.assertEqual(data, [{"id": 1, "name": "Test"}])

if __name__ == '__main__':
    unittest.main()
