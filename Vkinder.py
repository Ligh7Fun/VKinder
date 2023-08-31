from datetime import datetime
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
import random
import logging
import json
import re
import os
from dotenv import load_dotenv
from database.db import DataBase
from time import sleep

user_gender = None  # Переменная для хранения пола пользователя
favorites = {}  # Пустой словарь для хранения избранных пользователей
logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# Функция для поиска пользователей по заданным параметрам
def search_users(age_from, age_to, sex, city, status):
    search_params = {
        'age_from': age_from,
        'age_to': age_to,
        'sex': sex,
        'city': city,
        'status': status,
        'count': 10
    }
    response = vk.users.search(**search_params)
    users = response['items']
    return users


# Функция для отправки сообщения с возможной клавиатурой


def write_msg(user_id, message, keyboard=None, image_urls=None):
    attachments = []
    if image_urls:
        for image_url in image_urls:
            attachments.append(image_url)

    vk.messages.send(
        user_id=user_id,
        message=message,
        attachment=','.join(attachments) if image_urls is not None else None,
        keyboard=keyboard if keyboard is not None else None,
        random_id=random.randint(1, 10 ** 9)
    )

# Функция для обработки выбора действия


def process_action(user_id, action):
    print("Processing action selection for user", user_id)
    print("Received action:", action)
    # Удаление цифр и точки из начала строки
    action_text = re.sub(r'^\d+\.\s*', '', action)

    if action_text.lower() == "искать по городу из профиля":
        user_city = get_user_city(user_id)
        if user_city:
            # DB
            db.set_state_user(user_id, "waiting_for_age_from")
            db.set_search(self_id=user_id, city=user_city)
            print('city: ', user_city, 'user: ', user_id)
            # user_states[user_id] = "waiting_for_age_from"
            # Обновляем состояние для ввода возраста
            city_message = f"Город из вашего профиля: {user_city}."
            confirm_keyboard = create_confirm_city_keyboard(user_city)
            write_msg(user_id, city_message, keyboard=confirm_keyboard)
            return
        else:
            # DB
            db.set_state_user(user_id, "waiting_for_city")
            # user_states[user_id] = "waiting_for_city"
            action_keyboard = create_action_keyboard(user_gender)
            write_msg(user_id, "Город не указан в вашем профиле.\nВведите "
                               "город вручную:", keyboard=action_keyboard)
    else:
        # DB
        db.set_state_user(user_id, "waiting_for_city")
        # user_states[user_id] = "waiting_for_city"
        action_keyboard = create_action_keyboard(user_gender)
        write_msg(user_id, "Введите город для поиска:",
                  keyboard=action_keyboard)
    print("Sent city input prompt to user", user_id)


def process_confirm_change(user_id, choice):
    if choice.lower() == "да":
        # DB
        db.set_state_user(user_id, "waiting_for_city")
        # user_states[user_id] = "waiting_for_city"  # Вернуться к ожиданию
        # ввода города
        action_keyboard = create_action_keyboard(user_gender)
        write_msg(user_id, "Введите город для поиска:",
                  keyboard=action_keyboard)
    elif choice.lower() == "нет":
        # DB
        db.set_state_user(user_id, "waiting_for_action")
        # user_states[user_id] = "waiting_for_action"  # Вернуться к выбору
        # действия
        action_keyboard = create_action_keyboard(user_gender)
        write_msg(user_id, "Что вы хотите сделать?", keyboard=action_keyboard)
    else:
        write_msg(user_id, "Пожалуйста, ответьте \"Да\" или \"Нет\".")


# Словарь для хранения состояний пользователей
user_states = {}

# Функция для начала диалога с пользователем


