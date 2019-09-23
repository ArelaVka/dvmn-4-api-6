import requests
import os
import random
import sys
from dotenv import load_dotenv

load_dotenv()

group_id = os.getenv('GROUP_ID')
token = os.getenv('TOKEN')
vk_api_method = 'https://api.vk.com/method/'


def get_new_comics():
    url = 'https://xkcd.com/info.0.json'
    if not requests.get(url).ok:
        sys.exit('xkcd.com not allowed')
    response_json = requests.get(url).json()
    max_num = response_json['num']
    download_num = random.randint(1, max_num)
    url = 'https://xkcd.com/' + str(download_num) + '/info.0.json'
    response_json = requests.get(url).json()
    img_link = response_json['img']
    filename = img_link.split('/')[-1]
    response = requests.get(img_link)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)
    caption = response_json['alt']
    return filename, caption


def get_uploaded_photo_params(filename):
    method = 'photos.getWallUploadServer'
    url = '{}{}?access_token={}&v=5.101'.format(vk_api_method, method, token)
    response = requests.get(url)
    response_dict = response.json()
    first_field = list(response_dict.keys())[0]
    if first_field == 'error':
        error_message = response_dict['error']['error_msg']
        sys.exit(method + ': ' + error_message)
    response.raise_for_status()
    upload_url = response.json()['response']['upload_url']
    image_file_descriptor = open(filename, 'rb')
    request = requests.post(upload_url, files={'photo': image_file_descriptor})
    server, photo, hash = request.json().values()
    image_file_descriptor.close()
    os.remove(filename)
    return server, photo, hash


def get_saved_photo_id(server, photo, hash):
    method = 'photos.saveWallPhoto'
    url = '{}{}?access_token={}&v=5.101&server={}&photo={}&hash={}'.format(vk_api_method, method, token, server, photo,
                                                                           hash)
    response_post = requests.post(url)
    result = response_post.json()
    first_field = list(result.keys())[0]
    if first_field == 'error':
        error_message = result['error']['error_msg']
        sys.exit(method + ': ' + error_message)
    return result['response'][0]['id']


def upload_wall_post(message, attachments):
    method = 'wall.post'
    url = '{}{}?access_token={}&v=5.101&owner_id=-{}&from_group=1&message={}&attachments={}'.format(vk_api_method,
                                                                                                    method,
                                                                                                    token,
                                                                                                    group_id,
                                                                                                    message,
                                                                                                    attachments)
    result = requests.post(url).json()
    first_field = list(result.keys())[0]
    if first_field == 'error':
        error_message = result['error']['error_msg']
        sys.exit(method + ': ' + error_message)


if __name__ == '__main__':
    filename, caption = get_new_comics()
    server, photo, hash = get_uploaded_photo_params(filename)
    attachments = 'photo2094408_{}'.format(get_saved_photo_id(server, photo, hash))
    upload_wall_post(caption, attachments)
