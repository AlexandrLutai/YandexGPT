from YandexGPT.yandexGPTModel import YandexGPTModel
import json



class ChatScriptAnalyzer:
    def __init__(self, gpt:YandexGPTModel, instractionsPath:str):
        """
        Инициализирует объект анализатора сообщений пользователя.

        Args:
            gpt (YandexGPTModel): Экземпляр модели YandexGPT.
            instractionsPath (str): Путь к файлу инструкций.
        """
        self._gpt = gpt
        self._instractionsPath = instractionsPath
    
    def _get_scenaries(self, instructionsData:dict) -> str:
        """
        Получает сценарии из данных инструкций.

        Args:
            instructionsData (dict): Данные инструкций.

        Returns:
            str: Строка с возможными сценариями.
        """
        scenaries = "Возможные сценарии: \n"
        for key in instructionsData['scenaries'].keys():
            scenaries += key + ": "+ instructionsData['scenaries'][key] + "\n"
        return scenaries

    def _get_prompt(self, message:str) -> list:
        """
        Получает запрос для модели GPT.

        Args:
            message (str): Сообщение пользователя.

        Returns:
            list: Список сообщений для отправки в модель GPT.
        """
        with open(self._instractionsPath, encoding='utf-8') as f:
            instructionData = json.load(f)
        return [
            {
            "role": "system",
            "text": instructionData['instruction']
            },
            {
            "role": "system",
            "text": self._get_scenaries(instructionData)
            },
            {
                "role": "user",
                "text": message
            }
        ]

    def analyze(self, message:str) -> str:
        """
        Анализирует сообщение пользователя и отправляет его в модель GPT.

        Args:
            message (str): Сообщение пользователя.

        Returns:
            str: Ответ модели GPT.
        """
        return self._gpt.request(self._get_prompt(message))
      