def start_conversation(user_id):
    print("Starting conversation with user", user_id)

    # Отправка приветственного сообщения и клавиатуры для выбора пола
    message = ("Привет!\nЯ бот, который поможет вам найти интересных людей.\n"
               "Выберите пол, который вы ищете:")

    # Создание клавиатуры с кнопками для выбора пола
    keyboard = {
        "one_time": True,
        "buttons": [
            [{"action": {"type": "text", "label": "Мужчину"}, "color": "positive"}],
            [{"action": {"type": "text", "label": "Женщину"}, "color": "positive"}]
        ]
    }

    keyboard = json.dumps(keyboard, ensure_ascii=False)

    # Отправка сообщения с клавиатурой
    write_msg(user_id, message, keyboard)

    # Установка состояния пользователя в "ожидание выбора пола"
    # user_states[user_id] = "waiting_for_gender"
    # DB
    db.set_state_user(user_id, "waiting_for_gender")
    print("DB State: ", db.get_state_user(user_id), "user_id:", user_id)
    print("Sent gender selection keyboard to user", user_id)

# Функция для обработки выбора пола


def process_gender(user_id, gender):
    print("Processing gender selection for user", user_id)

    if gender.lower() == "мужчину" or gender.lower() == "женщину":
        # DB
        db.set_state_user(user_id, "waiting_for_action")
        print('gender: ', gender, 'user_id: ', user_id)
        db.set_search(self_id=user_id, sex=gender)
        # user_states[user_id] = "waiting_for_action"

        # Создание клавиатуры с кнопками для выбора действия
        action_keyboard = {
            "one_time": True,
            "buttons": [
                [{"action": {"type": "text",
                             "label": "1. Искать по городу из профиля"}, "color": "default"}],
                [{"action": {"type": "text",
                             "label": "2. Ввести другой город"}, "color": "default"}]
            ]
        }

        action_keyboard = json.dumps(action_keyboard, ensure_ascii=False)

        write_msg(user_id, "Что вы хотите сделать?", keyboard=action_keyboard)
        print("Sent action selection keyboard to user", user_id)
    else:
        write_msg(
            user_id, "Не поняла вашего выбора. Пожалуйста, выберите пол из списка.")
        print("Sent invalid gender response message to user", user_id)

# Функция для создания клавиатуры для выбора действия


def create_action_keyboard(gender):
    buttons = [
        [{"action": {"type": "text", "label": "1. Искать по городу из профиля"},
            "color": "positive"}],
        [{"action": {"type": "text", "label": "2. Ввести другой город"}, "color": "positive"}],
        [{"action": {"type": "text", "label": "3. ◀ Вернуться к выбору города"}, "color": "default"}]
    ]
    if gender == "male":
        buttons[0][0]["color"] = "blue"
    elif gender == "female":
        buttons[1][0]["color"] = "pink"
    keyboard = {
        "one_time": True,
        "buttons": buttons
    }
    return json.dumps(keyboard, ensure_ascii=False)


# Функция для получения города пользователя
def get_user_city(user_id):
    try:
        response = vk.users.get(user_ids=user_id, fields='city')
        city_info = response[0]['city']
        if city_info:
            city = city_info['title']
            return city
        else:
            return None
    except Exception as e:
        print("Error getting user city:", str(e))
        return None

# Функция для обработки ввода города


def process_city_input(user_id, city_name):
    if city_name.lower() == "из профиля":
        user_city = get_user_city(user_id)
        if user_city:
            keyboard = create_action_keyboard(user_gender)
            db.set_search(self_id=user_id, city=user_city)
            write_msg(user_id, f"Вы выбрали город из профиля: "
                               f"{user_city.title()}.", keyboard=keyboard)

        else:
            write_msg(user_id, "Город не указан в вашем профиле.\nВведите "
                               "город вручную:")
            # DB
            db.set_state_user(user_id, "waiting_for_city")
            # user_states[user_id] = "waiting_for_city"
    else:
        # DB
        db.set_state_user(user_id, "waiting_for_age_from")
        # user_states[user_id] = "waiting_for_age_from"  # Ожидание ввода
        # начального возраста
        db.set_search(self_id=user_id, city=city_name)
        write_msg(user_id, f"Вы выбрали город: {city_name.title()}.\nТеперь "
                           f"введите "
                           f"начальный возраст:")


# Функция для создания клавиатуры подтверждения города
def create_confirm_city_keyboard(city_name):
    keyboard = {
        "one_time": True,
        "buttons": [
            [{"action": {"type": "text", "label": f"Подтвердить "
                                                  f"{city_name.title()}"},
              "color": "positive"}],
            [{"action": {"type": "text", "label": "Ввести другой город"}, "color": "default"}],
            [{"action": {"type": "text",
                         "label": "◀️ Вернуться к выбору города"}, "color": "default"}]
        ]
    }
    return json.dumps(keyboard, ensure_ascii=False)


