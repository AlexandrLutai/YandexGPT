import requests
import json
from mTyping.dictTypes import MessageForPromptDict
class YandexGPTModel:

    def __init__(self, authKey:str, cloudBranch:str, temperature:float = 0.3):
        """
        Инициализирует объект модели YandexGPT.

        Args:
            authKey (str): Ключ авторизации для API.
            cloudBranch (str): Ветка облака для модели.
            temperature (float): Температура генерации текста.
        """
        self._headers ={
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {authKey}"
        } 
        self._competitions = {
            "stream": False,
            "temperature": temperature,
            "maxTokens": "1000"
        }
        self._url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self._modelUrl = f"gpt://{cloudBranch}/yandexgpt-lite"      

    
    def _fill_GPT_prompt(self, messages:list[MessageForPromptDict]):
        """
        Заполняет запрос для модели GPT.

        Args:
            messages (list): Список сообщений.

        Returns:
            dict: Заполненный запрос.
        """
        return {
            "modelUri": self._modelUrl,
            "completionOptions":self._competitions,
            'messages':messages
        }
    
    def request(self, messages:list[MessageForPromptDict]):
        """
        Отправляет запрос к модели GPT.

        Args:
            messages (list): Список сообщений.

        Returns:
            str: Ответ модели.
        """
        prompt = self._fill_GPT_prompt(messages)

        r = requests.post(url=self._url, json=prompt, headers=self._headers)
        print(r.text)
       
        if 'result' in r.text:
            return json.loads(r.text)['result']["alternatives"][0]["message"]['text']
        return r.text
