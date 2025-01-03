import requests
import json
from datetime import date, timedelta,datetime
from dataBase.localDB import DataBase
# Разобраться с хэшированием 
#Дописать функции получения данных из разных таблиц.
#Написать декорратор, проверяющий на валидность временный токен
class AlfaCRM: 
    def __init__(self, hostname:str, email:str, key:str):
        self.models = {
            "Students": "customer/index",
            "Locations": "location/index",
            "Group": "group/index",
            "Lessons": "lesson/index",
            "Teachers" : "teacher/index"}
        self.email = email
        self.key = key
        self.hostname = hostname
        self.header = self._fillHeader()
        self.brunchId = self._getBrunches()
    
        

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
        


class AlfaCRMDataWrapper:
    def __init__(self,dataBase:DataBase, crm:AlfaCRM, updatePeriotByNexLesson:int = 14, updatePeriodByPrevLesson:int = 7):
        self.crm = crm
        self.DB = dataBase
        self.data = {}
        self.updatePeriodToNext = updatePeriotByNexLesson
        self.updatePeriodToPrevious = updatePeriodByPrevLesson
    
  
    
    def _fillNextLessons(self):
        dateNextLesson = date.today() + timedelta(self.updatePeriodToNext)
        self.nextLessons = self.crm.getData("Lessons", {'status': 1,'date_from':date.today().strftime('%y-%m-%d'), 'date_to':dateNextLesson.strftime('%y-%m-%d')})
        

    def _fillPreviusLessons(self):
        datePreviousLesson= date.today() - timedelta(self.updatePeriodToPrevious)
        previousLesson = self.crm.getData("Lessons", {'status': 3, 'date_from':datePreviousLesson.strftime('%y-%m-%d'), 'date_to':date.today().strftime('%y-%m-%d')})
        self.previousLessons = []
        for i in previousLesson:
            if i['regular_id'] != None:
                self.previousLessons.append(i)
    
    def fillDataBase(self):
        self._fillNextLessons()
        self._fillPreviusLessons()
        self._fillGroupOccupancy()
        self._fillStudentAsences()
    def _fillGroupOccupancy(self):
        groupList =[]
        for lesson in self.nextLessons:
            groupList.append({
                'idsStudents': str(lesson['customer_ids']),
                'topic': str(self._getTopic(lesson['group_ids'])),
                'location':str(self._getLocationName(lesson['group_ids'])),
                'teachers': str(self._getTeachersName(lesson['group_ids'])),
                'day': str(getDayName(datetime.strptime(lesson['date'],'%Y-%m-%d'))),
                'time': str(datetime.strptime(lesson['time_from'],'%Y-%m-%d %H:%M:%S').time().strftime('%H:%M:%S')),
                'assignWorkOffs': 1,
                'groupId': lesson["group_ids"][0],
                'countStudents':len(lesson['customer_ids']),
                'limit': self._getGroupLimit(lesson['group_ids'])
            })
        self.DB.fillTableGroupOccupancy(groupList)
    def _getGroupLimit(self,id):
        groups = self.crm.getData("Group",{'id':id[0]})
        
        return groups[0]['limit']
    
    def _fillStudentAsences(self):
        asencesList =[]
        for lesson in self.previousLessons:
            for details in lesson['details']:
                if details['is_attend'] == 0:
                   asencesList.append(self._addStudent(lesson, details))
        self.DB.fillTableStudentAbsences(asencesList)

    def _addStudent(self,lesson:dict, details:dict):
        return {
            'id' : details['customer_id'],
            'name' : self._getStudentName(details['customer_id']),
            'date' : lesson['date'],
            'topic' : lesson['topic'],
            'groupId' : lesson['group_ids'][0],
            'phoneNumber': self._getStudentPhoneNumber(details['customer_id']),
            'teacher': self._getTeachersName(lesson['group_ids']),
            'assignWorksOff': 0
        }
    def _getStudentPhoneNumber(self, id):
        student = self.crm.getData("Students", {'id': id})
        if len(student):
            phones = student[0]['phone']
            return phones[0]
        else:
            return None
    def _getStudentName(self,id):
       
        student = self.crm.getData("Students", {'id': id})
        if len(student):
            return student[0]['name']
    
    def _getTeachersName(self, id:list):
        groups = self.crm.getData("Group",{'id':id[0]})
        return groups[0]['teacher_ids']
        
        
        
    
    #Костыль, чисто под нашу CRM, думать, как решить лучше
    def _getLocationName(self, id:list):
        groups = self.crm.getData("Group",{'id':id[0]})
        
        if 'ЮГ' in groups[0]['name']:
            return 'Юг'
        else:
            return 'Центр'
        

    def _getTopic(self,id:list):
        for i in self.previousLessons:
            if id[0] in i['group_ids']:
                return i['topic']

def getDayName(dateTtime:datetime):
    match(datetime.weekday(dateTtime)):
        case 0:
            return "Понедельник"
        case 1:
            return "Вторник"
        case 2:
            return "Среда"
        case 3:
            return "Четверг"
        case 4:
            return "Пятница"
        case 5: 
            return "Суббота"
        case 6:
            return "Воскресенье"

    
           
            
          
        

        



        