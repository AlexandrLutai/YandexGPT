from fastapi import FastAPI, Request
from Whatsupp.whatsuppMessageAnalyzer import WhatsuppMessageAnalyzer
from YandexGPT.yandexGPTManager import YandexGPTManager
from crm.AlfaCRM.alfaCRMDataManager import AlfaCRMDataManager
from dataBase.databaseManager import DataBaseManager
from Whatsupp.wazzup import Wazzup
from autorizationData.authorizationData import Config

class WebhookHandler:
    def __init__(self):
        """
        Инициализация класса WebhookHandler.
        """
        self.cfg = Config()
        self.app = FastAPI(on_startup=[self._initialize_dependencies])  # Используем on_startup
        self.whatsappManager = None
        self._setup_routes()

    def _setup_routes(self):
        """
        Настройка маршрутов FastAPI.
        """
        @self.app.post("/webhook")
        async def handle_webhook(request: Request):
            """
            Эндпоинт для получения вебхуков.
            """
            payload = await request.json()
            await self.process_webhook(payload)
            return {"status": "OK"}

    async def _initialize_dependencies(self):
        """
        Инициализация зависимостей при старте приложения.
        """
        gpt = YandexGPTManager(
            api_key=self.cfg.yandexGPTKey,
            cloudBranch=self.cfg.yandexCloudIdentificator,
            crm=AlfaCRMDataManager(self.cfg.crmEmail, self.cfg.crmhostname, self.cfg.crmKey),
            db=DataBaseManager("main.db")
        )
        whatsapp = await Wazzup.create(self.cfg.wazzup_api_key)  # Используем await для асинхронного создания
        self.whatsappManager = WhatsuppMessageAnalyzer(gpt=gpt, wazzup=whatsapp)

    async def process_webhook(self, payload: dict):
        """
        Обрабатывает данные вебхука.

        Args:
            payload (dict): Данные, полученные из вебхука.
        """
        await self.whatsappManager.analyze_message(payload)

# Создание экземпляра WebhookHandler
webhook_handler = WebhookHandler()
app = webhook_handler.app