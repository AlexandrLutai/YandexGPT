from abc import ABC, abstractmethod
from typing import List, Dict
from mTyping.dictTypes import CreateLessonModelDict, StudentAbsenceDict, LocationDict, RegularLessonDict

class CrmDataManagerInterface(ABC):
    @abstractmethod
    def getLocations(self) -> List[LocationDict]:
        """
        Получает список локаций.

        Returns:
            List[LocationDict]: Список локаций.
        """
        pass

    @abstractmethod
    def getRegularLessonsByLocationId(self, locationId: int) -> List[RegularLessonDict]:
        """
        Получает регулярные уроки по идентификатору локации.

        Args:
            locationId (int): Идентификатор локации.

        Returns:
            List[RegularLessonDict]: Список регулярных уроков.
        """
        pass
    
    @abstractmethod
    def getTeachers(self) -> List[Dict[str, str]]:
        """
        Получает список учителей.

        Returns:
            List[Dict[str, str]]: Список учителей.
        """
        pass

    @abstractmethod
    def getStudentsMissedLesson(self, groupId: int) -> List[StudentAbsenceDict]:
        """
        Получает список студентов, пропустивших урок.

        Args:
            groupId (int): Идентификатор группы.

        Returns:
            List[StudentAbsenceDict]: Список студентов, пропустивших урок.
        """
        pass

    @abstractmethod
    def addWorkOff(self, data: CreateLessonModelDict) -> None:
        """
        Добавляет отработку урока.

        Args:
            data (CreateLessonModelDict): Данные урока.
        """
        pass
