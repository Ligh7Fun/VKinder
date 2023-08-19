import vk_api
import random

# Авторизация бота
vk_session = vk_api.VkApi(token='ВАШ_ТОКЕН')
vk = vk_session.get_api()

# Функция для поиска пользователей по заданным параметрам
def search_users(age_from, age_to, sex, city, status):
    users = vk.users.search(
        age_from=age_from,
        age_to=age_to,
        sex=sex,
        city=city,
        status=status,
        count=10  # Количество пользователей для поиска
    )
    return users['items']

# Функция для получения топ-3 популярных фотографий пользователя
def get_top_photos(user_id):
    photos = vk.photos.get(owner_id=user_id, album_id='profile', extended=1)
    photos = sorted(photos['items'], key=lambda x: x['likes']['count'], reverse=True)
    top_photos = photos[:3]
    return top_photos

# Основной цикл бота
def main():
    while True:
        # Получаем параметры от пользователя (диапазон возраста, пол, город, семейное положение)
        age_from = int(input("Введите минимальный возраст: "))
        age_to = int(input("Введите максимальный возраст: "))
        sex = int(input("Введите пол (1 - женский, 2 - мужской): "))
        city = int(input("Введите ID города: "))
        status = int(input("Введите семейное положение (1 - не женат/не замужем, 2 - в активном поиске): "))

        # Поиск пользователей
        users = search_users(age_from, age_to, sex, city, status)

        # Отправка топ-3 фотографий пользователей
        for user in users:
            user_id = user['id']
            top_photos = get_top_photos(user_id)
            vk.messages.send(
                user_id=user_id,
                message="Вот топ-3 популярных фотографии с вашего профиля:",
                attachment=",".join([f'photo{photo["owner_id"]}_{photo["id"]}' for photo in top_photos])
            )

if __name__ == '__main__':
    main()
