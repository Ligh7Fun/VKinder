import logging
import requests
from io import BytesIO

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.upload import VkUpload
from vk_api.utils import get_random_id
from utils.utils import get_country_iso

logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    encoding='utf-8'
                    )


class Vkapi:
    def __init__(self, token_group: str, token_user: str, group_id: str):
        self.vk_group_session = vk_api.VkApi(token=token_group)
        self.vk_user_session = vk_api.VkApi(token=token_user)
        self.vk_group = self.vk_group_session.get_api()
        self.vk_user = self.vk_user_session.get_api()
        self.longpoll = VkBotLongPoll(vk=self.vk_group_session,
                                      group_id=group_id
                                      )
        self.upload = VkUpload(vk=self.vk_group)

    def upload_photo(self, url: str) -> str | None:
        """
        Загружает фото по заданному URL и возвращает сгенерированный
        идентификатор фото.

        Args:
            url (str): URL фото для загрузки.

        Returns:
            str: Сгенерированный идентификатор фото в формате
                'photo{profile_id}_{photo_id}_{access_key}'.
            None: Если не удалось загрузить.
        """
        try:
            img = requests.get(url).content
            f = BytesIO(img)  # Переводим в байты изображение

            response = self.upload.photo_messages(f)[0]  # Загружаем на сервер
            profile_id = response['owner_id']
            photo_id = response['id']
            access_key = response['access_key']
        except Exception as e:
            logging.error(f"Ошибка при загрузке фото: {e}")
            return None
        return f'photo{profile_id}_{photo_id}_{access_key}'

    def write_msg(self,
                  user_id: int,
                  message: str,
                  keyboard=None,
                  image_urls=None,
                  ) -> None:
        """
        Отправляет сообщение пользователю в VK с использованием VK API.

        Args:
            user_id (int):
                ID пользователя, которому будет отправлено сообщение.
            message (str): Сообщение, которое будет отправлено.
            keyboard (Optional):
                Клавиатура, которая будет прикреплена к сообщению.
            image_urls (Optional[List[str]]):
                URL-адреса изображений, которые будут прикреплены к сообщению.

        Returns:
            None.
        """
        attachments = []
        if image_urls:
            for image_url in image_urls:
                attachments.append(image_url)
        attachment = ','.join(attachments) if image_urls is not None else None

        self.vk_group_session.method(
                'messages.send',
                {
                    'user_id': user_id,
                    'message': message,
                    'random_id': get_random_id(),
                    'keyboard': keyboard,
                    'attachment': attachment,
                }
        )

    def get_user_city(self, user_id: int) -> str | None:
        """
        Получает город пользователя по его идентификатору.

        Args:
            user_id (int): Идентификатор пользователя.

        Returns:
            str | None: Город пользователя, если есть, иначе None.

        Raises:
            Exception: Если произошла ошибка при получении города пользователя.

        """
        try:
            response = self.vk_user.get(user_ids=user_id, fields='city')
            city_info = response[0]['city']
            if city_info:
                city = city_info['title']
                return city
            else:
                return None
        except Exception as e:
            logging.error(f"Ошибка при получении города пользователя: {e}")
            return None

    def get_city_id(self, city_name: str) -> int | None:
        """
        Получает идентификатор города по его названию.

        Args:
            city_name (str): Название города.

        Returns:
            int | None: Идентификатор города, если он есть, иначе None.
        """
        country_iso = get_country_iso(city_name=city_name)
        country_id = self.get_country_id(country_code=country_iso)
        response = self.vk_user.database.getCities(country_id=country_id,
                                                   q=city_name
                                                   )
        if response['count'] > 0:
            city = response['items'][0]
            return city['id']
        else:
            return None

    def get_country_id(self, country_code: str) -> int | None:
        """
        Получает идентификатор страны по её коду в формате ISO 3166-1 alpha-2.

        Args:
            country_code (str): Код страны.

        Returns:
            int | None: Идентификатор страны, если она есть, иначе None.
        """
        response = self.vk_user.database.getCountries(need_all=1,
                                                      code=country_code
                                                      )
        if response['count'] > 0:
            country = response['items'][0]
            return country['id']
        else:
            return None

    def get_top_photos(self, profile_id: int) -> list:
        """
        Получает топ-3 фотографии профиля с использованием VK API.

        Parameters:
            profile_id (int): Идентификатор профиля, с которого нужно
                получить фотографии.

        Returns:
            list: Список URL-адресов для топ-3 фотографий, если он есть,
                иначе пустой список.
        """
        try:
            photos_response = self.vk_user.photos.get(
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
            logging.error(f"Ошибка при получении фотографий: {e}")
            return []
        return photo_urls
