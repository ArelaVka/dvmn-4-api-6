import requests
import os
import random
from dotenv import load_dotenv

VK_API_URL = 'https://api.vk.com/method/'
VK_API_VERSION = '5.101'


def get_new_comics():
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    max_num = response.json()['num']
    download_num = random.randint(1, max_num)
    url = 'https://xkcd.com/{}/info.0.json'.format(str(download_num))
    response = requests.get(url)
    response.raise_for_status()
    response_data = response.json()
    img_link = response_data['img']
    filename = img_link.split('/')[-1]
    img_data = requests.get(img_link)
    with open(filename, 'wb') as file:
        file.write(img_data.content)
    caption = response_data['alt']
    return filename, caption


def check_vk_response(response):
    if 'error' in response:
        raise requests.HTTPError(response['error']['error_msg'])


def get_uploaded_photo_params(token, filename):
    method = 'photos.getWallUploadServer'
    url = VK_API_URL + method
    payload = {'access_token': token,
               'v': VK_API_VERSION}
    response = requests.get(url, params=payload).json()
    check_vk_response(response)
    upload_url = response['response']['upload_url']
    with open(filename, 'rb') as image_file_descriptor:
        upload_response = requests.post(upload_url, files={'photo': image_file_descriptor}).json()
        server = upload_response['server']
        photo = upload_response['photo']
        hash_value = upload_response['hash']
        image_file_descriptor.close()
        os.remove(filename)
        return server, photo, hash_value


def get_saved_photo_id(token, server, photo, hash_value):
    method = 'photos.saveWallPhoto'
    url = VK_API_URL + method
    payload = {'access_token': token,
               'v': VK_API_VERSION,
               'server': server,
               'photo': photo,
               'hash': hash_value}
    response = requests.post(url, params=payload).json()
    check_vk_response(response)
    return response['response'][0]['id']


def upload_wall_post(token, group_id, message, attachments):
    method = 'wall.post'
    url = VK_API_URL + method
    payload = {'access_token': token,
               'v': VK_API_VERSION,
               'owner_id': '-' + group_id,
               'message': message,
               'attachments': attachments}
    response = requests.post(url, params=payload).json()
    check_vk_response(response)


def main():
    token = os.getenv('TOKEN')
    group_id = os.getenv('GROUP_ID')
    filename, caption = get_new_comics()
    server, photo, hash_value = get_uploaded_photo_params(token, filename)
    attachments = 'photo2094408_{}'.format(get_saved_photo_id(token, server, photo, hash_value))
    upload_wall_post(token, group_id, caption, attachments)


if __name__ == '__main__':
    load_dotenv()
    main()
