from crm.crmDataManagerInterface import CrmDataManagerInterface
from YandexGPT.chatScriptAnalyzer import ChatScriptAnalyzer
from dataBase.database import DataBase
from functions.functions import get_duration, get_date_next_weekday
from mTyping.dictTypes import MessageForAnalyzeDict


import datetime
from typing import TypedDict



class MessageAnalyzer:
    
        
    def __init__(self, chatAnalyzer:ChatScriptAnalyzer, db:DataBase, crm:CrmDataManagerInterface):
        """
        Инициализирует объект анализатора сообщений.

        Args:
            chatAnalyzer (ChatScriptAnalyzer): Экземпляр анализатора сценариев.
            db (DataBase): Экземпляр базы данных.
            crm (CrmDataManagerInterface): Интерфейс менеджера данных CRM.
        """
        self._chatAnalyzer = chatAnalyzer
        self._db = db
        self._crm = crm
    

    def analyze_GPT_answer(self, data:MessageForAnalyzeDict):
        message = data['text']
        if "|" in data['text']:
           message = self._analyze_system_message(data)
        return message

    def _analyze_system_message(self, data:MessageForAnalyzeDict):
        message = data['text'].split('|')
        if "отработк" in message[0].lower():
            self._process_work_off_message(data)
            pass
        return message[-1]
        pass

    def _process_work_off_message(self, data:MessageForAnalyzeDict):
        message = data['text'].split('|')
        if 'success' in message[1].lower() :
            self._work_off_success(data)
            pass
        elif message[1].lower() == 'fail':
            self._work_off_fail(data)
            pass
        pass

    def _work_off_success(self, data:MessageForAnalyzeDict):
        """
        Обрабатывает успешное сообщение об отработке.

        Args:
            data (_Message): Данные сообщения, включающие идентификатор чата и текст сообщения.
        """
        try:
            idGroup = int(data['text'].split('|')[2])
            student = self._db.get_student(data['chatId'])
            regularLesson = self._db.get_regular_lessons(idGroup)
            groupOccupancy = self._db.get_group_occupancy_data(idGroup)
            dataForCRM = {
                'topic': student['topic'],
                'lesson_date': groupOccupancy['dateOfEvent'],
                'customer_ids':list([student['idStudent']]),
                'time_from': regularLesson['timeFrom'],
                'duration': get_duration(regularLesson['timeFrom'], regularLesson['timeTo']),
                'subject_id': regularLesson['subjectId'],
                'teacher_ids': list([regularLesson['teacher']])
            }

            dataForDB = {
                'count': groupOccupancy['count'] + 1
            }
            studentDataString = str({"idStudent":student['idStudent'], "topic":student['topic'], "idLesson":student['idLesson']})
            if groupOccupancy['newStudents'] == '' or groupOccupancy['newStudents'] is None:
                dataForDB['newStudents'] = studentDataString
            else:
                dataForDB['newStudents'] = f"{groupOccupancy['newStudents']}, {studentDataString}"

            self._crm.add_work_off(dataForCRM)
            self._db.updateData(dataForDB, "groupOccupancy", {'idGroup': idGroup})
            self._db.updateData({'dateLastConnection': datetime.date.today().strftime('%y-%m-%d'), 'groupForWorkingOut': idGroup},"StudentAbsences", {'phoneNumber': data['chatId']})
        except Exception as e:
            print(f"An error occurred while processing work off success: {e}")
        

    def _work_off_fail(self, data:MessageForAnalyzeDict):
        dateNextConnextion = int(data['text'].split('|')[2])
        dataForDB = {
            'dateLastConnection' : datetime.datetime.now().strftime('%Y-%m-%d'),
            'dateNextConnection': get_date_next_weekday(datetime.datetime.now().weekday()).strftime('%Y-%m-%d')
        }
        self._db.updateData(dataForDB, "StudentAbsences", {'phoneNumber': data['idChat']})

