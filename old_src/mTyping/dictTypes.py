from typing import TypedDict, List

class CreateLessonModelDict(TypedDict):
    topic: str
    lesson_date: str
    customer_ids: list[int]
    time_from: str
    duration: int
    subject_id: int
    teacher_ids: list[int]


class StudentAbsenceDict(TypedDict):
    idStudent: int
    date: str
    topic: str
    idGroup: int
    idLesson: int
    teacher: int
    phoneNumber: str
    name: str

class LocationDict(TypedDict):
    id: int
    name: str

class RegularLessonDict(TypedDict):
    idGroup: int
    topic: str
    idsStudents: str
    location: int
    teacher: int
    day: int
    timeFrom: str
    timeTo: str
    maxStudents: int
    lastUpdate: str
    subjectId: int

class GroupOccupancyDict(TypedDict):
    idGroup: int
    newStudents: int
    idsStudents: str
    dateOfEvent: str
    count: int
    lastUpdate: str
    worksOffsTopics: str

class MessageForPromptDict(TypedDict):
    role: str
    text: str

class MessageForAnalyzeDict(TypedDict):
    chatId: str
    text: str
