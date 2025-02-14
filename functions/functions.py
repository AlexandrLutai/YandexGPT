from contextlib import contextmanager
import datetime
import sqlite3

@contextmanager
def db_ops(db_name):
    conn = sqlite3.connect(db_name)
    try:
        cur = conn.cursor()
        yield cur
    except Exception as e:
        # do something with exception
        conn.rollback()
        raise e
    else:
        conn.commit()
    finally:
        conn.close()


def get_date_next_weekday(numberDay:int):
   
    d = datetime.timedelta( (7 + numberDay - datetime.date.today().weekday())%7 ).days
    return  datetime.date.today() + datetime.timedelta(d)

def get_day_name(day:int) ->str:
    match(day):
        case 0:
            return 'Понедельник'
        case 1:
            return 'Вторник'
        case 2:
            return 'Среда'
        case 3:
            return 'Четверг'
        case 4:
            return 'Пятница'
        case 5:
            return 'Суббота'
        case 6:
            return 'Воскресенье'
def assign_work_offs_to_text(assignWorkOffs:int) -> str:
    match assignWorkOffs:
        case 0:
            return "Не желательно"
        case 1: 
            return "Можно"


def get_duration(timeFrom:str, timeTo:str) -> int:
    """
    Получает длительность урока.

    Args:
        timeFrom (str): Время начала урока.
        timeTo (str): Время окончания урока.

    Returns:
        int: Длительность урока.
    """
    return (datetime.datetime.strptime(timeTo,"%H:%M") - datetime.datetime.strptime(timeFrom,"%H:%M")).total_seconds()//60