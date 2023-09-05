from datetime import datetime
from io import BytesIO
import random
import logging
import re
import os

from dotenv import load_dotenv
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.upload import VkUpload
import vk_api
import requests

from database.db import Database
from keyboards.keyboards import (create_action_keyboard,
                                 create_confirm_city_keyboard,
                                 create_search_or_city_keyboard,
                                 create_menu_keyboard,
                                 create_like_dislike_keyboard,
                                 create_start_conversation_keyboard,
                                 )

logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s'
                    )


# Функция для поиска пользователей по заданным параметрам
def upload_photo(url: str) -> str:
    img = requests.get(url).content
    f = BytesIO(img)  # Переводим в байты изображение

    response = upload.photo_messages(f)[0]  # Загружаем на сервер
    profile_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']

    return f'photo{profile_id}_{photo_id}_{access_key}'


# Функция для отправки сообщения с возможной клавиатурой
def write_msg(user_id: int,
              message: str,
              keyboard=None,
              image_urls=None,
              ) -> None:
    attachments = []
    if image_urls:
        for image_url in image_urls:
            attachments.append(image_url)
    attachment = ','.join(attachments) if image_urls is not None else None

    vk_session.method(
            'messages.send',
            {
                'user_id': user_id,
                'message': message,
                'random_id': random.randint(1, 10 ** 9),
                'keyboard': keyboard,
                'attachment': attachment,
            }
    )


# Функция для обработки выбора действия
def process_action(user_id: int, action: str) -> None:
    print("Processing action selection for user", user_id)
    print("Received action:", action)
    # Удаление цифр и точки из начала строки
    action_text = re.sub(r'^\d+\.\s*', '', action)

    if action_text.lower() == "искать по городу из профиля":
        user_city = get_user_city(user_id)
        if user_city:
            db.set_state_user(user_id, "waiting_for_age_from")
            db.set_search(self_id=user_id, city=user_city)
            print('city: ', user_city, 'user: ', user_id)
            # Обновляем состояние для ввода возраста
            city_message = f"Город из вашего профиля: {user_city}."
            confirm_keyboard = create_confirm_city_keyboard(user_city)
            write_msg(user_id, city_message, keyboard=confirm_keyboard)
            return
        else:
            db.set_state_user(user_id, "waiting_for_city")
            action_keyboard = create_action_keyboard()
            write_msg(user_id, "Город не указан в вашем профиле.\n"
                               "Введите город вручную:",
                      keyboard=action_keyboard
                      )
    else:
        db.set_state_user(user_id, "waiting_for_city")
        write_msg(user_id, "Введите город для поиска:")
    print("Sent city input prompt to user", user_id)


def process_confirm_change(user_id: int, choice: str) -> None:
    if choice.lower() == "да":
        db.set_state_user(user_id, "waiting_for_city")
        # Вернуться к ожиданию ввода города
        action_keyboard = create_action_keyboard()
        write_msg(user_id, "Введите город для поиска:",
                  keyboard=action_keyboard
                  )
    elif choice.lower() == "нет":
        db.set_state_user(user_id, "waiting_for_action")
        # Вернуться к выбору действия
        action_keyboard = create_action_keyboard()
        write_msg(user_id, "Что вы хотите сделать?",
                  keyboard=action_keyboard
                  )
    else:
        write_msg(user_id, "Пожалуйста, ответьте \"Да\" или \"Нет\".")


# Функция для начала диалога с пользователем
def start_conversation(user_id: int) -> None:
    print("Starting conversation with user", user_id)

    # Отправка приветственного сообщения и клавиатуры для выбора пола
    message = ("Привет!\nЯ бот, который поможет вам найти интересных людей.\n"
               "Выберите пол, который вы ищете:")

    keyboard = create_start_conversation_keyboard()
    # Отправка сообщения с клавиатурой
    write_msg(user_id=user_id, message=message, keyboard=keyboard)

    # Установка состояния пользователя в "ожидание выбора пола"
    db.set_state_user(user_id, "waiting_for_gender")
    print("DB State: ", db.get_state_user(user_id), "user_id:", user_id)
    print("Sent gender selection keyboard to user", user_id)


