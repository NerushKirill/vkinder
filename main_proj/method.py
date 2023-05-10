import vk_api
from vk_api.exceptions import ApiError

from config import ACCESS_TOKEN


class VkTools:

    def __init__(self, token):
        self.ext_api = vk_api.VkApi(token=token)

    def get_profile_info(self, user_id):
        try:
            info_ = self.ext_api.method('users.get', {'user_id': user_id,
                                                      'fields': 'bdate, city, sex',
                                                      })
        except ApiError:
            return

        return info_

    def user_search(self, city_id, age_from, age_to, sex, status, offset=None):
        try:
            profeles = self.ext_api.method('users.search', {'city_id': city_id,
                                                            'age_from': age_from,
                                                            'age_to': age_to,
                                                            'sex': sex,
                                                            'status': status,
                                                            'count': 10,
                                                            'offset': offset,
                                                            })
        except ApiError:
            return

        profeles = profeles['items']
        result = []
        for profele in profeles:
            if profele['is_closed'] is False:
                result.append({'name': profele['first_name'] + ' ' + profele['last_name'],
                               'id': profele['id'],
                               })
        return result

    def photos_get(self, user_id):
        photos = self.ext_api.method('photos.get', {'album_id': 'profile',
                                                    'owner_id': user_id,
                                                    'extended': 1,
                                                    })
        try:
            photos = photos['items']
        except KeyError:
            return

        result = []
        for num, photo in enumerate(photos):
            result.append({'owner_id': photo['owner_id'],
                           'id': photo['id'],
                           'likes': photo['likes']['count'],
                           'comments': photo['comments']['count']
                           })

        result.sort(key=lambda dictionary: (dictionary['likes'], dictionary['comments']), reverse=True)
        return result[:3]


tools = VkTools(ACCESS_TOKEN)
