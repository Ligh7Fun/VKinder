import logging
import re

from database.db import Database
from keyboards.keyboards import (create_action_keyboard,
                                 create_confirm_city_keyboard,
                                 create_like_dislike_keyboard,
                                 create_search_or_city_keyboard,
                                 create_start_conversation_keyboard,
                                 )
from vkapi.vkapi import Vkapi
from utils.utils import calculate_age, get_country_iso

logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    encoding='utf-8'
                    )


def process_action(vk: Vkapi,
                   db: Database,
                   user_id: int,
                   action: str
                   ) -> None:
    """
    Функция для обработки выбора действия

    Args:
        vk (Vkapi): Экземпляр класса Vkapi для выполнения вызовов VK API.
        db (Database): Экземпляр класса Database для взаимодействия с базой.
        user_id (int):  ID пользователя.
        action (str): Выбранное действие.

    Returns:
        None.
    """
    logging.info(f"Processing action selection for user: {user_id}")
    logging.info(f"Received action: {user_id}")
    # Удаление цифр и точки из начала строки
    action_text = re.sub(pattern=r'^\d+\.\s*', repl='', string=action)

    if action_text.lower() == "искать по городу из профиля":
        user_city = vk.get_user_city(user_id=user_id)
        if user_city:
            db.set_state_user(self_id=user_id, state="waiting_for_age_from")
            db.set_search(self_id=user_id, city=user_city)
            # Обновляем состояние для ввода возраста
            city_message = f"Город из вашего профиля: {user_city}."
            confirm_keyboard = create_confirm_city_keyboard(user_city)
            vk.write_msg(user_id=user_id,
                         message=city_message,
                         keyboard=confirm_keyboard
                         )
            return
        else:
            db.set_state_user(self_id=user_id, state="waiting_for_city")
            action_keyboard = create_action_keyboard()
            vk.write_msg(user_id=user_id,
                         message="Город не указан в вашем профиле.\n"
                                 "Введите город вручную:",
                         # keyboard=action_keyboard
                         )
    else:
        db.set_state_user(self_id=user_id, state="waiting_for_city")
        vk.write_msg(user_id=user_id, message="Введите город для поиска:")
    logging.info(f"Sent city input prompt to user: {user_id}")


def start_conversation(vk: Vkapi,
                       db: Database,
                       user_id: int
                       ) -> None:
    """
    Функция для начала диалога с пользователем

    Args:
        vk (Vkapi): Экземпляр класса Vkapi для выполнения вызовов VK API.
        db (Database): Экземпляр класса Database для взаимодействия с базой.
        user_id (int):  ID пользователя.

    Returns:
        None.
    """
    logging.info(f"Starting conversation with user: {user_id}")

    # Отправка приветственного сообщения и клавиатуры для выбора пола
    message = ("Привет!\nЯ бот, который поможет вам найти интересных людей.\n"
               "Выберите пол, который вы ищете:")

    keyboard = create_start_conversation_keyboard()
    # Отправка сообщения с клавиатурой
    vk.write_msg(user_id=user_id,
                 message=message,
                 keyboard=keyboard
                 )

    # Установка состояния пользователя в "ожидание выбора пола"
    db.set_state_user(self_id=user_id, state="waiting_for_gender")
    logging.info(f"Sent gender selection keyboard to user: {user_id}")
    logging.info(f"DB State: {db.get_state_user(self_id=user_id)}, "
                 f"user_id: {user_id}"
                 )


def process_gender(vk: Vkapi,
                   db: Database,
                   user_id: int,
                   gender: str
                   ) -> None:
    """
    Функция для обработки выбора пола

    Args:
        vk (Vkapi): Экземпляр класса Vkapi для выполнения вызовов VK API.
        db (Database): Экземпляр класса Database для взаимодействия с базой.
        user_id (int):  ID пользователя.
        gender (str): Выбранный пол.

    Returns:
        None.
    """
    logging.info(f"Processing gender selection for user: {user_id}")

    if gender.lower() == "мужчину" or gender.lower() == "женщину":
        db.set_search(self_id=user_id, sex=gender)

        # Создание клавиатуры с кнопками для выбора действия
        keyboard = create_action_keyboard()

        vk.write_msg(user_id=user_id,
                     message="Что вы хотите сделать?",
                     keyboard=keyboard
                     )
        db.set_state_user(self_id=user_id, state="waiting_for_action")
        logging.info(f"Sent action selection keyboard to user: {user_id}")
    else:
        vk.write_msg(
                user_id=user_id,
                message="Не поняла вашего выбора. "
                        "Пожалуйста, выберите пол из списка."
        )
        logging.info(f"Sent invalid gender response message to user: "
                     f"{user_id}"
                     )