# Функция для обработки подтверждения города
def process_confirm_city(user_id, city_name):
    if city_name.startswith("Подтвердить"):
        city = city_name[11:]
        # DB
        db.set_state_user(user_id, "waiting_for_age")
        # user_states[user_id] = "waiting_for_age"
        db.set_search(self_id=user_id, city=city)
        print('city: ', city, 'user: ', user_id)
        write_msg(user_id, f"Вы выбрали город: {city.title()}.\nТеперь "
                           f"введите желаемый возраст:")
    elif city_name == "Ввести другой город":
        # DB
        db.set_state_user(user_id, "waiting_for_city")
        # user_states[user_id] = "waiting_for_city"  # Изменено состояние на
        # ожидание ввода города
        write_msg(user_id, "Введите город:")


def process_age(user_id, age):
    print("Processing age input for user", user_id)
    try:
        age = int(age)
        if 0 <= age <= 150:  # Проверка на разумный диапазон возраста
            write_msg(user_id, f"Вы ввели возраст: {age}.\nМожете ввести "
                               f"другой город или продолжить поиск.")
            # DB
            db.set_state_user(user_id, "waiting_for_city")
            # user_states[user_id] = "waiting_for_city"  # Вернуться в
            # состояние ожидания ввода города
        else:
            write_msg(user_id, "Введите корректный возраст (от 0 до 150).")
    except ValueError:
        write_msg(user_id, "Введите числовой возраст (от 0 до 150).")


def process_age_from(user_id, age_from):
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
                               f"возраст:")

        else:
            write_msg(user_id, "Введите корректный возраст (от 0 до 150).")
    except ValueError:
        write_msg(user_id, "Введите числовой возраст (от 0 до 150).")


def process_age_to(user_id, age_to):
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
        # write_msg(user_id, f"Вы ввели конечный возраст: {age_to}.\nМожете "
        #                    f"ввести другой город или продолжить поиск.", keyboard=create_search_or_city_keyboard())
        write_msg(user_id, f"Вы ввели следующие данные:\n"
                  f"Пол: {data_for_search['sex']}\n"
                  f"Город: {data_for_search['city'].title()}\n"
                  f"Начальный возраст: {data_for_search['age_from']}\n"
                  f"Конечный возраст: {data_for_search['age_to']}",
                  keyboard=create_search_or_city_keyboard())
    except ValueError:
        write_msg(user_id, "Некорректный ввод. Пожалуйста, введите число.")


def create_search_or_city_keyboard():
    keyboard = {
        "one_time": True,
        "buttons": [
            [{"action": {"type": "text", "label": "Выбрать другой город"}, "color": "default"}],
            [{"action": {"type": "text", "label": "Начать поиск"}, "color": "positive"}]
        ]
    }
    return json.dumps(keyboard, ensure_ascii=False)


def process_list_favorites(user_id):
    pass


def get_city_id(city_name: str) -> int:
    response = vk_user.database.getCities(country_id=1, q=city_name)
    if response['count'] > 0:
        city = response['items'][0]
        return city['id']
    else:
        return None


# Функция для получения топ-фотографий пользователя
def get_top_photos(user_id) -> list:
    photos_response = vk_user.photos.get(
        owner_id=user_id, album_id='profile', extended=1)
    photos = photos_response['items']
    photos_sorted = sorted(
        photos, key=lambda x: x['likes']['count'], reverse=True)
    top_photos = photos_sorted[:3]
    photo_urls = [photo['sizes'][-1]['url']
                  for photo in top_photos]
    return photo_urls


# Считаем сколько лет
def calculate_age(bdate):
    bdate = datetime.strptime(bdate, '%d.%m.%Y')
    current_date = datetime.now()
    age = current_date.year - bdate.year
    if current_date.month < bdate.month or \
            (current_date.month == bdate.month
             and current_date.day < bdate.day):
        age -= 1

    return age


