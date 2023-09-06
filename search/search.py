from vk_api import vk_user  

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
