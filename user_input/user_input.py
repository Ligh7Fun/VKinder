from messaging import write_msg
from datetime import datetime


def process_confirm_city(user_id: int, city_name: str) -> None:
    if city_name.startswith("Подтвердить"):
        city = city_name[11:]
        db.set_state_user(user_id, "waiting_for_age")
        db.set_search(self_id=user_id, city=city)
        print('city: ', city, 'user: ', user_id)
        write_msg(user_id, f"Вы выбрали город: {city.title()}.\nТеперь"
                           f" введите желаемый возраст:"
                  )
    elif city_name == "Ввести другой город":
        # DB
        db.set_state_user(user_id, "waiting_for_city")
        # Изменено состояние на ожидание ввода города
        write_msg(user_id, "Введите город:")




def process_city_input(user_id: int, city_name: str) -> None:
    if city_name.lower() == "из профиля":
        user_city = get_user_city(user_id)
        if user_city:
            keyboard = create_action_keyboard()
            db.set_search(self_id=user_id, city=user_city)
            write_msg(user_id, f"Вы выбрали город из профиля: "
                               f"{user_city.title()}.", keyboard=keyboard
                      )

        else:
            write_msg(user_id, "Город не указан в вашем профиле.\n"
                               "Введите город вручную:"
                      )
            # DB
            db.set_state_user(user_id, "waiting_for_city")
            # user_states[user_id] = "waiting_for_city"
    else:
        # DB
        db.set_state_user(user_id, "waiting_for_age_from")
        # user_states[user_id] = "waiting_for_age_from"  # Ожидание ввода
        # начального возраста
        db.set_search(self_id=user_id, city=city_name)
        write_msg(user_id, f"Вы выбрали город: {city_name.title()}.\n"
                           f"Теперь введите начальный возраст:"
                  )
def process_age(user_id: int, age: int) -> None:
    print("Processing age input for user", user_id)
    try:
        age = int(age)
        if 0 <= age <= 150:  # Проверка на разумный диапазон возраста
            write_msg(user_id,
                      f"Вы ввели возраст: {age}.\nМожете ввести "
                      f"другой город или продолжить поиск."
                      )
            # DB
            db.set_state_user(user_id, "waiting_for_city")
            # Вернуться в состояние ожидания ввода города
        else:
            write_msg(user_id,
                      "Введите корректный возраст (от 0 до 150)."
                      )
    except ValueError:
        write_msg(user_id,
                  "Введите числовой возраст (от 0 до 150)."
                  ) 
        
def process_age_from(user_id: int, age_from: int) -> None:
    print("Processing age from input for user", user_id)
    try:
        age_from = int(age_from)
        if 0 <= age_from <= 150:  # Проверка на разумный диапазон возраста
            # DB
            db.set_state_user(user_id, "waiting_for_age_to")
            # user_states[user_id] = "waiting_for_age_to"  # Ожидание ввода
            # конечного возраста
            db.set_search(self_id=user_id, age_from=age_from)
            print('age_from', age_from, 'user: ', user_id)
            write_msg(user_id, f"Вы ввели начальный возраст: "
                               f"{age_from}.\nТеперь введите конечный "
                               f"возраст:"
                      )

        else:
            write_msg(user_id,
                      "Введите корректный возраст (от 0 до 150)."
                      )
    except ValueError:
        write_msg(user_id,
                  "Введите числовой возраст (от 0 до 150)."
                  ) 
        
def process_age_to(user_id: int, age_to: int) -> None:
    try:
        age_to = int(age_to)
        # DB
        db.set_state_user(user_id, "waiting_for_search_or_city")
        # user_states[user_id] = "waiting_for_search_or_city"  # Обновляем
        # состояние для выбора действия
        db.set_search(self_id=user_id, age_to=age_to)
        print('age_to', age_to, 'user: ', user_id)

        data_for_search = db.get_search(self_id=user_id)
        print(data_for_search)

        write_msg(user_id, f"Вы ввели следующие данные:\n"
                           f"Пол: {data_for_search['sex']}\n"
                           f"Город: {data_for_search['city'].title()}\n"
                           f"Начальный возраст: {data_for_search['age_from']}"
                           f"\nКонечный возраст: {data_for_search['age_to']}",
                  keyboard=create_search_or_city_keyboard()
                  )
        db.set_state_user(user_id, "showing_profiles")
    except ValueError:
        write_msg(user_id, "Некорректный ввод. "
                           "Пожалуйста, введите число."
                  )

def get_city_id(city_name: str) -> int | None:
    response = vk_user.database.getCities(country_id=1, q=city_name)
    if response['count'] > 0:
        city = response['items'][0]
        return city['id']
    else:
        return None





# Считаем сколько лет
def calculate_age(bdate: str) -> int:
    bdate = datetime.strptime(bdate, '%d.%m.%Y')
    current_date = datetime.now()
    age = current_date.year - bdate.year
    if current_date.month < bdate.month or \
            (current_date.month == bdate.month
             and current_date.day < bdate.day):
        age -= 1

    return age


