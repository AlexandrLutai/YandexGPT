import requests
import json

# Разобраться с хэшированием 
#Дописать функции получения данных из разных таблиц.
#Написать декорратор, проверяющий на валидность временный токен
class AlfaCRM: 
    def __init__(self, hostname:str, email:str, key:str):
        self.models = {
            "Students": "customer/index",
            "Locations": "location/index",
            "Group": "group/index",
            "Lessons": "lesson/index"}
        self.email = email
        self.key = key
        self.hostname = hostname
        self.header = self._fillHeader()
        self.brunchId = self._getBrunches();
    
        

    def _getTempToken(self):
        path = f"https://{self.hostname}/v2api/auth/login"
        r = requests.post(path,json.dumps({'email':self.email, 'api_key':self.key}))
        return json.loads(r.text)["token"]

    
    def _fillHeader(self):
        self.header = {'X-ALFACRM-TOKEN': self._getTempToken()}
    
    def _getBrunches(self):    
        path = f"https://{self.hostname}/v2api/branch/index"
        r = requests.post(path,data=json.dumps({"is_active" : 1}), headers = self.header)
        brunchDict = json.loads(r.text)
        if "items" in brunchDict:
            return self._getIdBrunches(brunchDict["items"])
        else:
            self._fillHeader()
            return self._getBrunches()
    
    def _getIdBrunches(self, brunches:list):       
        match(len(brunches)):
            case 1:
                return brunches[0]["id"]
            case _:
                return brunches[1]["id"]

        
    def getData(self,model:str, data: dict):
        path = f"https://{self.hostname}/v2api/{self.brunchId}/{self.models[model]}"
        r = requests.post(path,data=json.dumps(data),headers = self.header)
        dataDict = json.loads(r.text)
        if "items" in dataDict:
            return dataDict["items"]
        else:
            self._fillHeader()
            return self.getData()