#
def process_city_input(vk: Vkapi,
                       db: Database,
                       user_id: int,
                       city_name: str
                       ) -> None:
    """
    Функция для обработки ввода города

    Args:
        vk (Vkapi): Экземпляр класса Vkapi для выполнения вызовов VK API.
        db (Database): Экземпляр класса Database для взаимодействия с базой.
        user_id (int):  ID пользователя.
        city_name (str): Название города, указанное пользователем.

    Returns:
        None.
    """
    if city_name.lower() == "из профиля":
        user_city = vk.get_user_city(user_id=user_id)
        if user_city:
            keyboard = create_action_keyboard()
            db.set_search(self_id=user_id, city=user_city)
            vk.write_msg(user_id=user_id,
                         message=f"Вы выбрали город из профиля: "
                                 f"{user_city.title()}.",
                         keyboard=keyboard
                         )

        else:
            vk.write_msg(user_id=user_id,
                         message="Город не указан в вашем профиле.\n"
                                 "Введите город вручную:"
                         )
            db.set_state_user(self_id=user_id, state="waiting_for_city")
            logging.info(f"DB State: {db.get_state_user(self_id=user_id)}, "
                         f"user_id: {user_id}"
                         )
    else:
        db.set_state_user(self_id=user_id, state="waiting_for_age_from")
        logging.info(f"DB State: {db.get_state_user(self_id=user_id)}, "
                     f"user_id: {user_id}"
                     )
        db.set_search(self_id=user_id, city=city_name)
        vk.write_msg(user_id=user_id,
                     message=f"Вы выбрали город: {city_name.title()}.\n"
                             f"Теперь введите начальный возраст:"
                     )


# Функция для обработки подтверждения города
def process_confirm_city(vk: Vkapi,
                         db: Database,
                         user_id: int,
                         city_name: str
                         ) -> None:
    """
    Функция для обработки подтверждения города

    Args:
        vk (Vkapi): Экземпляр класса Vkapi для выполнения вызовов VK API.
        db (Database): Экземпляр класса Database для взаимодействия с базой.
        user_id (int):  ID пользователя.
        city_name (str): Название города, указанное пользователем.

    Returns:
        None.
    """
    if city_name.startswith("Подтвердить"):
        city = city_name[11:]
        db.set_state_user(self_id=user_id, state="waiting_for_age")
        db.set_search(self_id=user_id, city=city)
        vk.write_msg(user_id=user_id,
                     message=f"Вы выбрали город: {city.title()}.\n"
                             f"Теперь введите желаемый возраст:"
                     )
    elif city_name == "Ввести другой город":
        db.set_state_user(self_id=user_id, state="waiting_for_city")
        # Изменение состояния на ожидание ввода города
        vk.write_msg(user_id=user_id, message="Введите город:")


def process_age(vk: Vkapi,
                db: Database,
                user_id: int,
                age: int
                ) -> None:
    """
    Функция для обработки подтверждения возраста

    Args:
        vk (Vkapi): Экземпляр класса Vkapi для выполнения вызовов VK API.
        db (Database): Экземпляр класса Database для взаимодействия с базой.
        user_id (int):  ID пользователя.
        age (int): Возраст, указанный пользователем.

    Returns:
        None.
    """
    logging.info(f"Processing age input for user: {user_id}")
    try:
        age = int(age)
        if 0 <= age <= 150:  # Проверка на разумный диапазон возраста
            vk.write_msg(user_id=user_id,
                         message=f"Вы ввели возраст: {age}.\nМожете ввести "
                                 f"другой город или продолжить поиск."
                         )
            db.set_state_user(self_id=user_id, state="waiting_for_city")
            # Вернуться в состояние ожидания ввода города
        else:
            vk.write_msg(user_id=user_id,
                         message="Введите корректный возраст (от 0 до 150)."
                         )
    except ValueError:
        vk.write_msg(user_id=user_id,
                     message="Введите числовой возраст (от 0 до 150)."
                     )


def process_age_from(vk: Vkapi,
                     db: Database,
                     user_id: int,
                     age_from: int
                     ) -> None:
    """
    Функция для обработки подтверждения начального возраста

    Args:
        vk (Vkapi): Экземпляр класса Vkapi для выполнения вызовов VK API.
        db (Database): Экземпляр класса Database для взаимодействия с базой.
        user_id (int):  ID пользователя.
        age_from (int): Начальный возраст, указанный пользователем.

    Returns:
        None.
    """
    logging.info(f"Processing age from input for user: {user_id}")
    try:
        age_from = int(age_from)
        if 0 <= age_from <= 150:  # Проверка на разумный диапазон возраста
            db.set_state_user(self_id=user_id, state="waiting_for_age_to")
            db.set_search(self_id=user_id, age_from=age_from)
            vk.write_msg(user_id=user_id,
                         message=f"Вы ввели начальный возраст: "
                                 f"{age_from}.\nТеперь введите конечный "
                                 f"возраст:"
                         )

        else:
            vk.write_msg(user_id=user_id,
                         message="Введите корректный возраст (от 0 до 150)."
                         )
    except ValueError:
        vk.write_msg(user_id=user_id,
                     message="Введите числовой возраст (от 0 до 150)."
                     )


