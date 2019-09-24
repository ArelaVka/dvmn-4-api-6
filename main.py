import requests
import os
import random
import sys
from dotenv import load_dotenv


def get_new_comics():
    url = 'https://xkcd.com/info.0.json'
    if not requests.get(url).ok:
        sys.exit('xkcd.com not allowed')
    max_num = requests.get(url).json()['num']
    download_num = random.randint(1, max_num)
    url = 'https://xkcd.com/{}/info.0.json'.format(str(download_num))
    response = requests.get(url).json()
    img_link = response['img']
    filename = img_link.split('/')[-1]
    img_data = requests.get(img_link)
    img_data.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(img_data.content)
    caption = response['alt']
    return filename, caption


def get_uploaded_photo_params(filename):
    method = 'photos.getWallUploadServer'
    url = 'https://api.vk.com/method/' + method
    payload = {'access_token': TOKEN,
               'v': '5.101'}
    response = requests.get(url, params=payload).json()
    first_field = list(response.keys())[0]
    if first_field == 'error':
        error_message = response['error']['error_msg']
        sys.exit(method + ': ' + error_message)
    upload_url = response['response']['upload_url']
    image_file_descriptor = open(filename, 'rb')
    request = requests.post(upload_url, files={'photo': image_file_descriptor})
    server, photo, hash_value = request.json().values()
    image_file_descriptor.close()
    os.remove(filename)
    return server, photo, hash_value


def get_saved_photo_id(server, photo, hash_value):
    method = 'photos.saveWallPhoto'
    url = 'https://api.vk.com/method/' + method
    payload = {'access_token': TOKEN,
               'v': '5.101',
               'server': server,
               'photo': photo,
               'hash': hash_value}
    result = requests.post(url, params=payload).json()
    first_field = list(result.keys())[0]
    if first_field == 'error':
        error_message = result['error']['error_msg']
        sys.exit(method + ': ' + error_message)
    return result['response'][0]['id']


def upload_wall_post(message, attachments):
    method = 'wall.post'
    url = 'https://api.vk.com/method/' + method
    payload = {'access_token': TOKEN,
               'v': '5.101',
               'owner_id': '-' + GROUP_ID,
               'from_group': '1',
               'message': message,
               'attachments': attachments}
    result = requests.post(url, params=payload).json()
    first_field = list(result.keys())[0]
    if first_field == 'error':
        error_message = result['error']['error_msg']
        sys.exit(method + ': ' + error_message)


def main():
    filename, caption = get_new_comics()
    server, photo, hash_value = get_uploaded_photo_params(filename)
    attachments = 'photo2094408_{}'.format(get_saved_photo_id(server, photo, hash_value))
    upload_wall_post(caption, attachments)


if __name__ == '__main__':
    load_dotenv()
    GROUP_ID = os.getenv('GROUP_ID')
    TOKEN = os.getenv('TOKEN')
    main()
