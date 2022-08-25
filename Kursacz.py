import requests
from pprint import pprint


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def get_profile_photo(self):
        get_profile_photo_url = self.url + 'photos.get'
        get_profile_photo_params = {
            'extended': '1',
            'album_id': 'profile',
        }
        res = requests.get(get_profile_photo_url, params={**self.params, **get_profile_photo_params})
        downloads_list = []
        for photo in res.json()['response']['items']:
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
            downloads_list.append(download_dict)
        return downloads_list


class YaUser:
    def __init__(self, token):
        self.token = token

    def upload_vk_foto(self, photos_list):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        for el in photos_list:
            headers = {'Content_Type': 'aplication/json',
                       'Authorization': 'OAuth {}'.format(self.token)}
            params = {'path': 'HT_for_Netology/{}.jpg' .format(el['name']), 'overwrite': 'true'}
            page = requests.get(url, params=params, headers=headers).json()
            href = page.get('href', '')
            response = requests.put(href, data=el['photo'])
            response.raise_for_status()
            if response.status_code == 201:
                el['status'] = 'Saving successful'
        return photos_list


# Введите соответствующие токены в файлы "Yaoktoken.txt" и "VKtoken.txt"
if __name__ == '__main__':
    with open('VKtoken.txt', 'r') as file_obj:
        VK_token = file_obj.read().strip()
    with open('YAtoken.txt', 'r') as file_obj:
        YA_token = file_obj.read().strip()

    vk_client = VkUser(VK_token, '5.131')
    photos = vk_client.get_profile_photo()
    ya_client = YaUser(YA_token)
    ya_client.upload_vk_foto(photos)
    pprint(photos)
