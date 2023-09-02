from datetime import datetime
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

import random
import logging
import json
import re
import os
from dotenv import load_dotenv
from database.db import DataBase
from time import sleep
from threading import Thread


user_gender = None  # Переменная для хранения пола пользователя
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
def write_msg(user_id: int,
              message: str,
              keyboard=None,
              image_urls=None) -> None:
    attachments = []
    if image_urls:
        for image_url in image_urls:
            attachments.append(image_url)
    attachment = ','.join(attachments) if image_urls is not None else None
    
    # Создайте клавиатуру с кнопкой "Показать избранное"
    show_favorites_button = {
        "action": {
            "type": "text",
            "label": "Показать избранное"
        },
        "color": "primary"
    }
    
    if keyboard:
        keyboard = json.loads(keyboard)
        keyboard["buttons"].append([show_favorites_button])
    else:
        keyboard = {
            "one_time": False,
            "buttons": [[show_favorites_button]]
        }
    
    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    
    print('attachment: ', attachment)
    vk_session.method(
        'messages.send',
        {
            'user_id': user_id,
            'message': message,
            'random_id': 0,
            'keyboard': keyboard,
            'attachment': attachment,
        }
    )
def show_favorites(user_id):
    liked_list = db.request_liked_list(user_id)

    if liked_list:
        for liked_user in liked_list:
           
            profile = db.get_user_profile(liked_user['viewedvkid'])
            if profile:
                
                message = f"ID пользователя: {profile['vk_id']}\nИмя: {profile['first_name']} {profile['last_name']}\nГород: {profile.get('city', 'N/A')}"
                
                write_msg(user_id=user_id, message=message)
    else:
        write_msg(user_id=user_id, message="Список избранных пользователей пуст.") 
        




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
        db.set_state_user(user_id, "showing_profiles")
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

favorites = {}
def add_to_favorites(user_id, profile):
    if user_id not in favorites:
        favorites[user_id] = []  # Создаем список избранных для пользователя, если его еще нет

    favorites[user_id].append(profile)  # Добавляем профиль в избранные для данного пользователя
    write_msg(user_id, "Пользователь добавлен в избранные.")



def get_city_id(city_name: str) -> int:
    response = vk_user.database.getCities(country_id=1, q=city_name)
    if response['count'] > 0:
        city = response['items'][0]
        return city['id']
    else:
        return None


# Функция для получения топ-фотографий пользователя
def get_top_photos(user_id) -> list:
    try:
        photos_response = vk_user.photos.get(
            owner_id=user_id, album_id='profile', extended=1)
        photos = photos_response['items']
        photos_sorted = sorted(
            photos, key=lambda x: x['likes']['count'], reverse=True)
        top_photos = photos_sorted[:3]
        photo_urls = [photo['sizes'][-1]['url']
                      for photo in top_photos]
    except Exception as e:
        print("Error getting top photos:", str(e))
        index = db.get_search_index(self_id=user_id)
        db.set_search_index(self_id=user_id, new_index=index+1)
        return None
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


def process_search(user_id: int) -> None:
    data = db.get_search(user_id)
    count = 50
    sex = '1' if data['sex'].lower() == 'женщину' else '2'
    print('city id: ', get_city_id(data['city']))

    search_results = vk_user.users.search(count=count,
                                          sex=sex,
                                          city=get_city_id(data['city']),
                                          age_from=str(data['age_from']),
                                          age_to=str(data['age_to']),
                                          has_photo='1',
                                          status='6',
                                          sort=0,
                                          fields="city, bdate, sex")
    print(len(search_results['items']))
    print()
    print(search_results['items'])
    print("***"*20)

    # Сохраняем результаты поиска в базе данных
    db.set_search(self_id=user_id, results=search_results['items'])

    # Устанавливаем состояние пользователя для показа профилей
    db.set_state_user(self_id=user_id, state="showing_profiles")
    # Устанавливаем начальный индекс на 0
    if db.get_search_index(self_id=user_id) == 0:
        db.set_search_index(self_id=user_id, new_index=0)

    # Отображаем первый профиль
    display_profile(user_id=user_id)
    inner_go_work = Thread(
        target=go_work, args=(user_id, db.session))
    inner_go_work.start()


