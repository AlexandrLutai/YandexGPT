import aiohttp 
import json
class Wazzup:
    def __init__(self,api_key):
        self.header = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def _get_channel_id(self):
        # Доработать! На данный момент отсутствует возможность выбора канала
        url = "https://api.wazzup24.com/v3/channels"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.header) as response:
                data = await response.json()  
                return data[0]["channelId"]

    async def send_message(self, phone_number, message):
        url = "https://api.wazzup24.com/v3/message"
        data = {
            "channelId": self._channel_id,
            "chatType": "whatsapp",
            "chatId": phone_number,
            "text": message,
        }
        print(data)
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.header, json=data) as response:
                return await response.json()

    @classmethod
    async def create(cls, api_key):
        self = cls(api_key)
        self._channel_id = await self._get_channel_id()
        return self


