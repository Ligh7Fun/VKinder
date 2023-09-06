from datetime import datetime
from io import BytesIO
import random
import logging
import re
import os

from dotenv import load_dotenv
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.upload import VkUpload
import vk_api
import requests



from photos.photos import (upload_photo,
                           get_top_photos)

from keyboards.keyboards import (create_action_keyboard,
                                 create_confirm_city_keyboard,
                                 create_search_or_city_keyboard,
                                 create_menu_keyboard,
                                 create_like_dislike_keyboard,
                                 create_start_conversation_keyboard,
                                 )

logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s'
                    ) 


from keyboards.keyboards import (create_action_keyboard,
                                 create_confirm_city_keyboard,
                                 create_search_or_city_keyboard,
                                 create_menu_keyboard,
                                 create_like_dislike_keyboard,
                                 create_start_conversation_keyboard,
                                 )

logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s'
                    ) 

from messaging.messaging import write_msg
from user_actions.user_actions import process_action, process_confirm_change
from user_management.user_management import start_conversation, process_gender, get_user_city
from search.search import process_search 
from user_actions.user_actions import (process_confirm_city,
                                       process_city_input,
                                       process_age,process_age_from,
                                       process_age_to,
                                       get_city_id,
                                       calculate_age)
from profile_display.profile_display import display_profile 
from message_handler import handle_message 
from vkapi.vkapi import Vk






def main():
    vk = Vk()  
    for event in vk.longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            handle_message(event, vk.db)




if __name__ == "__main__":
    main()
    logging.info("Bot started")
    print("Bot started")
  
