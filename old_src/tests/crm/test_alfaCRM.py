# import unittest
# import aiounittest
# from unittest.mock import AsyncMock, patch, MagicMock
# from crm.AlfaCRM.alfaCRM import AlfaCRM
# import aiohttp

# class TestAlfaCRM(aiounittest.AsyncTestCase):

#     def setUp(self):
#         self.crm = AlfaCRM('hostname', 'email', 'key')
#         self.crm._header = {'X-ALFACRM-TOKEN': 'token', 'Content-Type': 'application/json', 'Accept': 'application/json'}
#         self.crm._brunchId = 1

# if __name__ == '__main__':
#     unittest.main()