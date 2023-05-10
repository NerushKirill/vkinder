import datetime
import re

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from main_proj.method import tools

from db.db import create_db, reset, add_candidate, check_candidate, like_candidate, my_favorite

from main_proj.keyboard import keyboard_start, keyboard_search, keyboard_settings, keyboard_settings_age,  \
    keyboard_settings_status, keyboard_settings_sex, keyboard_settings_clear, keyboard_info


class BotInterface:
    def __init__(self, token):
        self.bot = vk_api.VkApi(token=token)

        # main
        self.first_start_flag: bool = False
        self.about_me: dict = {}
        self.candidate_list: list = []
        self.candidate: dict = {}

        # search settings
        self.city_id: int = 1
        self.age_from: int = 18
        self.age_to: int = 99
        self.sex: int = 1
        self.status: int = 6
        self.offset: int = 0

    def check_status(self):
        if self.status == 1:
            return 'холост'
        elif self.status == 6:
            return 'в активном поиске'
        else:
            return 'укажите статус в настройках'

    def check_sex(self):
        if self.sex == 1:
            return 'ищем женщин'
        elif self.sex == 2:
            return 'ищем мужчин'
        else:
            return 'укажите пол в настройках'

    def list_link(self, lst):
        line = ''
        for i in lst:
            for j in i:
                line = line + str(j) + ' '
            line = line + '\n'

        return line

    def candidate_(self, event, candidat):
        current_year = datetime.datetime.now().year

        c_id = candidat['id']
        info = tools.get_profile_info(candidat['id'])
        photos = tools.photos_get(candidat['id'])
        link = f"https://vk.com/id{candidat['id']}"

        f_name = info[0]['first_name']
        l_name = info[0]['last_name']

        bdate = info[0]['bdate']
        byears = datetime.datetime.strptime(bdate, '%d.%m.%Y').year
        age = current_year - byears

        candidate = {'id': c_id,
                     'first_name': f_name,
                     'last_name': l_name,
                     'age': age,
                     'user_id': event.user_id,
                     'link': link}

        return candidate, photos

    def message_send(self, user_id, message, attachment=None, keyboard=None, carousel=None):
        self.bot.method('messages.send', {'user_id': user_id,
                                          'message': message,
                                          'random_id': get_random_id(),
                                          'attachment': attachment,
                                          'keyboard': keyboard,
                                          'template': carousel,
                                          })

    def searching(self):
        self.candidate_list = tools.user_search(self.city_id, self.age_from, self.age_to,
                                                self.sex, self.status, self.offset)

        self.candidate_list = [_ for _ in self.candidate_list if check_candidate(_) == 0]
        self.offset += 5

    def search(self, event):
        while len(self.candidate_list) == 0:
            self.searching()

        candidat = self.candidate_list.pop()

        candidat_all = self.candidate_(event, candidat)
        candidat_profile = candidat_all[0]
        candidat_photo = candidat_all[1]

        self.candidate = candidat_profile
        add_candidate(candidat_profile)

        for photo in candidat_photo:
            media = f"photo{photo['owner_id']}_{photo['id']}"
            self.message_send(event.user_id, '', attachment=media, keyboard=keyboard_search)

        self.message_send(event.user_id, f"{self.candidate['first_name']} "
                                         f"{self.candidate['last_name']}, "
                                         f"{self.candidate['age']}.",
                          keyboard=keyboard_search)

    def like(self, event):
        if self.candidate:
            like_candidate(self.candidate)
            self.message_send(event.user_id, f"{self.candidate['link']}", keyboard=keyboard_search)
            self.message_send(event.user_id, f"Кандидат добавлен в список фаворитов.\n"
                                             f"Ищем дальше!",
                              keyboard=keyboard_search)
            self.search(event)
        else:
            self.search(event)

    def dis_like(self, event):
        self.search(event)

    def favorite(self, event):
        list_favorite = self.list_link(my_favorite())
        if len(list_favorite) > 0:
            self.message_send(event.user_id, f"Фавориты: \n{list_favorite}", keyboard=keyboard_search)
        else:
            self.message_send(event.user_id, f"Список фаворитов пуст.\n"
                                             f"Поставте лайк тому, кто "
                                             f"Вам понравится и он появится в списке фаворитов.",
                              keyboard=keyboard_search)

    def help(self, event, message):
        msg = re.findall('быстрый старт|информация обо мне|информация о приложении', message)
        if len(msg) != 0:
            if msg[0] == 'быстрый старт':
                self.message_send(event.user_id, f"Быстрый старт.", keyboard=keyboard_info)
            elif msg[0] == 'информация обо мне':
                current_year = datetime.datetime.now().year

                bdate = self.about_me[0]['bdate']
                byears = datetime.datetime.strptime(bdate, '%d.%m.%Y').year
                age = current_year - byears

                self.message_send(event.user_id, f"Информация обо мне.\n"
                                                 f"{self.about_me[0]['first_name']} {self.about_me[0]['last_name']}, "
                                                 f"{age}, {self.about_me[0]['city']['title']}.",
                                  keyboard=keyboard_info)
            elif msg[0] == 'информация о приложении':
                self.message_send(event.user_id, f"Выпускная работа VKinder - 2023 г.",
                                  keyboard=keyboard_info)
        else:
            self.message_send(event.user_id, f"Выбери интересующий тебя пункт меню.", keyboard=keyboard_info)

    def start(self, event, message):
        msg = re.findall('поиск|помощь|нравится|не нравится|фавориты|в начало', message)
        if len(msg) != 0:
            if msg[0] == 'поиск':
                self.search(event)
            elif msg[0] == 'нравится':
                self.like(event)
            elif msg[0] == 'не нравится':
                self.dis_like(event)
            elif msg[0] == 'фавориты':
                self.favorite(event)
            elif msg[0] == 'помощь':
                self.help(event, message)
            elif msg[0] == 'в начало':
                self.message_send(event.user_id, f"Начнем наш поиск.", keyboard=keyboard_start)
            else:
                self.message_send(event.user_id, f"Такой команды нет.", keyboard=keyboard_start)
        else:
            self.message_send(event.user_id, f"Такой команды нет.", keyboard=keyboard_start)

    def set_info(self, event, keyboard=keyboard_settings):
        self.message_send(event.user_id, f"Текущие настройки поиска:\n"
                                         f"возраст - от {self.age_from} до {self.age_to},\n"
                                         f"пол - {self.check_sex()},\n"
                                         f"cтатус - {self.check_status()}.",
                          keyboard=keyboard)

    def set_age(self, event, config):
        age_dig = re.findall('\d\d', config)
        age_str = re.findall('без ограничений', config)
        if len(age_dig) == 2:
            if int(age_dig[0]) >= 18 and int(age_dig[1]) >= 18:
                self.age_from = age_dig[0]
                self.age_to = age_dig[1]

                self.message_send(event.user_id, f"Ищем партнера от {self.age_from} до {self.age_to}.",
                                  keyboard=keyboard_settings_age)
            else:
                self.message_send(event.user_id, f"Допускается поиск партнера от 18 лет.",
                                  keyboard=keyboard_settings_age)
        elif len(age_str) == 1:
            if age_str[0] == 'без ограничений':
                self.age_from = 18
                self.age_to = 99
                self.message_send(event.user_id, f"Ищем партнера от {self.age_from} до {self.age_to}.",
                                  keyboard=keyboard_settings_age)
            else:
                self.message_send(event.user_id, "Не корректный ввод, попробуйте еще раз.",
                                  keyboard=keyboard_settings_age)
            self.candidate_list = []
        else:
            self.message_send(event.user_id, f"Выберите из списка или напишите свой\n"
                                             f"пример: \n/возраст 18-25",
                              keyboard=keyboard_settings_age)

    def set_sex(self, event, config):
        sex = re.findall('[ЖжМм]', config)
        if len(sex) != 0:
            if sex[0] in ['Ж', 'ж']:
                self.sex = 1
                self.message_send(event.user_id, f"{self.check_sex()}.",
                                  keyboard=keyboard_settings_sex)
            elif sex[0] in ['М', 'м']:
                self.sex = 2
                self.message_send(event.user_id, f"{self.check_sex()}",
                                  keyboard=keyboard_settings_sex)
            else:
                self.message_send(event.user_id, f"Выберете пол партнера из списка.",
                                  keyboard=keyboard_settings_sex)
                self.candidate_list = []
        else:
            self.message_send(event.user_id, f"Выберете пол партнера из списка.",
                              keyboard=keyboard_settings_sex)

    def set_status(self, event, config):
        status = re.findall('холост|в активном поиске', config)
        if len(status) != 0:
            if status[0] == 'холост':
                self.status = 1
                self.message_send(event.user_id, f"Ищем холостых партнеров.",
                                  keyboard=keyboard_settings_status)
            elif status[0] == 'в активном поиске':
                self.status = 6
                self.message_send(event.user_id, f"Ищем партнеров в активном поиске.",
                                  keyboard=keyboard_settings_status)
            else:
                self.message_send(event.user_id, f"Поиск людей с таким статусом не предусмотрен.",
                                  keyboard=keyboard_settings_status)
            self.candidate_list = []
        else:
            self.message_send(event.user_id, f"Выбери статус партнера.",
                              keyboard=keyboard_settings_status)

    def set_clear(self, event, config):
        clear = re.findall('/д@, я пoдтвержд@ю cбpoc/', config)
        if len(clear) != 0:
            if clear[0] == '/д@, я пoдтвержд@ю cбpoc/':
                self.first_start_flag = False

                self.age_from = 1
                self.age_to = 99
                self.sex = 1
                self.status = 6
                self.offset = 0
                self.candidate_list: list = []
                self.candidate: dict = {}

                reset()

                self.message_send(event.user_id, f"Начнем сначала!.",
                                  keyboard=keyboard_start)
            else:
                self.message_send(event.user_id, f"Если вы хотите сбросить все настройки и ",
                                  keyboard=keyboard_settings_clear)
        else:
            self.message_send(event.user_id, f"В результате сброса:\n"
                                             f"- Ваши настройки поиска будут сброшены до значения по умолчанию;\n"
                                             f"- список Ваших фаворитов будет очищен.",
                              keyboard=keyboard_settings_clear)

    def settings(self, event, config):
        conf_ = re.search('информация|возраст|пол|статус|сброс', config)
        if conf_:
            conf = re.findall('информация|возраст|пол|статус|сброс', config)
            if conf[0] == 'информация':
                self.set_info(event)
            elif conf[0] == 'возраст':
                self.set_age(event, config)
            elif conf[0] == 'пол':
                self.set_sex(event, config)
            elif conf[0] == 'статус':
                self.set_status(event, config)
            elif conf[0] == 'сброс':
                self.set_clear(event, config)
            else:
                self.message_send(event.user_id, f"Неизвестная команда.",
                                  keyboard=keyboard_settings)
        else:
            self.message_send(event.user_id, f"Выберите нужные настройки из списка.",
                              keyboard=keyboard_settings)

    def main(self, event, message):
        msg = re.search('\B/.{1,}', message)
        msg_s = re.search('[Нн]астройки', message)
        if msg or msg_s:
            self.settings(event, message)
        else:
            self.start(event, message)

    def handler(self):
        longpoll = VkLongPoll(self.bot)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                create_db()
                msg = event.text.lower()

                self.about_me = tools.get_profile_info(event.user_id)
                self.city_id = self.about_me[0].get('city').get('id')

                if self.first_start_flag is False:
                    self.set_info(event, keyboard_start)
                    self.first_start_flag = True

                self.main(event, msg)
