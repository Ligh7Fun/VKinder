import json


def create_action_keyboard() -> str:
    """
    Создает клавиатуру с кнопками действий.

    Args:
        None.

    Returns:
        str: JSON-строка, представляющая созданную клавиатуру.
    """
    keyboard = {
        "one_time": True,
        "buttons": [
            [{"action": {"type": "text",
                         "label": "1. Искать по городу из профиля"},
              "color": "positive"}],
            [{"action": {"type": "text", "label": "2. Ввести другой город"},
              "color": "positive"}],
        ]
    }
    return json.dumps(keyboard, ensure_ascii=False)


def create_confirm_city_keyboard(city_name: str) -> str:
    """
    Создает клавиатуру для подтверждения города.

    Args:
        city_name (str): Название города для подтверждения.

    Returns:
        str: JSON-строка, представляющая созданную клавиатуру.
    """
    keyboard = {
        "one_time": True,
        "buttons": [
            [{"action": {"type": "text", "label": f"Подтвердить "
                                                  f"{city_name.title()}"},
              "color": "positive"}],
            [{"action": {"type": "text", "label": "Ввести другой город"},
              "color": "default"}],
        ]
    }
    return json.dumps(keyboard, ensure_ascii=False)


def create_search_or_city_keyboard():
    """
    Создает клавиатуру для поиска или выбора города.

    Args:
        None.

    Returns:
         str: JSON-строка, представляющая созданную клавиатуру.
    """
    keyboard = {
        "one_time": True,
        "buttons": [
            [{"action": {"type": "text", "label": "Изменить настройки"},
              "color": "default"}],
            [{"action": {"type": "text", "label": "Начать поиск"},
              "color": "positive"}]
        ]
    }
    return json.dumps(keyboard, ensure_ascii=False)


def create_menu_keyboard():
    """
    Создает клавиатуру с меню.

    Args:
        None.

    Returns:
        str: JSON-строка, представляющая созданную клавиатуру.
    """
    keyboard = {
        "one_time": True,
        "buttons": [
            [{"action": {"type": "text", "label": "Изменить настройки"},
              "color": "default"}],
            [{"action": {"type": "text", "label": "Продолжить"},
              "color": "positive"},
             {"action": {"type": "text", "label": "Избранное"},
              "color": "positive"}]
        ]
    }
    return json.dumps(keyboard, ensure_ascii=False)


def create_like_dislike_keyboard():
    """
    Создает клавиатуру для лайков и дизлайков с использованием VK API.

    Args:
        None.

    Returns:
        str: JSON-строка, представляющая созданную клавиатуру.
    """
    keyboard = {
        "inline": True,
        "buttons": [
            [{"action": {"type": "text", "label": "👍 Лайк"},
              "color": "positive"},
             {"action": {"type": "text", "label": "Меню"}, "color": "default"},
             {"action": {"type": "text", "label": "👎 Дизлайк"},
              "color": "negative"}]
        ]
    }
    return json.dumps(keyboard, ensure_ascii=False)


def create_start_conversation_keyboard():
    """
    Создает клавиатуру для начала разговора.

    Args:
        None.

    Returns:
        str: JSON-строка, представляющая созданную клавиатуру.
    """
    keyboard = {
        "one_time": True,
        "buttons": [
            [{"action": {"type": "text", "label": "Мужчину"},
              "color": "positive"}],
            [{"action": {"type": "text", "label": "Женщину"},
              "color": "positive"}]
        ]
    }

    return json.dumps(keyboard, ensure_ascii=False)
