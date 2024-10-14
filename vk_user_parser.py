import requests
import json
import argparse
import os

def load_config(config_file='config.json'):
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

def get_vk_user_info(user_id=None, result_file='vk_user_info.json'):
    config = load_config()
    access_token = config.get('access_token')
    version = '5.199'  # Версия API

    user_info_url = f'https://api.vk.com/method/users.get'
    user_info_params = {
        'user_ids': user_id,
        'access_token': access_token,
        'v': version
    }
    user_response = requests.get(user_info_url, params=user_info_params)
    user_data = user_response.json()    

    if 'response' not in user_data:
        print('Ошибка при получении информации о пользователе.')
        return

    user = user_data['response'][0]

    followers_url = f'https://api.vk.com/method/users.getFollowers'
    followers_params = {
        'user_id': user['id'],
        'access_token': access_token,
        'v': version
    }
    followers_response = requests.get(followers_url, params=followers_params)
    followers_data = followers_response.json()

    subscriptions_url = f'https://api.vk.com/method/users.getSubscriptions'
    subscriptions_params = {
        'user_id': user['id'],
        'extended': 1,
        'access_token': access_token,
        'v': version
    }
    subscriptions_response = requests.get(subscriptions_url, params=subscriptions_params)
    subscriptions_data = subscriptions_response.json()

    if 'response' in followers_data and followers_data['response']['count'] > 0:
        followers_count = followers_data['response']['count']
    else:
        followers_count = 0

    if 'response' in subscriptions_data and subscriptions_data['response']['count'] > 0:
        subscriptions_count = subscriptions_data['response']['count']
        groups = subscriptions_data['response']['items']
    else:
        subscriptions_count = 0
        groups = []

    result = {
        'user_id': user['id'],
        'user_name': user['first_name'] + ' ' + user['last_name'],
        'followers_count': followers_count,
        'subscriptions_count': subscriptions_count,
        'groups': groups
    }

    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print(f'Информация о пользователе сохранена в {result_file}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Получение информации о пользователе ВК')
    parser.add_argument('--user_id', type=str, help='Идентификатор пользователя ВК')
    parser.add_argument('--result_file', type=str, default='vk_user_info.json', help='Путь к файлу результата')

    args = parser.parse_args()
    get_vk_user_info(user_id=args.user_id, result_file=args.result_file)