# Функция для обработки выбора пола
def process_gender(user_id: int, gender: str) -> None:
    print("Processing gender selection for user", user_id)

    if gender.lower() == "мужчину" or gender.lower() == "женщину":
        print('gender: ', gender, 'user_id: ', user_id)
        db.set_search(self_id=user_id, sex=gender)

        # Создание клавиатуры с кнопками для выбора действия
        keyboard = create_action_keyboard()

        write_msg(user_id, "Что вы хотите сделать?",
                  keyboard=keyboard
                  )
        db.set_state_user(user_id, "waiting_for_action")
        print("Sent action selection keyboard to user", user_id)
    else:
        write_msg(
                user_id=user_id,
                message="Не поняла вашего выбора. "
                        "Пожалуйста, выберите пол из списка."
        )
        print("Sent invalid gender response message to user", user_id)


# Функция для получения города пользователя
def get_user_city(user_id: int) -> str | None:
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


# Функция для обработки подтверждения города
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


# Функция для получения топ-фотографий пользователя
def get_top_photos(profile_id: int) -> list:
    try:
        photos_response = vk_user.photos.get(
                owner_id=profile_id, album_id='profile', extended=1
        )
        photos = photos_response['items']
        photos_sorted = sorted(
                photos, key=lambda x: x['likes']['count'], reverse=True
        )
        top_photos = photos_sorted[:3]
        photo_urls = [photo['sizes'][-1]['url']
                      for photo in top_photos]
    except Exception as e:
        print("Error getting top photos:", str(e))
        return []
    return photo_urls


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


def process_search(user_id: int) -> None:
    write_msg(user_id, "Начинаем искать...")
    data = db.get_search(user_id)
    count = 50
    sex = '1' if data['sex'].lower() == 'женщину' else '2'
    print('city id: ', get_city_id(data['city']))

    search_results = vk_user.users.search(count=count,
                                          country=1,  # Россия
                                          sex=sex,
                                          city=get_city_id(data['city']),
                                          age_from=str(data['age_from']),
                                          age_to=str(data['age_to']),
                                          has_photo='1',
                                          status='6',
                                          sort=1,
                                          fields="city, bdate, sex"
                                          )
    print(len(search_results['items']))
    print()
    print(search_results['items'])
    print("***" * 20)

    # Сохраняем результаты поиска в базе данных
    db.set_search(self_id=user_id, results=None)
    db.set_search(self_id=user_id, results=search_results['items'])

    # Устанавливаем состояние пользователя для показа профилей
    db.set_state_user(self_id=user_id, state="showing_profiles")
    # Устанавливаем начальный индекс на 0
    if db.get_search_index(self_id=user_id) == 0:
        db.set_search_index(self_id=user_id, new_index=0)

    # Отображаем первый профиль
    display_profile(user_id=user_id)


def display_profile(user_id: int):
    search_results = db.get_search_results(self_id=user_id)
    index = db.get_search_index(self_id=user_id)
    print('index: ', index)
    if index < len(search_results):
        profile = search_results[index]
        url = "https://vk.com/id" + str(profile['id'])
        # Формируем сообщение с информацией о профиле
        message = (f"Имя: {profile['first_name']} "
                   f"{profile['last_name']}\n "
                   f"Возраст: {calculate_age(profile['bdate'])}\n"
                   f"Город: {profile.get('city', {}).get('title', 'N/A')}\n"
                   f"Ссылка на профиль: {url}")
        # Получаем топ-фотографии профиля
        top_photos = get_top_photos(profile_id=profile['id'])
        print("*** top_photos ***:", top_photos)

        if not top_photos:
            message += "\nНет фотографий или профиль закрыт"

        # Создаем встроенную клавиатуру с кнопками "лайка" и "дизлайка"
        keyboard = create_like_dislike_keyboard()
        # Отправляем сообщение с клавиатурой и изображениями
        write_msg(user_id=user_id,
                  message=message,
                  keyboard=keyboard,
                  image_urls=[upload_photo(photo) for photo in top_photos]
                  )
    else:
        # Больше профилей нет для отображения
        write_msg(user_id=user_id,
                  message="Больше профилей для отображения нет."
                  )


