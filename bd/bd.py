from pymongo import MongoClient


def start_bd():
    client = MongoClient()
    VK_db = client['VK_db']
    skip_ids = VK_db['skip_ids']
    top10_users_mongo = VK_db['top10users']
    skip_ids.insert_one({'ID': [0]})
    return skip_ids, top10_users_mongo


def get_skip_ids_list(skip_ids):
    skip_ids_list = skip_ids.find_one()['ID']
    return skip_ids_list


def write_users_in_skip_id_bd(top10_users, skip_ids):
    for id in top10_users:
        skip_ids.update_one({'ID': skip_ids.find_one()['ID']}, {'$push': {'ID': id}})


def write_top10users_bd(data, top10_users_mongo):
    top10_users_mongo.insert_one({'users': data})
