from bs4 import BeautifulSoup
import requests
import lxml
from bd import add_products, close_db, add_category_stats
from urllib.parse import urljoin
from datetime import datetime
import math
import time

HEADERS = {"User-Agent": "Mozilla/5.0"}


base_url='https://mi-shop.com/catalog/audio/'

response = requests.get(base_url)
soup = BeautifulSoup(response.text, 'lxml')
today = datetime.now().strftime("%Y-%m-%d") # сегодняшняя дата
container = soup.select_one("div.page-content__subtitle-catalog span")
text = container.get_text(strip=True).split()
product_count = int(text[0])# количество товаров
product_for_pages = 12
count_pages = math.ceil(product_count / product_for_pages)




def fetch(url):
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'lxml')
    tag_url = soup.select(".b-product-card.js-stats-box.js-mi-autoheight-section-item")
    urls = ["https://mi-shop.com" + link.get("href") for link in tag_url]
    return urls


def scroll_page():
    tasks = []
    for page in range(1, count_pages + 1): 
        if page == 1:
            url = base_url
        else:
            url = f"https://mi-shop.com/catalog/audio/?PAGEN_1={page}"
        tasks.extend(fetch(url))
    return tasks



def fetch1(url):
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        name = (soup.select_one(".b-product-info__title.b-product-info__title--compare"))
        price = (soup.select_one(".b-product-info__price-new"))
        img_tag = (soup.select_one("div.b-slider-images picture img"))
        if img_tag and img_tag.has_attr("src"):
            img_url = urljoin(url, img_tag["src"])
            image = requests.get(img_url).content
        else:
            image = "Нет картинки"
        article_tag = (soup.select_one(".b-article"))
        color = (soup.select_one(".b-product-info__stat-color.is-active img"))
        name = name.get_text(strip=True)
        price = price.get_text(strip=True) if price else "Нет в наличие"
        article = ''.join(filter(str.isdigit, article_tag.get_text(strip=True))) if article_tag else "000000"
        color = color['alt'] if color else "ERORR"
        return (name, price, image, color, article)
    except Exception as e:
        print(f"Error: {e}")
        

def main1(urls): 
    tasks = []
    for url in urls:
        task = fetch1(url)
        if task:
            tasks.append(task)
    return tasks



def main_sync():
    start_time = time.time()
    entry_id = add_category_stats(today, product_count)
    urls = scroll_page()
    results = main1(urls)
    add_products(entry_id, results)
    close_db()
    end_time = time.time()
    time_work = end_time - start_time
    print(f"Парсинг занял: {time_work:.2f} секунд")

