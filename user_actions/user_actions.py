import re
from db import db 

from database.db import Database 

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