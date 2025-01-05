import requests
import json
from datetime import date, timedelta,datetime
from dataBase.localDB import DataBase
import re
# Разобраться с хэшированием 
#Дописать функции получения данных из разных таблиц.
#Написать декорратор, проверяющий на валидность временный токен
class AlfaCRM: 
    def __init__(self, hostname:str, email:str, key:str):
        self.models = {
            "Students": "customer/index",
            "Locations": "location/index",
            "Groups": "group/index",
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
        

#Пересмотреть функции доступа к CRM, из за частых обращений работает крайне долго,
#Подумать над тем, что бы вытягивать все нужные данные одним запросом.
class AlfaCRMDataWrapper:
    def __init__(self,dataBase:DataBase, crm:AlfaCRM, updatePeriotByNexLesson:int = 7, updatePeriodByPrevLesson:int = 7):
        self.crm = crm
        self.DB = dataBase
        self.data = {}
        self.updatePeriodToNext = updatePeriotByNexLesson
        self.updatePeriodToPrevious = updatePeriodByPrevLesson
        self._lastUpdate = None
       
   
    def _fillNextLessons(self) -> list:
        
        dateNextLesson = date.today() + timedelta(self.updatePeriodToNext)
        nextLessons =[]
        page = 0
        while True:
            temp = self.crm.getData("Lessons", {'status': 1,'date_from':date.today().strftime('%y-%m-%d'), 'date_to':dateNextLesson.strftime('%y-%m-%d'),'page':page})
            if not temp:
                break
            lessonFilter =[]
            for i in temp:
                if i['regular_id'] != None:
                    lessonFilter.append(i)
            page +=1
            nextLessons.append(lessonFilter)
        return nextLessons
    
    
    def _fillPreviusLessons(self) -> list:
        datePreviousLesson= date.today() - timedelta(self.updatePeriodToPrevious)
        previousLesson = []
        page = 0
        while True:
            temp = self.crm.getData("Lessons", {'status': 3, 'date_from':datePreviousLesson.strftime('%y-%m-%d'), 'date_to':date.today().strftime('%y-%m-%d'),'page':page})
            if not temp:
                break
            lessonFilter =[]
            for i in temp:
                if i['regular_id'] != None:
                    lessonFilter.append(i)
            page +=1
            previousLesson.append(lessonFilter)
        return previousLesson
    
   
    def _fillGroups(self)->list:
        groups = []
        page =0
        while True:
            onePage = self.crm.getData("Groups", {"removed":0, "page":page})
            page +=1
            if not onePage:
                break
            groups.append(onePage)
        return groups
    
  
    def _fillStudents(self) ->list:
        page =0
        students = []
        while True:
            onePage = self.crm.getData("Students", {"removed":0, "is_study": 1, "page":page, 'withGroups':False})
            page +=1
            if not onePage:
                break
            students.append(onePage)
        return students
    
    
    def _findRecord(self,table:list,key:str,value):
        for page in table:
            for record in page:
                if record[key] == value:
                    return record
        return []
    
    def _fillTempLists(self):
        self._studentsData =self._fillStudents()
        self._groupData = self._fillGroups()
        self._nextLessonsData = self._fillNextLessons()
        self._previusLessonData = self._fillPreviusLessons()

    def _clearTempLists(self):
        self._studentsData.clear() 
        self._groupData.clear()
        self._nextLessonsData.clear()
        self._previusLessonData.clear()

    #Подумать над периодом синхронизации, раз в какой то промежуток времени
    def synchronizeGroupOccupancyTable(self,synchronizeAnyware:bool = False):
        self._fillTempLists()      
        self._fillTableGroupOccupancy()
        self._clearTempLists()

    def addStudentInTableStudentAsences(self):
        self._fillTempLists()      
        self._fillTableStudentAsences()
        self._clearTempLists()
    

    
    def _fillTableGroupOccupancy(self):
        groupList =[]
        for page in self._nextLessonsData:
            for lesson in page:
                group = self._findRecord(self._groupData,'id',lesson['group_ids'][0])
                groupList.append({
                    'idsStudents': ','.join(map(str,lesson['customer_ids'])),
                    'topic': lesson['topic'],
                    'location':self._getLocationName(group),
                    'teachers': ', '.join(group['teacher_ids']),
                    'day': getDayName(datetime.strptime(lesson['date'],'%Y-%m-%d')),
                    'time': datetime.strptime(lesson['time_from'],'%Y-%m-%d %H:%M:%S').time().strftime('%H:%M'),
                    'assignWorkOffs': 1,
                    'idGroup': lesson["group_ids"][0],
                    'countStudents':len(lesson['customer_ids']),
                    'limit': group['limit']
                })
        self.DB.fillTableGroupOccupancy(groupList)
    
    def _fillTableStudentAsences(self):
        
        for page in self._previusLessonData:
            record = []
            for lesson in page:
                for students in lesson['details']:
                    if not students['is_attend']:
                        if student := self._getAsence(lesson,students['customer_id']):
                            record.append(student)
        self.DB.fillTableStudentAbsences(record)
    
    # def _fillStudentAsences(self):
    #     asencesList =[]
    #     for lesson in self.previousLessons:
    #         for details in lesson['details']:
    #             if details['is_attend'] == 0:
    #                asencesList.append(self._addStudent(lesson, details))
    #     self.DB.fillTableStudentAbsences(asencesList)

    def _getAsence(self,lesson:dict, idStudent:int):
        
        student = self._findRecord(self._studentsData,'id', idStudent)
        if student:
            group = self._findRecord(self._groupData, 'id',lesson['group_ids'][0])
            return {
                'id' : idStudent,
                'name' : student['name'],
                'date' : lesson['date'],
                'topic' : lesson['topic'],
                'idGroups' : ', '.join(map(str,lesson['group_ids'])),
                'idLesson': lesson['id'],
                'phoneNumber': student['phone'][0].replace('+','').replace('-','').replace('(','').replace(')',''),
                'teacher':','.join(group['teacher_ids']),
            
            
            
        }
    #Костыль, чисто под нашу CRM, думать, как решить лучше
    def _getLocationName(self, group:list):
        if 'ЮГ' in group['name']:
            return 'Юг'
        else:
            return 'Центр'

    
    # def fillDataBase(self):
    #     self._fillNextLessons()
    #     self._fillPreviusLessons()
    #     self._fillGroupOccupancy()
    #     self._fillStudentAsences()
    # def _fillGroupOccupancy(self):
    #     groupList =[]
    #     for lesson in self.nextLessons:
    #         groupList.append({
    #             'idsStudents': str(lesson['customer_ids']),
    #             'topic': str(self._getTopic(lesson['group_ids'])),
    #             'location':str(self._getLocationName(lesson['group_ids'])),
    #             'teachers': str(self._getTeachersName(lesson['group_ids'])),
    #             'day': str(getDayName(datetime.strptime(lesson['date'],'%Y-%m-%d'))),
    #             'time': str(datetime.strptime(lesson['time_from'],'%Y-%m-%d %H:%M:%S').time().strftime('%H:%M:%S')),
    #             'assignWorkOffs': 1,
    #             'groupId': lesson["group_ids"][0],
    #             'countStudents':len(lesson['customer_ids']),
    #             'limit': self._getGroupLimit(lesson['group_ids'])
    #         })
    #     self.DB.fillTableGroupOccupancy(groupList)
    # def _getGroupLimit(self,id):
    #     groups = self.crm.getData("Group",{'id':id[0]})
        
    #     return groups[0]['limit']
    
    # def _getStudentPhoneNumber(self, id):
    #     student = self.crm.getData("Students", {'id': id})
    #     if len(student):
    #         phones = student[0]['phone']
    #         return phones[0]
    #     else:
    #         return "None"
    # def _getStudentName(self,id):
       
    #     student = self.crm.getData("Students", {'id': id})
    #     if len(student):
    #         return student[0]['name']
    #     return "None"
    
    # def _getTeachersName(self, id:list):
    #     groups = self.crm.getData("Group",{'id':id[0]})
    #     return groups[0]['teacher_ids']
        
        
        
    
   
        

    # def _getTopic(self,id:list):
    #     for i in self.previousLessons:
    #         if id[0] in i['group_ids']:
    #             return i['topic']

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

    
           
            
          
        

        



        