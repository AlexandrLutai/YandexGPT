import aiohttp
import json
from typing import Callable




class AlfaCRM:
    """
    Класс для взаимодействия с API AlfaCRM.
    Атрибуты:
        MODELS_FOR_GETTING_DATA (dict): Константный словарь, содержащий пути для получения данных из различных моделей.
        MODELS_FOR_CREATING (dict): Константный словарь, содержащий пути для создания новых записей в различных моделях.
    """
    def _handle_401(func: Callable) -> Callable:
        """
        Декоратор для обработки ошибки 401 и повторного выполнения запроса.
        """
        async def wrapper(self, *args, **kwargs):
            try:
                response = await func(self, *args, **kwargs)
                response.raise_for_status()
                return response
            except aiohttp.ClientResponseError as e:
                if 'response' in locals() and e.status == 401:
                    await self._fill_header()
                    try:
                        response = await func(self, *args, **kwargs)
                        response.raise_for_status()
                        return response
                    except aiohttp.ClientResponseError as e:
                        print(f"Ошибка при повторном выполнении запроса: {e}")
                        return None
                else:
                    print(f"Ошибка при выполнении запроса: {e}")
                    return None
        return wrapper

    MODELS_FOR_GETTING_DATA = {
        "RegularLessons": "regular-lesson/index",
        "Students": "customer/index",
        "Locations": "location/index",
        "Groups": "group/index",
        "Lessons": "lesson/index",
        "Teachers": "teacher/index",
        "Locations": "location/index",
    }
    MODELS_FOR_CREATING = {
        "Lessons": "lesson/create",
    }

    def __init__(self, hostname: str, email: str, key: str):
        """
        Инициализирует объект AlfaCRM.

        Args:
            hostname (str): Имя хоста в CRM.
            email (str): Электронная почта для авторизации.
            key (str): API ключ для авторизации.
        """
        self._email = email
        self._key = key
        self._hostname = hostname
        
        self._fill_header()
        self._brunchId = self._get_id_brunches(self.get_items(self._get_brunches()))

    async def _get_temp_token(self) -> str:
        """
        Получает временный токен для авторизации.

        Returns:
            str: Временный токен.
        """
        path = f"https://{self._hostname}/v2api/auth/login"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(path, json={'email': self._email, 'api_key': self._key}) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data["token"]
            except aiohttp.ClientResponseError as e:
                print(f"Ошибка при получении временного токена: {e}")
                return ""

    async def _fill_header(self) -> None:
        """
        Заполняет заголовок запроса временным токеном.
        """
        token = await self._get_temp_token()
        self._header = {'X-ALFACRM-TOKEN': token, 'Content-Type': 'application/json', 'Accept': 'application/json'}

    @_handle_401
    async def _get_brunches(self) -> aiohttp.ClientResponse:
        """
        Получает данные филиалов.

        Returns:
            aiohttp.ClientResponse: Ответ от сервера.
        """
        path = f"https://{self._hostname}/v2api/branch/index"
        async with aiohttp.ClientSession() as session:
            return await session.post(path, json={"is_active": 1}, headers=self._header)

    async def _get_id_brunches(self, brunches: list[int]) -> int:
        """
        !!!!Доработать!!!!
            Предоставить выбор филиала пользователю.

        Получает идентификатор филиала из списка филиалов.

        Args:
            brunches (list): Список филиалов.

        Returns:
            int: Идентификатор филиала.
        """
        match len(brunches):
            case 1:
                return brunches[0]["id"]
            case _:
                return brunches[1]["id"]

    @_handle_401
    async def create_model(self, model: str, data: dict[str, any]) -> aiohttp.ClientResponse:
        """
        Создает модель в CRM.

        Args:
            model (str): Название модели. Ключ словаря MODELS_FOR_CREATING.
            data (dict[str, any]): Данные для создания модели.

        Returns:
            aiohttp.ClientResponse: Ответ от сервера.
        """
        path = f"https://{self._hostname}/v2api/{self._brunchId}/{AlfaCRM.MODELS_FOR_CREATING[model]}"
        async with aiohttp.ClientSession() as session:
            return await session.post(path, json=data, headers=self._header)

    @_handle_401
    async def get_data(self, model: str, data: dict[str, any]) -> aiohttp.ClientResponse:
        """
        Получает данные из CRM.

        Args:
            model (str): Название модели. Ключ словаря MODELS_FOR_GETTING_DATA.
            data (dict[str, any]): Данные для запроса.

        Returns:
            aiohttp.ClientResponse: Ответ от сервера.
        """
        path = f"https://{self._hostname}/v2api/{self._brunchId}/{AlfaCRM.MODELS_FOR_GETTING_DATA[model]}"
        async with aiohttp.ClientSession() as session:
            return await session.post(path, json=data, headers=self._header)

    async def get_items(self, response: aiohttp.ClientResponse) -> dict[str, any]:
        """
        Получает список данных из ответа.

        Args:
            response (aiohttp.ClientResponse): Ответ от сервера.

        Returns:
            list: Список данных.
        """
        try:
            response.raise_for_status()
            data = await response.json()
            return data["items"]
        except aiohttp.ClientResponseError as e:
            print(f"Ошибка при получении данных: {e}")
            return []



















