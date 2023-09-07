import re
from keyboards.keyboards import (create_action_keyboard,
                                 create_confirm_city_keyboard,
                                 create_search_or_city_keyboard,
                                 create_menu_keyboard,
                                 create_like_dislike_keyboard,
                                 create_start_conversation_keyboard,
                                 )




from keyboards.keyboards import (create_action_keyboard,
                                 create_confirm_city_keyboard,
                                 create_search_or_city_keyboard,
                                 create_menu_keyboard,
                                 create_like_dislike_keyboard,
                                 create_start_conversation_keyboard,
                                 )

from messaging.messaging import write_msg
from user_management.user_management import start_conversation, process_gender, get_user_city
from search.search import process_search 
from profile_display.profile_display import display_profile 
from message_handler import handle_message 
from vkapi.vkapi import Vk

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