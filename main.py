from pprint import pprint
from urllib.parse import urlencode
import time
import json
import vk
import operator
from collections import Counter
from pymongo import MongoClient
from bson import json_util


class VK:
    def get_token(self):
        VK_API = 7054934
        BASE_URL = 'https://oauth.vk.com/authorize'
        authorization = {
            'client_id': VK_API,
            'display': 'popup',
            'scope': 'friends, groups',
            'response_type': 'token',
            'v': '5.101'
        }
        pprint('?'.join((BASE_URL, urlencode(authorization))))
        token = input('Вставьте сюда access_token: ')
        self.token = token
        session = vk.Session(access_token=self.token)
        api = vk.API(session)
        return api

    def get_user_id(self, api):
        user_id = None
        user = input('Введите ID или коротий адрес страницы: ')
        while user_id == None:
            try:
                user_info = api.users.get(v='5.101', user_ids=user)
                user_id = user_info[0]['id']
            except vk.exceptions.VkAPIError:
                print('Такого пользователя не существует!')
                user = input('Введите ID или коротий адрес страницы: ')
        return user_id

    def set_age_for_search(self):
        age_line = []
        age_from, age_to = map(str, input(
            'Введите через пробел возраст ОТ которого и ДО которого искать: ').split())
        age_line.append(int(age_from))
        age_line.append(int(age_to))
        return age_line

    def get_user_info(self, api, user_id):
        user_info = api.users.get(v='5.101', user_ids=user_id, fields='interests, sex, city, books, music')
        return user_info

    def set_city_for_search(self, api, user_info):
        try:
            city = user_info[0]['city']['id']
        except KeyError:
            city_input = input('В каком городе будем искать: ')
            city = api.database.getCities(v='5.101', country_id=1, q=city_input)
            city = city['items'][0]['id']
        return city

    def set_sex_for_search(self, user_info):
        if user_info[0]['sex'] == 1:
            sex = 2
        elif user_info[0]['sex'] == 2:
            sex = 1
        else:
            print('Какой пол будем искать? Введите 1 если женский и 2 если мужской')
            sex_input = input()
            sex = int(sex_input)
        return sex

    def get_interests(self, user_info):
        interests = \
            (user_info[0]['music'] + ' ' + user_info[0]['interests'] + ' ' + user_info[0]['books'])\
                .replace(',', '').split(' ')
        filter_interests = [item for item in interests if item != '']
        return filter_interests

    def get_groups(self, api, user_id):
        groups_response = api.groups.get(v='5.101', user_id=user_id)
        groups = groups_response['items']
        return groups

    def search(self, api, city, sex, age_line):
        res = api.users.search(v='5.101', city=city, sex=sex, age_from=age_line[0], age_to=age_line[1])
        print('...')
        offset = 0
        users_list = []
        while offset < res['count']:
            try:
                users = api.users.search(v='5.101', city=city, sex=sex, age_from=age_line[0], age_to=age_line[1],
                                         count=1000, offset=offset)
                print('...')
            except vk.exceptions.VkAPIError:
                time.sleep(1)
                continue
            for user in users['items']:
                users_list.append(user['id'])
            offset += 1000
        return users_list

    def count_groups_match_points(self, api, users_list):
        group_matches = {}
        for id in users_list:
            try:
                groups = api.groups.get(v='5.101', user_id=str(id))
                print('...')
                group_matches[id] = len(set(groups).intersection(set(groups['items'])))
            except vk.exceptions.VkAPIError:
                print('...ops')
                time.sleep(1)
                continue
        group_matches = sorted(group_matches.items(), key=operator.itemgetter(1), reverse=True)
        group_matches = dict(group_matches)
        return group_matches

    def count_interests_match_points(self, api, users_list, filter_interests):
        interests_matches = {}
        for id in users_list:
            try:
                user = api.users.get(v='5.101', user_id=str(id), fields='interests, books, music')
                print('...')
                time.sleep(0.34)
                try:
                    interests = \
                        (user[0]['music'] + ' ' + user[0]['interests'] + ' ' + user[0]['books']) \
                            .replace(',', '').split(' ')
                    interests_filter = [item for item in interests if item != '']
                except KeyError:
                    continue
                except vk.exceptions.VkAPIError:
                    time.sleep(1)
                interests_matches[id] = len(set(filter_interests).intersection(set(interests_filter)))
            except vk.exceptions.VkAPIError:
                print('...ops')
                time.sleep(1)
                continue
        interests_matches = sorted(interests_matches.items(), key=operator.itemgetter(1), reverse=True)
        interests_matches = dict(interests_matches)
        return interests_matches

    def count_total_match_points(self, interests_matches, group_matches):
        groups_and_interests_match = (interests_matches, group_matches)
        total_match_points = Counter()
        for item in groups_and_interests_match:
            total_match_points.update(item)
        total_match_points = dict(total_match_points)
        total_match_points = sorted(total_match_points.items(), key=operator.itemgetter(1), reverse=True)
        return total_match_points

    def get_top10_users(self, total_match_points):
        top10_users = []
        for user in total_match_points:
            try:
                for id in skip_ids.find_one()['ID']:
                    if user[0] != id and len(top10_users) != 10 and user[0] not in top10_users:
                        top10_users.append(user[0])
                        skip_ids.update_one({'ID': skip_ids.find_one()['ID']}, {'$push': {'ID': user[0]}})
            except TypeError:
                skip_ids.insert_one({'ID': [0]})
                continue
        return top10_users

    def get_photos(self, api, top10_users):
        to_write = []
        for id in top10_users:
            top_likes_list = []
            photo = api.photos.get(v='5.101', owner_id=id, album_id='profile', extended='likes')
            time.sleep(0.34)
            user = api.users.get(v='5.101', user_ids=id)
            print('...photo')
            time.sleep(0.34)
            top_3_photo = []
            for i in photo['items']:
                top_likes_list.append(i['likes']['count'])
                top_likes_list.sort(reverse=True)
            for i in photo['items']:
                if i['likes']['count'] in top_likes_list[:3]:
                    top_3_photo.append(i['sizes'][-1]['url'])
            to_write.append({'id': id, 'first_name': user[0]['first_name'], 'last_name': user[0]['last_name'],
                             'url': top_3_photo})
        return to_write

    def write_top10users(self, to_write):
        with open('data/top10users.json', 'w', encoding='utf-8') as file:
            json.dump(to_write, file, ensure_ascii=False, indent=2)
        with open('data/top10users.json', 'r', encoding='utf-8') as file:
            data = json_util.loads(file.read())
            top10_users_mongo.insert_one({'users': data})
            print(data)


if __name__ == '__main__':
    client = MongoClient()
    VK_db = client['VK_db']
    skip_ids = VK_db['skip_ids']
    top10_users_mongo = VK_db['top10users']

    user = VK()
    api = user.get_token()
    user_id = user.get_user_id(api)
    age_line = user.set_age_for_search()
    user_info = user.get_user_info(api, user_id)
    city = user.set_city_for_search(api, user_info)
    sex = user.set_sex_for_search(user_info)
    interests = user.get_interests(user_info)
    groups = user.get_groups(api, user_id)
    users_list = user.search(api, city, sex, age_line)
    group_matches = user.count_groups_match_points(api, users_list)
    interests_matches = user.count_interests_match_points(api, users_list, interests)
    total_match_points = user.count_total_match_points(interests_matches, group_matches)
    top10_users = user.get_top10_users(total_match_points)
    photos = user.get_photos(api, top10_users)
    user.write_top10users(photos)