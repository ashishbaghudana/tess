import datetime


def string_to_date(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")


def date_to_string():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")
