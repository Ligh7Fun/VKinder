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
