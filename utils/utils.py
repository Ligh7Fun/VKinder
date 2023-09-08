from datetime import datetime


def calculate_age(birth_date: str) -> int:
    """
    Рассчитывает возраст на основе заданной даты рождения.

    Args:
        birth_date (str): Дата рождения в формате 'дд.мм.гггг'.

    Returns:
        int: Рассчитанный возраст на основе текущей даты.

    """
    birth_date = datetime.strptime(birth_date, '%d.%m.%Y')
    current_date = datetime.now()
    age = current_date.year - birth_date.year
    if current_date.month < birth_date.month or \
            (current_date.month == birth_date.month
             and current_date.day < birth_date.day):
        age -= 1

    return age