def process_search(user_id):
    data = db.get_search(self_id=user_id)
    count = 5
    sex = '1' if data['sex'].lower() == 'женщину' else '2'
    print('city id: ', get_city_id(data['city']))
    user_list = vk_user.users.search(count=count,
                                     sex=sex,
                                     city=get_city_id(data['city']),
                                     age_from=str(data['age_from']),
                                     age_to=str(data['age_to']),
                                     has_photo='1',
                                     status='6',
                                     sort=0,
                                     fields="city, bdate, sex")
    print(len(user_list['items']))

    for item in user_list['items']:
        id = item['id']
        try:
            top_photos = get_top_photos(id)
            print('top photos: ', top_photos)
            city = item.get('city', {}).get('title', 'N/A')
            first_name = item['first_name']
            last_name = item['last_name']
            bday = item['bdate']
            res = f"ID: {id}\nCity: {city}\nName: {first_name} {last_name}\nBday: {bday} ({calculate_age(bday)} лет)"
            print(res)
            print()
            write_msg(user_id=user_id, message=res, image_urls=top_photos)

        except Exception as e:
            print(e)
        sleep(3)

    return user_list


def main():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                user_id = event.user_id
                # DB
                db.add_user(user_id)
                print("DB State: ", db.get_state_user(
                    user_id), "user_id:", user_id)

                request = event.text.lower()

                logging.info(
                    f"Received message from user {user_id}: {request}")

                if request == "начать" or request == "start":
                    if db.get_state_user(user_id) is None:
                        db.set_state_user(user_id, "waiting_for_gender")
                    start_conversation(user_id)
                elif request == "пока":
                    write_msg(user_id, "До свидания!")
                elif request == "избранные":
                    process_list_favorites(user_id)
                else:
                    # DB
                    user_state_db = db.get_state_user(user_id)

                    if user_state_db == "waiting_for_gender":
                        process_gender(user_id, request)
                    elif user_state_db == "waiting_for_action":
                        process_action(user_id, request)
                    elif user_state_db == "waiting_for_city":
                        process_city_input(user_id, request)
                    elif user_state_db == "waiting_for_age_from":
                        process_age_from(user_id, request)
                    elif user_state_db == "waiting_for_age_to":
                        process_age_to(user_id, request)
                    elif user_state_db == "waiting_for_search_or_city":
                        if request == "выбрать другой город":
                            db.set_state_user(user_id, "waiting_for_city")
                            # user_state_db = "waiting_for_city"
                            write_msg(user_id, "Введите город для поиска:")
                        elif request == "начать поиск":
                            process_search(user_id)

                    # if user_id in user_states:
                    #     if user_states[user_id] == "waiting_for_gender":
                    #         process_gender(user_id, request)
                    #     elif user_states[user_id] == "waiting_for_action":
                    #         process_action(user_id, request)
                    #     elif user_states[user_id] == "waiting_for_city":
                    #         process_city_input(user_id, request)
                    #     elif user_states[user_id] == "waiting_for_age_from":
                    #         process_age_from(user_id, request)
                    #     elif user_states[user_id] == "waiting_for_age_to":
                    #         process_age_to(user_id, request)
                    #     elif user_states[user_id] == "waiting_for_search_or_city":
                    #         if request == "выбрать другой город":
                    #             user_states[user_id] = "waiting_for_city"
                    #             write_msg(user_id, "Введите город для поиска:")
                    #         elif request == "начать поиск":
                    #             process_search(user_id, age_from, age_to)
                    # else:
                    #     write_msg(user_id, "Не поняла вашей команды. Пожалуйста, начните с выбора пола.")


if __name__ == "__main__":
    # Загрузка токена из файла "token.txt"
    load_dotenv()
    token = os.getenv("TOKEN")
    token_user = os.getenv("TOKEN_USER")

    # DB initialization
    db = DataBase()
    db.create_tables()

    # Инициализация VK API
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()

    # User API
    vk_session_user = vk_api.VkApi(token=token_user)
    vk_user = vk_session_user.get_api()

    # Инициализация LongPoll
    longpoll = VkLongPoll(vk_session)

    # Запуск бота
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Bot started")
    print("Bot started")
    main()
