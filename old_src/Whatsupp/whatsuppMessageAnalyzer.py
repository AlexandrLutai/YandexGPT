import dataBase.database as DataBase
from Whatsupp.wazzup import  Wazzup
from YandexGPT.yandexGPTManager import YandexGPTManager
class WhatsuppMessageAnalyzer:
    def __init__(self,wazzup:Wazzup , gpt:YandexGPTManager):
        """
        Инициализирует объект WhatsuppMessageAnalyzer.
        """
        self._wazzup = wazzup
        self._gpt = gpt
        pass

    async def analyze_message(self, message:dict[str:str]):
        gpt_message = await self._gpt.send_gpt_message(message)
        await self._wazzup.send_message(phone_number=message["messages"][0]["chatId"], message=gpt_message )
        pass