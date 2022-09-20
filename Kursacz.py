import requests
from tqdm import trange
import json


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def get_profile_photo(self):
        profile_photo_url = self.url + 'photos.get'
        profile_photo_params = {
            'extended': '1',
            'album_id': 'profile',
        }
        res = requests.get(profile_photo_url, params={**self.params, **profile_photo_params}).json()
        downloads_list = []
        for photo in res['response']['items']:
            download_dict = {}
            name = str(photo['likes']['count'])
            url = photo['sizes'][-1]['url']
            download_dict['url'] = url
            download_link = requests.get(url)
            download_dict['photo'] = download_link
            for el in downloads_list:
                if name == el['name']:
                    name += '_' + str(photo['date'])
            download_dict['name'] = name
            download_dict['status'] = 'Ready to upload'
            downloads_list.append(download_dict)
        return downloads_list


class YaUser:
    def __init__(self, token):
        self.token = token
        self.headers = {'Content_Type': 'aplication/json',
                       'Authorization': 'OAuth {}'.format(self.token)}

    def create_folder(self, folder_name):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.headers
        params = {'path': folder_name}
        res = requests.get(url, params=params, headers=headers)
        if res.status_code == 404:
            res = requests.put(url, params=params, headers=headers)
            print('Folder created!')
        elif res.status_code == 200:
            print('Folder already created!')

    def upload_vk_foto(self, photos_list, folder_name, photos_amount):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.headers
        i = 0
        data = []
        for photo in trange(photos_amount, desc='Loading'):
                el = photos_list[i]
                d = {}
                d['name'] = el['name']
                d['url'] = el['url']
                params = {'path': '{}/{}.jpg' .format(folder_name, el['name']), 'overwrite': 'true'}
                page = requests.get(url, params=params, headers=headers).json()
                href = page.get('href', '')
                response = requests.put(href, data=el['photo'])
                response.raise_for_status()
                if response.status_code == 201:
                    d['status'] = 'Successful upload'
                else:
                    d['status'] = 'Upload denied'
                data.append(d)
                i += 1
        with open('C:/My_Homeworks_for_Netology/Kursach/data.txt', 'w') as outfile:
            json.dump(data, outfile)


if __name__ == "__main__":
    with open('C:/My_Homeworks_for_Netology/Kursach/VKtoken.txt') as file_obj:
        VK_token = file_obj.read().strip()
    with open('C:/My_Homeworks_for_Netology/Kursach/YAtoken.txt') as file_obj:
        YA_token = file_obj.read().strip()

    vk_client = VkUser(VK_token, '5.131')
    photos = vk_client.get_profile_photo()
    ya_user = YaUser(YA_token)
    folder = 'VK_photos'
    ya_user.create_folder(folder)
    ya_user.upload_vk_foto(photos, folder, 3)
    