from dotenv import load_dotenv
import os

# Загрузка переменных из .env в корне проекта
load_dotenv(dotenv_path="config.env")

class Config:
    def __init__(self):
        self.crmEmail = os.getenv("CRM_EMAIL")
        self.crmhostname = os.getenv("CRM_HOSTNAME")
        self.crmKey = os.getenv("CRM_KEY")
        self.yandexGPTKey = os.getenv("YANDEX_GPT_KEY")
        self.yandexCloudIdentificator = os.getenv("YANDEX_CLOUD_IDENTIFICATOR")
        self.wazzup_api_key = os.getenv("WAZZUP_API_KEY")