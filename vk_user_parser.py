import requests
import json
import argparse
import os
import logging

logger = logging.getLogger(__name__)


def get_vk_user_info(vk_api, neo4j_handler, user_id, level=2):
    logger.info(f'Получаем информацию для пользователя {user_id}')
    

    user_info_url = f'https://api.vk.com/method/users.get'
    user_info_params = {
        'user_ids': user_id,
        'fields': 'city,sex,screen_name',
        'access_token': vk_api['access_token'],
        'v': vk_api['version']
    }
    user_response = requests.get(user_info_url, params=user_info_params)
    user_data = user_response.json()    

    if len(user_data['response']) == 0:
        logger.error(f"Ошибка получения информации о пользователе, ответ пустой: {user_response.text}")
        return

    user = user_data['response'][0]

    user_dict = {
        'id': user['id'],
        'name': user['first_name'] + ' ' + user['last_name'],
        'screen_name': user.get('screen_name', ''),
        'sex': user.get('sex', ''),
        'city': user.get('city', {}).get('title', '') if user.get('city') else ''
    }
    logger.info(f"Текущий пользователь: {user_dict}")
    neo4j_handler.create_user(user_dict)

    followers_url = f'https://api.vk.com/method/users.getFollowers'
    followers_params = {
        'user_id': user['id'],
        'access_token': vk_api['access_token'],
        'v': vk_api['version']
    }

    followers_response = requests.get(followers_url, params=followers_params)
    followers_data = followers_response.json()
    followers = followers_data.get('response', {}).get('items', [])

    subscriptions_url = f'https://api.vk.com/method/users.getSubscriptions'
    subscriptions_params = {
        'user_id': user['id'],
        'extended': 1,
        'access_token': vk_api['access_token'],
        'v': vk_api['version']
    }

    subscriptions_response = requests.get(subscriptions_url, params=subscriptions_params)
    subscriptions_data = subscriptions_response.json()
    groups = subscriptions_data.get('response', {}).get('items', [])

    for follower in followers:
        logger.info(f"Фолловеры пользователя {user_id}: {follower}")
        neo4j_handler.create_follow_relationship(follower, user['id'])
        if level > 1:
            get_vk_user_info(vk_api, neo4j_handler, follower, level - 1)

    for group in groups:
        # Некоторые страницы считаются группами, поэтому их нужно пропустить
        if group['type'] == 'profile':
            continue

        group_data = {
            'id': group['id'],
            'name': group['name'],
            'screen_name': group.get('screen_name', '')
        }
        neo4j_handler.create_group(group_data)
        neo4j_handler.create_subscribe_relationship(user['id'], group['id'])
    
