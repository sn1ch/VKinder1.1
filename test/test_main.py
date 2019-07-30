import unittest
from unittest.mock import patch
from VKinder.main import VK
import vk
import time


class Test_VKinder(unittest.TestCase):
    def setUp(self):
        with open('fixture/token.txt', 'r', encoding='UTF-8') as f:
            token = f.read()
        session = vk.Session(access_token=token)
        self.api = vk.API(session)
        self.user_id = 17820325
        self.user_info = self.api.users.get(v='5.101', user_ids=self.user_id,
                                            fields='interests, sex, city, books, music')
        time.sleep(0.34)
        self.fake_user_info = ['try', 'la', 2]
        self.break_api = 'not session'

    @patch('builtins.input', lambda *args: 'sn1ch')
    def test_get_user_id(self):
        time.sleep(0.34)
        self.assertEqual(VK.get_user_id(self, self.api), 17820325)

    @patch('builtins.input', lambda *args: 'any string')
    def test_set_age_for_search_not_number_input(self):
        with self.assertRaises(ValueError):
            VK.set_age_for_search(self)

    def test_get_user_info_user_if_api_is_breack(self):
        time.sleep(0.34)
        with self.assertRaises(AttributeError):
            VK.get_user_info(self, self.break_api, self.user_id)

    @patch('builtins.input', lambda *args: 'string11111')
    def test_set_city_for_search_whith_incorrect_input(self):
        time.sleep(0.34)
        with self.assertRaises(IndexError):
            VK.set_city_for_search(self, self.api, self.user_info)

    def test_set_sex_for_search(self):
        time.sleep(0.34)
        self.assertEqual(VK.set_sex_for_search(self, self.user_info), 1)

    def test_get_interests(self):
        with self.assertRaises(TypeError):
            VK.get_interests(self, self.fake_user_info)

    def test_get_groups(self):
        self.assertGreater(VK.get_groups(self, self.api, self.user_id), [1])

    def test_search_incorrect_age_line(self):
        time.sleep(0.34)
        self.assertNotEqual(VK.search(self, self.api, city=1, sex=1, age_line=[18, 9]), [1])

    def test_count_groups_match_points(self):
        self.assertDictEqual(VK.count_groups_match_points(self, self.api, users_list=[1, 2]), {1: 0})

    def test_count_interests_match_points(self):
        self.assertDictEqual(VK.count_interests_match_points(self, self.api, users_list=[1, 2], filter_interests=[]),
                             {1: 0})

    def test_count_total_match_points(self):
        self.assertListEqual(VK.count_total_match_points(self, interests_matches={1: 0}, group_matches={1: 0, 2: 0}),
                             [(1, 0), (2, 0)])

    def test_get_top10_users(self):
        with self.assertRaises(NameError):
            VK.get_top10_users(self, total_match_points={1: 0})

    def test_get_photos(self):
        self.assertListEqual(VK.get_photos(self, self.api, top10_users=[17820325]),
                             [{'id': 17820325, 'first_name': 'Сергей', 'last_name': 'Курочкин',
                               'url': ['https://pp.userapi.com/c604729/v604729325/31f98/wZygqHowo3E.jpg',
                                       'https://pp.userapi.com/c824409/v824409121/6bb15/WeHXY_27YuM.jpg']}
                              ])


if __name__ == '__main__':
    unittest.main()
