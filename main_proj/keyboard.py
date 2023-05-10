import json


def get_but(text, color='secondary'):
    return {
        "action": {
            "type": "text",
            "payload": "{\"button\": \"" + "1" + "\"}",
            "label": f"{text}"
        },
        "color": f"{color}"
    }


def keyboard_render(keyboard):
    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard


# homepage
keyboard_1 = {
    "one_time": False,
    "buttons": [
        [get_but('поиск', 'positive')],
        [get_but('настройки', 'primary')],
        [get_but('помощь')]
    ]
}

# run
keyboard_2 = {
    "one_time": False,
    "buttons": [
        # [get_but('далее', 'primary')],
        [get_but('не нравится', 'negative'), get_but('нравится', 'positive')],
        [get_but('фавориты', 'primary')],
        [get_but('в начало')]
    ]
}

# settings
keyboard_3 = {
    "one_time": False,
    "buttons": [
        [get_but('/информация', 'positive')],
        [get_but('/возраст', 'primary'), get_but('/пол', 'primary')],
        [get_but('/статус', 'primary'), ],
        [get_but('/сброс', 'negative')],
        [get_but('в начало')]
    ]
}

keyboard_4 = {
    "one_time": False,
    "buttons": [
        [get_but('/возраст 18-25', 'primary'), get_but('/возраст 25-35', 'primary')],
        [get_but('/возраст без ограничений', 'primary')],
        [get_but('/возраст свой вариант', 'primary')],
        [get_but('назад в настройки')],
        [get_but('в начало')]
    ]
}

keyboard_5 = {
    "one_time": False,
    "buttons": [
        [get_but('/статус - холост', 'primary'), get_but('/статус - в активном поиске', 'primary')],
        [get_but('назад в настройки')],
        [get_but('в начало')]
    ]
}

keyboard_6 = {
    "one_time": False,
    "buttons": [
        [get_but('/пол Ж', 'primary'), get_but('/пол М', 'primary')],
        [get_but('назад в настройки')],
        [get_but('в начало')]
    ]
}

keyboard_7 = {
    "one_time": False,
    "buttons": [
        [get_but('/сброс/д@, я пoдтвержд@ю cбpoc/', 'negative')],
        [get_but('назад в настройки')],
        [get_but('в начало')]
    ]
}

keyboard_8 = {
    "one_time": False,
    "buttons": [
        [get_but('помощь - быстрый старт', 'positive')],
        [get_but('помощь - информация обо мне', 'primary')],
        [get_but('помощь - информация о приложении', 'primary')],
        [get_but('в начало')]
    ]
}


keyboard_start = keyboard_render(keyboard_1)
keyboard_search = keyboard_render(keyboard_2)
keyboard_info = keyboard_render(keyboard_8)
keyboard_settings = keyboard_render(keyboard_3)
keyboard_settings_age = keyboard_render(keyboard_4)
keyboard_settings_status = keyboard_render(keyboard_5)
keyboard_settings_sex = keyboard_render(keyboard_6)
keyboard_settings_clear = keyboard_render(keyboard_7)
