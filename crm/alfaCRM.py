import requests
import json
from datetime import date, timedelta,datetime
from dataBase.DataBase import DataBase
from abc import ABC, abstractmethod

class CrmDataManagerInterface(ABC):

    @abstractmethod
    def getLocations(self):
        pass

    @abstractmethod
    def getRegularLessonsByLocationId(self):
        pass
    
    @abstractmethod
    def getTeachers(self):
        pass

    
    @abstractmethod
    def getStudentsMissedLesson(self):
        pass

    @abstractmethod
    def getLocations(self):
        pass

    @abstractmethod
    def addWorkOff(self):
        pass


# Разобраться с хэшированием 
#Дописать функции получения данных из разных таблиц.
#Написать декорратор, проверяющий на валидность временный токен
class AlfaCRM: 
    def __init__(self, hostname:str, email:str, key:str):
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
        self._brunchId = self._getBrunches()
    
        

    def _getTempToken(self) -> str:
        path = f"https://{self._hostname}/v2api/auth/login"
        r = requests.post(path,json.dumps({'email':self._email, 'api_key':self._key}))
        return json.loads(r.text)["token"]

    
    def _fillHeader(self) -> None:
        self._header = {'X-ALFACRM-TOKEN': self._getTempToken()}
    
    def _getBrunches(self) -> int:    
        path = f"https://{self._hostname}/v2api/branch/index"
        r = requests.post(path,data=json.dumps({"is_active" : 1}), headers = self._header)
        brunchDict = json.loads(r.text)
        if "items" in brunchDict:
            return self._getIdBrunches(brunchDict["items"])
        else:
            self._fillHeader()
            return self._getBrunches()
    
    def _getIdBrunches(self, brunches:list) ->int:       
        match(len(brunches)):
            case 1:
                return brunches[0]["id"]
            case _:
                return brunches[1]["id"]

    def createModel(self, model:str, data:dict[str:any]):
        path = f"https://{self._hostname}/v2api/{self._brunchId}/{self._createModels[model]}"
        r = requests.post(path,data,headers = self._header)
        return r.text
        
    def getData(self,model:str, data: dict[str:any]) -> list:
        path = f"https://{self._hostname}/v2api/{self._brunchId}/{self._getModels[model]}"
        r = requests.post(path,data=json.dumps(data),headers = self._header)
        dataDict = json.loads(r.text)
        if "items" in dataDict:
            return dataDict["items"]
        else:
            self._fillHeader()
            return self.getData()
    
   
        