def display_profile(user_id):
    search_results = db.get_search_results(self_id=user_id)
    index = db.get_search_index(self_id=user_id)
    print('index: ', index)
    if index < len(search_results):
        profile = search_results[index]
        # Формируем сообщение с информацией о профиле, включая его ID
        message = f"ID пользователя: {profile['id']}\nИмя: {profile['first_name']} {profile['last_name']}\nГород: {profile.get('city', {}).get('title', 'N/A')}"
        
        try:
            # Получаем топ-фотографии профиля
            top_photos = get_top_photos(profile['id'])
            if top_photos is None:
                # !!!нужно прервать и передать другую карточку
                db.set_search_index(self_id=user_id, new_index=index + 1)
                display_profile(user_id=user_id)
        except Exception as e:
            # Обработка ошибки при получении фотографий
            print(f"Error getting top photos: {e}")
            top_photos = []

        # Создаем встроенную клавиатуру с кнопками "лайка" и "дизлайка"
        keyboard = create_like_dislike_keyboard()
        # Отправляем сообщение с клавиатурой и изображениями
        write_msg(user_id=user_id, message=message,
                  keyboard=keyboard, image_urls=top_photos)
    else:
        # Больше профилей нет для отображения
        write_msg(user_id=user_id,
                  message="Больше профилей для отображения нет.")




def create_like_dislike_keyboard():
    keyboard = {
        "inline": True,
        "buttons": [
            [{"action": {"type": "text", "label": "👍 Лайк"}, "color": "positive"},
             {"action": {"type": "text", "label": "👎 Дизлайк"}, "color": "negative"}]
        ]
    }
    return json.dumps(keyboard, ensure_ascii=False)

def view_favorites(user_id, favorites):
   
    user_favorites = favorites.get(user_id, [])

    if not user_favorites:
        write_msg(user_id, "Список избранных пользователей пуст.")
        return

 
    favorites_message = "Список избранных пользователей:\n"
    for favorite in user_favorites:
        favorites_message += f"{favorite}\n"

 
    write_msg(user_id, favorites_message)




def go_work(user_id, session):
    while True:
        print('start thread for user_id: ', user_id)
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                print('new message from user_id: ', user_id)
                request = event.obj.message["text"]
                print('request: ', request)
                if request == "👍 Лайк":
                    search_results = db.get_search_results(self_id=user_id)
                    index = db.get_search_index(self_id=user_id)
                    profile = search_results[index]["id"]
                    add_to_favorites(user_id, profile)
                    db.add_like(self_id=user_id, user_id=profile)
                    db.set_search_index(self_id=user_id, new_index=index + 1)
                    display_profile(user_id=user_id)
                    break
                if request == "👎 Дизлайк":
                    search_results = db.get_search_results(self_id=user_id)
                    index = db.get_search_index(self_id=user_id)
                    profile = search_results[index]["id"]
                    db.add_dislike(self_id=user_id, user_id=profile)
                    db.set_search_index(self_id=user_id, new_index=index + 1)
                    display_profile(user_id=user_id)
                    break
                if request.lower() == "назад":
                    break
                if request.lower() == "меню":
                    break
                if request.lower() == "продолжить":
                    print('continue')
                    display_profile(user_id=user_id)
                    break
                if request.lower() == "стоп":
                    write_msg(user_id=user_id, message="До свидания!")
                    continue



def main():
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message["from_id"]

            # DB
            db.add_user(user_id)
            print("DB State: ", db.get_state_user(
                user_id), "user_id:", user_id)

            request = event.obj.message["text"].lower()

            logging.info(
                f"Received message from user {user_id}: {request}")

            if request == "начать" or request == "start":
                if db.get_state_user(user_id) is None:
                    db.set_state_user(user_id, "waiting_for_gender")
                start_conversation(user_id)
            elif request == "пока":
                write_msg(user_id, "До свидания!")
            elif request == "избранные":
                view_favorites(user_id, favorites)  
            elif request.lower() == "показать избранное":
                view_favorites(user_id, favorites)  
            else:
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
                        write_msg(user_id, "Введите город для поиска:")
                elif request == "начать поиск" and user_state_db == "showing_profiles":
                    process_search(user_id)
                elif request == "продолжить" and user_state_db == "showing_profiles":
                    display_profile(user_id=user_id)
                    inner_go_work = Thread(
                        target=go_work, args=(user_id, db.session))
                    inner_go_work.start()


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
    # longpoll = VkLongPoll(vk_session)
    longpoll = VkBotLongPoll(vk_session, group_id='222099959')

    # Запуск бота
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Bot started")
    print("Bot started")
    main()

