import requests

class YandexGPT:

    def __init__(self, authKey, cloudBranch,temperature:float = 0.3):
        self._headers ={
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {authKey}"
        } 
        self._modelUrl = f"gpt://{cloudBranch}/yandexgpt-lite",        
        self._competitions = {
            "stream": False,
            "temperature": temperature,
            "maxTokens": "2000"
        }
        self._url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    def _fillGPTPrompt(self, messages:list):
        return {
            "modelUri": self.url,
            "completionOptions":self._competitions,
            'messages':messages
        }
    
    def _gptRequest(self,messages:list):
        return requests.post(url=self._url, data=self._fillGPTPrompt(messages), headers=self._headers).text

        