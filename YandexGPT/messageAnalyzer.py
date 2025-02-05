from crm.crmDataManagerInterface import CrmDataManagerInterface
from YandexGPT.chatScriptAnalyzer import ChatScriptAnalyzer
from dataBase.mainDataBase import DataBase
from functions.functions import getDuration, getDateNextWeekday
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
    

    def analyzeGPTAnswer(self, data:MessageForAnalyzeDict):
        message = data['text']
        if "|" in data['text']:
           message = self._analyzeSystemMessage(data)
        return message

    def _analyzeSystemMessage(self, data:MessageForAnalyzeDict):
        message = data['text'].split('|')
        if "отработк" in message[0].lower():
            self._processWorkOffMessage(data)
            pass
        return message[-1]
        pass

    def _processWorkOffMessage(self, data:MessageForAnalyzeDict):
        message = data['text'].split('|')
        if 'success' in message[1].lower() :
            self._workOffSuccess(data)
            pass
        elif message[1].lower() == 'fail':
            self._workOffFail(data)
            pass
        pass

    def _workOffSuccess(self, data:MessageForAnalyzeDict):
        """
        Обрабатывает успешное сообщение об отработке.

        Args:
            data (_Message): Данные сообщения, включающие идентификатор чата и текст сообщения.
        """
        try:
            idGroup = int(data['text'].split('|')[2])
            student = self._db.getStudent(data['chatId'])
            regularLesson = self._db.getRegularLessons(idGroup)
            groupOccupancy = self._db.getGroupOccupancyData(idGroup)
            dataForCRM = {
                'topic': student['topic'],
                'lesson_date': groupOccupancy['dateOfEvent'],
                'customer_ids':list([student['idStudent']]),
                'time_from': regularLesson['timeFrom'],
                'duration': getDuration(regularLesson['timeFrom'], regularLesson['timeTo']),
                'subject_id': regularLesson['subjectId'],
                'teacher_ids': list([regularLesson['teacher']])
            }

            dataForDB = {
                'worksOffsTopics': f"{groupOccupancy['worksOffsTopics']}, {student['topic']}",
                'newStudents': f"{groupOccupancy['newStudents']}, {student['idStudent']}",
                'count': groupOccupancy['count'] + 1
            }
            self._crm.addWorkOff(dataForCRM)
            self._db.updateData(dataForDB, "groupOccupancy", {'idGroup': idGroup})
        except Exception as e:
            print(f"An error occurred while processing work off success: {e}")
        

    def _workOffFail(self, data:MessageForAnalyzeDict):
        dateNextConnextion = int(data['text'].split('|')[2])
        dataForDB = {
            'dateLastConnection' : datetime.datetime.now().strftime('%Y-%m-%d'),
            'dateNextConnection': getDateNextWeekday(datetime.datetime.now().weekday()).strftime('%Y-%m-%d')
        }
        self._db.updateData(dataForDB, "StudentAbsences", {'phoneNumber': data['idChat']})

