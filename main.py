import logging
import os

from dotenv import load_dotenv
from vk_api.bot_longpoll import VkBotEventType

from database.db import Database
from process.message_handler import message_handler
from vkapi.vkapi import Vkapi


logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    encoding='utf-8'
                    )


def main():
    for event in vk.longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message["from_id"]
            db.add_user(user_id)
            request = event.obj.message["text"].lower()
            db_state = db.get_state_user(user_id)

            logging.info(
                    f"Received message from user {user_id} "
                    f"state {db_state}: {request}"
            )

            message_handler(vk=vk, db=db, user_id=user_id, request=request)


if __name__ == "__main__":

    load_dotenv()

    # VK API initialization
    token_group = os.getenv("TOKEN_GROUP")
    token_user = os.getenv("TOKEN_USER")
    group_id = os.getenv("GROUP_ID")
    vk = Vkapi(token_group=token_group,
               token_user=token_user,
               group_id=group_id
               )

    # DB initialization
    usernamedb = os.getenv("USERNAMEDB")
    password = os.getenv("PASSWORD")
    host = os.getenv("HOST")
    port = os.getenv("PORT")
    databasename = os.getenv("DATABASENAME")
    DSN = f"postgresql://{usernamedb}:{password}@{host}:{port}/{databasename}"
    db = Database(DSN)
    db.create_tables()
    db.add_status(status="Like")
    db.add_status(status="Dislike")

    # Запуск бота
    logging.info("Bot started")
    main()
