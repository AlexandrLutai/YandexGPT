from abc import ABC, abstractmethod
from typing import List, Dict
from mTyping.dictTypes import CreateLessonModelDict, StudentAbsenceDict, LocationDict, RegularLessonDict

class CrmDataManagerInterface(ABC):
    @abstractmethod
    def get_locations(self) -> List[LocationDict]:
        """
        Получает список локаций.

        Returns:
            List[LocationDict]: Список локаций.
        """
        pass

    @abstractmethod
    def get_regular_lessons_by_location_id(self, locationId: int) -> List[RegularLessonDict]:
        """
        Получает регулярные уроки по идентификатору локации.

        Args:
            locationId (int): Идентификатор локации.

        Returns:
            List[RegularLessonDict]: Список регулярных уроков.
        """
        pass
    
    @abstractmethod
    def get_teachers(self) -> List[Dict[str, str]]:
        """
        Получает список учителей.

        Returns:
            List[Dict[str, str]]: Список учителей.
        """
        pass

    @abstractmethod
    def get_students_missed_lesson(self, groupId: int) -> List[StudentAbsenceDict]:
        """
        Получает список студентов, пропустивших урок.

        Args:
            groupId (int): Идентификатор группы.

        Returns:
            List[StudentAbsenceDict]: Список студентов, пропустивших урок.
        """
        pass

    @abstractmethod
    def add_work_off(self, data: CreateLessonModelDict) -> None:
        """
        Добавляет отработку урока.

        Args:
            data (CreateLessonModelDict): Данные урока.
        """
        pass
