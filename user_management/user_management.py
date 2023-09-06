from vk_api import vk 
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.upload import VkUpload
import vk_api

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

