import requests
from bs4 import BeautifulSoup
import os
import time
from dotenv import load_dotenv
import sqlite3
import re
from database import *

load_dotenv()  # Включение библиотеки
URL = os.getenv('URL')
HOST = os.getenv('HOST')
HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
}

class CategoryParser:
    def __init__(self, url, name, category_id, pages=3, download=False):
        self.url = url
        self.name = name
        self.category_id = category_id
        self.pages = pages
        self.download = download

    def get_html(self, i):  # 3
        html = requests.get(self.url + f'/page{i}', headers=HEADER).text
        return html

    def get_soup(self, i):  # 2
        html = self.get_html(i)
        soup = BeautifulSoup(html, 'html.parser')
        return soup

    def get_data(self):
        for i in range(1, self.pages + 1):
            soup = self.get_soup(i)  # 1
            images_blocks = soup.find_all('a', class_='wallpapers__link')
            time.sleep(5)
            for block in images_blocks:

                try:
                    time.sleep(5)
                    image_link = block.find('img', class_='wallpapers__image').get('src')
                    #print(image_link)
                    '''Вариант №1 заменяем 300х168 на 1920х1080'''
                    image_link_v1 = image_link.replace('300x168', '1920x1080')
                    #print(image_link_v1)
                    '''Вариант №2 заменяем'''
                    info = block.find('span', class_='wallpapers__info').get_text(strip=True)
                    image_link_v2 = image_link.replace('300x168', re.search(r'\d{4}x\d{3}', info)[0])
                    #print(image_link_v2)
                    '''Вариант №3 заменяем'''
                    wallpapers_link = HOST + block.get('href')
                    wallpapers_html = requests.get(wallpapers_link, headers=HEADER).text
                    wallpapers_soup = BeautifulSoup(wallpapers_html, 'html.parser')
                    resolution = wallpapers_soup.find_all('span', class_='wallpaper-table__cell')[1].get_text(strip=True)
                    image_link_v3 = image_link.replace('300x168', resolution)
                    print(image_link_v3)
                    save_to_db(image_link_v3, self.category_id)

                    if self.download:
                        if self.name not in os.listdir():
                            os.mkdir(str(self.name))
                        response_image = requests.get(image_link_v3, headers=HEADER).content
                        # https://images.wallpaperscraft.ru/image/single/polet_shar_nebo_86980_1920x1080.jpg
                        image_name = image_link_v3.split('/')[-1]
                        with open(f'{self.name}/{image_name}', mode='wb') as file:
                            file.write(response_image)

                except:
                    print('Не могу открыть...........')



def parsing():
    html = requests.get(URL).text
    soup = BeautifulSoup(html, 'html.parser')
    block = soup.find('ul', class_='filters__list')
    filters = block.find_all('a', class_='filter__link')
    for f in filters:
        filter_link = HOST + f.get('href')
        name = f.get_text(strip=True)
        true_name = re.search(r'[3]*[A-Za-zА-Яа-я-]+', name)[0]
        pages = int(re.search(r'[0-9][0-9]+', name)[0]) // 15
        category_id = insert_or_ignore(true_name)
        parser = CategoryParser(url=filter_link, name=true_name, category_id=category_id, pages=pages)
        parser.get_data()


parsing()
