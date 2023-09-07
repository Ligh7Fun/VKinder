



def handle_message(event):
    user_id = event.obj.message["from_id"]

    # DB
    db.add_user(user_id)
    print("DB State: ", db.get_state_user(user_id), "user_id:", user_id)

    request = event.obj.message["text"].lower()

    logging.info(f"Received message from user {user_id}: {request}")

    if request in ["начать", "старт", "start", "сменить настройки"]:
        handle_start(user_id)
    else:
        handle_user_state(user_id, request)

def handle_start(user_id):
    if db.get_state_user(user_id) is None:
        db.set_state_user(user_id, "waiting_for_gender")

    if db.get_state_user(user_id) == "showing_profiles":
        process_search(user_id)

    start_conversation(user_id)

def handle_user_state(user_id, request):
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
    elif request == "изменить настройки" and user_state_db == "showing_profiles":
        db.set_state_user(user_id, "waiting_for_city")
        start_conversation(user_id)
    elif user_state_db == "showing_profiles":
        handle_showing_profiles(user_id, request)
    else:
        write_msg(user_id, f"Вы ранее уже заполнили профиль, выберите действие.",
                  keyboard=create_search_or_city_keyboard()
                  )

def handle_showing_profiles(user_id, request):
    if request == "начать поиск":
        process_search(user_id)
    elif request == "продолжить":
        display_profile(user_id=user_id)
    elif request == "меню":
        write_msg(user_id, f"Выберите действие.", keyboard=create_menu_keyboard())
    elif request == "👍 лайк":
        handle_like(user_id)
    elif request == "👎 дизлайк":
        handle_dislike(user_id)
    elif request == "избранное":
        handle_favorites(user_id)

def handle_like_or_dislike(user_id, action):
    search_results = db.get_search_results(self_id=user_id)
    index = db.get_search_index(self_id=user_id)
    profile = search_results[index]["id"]
    first_name = search_results[index]["first_name"]
    last_name = search_results[index]["last_name"]

    if action == "like":
        db_action = db.add_like
    elif action == "dislike":
        db_action = db.add_dislike
    else:
        return

    if not db.is_viewed(self_id=user_id, user_id=profile):
        db_action(self_id=user_id, user_id=profile, first_name=first_name, last_name=last_name)

    db.set_search_index(self_id=user_id, new_index=index + 1)
    display_profile(user_id=user_id) 

def handle_favorites(user_id):
    write_msg(user_id, f"Список избранных пользователей", keyboard=create_menu_keyboard())
    req_like = db.request_liked_list(self_id=user_id)

    url = "https://vk.com/id"
    req_list = "\n".join([
        f"{item['first_name']} {item['last_name']} {url}{item['viewed_vk_id']}"
        for item in req_like]
    )
    write_msg(user_id, req_list)