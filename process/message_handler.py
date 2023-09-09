from database.db import Database
from keyboards.keyboards import (create_search_or_city_keyboard,
                                 create_menu_keyboard,

                                 )
from process.process import (display_profile,
                             process_action,
                             process_age_from,
                             process_age_to,
                             process_city_input,
                             process_gender,
                             process_search,
                             start_conversation,
                             )
from vkapi.vkapi import Vkapi


def message_handler(vk: Vkapi,
                    db: Database,
                    user_id: int,
                    request: str
                    ) -> None:
    if request in ["начать", "старт", "start", "сменить настройки"]:
        if db.get_state_user(self_id=user_id) is None:
            db.set_state_user(self_id=user_id,
                              state="waiting_for_gender"
                              )

        if db.get_state_user(self_id=user_id) == "showing_profiles":
            process_search(vk=vk, db=db, user_id=user_id)

        start_conversation(vk=vk, db=db, user_id=user_id)

    else:
        user_state_db = db.get_state_user(user_id)

        if user_state_db == "waiting_for_gender":
            process_gender(vk=vk, db=db, user_id=user_id,
                           gender=request
                           )
        elif user_state_db == "waiting_for_action":
            process_action(vk=vk, db=db, user_id=user_id,
                           action=request
                           )
        elif user_state_db == "waiting_for_city":
            process_city_input(vk=vk, db=db, user_id=user_id,
                               city_name=request
                               )
        elif user_state_db == "waiting_for_age_from":
            process_age_from(vk=vk, db=db, user_id=user_id,
                             age_from=request
                             )
        elif user_state_db == "waiting_for_age_to":
            process_age_to(vk=vk, db=db, user_id=user_id,
                           age_to=request
                           )
        elif request == "изменить настройки" \
                and user_state_db == "showing_profiles":
            db.set_state_user(self_id=user_id,
                              state="waiting_for_city"
                              )
            start_conversation(vk=vk, db=db, user_id=user_id)
        elif user_state_db == "showing_profiles":
            if request == "начать поиск":
                process_search(vk=vk, db=db, user_id=user_id)
            elif request == "продолжить":
                display_profile(vk=vk, db=db, user_id=user_id)
            elif request == "меню":
                vk.write_msg(user_id=user_id,
                             message="Выберите действие.",
                             keyboard=create_menu_keyboard()
                             )
            elif request == "👍 лайк" or request == "👎 дизлайк":
                search_results = db.get_search_results(self_id=user_id)
                index = db.get_search_index(self_id=user_id)
                profile = search_results[index]["id"]
                first_name = search_results[index]["first_name"]
                last_name = search_results[index]["last_name"]
                if request == "👍 лайк" and not db.is_viewed(
                        self_id=user_id, user_id=profile
                ):
                    db.add_like(self_id=user_id, user_id=profile,
                                first_name=first_name,
                                last_name=last_name
                                )
                elif request == "👎 дизлайк" and not db.is_viewed(
                        self_id=user_id, user_id=profile
                ):
                    db.add_dislike(self_id=user_id, user_id=profile,
                                   first_name=first_name,
                                   last_name=last_name
                                   )
                db.set_search_index(self_id=user_id,
                                    new_index=index + 1
                                    )
                display_profile(vk=vk, db=db, user_id=user_id)

            elif request == "избранное":
                vk.write_msg(user_id=user_id,
                             message=f"Список избранных пользователей",
                             keyboard=create_menu_keyboard()
                             )
                req_like = db.request_liked_list(self_id=user_id)

                url = "https://vk.com/id"
                req_list = "\n".join([
                    f"{item['first_name']} {item['last_name']} "
                    f"{url}{item['viewed_vk_id']}"
                    for item in req_like]
                )
                vk.write_msg(user_id=user_id, message=req_list)
        else:
            vk.write_msg(user_id=user_id,
                         message=f"Вы ранее уже заполнили профиль, "
                                 f"выберите действие.",
                         keyboard=create_search_or_city_keyboard()
                         )
