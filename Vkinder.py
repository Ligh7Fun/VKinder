
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
import random
import logging
import json
import re

# Инициализация переменных
user_gender = None  # Переменная для хранения пола пользователя
favorites = {}  # Пустой словарь для хранения избранных пользователей
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

# Функция для получения топ-фотографий пользователя
def get_top_photos(user_id):
    photos_response = vk.photos.get(owner_id=user_id, album_id='profile', extended=1)
    photos = photos_response['items']
    photos_sorted = sorted(photos, key=lambda x: x['likes']['count'], reverse=True)
    top_photos = photos_sorted[:3]
    return top_photos

# Функция для отправки сообщения с возможной клавиатурой
def write_msg(user_id, message, keyboard=None):
    vk.messages.send(
        user_id=user_id,
        message=message,
        keyboard=keyboard if keyboard is not None else None,
        random_id=random.randint(1, 10 ** 9)
    )

# Функция для обработки выбора действия
def process_action(user_id, action):
    print("Processing action selection for user", user_id)
    print("Received action:", action)
    action_text = re.sub(r'^\d+\.\s*', '', action)  # Удаление цифр и точки из начала строки
    
    # Обработка выбора "Искать по городу из профиля"
    if action_text.lower() == "искать по городу из профиля":
        user_city = get_user_city(user_id)
        if user_city:
            user_states[user_id] = "waiting_for_age"
            city_message = f"Город из вашего профиля: {user_city}."
            confirm_keyboard = create_confirm_city_keyboard(user_city)
            write_msg(user_id, city_message, keyboard=confirm_keyboard)
            return
        else:
            user_states[user_id] = "waiting_for_city"
            action_keyboard = create_action_keyboard(user_gender)
            write_msg(user_id, "Город не указан в вашем профиле. Введите город вручную:", keyboard=action_keyboard)
    else:
        user_states[user_id] = "waiting_for_city"
        action_keyboard = create_action_keyboard(user_gender)
        write_msg(user_id, "Введите город для поиска:", keyboard=action_keyboard)
    print("Sent city input prompt to user", user_id)

# Словарь для хранения состояний пользователей
user_states = {}

# Функция для начала диалога с пользователем
def start_conversation(user_id):
    print("Starting conversation with user", user_id)
    
    # Отправка приветственного сообщения и клавиатуры для выбора пола
    message = "Привет! Я бот, который поможет вам найти интересных людей. Выберите пол, который вы ищете:"
    
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
    user_states[user_id] = "waiting_for_gender"
    print("Sent gender selection keyboard to user", user_id)

# Функция для обработки выбора пола
def process_gender(user_id, gender):
    print("Processing gender selection for user", user_id)
    if gender.lower() == "мужчину" or gender.lower() == "женщину":
        user_states[user_id] = "waiting_for_action"
        
        # Создание клавиатуры с кнопками для выбора действия
        action_keyboard = {
            "one_time": True,
            "buttons": [
                [{"action": {"type": "text", "label": "1. Искать по городу из профиля"}, "color": "default"}],
                [{"action": {"type": "text", "label": "2. Ввести другой город"}, "color": "default"}]
            ]
        }
        
        action_keyboard = json.dumps(action_keyboard, ensure_ascii=False)
        
        write_msg(user_id, "Что вы хотите сделать?", keyboard=action_keyboard)
        print("Sent action selection keyboard to user", user_id)
    else:
        write_msg(user_id, "Не поняла вашего выбора. Пожалуйста, выберите пол из списка.")
        print("Sent invalid gender response message to user", user_id)

# Функция для создания клавиатуры для выбора действия
def create_action_keyboard(gender):
    buttons = [
        [{"action": {"type": "text", "label": "1. Искать по городу из профиля"}, "color": "positive"}],
        [{"action": {"type": "text", "label": "2. Ввести другой город"}, "color": "positive"}]
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
            keyboard = create_action_keyboard(user_id)
            write_msg(user_id, f"Вы выбрали город из профиля: {user_city}.", keyboard=keyboard)
        else:
            write_msg(user_id, "Город не указан в вашем профиле. Введите город вручную:")
            user_states[user_id] = "waiting_for_city"
    else:
        user_states[user_id] = "waiting_for_age"
        write_msg(user_id, f"Вы выбрали город: {city_name}. Теперь введите желаемый возраст:")

# Функция для создания клавиатуры подтверждения города
def create_confirm_city_keyboard(city_name):
    keyboard = {
        "one_time": True,
        "buttons": [
            [{"action": {"type": "text", "label": f"Подтвердить {city_name}"}, "color": "positive"}],
            [{"action": {"type": "text", "label": "Ввести другой город"}, "color": "default"}]
        ]
    }
    return json.dumps(keyboard, ensure_ascii=False)

# Функция для обработки подтверждения города
def process_confirm_city(user_id, city_name):
    if city_name.startswith("Подтвердить"):
        city = city_name[11:]
        user_states[user_id] = "waiting_for_age"
        write_msg(user_id, f"Вы выбрали город: {city}. Теперь введите желаемый возраст:")
    elif city_name == "Ввести другой город":
        user_states[user_id] = "waiting_for_city"
        write_msg(user_id, "Введите город:")
    else:
        write_msg(user_id, "Не поняла вашего выбора. Пожалуйста, выберите действие из списка.")

def main():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                user_id = event.user_id
                request = event.text.lower()
                
                logging.info(f"Received message from user {user_id}: {request}")
                
                if request == "начать" or request == "start":
                    start_conversation(user_id)
                elif request == "пока":
                    write_msg(user_id, "До свидания!")
                elif request == "избранные":
                    process_list_favorites(user_id)
                else:
                    if user_id in user_states:
                        if user_states[user_id] == "waiting_for_gender":
                            process_gender(user_id, request)
                        elif user_states[user_id] == "waiting_for_action":
                            process_action(user_id, request)
                        elif user_states[user_id] == "waiting_for_city":
                            process_city_input(user_id, request)
                        elif user_states[user_id] == "waiting_for_age":
                            process_age(user_id, request)
                    else:
                        write_msg(user_id, "Не поняла вашей команды. Пожалуйста, начните с выбора пола.")

if __name__ == "__main__":
    # Загрузка токена из файла "token.txt"
    with open("token.txt", "r") as token_file:
        token = token_file.read().strip()

    # Инициализация VK API
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()

    # Инициализация LongPoll
    longpoll = VkLongPoll(vk_session)

    # Запуск бота
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Bot started")
    main()