def main():
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:

            user_id = event.obj.message["from_id"]

            # DB
            db.add_user(user_id)
            print("DB State: ", db.get_state_user(
                    user_id
            ), "user_id:", user_id
                  )

            request = event.obj.message["text"].lower()

            logging.info(
                    f"Received message from user {user_id}: {request}"
            )

            if request in ["начать", "старт", "start", "сменить настройки"]:
                if db.get_state_user(user_id) is None:
                    db.set_state_user(user_id, "waiting_for_gender")

                if db.get_state_user(user_id) == "showing_profiles":
                    process_search(user_id)

                start_conversation(user_id)

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
                elif request == "изменить настройки" \
                        and user_state_db == "showing_profiles":
                    db.set_state_user(user_id, "waiting_for_city")
                    start_conversation(user_id)
                elif user_state_db == "showing_profiles":
                    print('user_state_db "showing_profiles"')
                    if request == "начать поиск":
                        process_search(user_id)
                    elif request == "продолжить":
                        display_profile(user_id=user_id)
                    elif request == "меню":
                        write_msg(user_id, f"Выберите действие.",
                                  keyboard=create_menu_keyboard()
                                  )
                    elif request == "👍 лайк":
                        search_results = db.get_search_results(self_id=user_id)
                        index = db.get_search_index(self_id=user_id)
                        profile = search_results[index]["id"]
                        first_name = search_results[index]["first_name"]
                        last_name = search_results[index]["last_name"]
                        if not db.is_viewed(self_id=user_id, user_id=profile):
                            db.add_like(self_id=user_id, user_id=profile,
                                        first_name=first_name,
                                        last_name=last_name
                                        )
                        db.set_search_index(self_id=user_id,
                                            new_index=index + 1
                                            )
                        display_profile(user_id=user_id)

                    elif request == "👎 дизлайк":
                        search_results = db.get_search_results(self_id=user_id)
                        index = db.get_search_index(self_id=user_id)
                        profile = search_results[index]["id"]
                        first_name = search_results[index]["first_name"]
                        last_name = search_results[index]["last_name"]
                        if not db.is_viewed(self_id=user_id, user_id=profile):
                            db.add_dislike(self_id=user_id, user_id=profile,
                                           first_name=first_name,
                                           last_name=last_name
                                           )
                        db.set_search_index(self_id=user_id,
                                            new_index=index + 1
                                            )
                        display_profile(user_id=user_id)

                    elif request == "избранное":
                        write_msg(user_id,
                                  f"Список избранных пользователей",
                                  keyboard=create_menu_keyboard()
                                  )
                        req_like = db.request_liked_list(self_id=user_id)

                        url = "https://vk.com/id"
                        req_list = "\n".join([
                            f"{item['first_name']} {item['last_name']} "
                            f"{url}{item['viewed_vk_id']}"
                            for item in req_like]
                        )
                        write_msg(user_id, req_list)
                else:
                    write_msg(user_id,
                              f"Вы ранее уже заполнили профиль, "
                              f"выберите действие.",
                              keyboard=create_search_or_city_keyboard()
                              )


if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("TOKEN_GROUP")
    token_user = os.getenv("TOKEN_USER")
    group_id = os.getenv("GROUP_ID")

    # DB initialization
    usernamedb = os.getenv("USERNAMEDB")
    password = os.getenv("PASSWORD")
    host = os.getenv("HOST")
    port = os.getenv("PORT")
    databasename = os.getenv("DATABASENAME")
    DSN = f"postgresql://{usernamedb}:{password}@{host}:{port}/{databasename}"
    db = Database(DSN)
    db.create_tables()

    # Group API
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()

    # User API
    vk_session_user = vk_api.VkApi(token=token_user)
    vk_user = vk_session_user.get_api()

    # Инициализация LongPoll
    longpoll = VkBotLongPoll(vk_session, group_id=group_id)
    upload = VkUpload(vk_session)

    # Запуск бота
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s'
                        )
    logging.info("Bot started")
    print("Bot started")
    main()
