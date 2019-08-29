import requests
import os


def get_new_comics():
    url = 'https://xkcd.com/info.0.json'
    response_json = requests.get(url).json()
    img_link = response_json['img']
    filename = img_link.split('/')[-1]
    with open(filename, 'wb') as file:
            file.write(requests.get(img_link).content)

if __name__ == '__main__':
    get_new_comics()
    # print('Download from {}'.format(get_new_comics()))
