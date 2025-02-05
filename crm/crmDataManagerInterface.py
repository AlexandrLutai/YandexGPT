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
    def addWorkOff(self):
        pass
