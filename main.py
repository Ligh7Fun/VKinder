import logging
import os

from dotenv import load_dotenv
from vk_api.bot_longpoll import VkBotEventType

from database.db import Database
from keyboards.keyboards import (create_search_or_city_keyboard,
                                 create_menu_keyboard,

                                 )
from process.process import (display_profile,
                             process_action,
                             process_age_from,
                             process_age_to,
                             process_city_input,
                             process_gender,
                             process_search,
                             start_conversation,
                             )
from vkapi.vkapi import Vkapi

logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    encoding='utf-8'
                    )


from typing import Dict, List


def handle_start_request(user_id: int, db: Database) -> None:
    """
    Обрабатывает начало общения с ботом.

    Args:
        user_id (int): ID пользователя.
        db (Database): Экземпляр класса Database для взаимодействия с базой.

    Returns:
        None.
    """
    if db.get_state_user(self_id=user_id) is None:
        db.set_state_user(self_id=user_id, state="waiting_for_gender")

def handle_showing_profiles(user_id: int, vk: Vkapi, db: Database) -> None:
    """
    Обрабатывает запрос на отображение профилей пользователей.

    Args:
        user_id (int): ID пользователя.
        vk (Vkapi): Экземпляр класса Vkapi для выполнения вызовов VK API.
        db (Database): Экземпляр класса Database для взаимодействия с базой.

    Returns:
        None.
    """
    process_search(vk=vk, db=db, user_id=user_id)

def handle_change_settings(user_id: int, db: Database, vk: Vkapi) -> None:
    """
    Обрабатывает запрос на изменение настроек профиля.

    Args:
        user_id (int): ID пользователя.
        db (Database): Экземпляр класса Database для взаимодействия с базой.
        vk (Vkapi): Экземпляр класса Vkapi для выполнения вызовов VK API.

    Returns:
        None.
    """
    db.set_state_user(self_id=user_id, state="waiting_for_city")
    start_conversation(vk=vk, db=db, user_id=user_id)

def handle_like_dislike_actions(request: str, user_id: int, db: Database, vk: Vkapi) -> None:
    """
    Обрабатывает действия "лайк" и "дизлайк" для профилей пользователей.

    Args:
        request (str): Запрос пользователя ("👍 лайк" или "👎 дизлайк").
        user_id (int): ID пользователя.
        db (Database): Экземпляр класса Database для взаимодействия с базой.
        vk (Vkapi): Экземпляр класса Vkapi для выполнения вызовов VK API.

    Returns:
        None.
    """
    search_results = db.get_search_results(self_id=user_id)
    index = db.get_search_index(self_id=user_id)
    profile = search_results[index]["id"]
    first_name = search_results[index]["first_name"]
    last_name = search_results[index]["last_name"]
    
    if request == "👍 лайк" and not db.is_viewed(self_id=user_id, user_id=profile):
        db.add_like(self_id=user_id, user_id=profile, first_name=first_name, last_name=last_name)
    elif request == "👎 дизлайк" and not db.is_viewed(self_id=user_id, user_id=profile):
        db.add_dislike(self_id=user_id, user_id=profile, first_name=first_name, last_name=last_name)
    
    db.set_search_index(self_id=user_id, new_index=index + 1)
    display_profile(vk=vk, db=db, user_id=user_id)

def handle_favorite_actions(user_id: int, db: Database, vk: Vkapi) -> None:
    """
    Обрабатывает действия, связанные с избранными профилями.

    Args:
        user_id (int): ID пользователя.
        db (Database): Экземпляр класса Database для взаимодействия с базой.
        vk (Vkapi): Экземпляр класса Vkapi для выполнения вызовов VK API.

    Returns:
        None.
    """
    vk.write_msg(user_id=user_id, message=f"Список избранных пользователей", keyboard=create_menu_keyboard())
    req_like = db.request_liked_list(self_id=user_id)
    
    url = "https://vk.com/id"
    req_list = "\n".join([f"{item['first_name']} {item['last_name']} {url}{item['viewed_vk_id']}" for item in req_like])
    vk.write_msg(user_id=user_id, message=req_list)

def handle_state(user_id: int, vk: Vkapi, db: Database, request: str) -> None:
    """
    Основная функция для управления состоянием пользователя.

    Args:
        user_id (int): ID пользователя.
        vk (Vkapi): Экземпляр класса Vkapi для выполнения вызовов VK API.
        db (Database): Экземпляр класса Database для взаимодействия с базой.
        request (str): Запрос пользователя.

    Returns:
        None.
    """
    user_state_db = db.get_state_user(user_id)

    if user_state_db == "waiting_for_gender":
        process_gender(vk=vk, db=db, user_id=user_id, gender=request)
    elif user_state_db == "waiting_for_action":
        process_action(vk=vk, db=db, user_id=user_id, action=request)
    elif user_state_db == "waiting_for_city":
        process_city_input(vk=vk, db=db, user_id=user_id, city_name=request)
    elif user_state_db == "waiting_for_age_from":
        process_age_from(vk=vk, db=db, user_id=user_id, age_from=request)
    elif user_state_db == "waiting_for_age_to":
        process_age_to(vk=vk, db=db, user_id=user_id, age_to=request)
    elif user_state_db == "showing_profiles":
        if request == "начать поиск":
            process_search(vk=vk, db=db, user_id=user_id)
        elif request == "продолжить":
            display_profile(vk=vk, db=db, user_id=user_id)
        elif request == "меню":
            vk.write_msg(user_id=user_id, message="Выберите действие.", keyboard=create_menu_keyboard())
        elif request == "избранное":
            handle_favorite_actions(user_id, db, vk)
        else:
            handle_like_dislike_actions(request, user_id, db, vk)
    else:
        vk.write_msg(user_id=user_id, message=f"Вы ранее уже заполнили профиль, выберите действие.", keyboard=create_search_or_city_keyboard())



def main():
    for event in vk.longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message["from_id"]
            db.add_user(user_id)
            request = event.obj.message["text"].lower()
            db_state = db.get_state_user(user_id)

            logging.info(f"Received message from user {user_id} state {db_state}: {request}")

            if request in ["начать", "старт", "start", "сменить настройки"]:
                handle_start_request(user_id, db)
                handle_showing_profiles(user_id, vk, db)
            else:
                if request == "изменить настройки" and db_state == "showing_profiles":
                    handle_change_settings(user_id, db, vk)
                else:
                    handle_state(user_id, vk, db, request)



if __name__ == "__main__":

    load_dotenv()

    # VK API initialization
    token_group = os.getenv("TOKEN_GROUP")
    token_user = os.getenv("TOKEN_USER")
    group_id = os.getenv("GROUP_ID")
    vk = Vkapi(token_group=token_group,
               token_user=token_user,
               group_id=group_id
               )

    # DB initialization
    usernamedb = os.getenv("USERNAMEDB")
    password = os.getenv("PASSWORD")
    host = os.getenv("HOST")
    port = os.getenv("PORT")
    databasename = os.getenv("DATABASENAME")
    DSN = f"postgresql://{usernamedb}:{password}@{host}:{port}/{databasename}"
    db = Database(DSN)
    db.create_tables()
    db.add_status(status="Like")
    db.add_status(status="Dislike")

    # Запуск бота
    logging.info("Bot started")
    main()
