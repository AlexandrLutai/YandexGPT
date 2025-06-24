from crm.crmDataManagerInterface import CrmDataManagerInterface
from dataBase.databaseManager import DataBaseManager
from functions.functions import get_duration, get_date_next_weekday
from mTyping.dictTypes import MessageForAnalyzeDict

import datetime
from typing import TypedDict

class GptMessageAnalyzer:
    def __init__(self, db: DataBaseManager, crm: CrmDataManagerInterface):
        """
        Инициализирует объект анализатора сообщений.

        Args:
            chatAnalyzer (ChatScriptAnalyzer): Экземпляр анализатора сценариев.
            db (DataBase): Экземпляр базы данных.
            crm (CrmDataManagerInterface): Интерфейс менеджера данных CRM.
        """
        
        self._db = db
        self._crm = crm

    async def analyze_GPT_answer(self, data: MessageForAnalyzeDict) -> str:
        """
        Асинхронно анализирует ответ модели GPT.

        Args:
            data (MessageForAnalyzeDict): Данные для анализа.

        Returns:
            str: Сообщение после анализа.
        """
        message = data['text']
        if "|" in data['text']:
            message = await self._analyze_system_message(data)
        return message

    async def _analyze_system_message(self, data: MessageForAnalyzeDict) -> str:
        """
        Асинхронно анализирует системное сообщение.

        Args:
            data (MessageForAnalyzeDict): Данные для анализа.

        Returns:
            str: Сообщение после анализа.
        """
        message = data['text'].split('|')
        if "отработк" in message[0].lower():
            await self._process_work_off_message(data)
        return message[-1]

    async def _process_work_off_message(self, data: MessageForAnalyzeDict) -> None:
        """
        Асинхронно обрабатывает сообщение об отработке.

        Args:
            data (MessageForAnalyzeDict): Данные для анализа.
        """
        message = data['text'].split('|')
        if 'success' in message[1].lower():
            await self._work_off_success(data)
        elif message[1].lower() == 'fail':
            await self._work_off_fail(data)

    async def _work_off_success(self, data: MessageForAnalyzeDict) -> None:
        """
        Асинхронно обрабатывает успешное сообщение об отработке.

        Args:
            data (MessageForAnalyzeDict): Данные сообщения, включающие идентификатор чата и текст сообщения.
        """
        try:
            idGroup = int(data['text'].split('|')[2])
            student = await self._db.get_student(data['chatId'])
            regularLesson = await self._db.get_regular_lessons(idGroup)
            groupOccupancy = await self._db.get_group_occupancy_data(idGroup)
            dataForCRM = {
                'topic': student['topic'],
                'lesson_date': groupOccupancy['dateOfEvent'],
                'customer_ids': list([student['idStudent']]),
                'time_from': regularLesson['timeFrom'],
                'duration': await get_duration(regularLesson['timeFrom'], regularLesson['timeTo']),
                'subject_id': regularLesson['subjectId'],
                'teacher_ids': list([regularLesson['teacher']])
            }

            dataForDB = {
                'count': groupOccupancy['count'] + 1
            }
            studentDataString = str({"idStudent": student['idStudent'], "topic": student['topic'], "idLesson": student['idLesson']})
            if groupOccupancy['newStudents'] == '' or groupOccupancy['newStudents'] is None:
                dataForDB['newStudents'] = studentDataString
            else:
                dataForDB['newStudents'] = f"{groupOccupancy['newStudents']}, {studentDataString}"

            await self._crm.add_work_off(dataForCRM)
            await self._db.update_data(dataForDB, "GroupOccupancy", {'idGroup': idGroup})
            await self._db.update_data({'dateLastConnection': datetime.date.today().strftime('%y-%m-%d'), 'groupForWorkingOut': idGroup}, "StudentAbsences", {'phoneNumber': data['chatId']})
        except Exception as e:
            print(f"An error occurred while processing work off success: {e}")

    async def _work_off_fail(self, data: MessageForAnalyzeDict) -> None:
        """
        Асинхронно обрабатывает неудачное сообщение об отработке.

        Args:
            data (MessageForAnalyzeDict): Данные сообщения, включающие идентификатор чата и текст сообщения.
        """
        dateNextConnection = int(data['text'].split('|')[2])
        dataForDB = {
            'dateLastConnection': datetime.datetime.now().strftime('%Y-%m-%d'),
            'dateNextConnection': (await get_date_next_weekday(datetime.datetime.now().weekday())).strftime('%Y-%m-%d')
        }
        await self._db.update_data(dataForDB, "StudentAbsences", {'phoneNumber': data['chatId']})

