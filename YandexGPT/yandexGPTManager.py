from YandexGPT.yandexGPTChatBot import YandexGPTChatBot
from YandexGPT.chatScriptAnalyzer import ChatScriptAnalyzer
from YandexGPT.gptMessageAnalyzer import GptMessageAnalyzer
from YandexGPT.yandexGPTModel import YandexGPTModel
from crm.crmDataManagerInterface import CrmDataManagerInterface
from dataBase.databaseManager import DataBaseManager

from datetime import datetime
class YandexGPTManager:

    def __init__(self, api_key, crm:CrmDataManagerInterface, db:DataBaseManager):
        model = YandexGPTModel(api_key)
        self.chat_bot = YandexGPTChatBot(model)
        self.chat_script_analyzer = ChatScriptAnalyzer(model, "prompts/chatBotPrompst.json")
        self.gpt_message_analyzer = GptMessageAnalyzer()
        self.chat_scenaries = {}


    
    async def send_gpt_message(self,message:dict):
        message_text = message['messages'][0]['text']
        chat_id = message[0]['chatId']
        script = await self.chat_script_analyzer.analyze(message_text)
        if script == None:
            return "Чат-бот не может ответить на ваш вопрос, чат передан менеджеру"
            #Реализовать отправку сообщения менеджеру
        elif script == "neutral":
            if not chat_id in self.chat_scenaries:
                return "Сообщение не распознано, переформулируйте запрос"
        else:
            self.chat_scenaries[chat_id] = {"script": script, "time_to_start_dialog":datetime.now()}
        gpt_message = await self.chat_bot.send_message( self.chat_scenaries[chat_id]["script"],chat_id, message_text)

        message_for_user = self.gpt_message_analyzer.analyze_GPT_answer(gpt_message)
        return message_for_user



