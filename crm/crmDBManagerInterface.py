from abc import ABC, abstractmethod
from typing import List, Dict

class CrmDBManagerInterface(ABC):

    @abstractmethod
    def synchronise_teachers(self):
        pass

    @abstractmethod
    def synchronise_regular_lessons(self):
        pass

    @abstractmethod
    def insert_in_student_absences(self):
        pass