#Пересмотреть функции доступа к CRM, из за частых обращений работает крайне долго,
#Подумать над тем, что бы вытягивать все нужные данные одним запросом.
class AlfaCRMDataManager(CrmDataManagerInterface):
    def __init__(self, crm:AlfaCRM, updatePeriotByNexLesson:int = 7, updatePeriodByPrevLesson:int = 7):
        self._crm = crm
        
        self._updatePeriodToNextLesson = 7
        self._updatePeriodToPreviousLesson = updatePeriodByPrevLesson
    
    def _getRegularLessons(self, allLessons:list) -> list:
        regularLessons = []
        for i in allLessons:
            if i['regular_id'] != None:
                regularLessons.append(i)
        return regularLessons
    
    def _getNextLessonsByLocation(self, locationId:int) ->list:
        page = 0 
        dateNextLesson = date.today() + timedelta(self._updatePeriodToNextLesson)
        data = {'status': 1,'date_from':date.today().strftime('%y-%m-%d'), 'date_to': dateNextLesson.strftime('%y-%m-%d'),'page':page,'location_ids': [locationId]}
        lessons = []
        while True:
            data['page'] = page
            temp = self._crm.getData("Lessons", data)
            if not temp:
                break
            page+=1
            lessons.append(self._getRegularLessons(temp))
        return lessons
    
    def _getPreviusLessonByGroupId(self, groupId:int) -> list:
        datePreviousLesson= date.today() - timedelta(self._updatePeriodToPreviousLesson)
        data = {'status': 3,'group_id':groupId, 'date_from':datePreviousLesson.strftime('%y-%m-%d'), 'date_to':date.today().strftime('%y-%m-%d')}
        temp = self._crm.getData("Lessons", data)
        return temp
    
    def getLocations(self) -> list:
        locations = self._crm.getData('Locations', {'is_active':1}) 
        return self._formatLocationsData(locations)
   
    
    def _formatLocationsData(self, locations:list) ->list:
        locationsList = []
        for i in locations:
            locationsList.append({'id':i['id'], 'name':i['name']})
        return locationsList
    
    def getRegularLessonsByLocationId(self, locationId:int) -> list:

        nextLesson = self._getNextLessonsByLocation(locationId)
        regularLesson = []
        for page in nextLesson:
            for item in page:
                print(f"getRegularLessonsByLocationId {item}")
                groupId =item['group_ids'][0]
                prev = self._getPreviusLessonByGroupId(groupId)[0]
                regularLesson.append(
                    {
                        'idGroup' : groupId,
                        'topic' : prev['topic'],
                        'idsStudents': str(item['customer_ids']),
                        'location': locationId,
                        'teacher' : item['teacher_ids'][0],
                        'day' :datetime.strptime(item['date'],'%Y-%m-%d').weekday(),
                        'timeFrom' : datetime.strptime(item['time_from'],'%Y-%m-%d %H:%M:%S').time().strftime('%H:%M'),
                        'timeTo' : datetime.strptime(item['time_to'],'%Y-%m-%d %H:%M:%S').time().strftime('%H:%M'),
                        'maxStudents' : self._getGroupById(groupId)[0]['limit'],
                        'lastUpdate' : date.today().strftime('Y-%m-%d')
                    }
                )
        return regularLesson

    def _getGroupById(self, groupId:int)->list:
        return self._crm.getData("Groups", {"id":groupId})
    
    def getTeachers(self) -> list:
        page = 0
        teachers = []
        while True:
            l = self._crm.getData('Teachers', {'removed': 1,'page' : page})
            if not l:
                break
            teachers.append(l)
            page +=1
        return self._formatTeachersData(teachers)

    def _formatTeachersData(sef, data:list):
        teachers = []
        for page in data:
            for item in page:
                teachers.append({'id':item['id'], 'name': item['name']})
        return teachers
    
   
        
    def getStudentsMissedLesson(self, groupId:int) -> list:
        group = self._getPreviusLessonByGroupId(groupId)[0]
        skipping = []
        allStudents = self._getStudents()
        for student in group['details']:
            if not student['is_attend']:
                studentData = self._findStudent(allStudents,'id',student['customer_id'] )
                if studentData:
                    skipping.append(
                    {
                        'idStudent': student['customer_id'],
                        'date': group['date'],
                        'topic': group['topic'],
                        'idGroup' : group['group_ids'][0],
                        'idLesson' : group['id'],
                        'teacher' : group['teacher_ids'][0],
                        'phoneNumber': studentData['phone'][0] ,
                        'name': studentData['name']          
                    }
                    )
        return skipping


    def _getStudents(self) ->list:
        page =0
        students = []
        while True:
            onePage = self._crm.getData("Students", {"removed":0, "is_study": 1, "page":page, 'withGroups':False})
            page +=1
            if not onePage:
                break
            students.append(onePage)
        return students
    
    def _findStudent(self,table:list,key:str,value):
        for page in table:
            for record in page:
                if record[key] == value:
                    return record
        return []
   
    def _fillTempLists(self):
        self._groupData = self._getGroups()
        self._nextLessonsData = self._getNextLessons()
        self._previusLessonData = self._getPreviusLessons()

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
    
   

    def _fillTableStudentAsences(self):
        
        for page in self._previusLessonData:
            record = []
            for lesson in page:
                for students in lesson['details']:
                    if not students['is_attend']:
                        if student := self._getAsence(lesson,students['customer_id']):
                            record.append(student)
        self._DB.fillTableStudentAbsences(record)

    def addWorkOff(self):
        self._crm.createModel()
    
           
            
class AlfaCRMDBManager():

    def __init__(self,dataBase:DataBase, alfaCRMDataManager:AlfaCRMDataManager):
        self.db = dataBase
        self.dataManager = alfaCRMDataManager
        pass
    
    def synchroniseTeachers(self):
        self.db.synchroniseTeachers(self.dataManager.getTeachers())
        print('synchroniseTeachers Ok')

    def synchroniseRegularLessons(self):
        locations = self.db.getAllLocations()
        allLessons = []
        for location in locations:
            print(f'synchroniseRegularLessons location {location}')
            lessons = self.dataManager.getRegularLessonsByLocationId(location['id'])
            allLessons+= lessons
        self.db.synchroniseTableRegularLessons(allLessons)
        print(f'synchroniseRegularLessons done')

    def insertInStudentAbsences(self):
        idsGroups = self.db.getRegularLessonsIds()
        for i in idsGroups:
            print(" insertInStudentAbsences group id ", i )
            students = self.dataManager.getStudentsMissedLesson(i)
            self.db.fillTableStudentAbsences(students)





    

        

        



        