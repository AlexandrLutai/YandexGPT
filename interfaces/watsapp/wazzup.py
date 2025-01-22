import requests
class Wazzup:

    def __init__(self, token: str):
        self.headers = {
            'Content-Type': 'application/json',
            "Authorization": f"Bearer {token}",
        }
        self.getChannels() # Переписать
    
    #Метод костыльный, добавить возможность выбора каналов через интерфейс
    def getChannels(self) -> list[dict[str, str]]:
        channels = requests.get("https://api.wazzup24.com/v3/channels", headers=self.headers)
        channelsJson = channels.json()[0] #Костыль, реализовать выборку канала
        self.channelInfo = {"channelId": channelsJson['channelId'], "chatType": channelsJson['transport']}
    
    def sendMessage(self, text: str, chatType: str, chatId: str) -> str:
        response = requests.post("https://api.wazzup24.com/v3/message", json={"chatId":chatId,"text":text,"chatType" : self.channelInfo["chatType"],  "channelId":self.channelInfo["channelId"]}, headers=self.headers)
        return response.text
    
    def getWebhooks(self) -> list[dict[str, str]]:
        response = requests.patch("https://api.wazzup24.com/v3/webhooks",json={'webhooksUri': 'http://109.196.98.237:8080/', "subscriptions": {"messagesAndStatuses": True,"contactsAndDealsCreation": True}}, headers=self.headers)
        print(response.text)