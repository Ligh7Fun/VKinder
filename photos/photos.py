import requests
from io import BytesIO

def upload_photo(url: str) -> str:
    img = requests.get(url).content
    f = BytesIO(img)  # Переводим в байты изображение

    response = upload.photo_messages(f)[0]  # Загружаем на сервер
    profile_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']

    return f'photo{profile_id}_{photo_id}_{access_key}'

def get_top_photos(profile_id: int) -> list:
    try:
        photos_response = vk_user.photos.get(
            owner_id=profile_id, album_id='profile', extended=1
        )
        photos = photos_response['items']
        photos_sorted = sorted(
            photos, key=lambda x: x['likes']['count'], reverse=True
        )
        top_photos = photos_sorted[:3]
        photo_urls = [photo['sizes'][-1]['url']
                      for photo in top_photos]
    except Exception as e:
        print("Error getting top photos:", str(e))
        return []
    return photo_urls