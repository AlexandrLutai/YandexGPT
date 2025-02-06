import requests
import json
from typing import Callable
# Разобраться с хэшированием 
#Дописать функции получения данных из разных таблиц.
#Написать декорратор, проверяющий на валидность временный токен

def handle_401(func: Callable) -> Callable:
    """
    Декоратор для обработки ошибки 401 и повторного выполнения запроса.

    Args:
        func (Callable): Функция для выполнения запроса.

    Returns:
        Callable: Обернутая функция.
    """
    def wrapper(self, *args, **kwargs):
        try:
            response = func(self, *args, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if response.status_code == 401:
                self._fillHeader()
                try:
                    response = func(self, *args, **kwargs)
                    response.raise_for_status()
                    return response
                except requests.RequestException as e:
                    print(f"Ошибка при повторном выполнении запроса: {e}")
                    return None
            else:
                print(f"Ошибка при выполнении запроса: {e}")
                return None
    return wrapper

class AlfaCRM: 
    def __init__(self, hostname:str, email:str, key:str):
        """
        Инициализирует объект AlfaCRM.

        Args:
            hostname (str): Хостнейм CRM.
            email (str): Электронная почта для авторизации.
            key (str): API ключ для авторизации.
        """
        self._getModels = {
            "RegularLessons":"regular-lesson/index",
            "Students": "customer/index",
            "Locations": "location/index",
            "Groups": "group/index",
            "Lessons": "lesson/index",
            "Teachers" : "teacher/index",
            "Locations" : "location/index",
            }
        self._createModels = {
            "Lessons" : "lesson/create",
        }
        self._email = email
        self._key = key
        self._hostname = hostname
        self._fillHeader()
        self._brunchId = self._getIdBrunches(self.getItems(self._getBrunches()))
    
        

    def _getTempToken(self) -> str:
        """
        Получает временный токен для авторизации.
        
        Returns:
            str: Временный токен.
        """
        path = f"https://{self._hostname}/v2api/auth/login"
        r = requests.post(path,json.dumps({'email':self._email, 'api_key':self._key}))
        return json.loads(r.text)["token"]

    
    def _fillHeader(self) -> None:
        """
        Заполняет заголовок запроса временным токеном.
        """
        self._header = {'X-ALFACRM-TOKEN': self._getTempToken()}
    
    @handle_401
    def _getBrunches(self) -> requests.Response:    
        """
        Получает ответ с данными филиалов.

        Returns:
            requests.Response: Ответ от сервера.
        """
        path = f"https://{self._hostname}/v2api/branch/index"
        return requests.post(path,data=json.dumps({"is_active" : 1}), headers = self._header)
        
            
    
    def _getIdBrunches(self, brunches:list[int]) ->int:       
        """
        Получает идентификатор филиала из списка филиалов.

        Args:
            brunches (list): Список филиалов.

        Returns:
            int: Идентификатор филиала.
        """
        match(len(brunches)):
            case 1:
                return brunches[0]["id"]
            case _:
                return brunches[1]["id"]


    @handle_401
    def createModel(self, model:str, data: dict[str:any]) -> requests.Response:
        """
        Создает модель в CRM.

        Args:
            model (str): Название модели.
            data (dict[str:any]): Данные для создания модели.

        Returns:
            requests.Response: Ответ от сервера.
        """
        self._header.update({'Content-Type': 'application/json', 'Accept': 'application/json'})
        path = f"https://{self._hostname}/v2api/{self._brunchId}/{self._createModels[model]}"
        return requests.post(path,json.dumps(data),headers = self._header)
        
            
    
        
    @handle_401
    def getData(self,model:str, data: dict[str:any]) -> requests.Response:
        """
        Получает данные из CRM.

        Args:
            model (str): Название модели.
            data (dict[str:any]): Данные для запроса. Передавать можно любые поля, доступные по выбранной ветке.

        Returns:
            requests.Response: Ответ от сервера.
        """
        path = f"https://{self._hostname}/v2api/{self._brunchId}/{self._getModels[model]}"
        return requests.post(path,data=json.dumps(data),headers = self._header)
        

    def getItems(self, response: requests.Response) -> list:
        """
        Получает список данных из ответа.

        Args:
            response (requests.Response): Ответ от сервера.

        Returns:
            list: Список данных.
        """
        return json.loads(response.text)["items"]



