def process_age_to(vk: Vkapi, db: Database, user_id: int, age_to: int
                   ) -> None:
    """
    Функция для обработки подтверждения конечного возраста

    Args:
        vk (Vkapi): Экземпляр класса Vkapi для выполнения вызовов VK API.
        db (Database): Экземпляр класса Database для взаимодействия с базой.
        user_id (int):  ID пользователя.
        age_to (int): Конечный возраст, указанный пользователем.

    Returns:
        None.
    """
    try:
        age_to = int(age_to)
        db.set_state_user(self_id=user_id, state="waiting_for_search_or_city")
        db.set_search(self_id=user_id, age_to=age_to)

        data_for_search = db.get_search(self_id=user_id)

        vk.write_msg(user_id,
                     message=f"Вы ввели следующие данные:\n"
                             f"Пол: {data_for_search['sex']}\n"
                             f"Город: {data_for_search['city'].title()}\n"
                             f"Начальный возраст: "
                             f"{data_for_search['age_from']}"
                             f"\nКонечный возраст: "
                             f"{data_for_search['age_to']}",
                     keyboard=create_search_or_city_keyboard()
                     )
        db.set_state_user(self_id=user_id, state="showing_profiles")
    except ValueError:
        vk.write_msg(user_id=user_id,
                     message="Некорректный ввод. Пожалуйста, введите число."
                     )


def process_search(vk: Vkapi, db: Database, user_id: int) -> None:
    """
    Процесс поиска для указанного пользователя.

    Args:
        vk (Vkapi): Экземпляр класса Vkapi для выполнения вызовов VK API.
        db (Database): Экземпляр класса Database для взаимодействия с базой.
        user_id (int): ID пользователя.

    Returns:
        None
    """
    vk.write_msg(user_id=user_id, message="Начинаем искать...")
    data = db.get_search(user_id)
    count = 50
    sex = '1' if data['sex'].lower() == 'женщину' else '2'
    city = data['city']
    age_from = data['age_from']
    age_to = data['age_to']
    country_iso = get_country_iso(city_name=city)
    print(country_iso)
    country_id = vk.get_country_id(country_code=country_iso)

    search_results = vk.vk_user.users.search(count=count,
                                             country_id=country_id,
                                             sex=sex,
                                             city_id=vk.get_city_id(
                                                     city_name=city
                                             ),
                                             age_from=str(age_from),
                                             age_to=str(age_to),
                                             has_photo=True,
                                             status='6',
                                             sort=1,
                                             fields="city, bdate, sex"
                                             )

    # Сохраняем результаты поиска в базе данных
    db.set_search(self_id=user_id, results=None)
    db.set_search(self_id=user_id, results=search_results['items'])

    # Устанавливаем состояние пользователя для показа профилей
    db.set_state_user(self_id=user_id, state="showing_profiles")
    # Устанавливаем начальный индекс на 0
    if db.get_search_index(self_id=user_id) == 0:
        db.set_search_index(self_id=user_id, new_index=0)

    # Отображаем первый профиль
    display_profile(vk=vk, db=db, user_id=user_id)


def display_profile(vk: Vkapi, db: Database, user_id: int):
    """
    Отображает информацию о профиле пользователя.

    Args:
        vk (Vkapi): Экземпляр класса Vkapi для выполнения вызовов VK API.
        db (Database): Экземпляр класса Database для взаимодействия с базой.
        user_id (int): ID пользователя.

    Returns:
        None
    """
    search_results = db.get_search_results(self_id=user_id)
    index = db.get_search_index(self_id=user_id)
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
        top_photos = vk.get_top_photos(profile_id=profile['id'])

        if not top_photos:
            message += "\nНет фотографий или профиль закрыт"

        # Создаем встроенную клавиатуру с кнопками "лайка" и "дизлайка"
        keyboard = create_like_dislike_keyboard()
        # Отправляем сообщение с клавиатурой и изображениями
        image_urls = [vk.upload_photo(photo) for photo in top_photos]
        image_urls = [url for url in image_urls if
                      url is not None]  # Фильтруем пустые URL-адреса
        vk.write_msg(user_id=user_id,
                     message=message,
                     keyboard=keyboard,
                     image_urls=image_urls
                     )
    else:
        # Больше профилей нет для отображения
        vk.write_msg(user_id=user_id,
                     message="Больше профилей для отображения нет."
                     )
