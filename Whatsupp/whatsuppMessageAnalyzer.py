import dataBase.database as DataBase
from crm.crmDataManagerInterface import CrmDataManagerInterface
from YandexGPT.yandexGPTChatBot import YandexGPTChatBot
class WhatsuppMessageAnalyzer:
    def __init__(self, db:DataBase, crm:CrmDataManagerInterface, gpt:YandexGPTChatBot):
        """
        Инициализирует объект WhatsuppMessageAnalyzer.
        """
        self._db = db
        self._crm = crm
        self._gpt = gpt
        pass

    async def analyze_message(self, message:dict[str:str]):
        if context := await self._gpt.get_current_context(message['chatId']) != None:
            
            pass
        else:
            pass
        pass