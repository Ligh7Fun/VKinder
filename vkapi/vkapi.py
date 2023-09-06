import os
from dotenv import load_dotenv
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.upload import VkUpload
from database import Database 
class Vk:
    def __init__(self):
        load_dotenv()
        token = os.getenv("TOKEN_GROUP")
        token_user = os.getenv("TOKEN_USER")
        group_id = os.getenv("GROUP_ID")

        # DB initialization
        usernamedb = os.getenv("USERNAMEDB")
        password = os.getenv("PASSWORD")
        host = os.getenv("HOST")
        port = os.getenv("PORT")
        databasename = os.getenv("DATABASENAME")
        DSN = f"postgresql://{usernamedb}:{password}@{host}:{port}/{databasename}"
        self.db = Database(DSN)
        self.db.create_tables()

        # Group API
        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()

        # User API
        self.vk_session_user = vk_api.VkApi(token=token_user)
        self.vk_user = self.vk_session_user.get_api()

       # Инициализация LongPoll
        self.longpoll = VkBotLongPoll(self.vk_session, group_id=group_id)
        self.upload = VkUpload(self.vk_session)
