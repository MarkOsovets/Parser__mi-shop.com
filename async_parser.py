from bs4 import BeautifulSoup
import requests
import lxml
#from selenium import webdriver
#from selenium.webdriver.common.by import By
#from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.common.action_chains import ActionChains
import aiohttp
import asyncio
from bd import add_products, close_db, add_category_stats
from urllib.parse import urljoin
from datetime import datetime
import math
import time


#chrome_path = "/usr/bin/google-chrome-stable"

HEADERS = {"User-Agent": "Mozilla/5.0"}

#options = Options()
#options.binary_location = chrome_path
#options.add_experimental_option("prefs", {
#    "profile.managed_default_content_settings.images": 2
#    "profile.managed_default_content_settings.stylesheet": 2,
#    "profile.managed_default_content_settings.geolocation":2,
#    "profile.managed_default_content_settings.javascript": 1 # 1 - разрешить, 2 - блокировать
#    "profile.managed_default_content_settings.media_stream": 2,
#})


base_url='https://mi-shop.com/catalog/audio/'
#browser = webdriver.Chrome(options=options)
#browser.get(url)



response = requests.get(base_url, headers=HEADERS)
soup = BeautifulSoup(response.text, 'lxml')
today = datetime.now().strftime("%Y-%m-%d") # сегодняшняя дата
container = soup.select_one("div.page-content__subtitle-catalog span")
text = container.get_text(strip=True).split()
product_count = int(text[0])# количество товаров
product_for_pages = 12
count_pages = math.ceil(product_count / product_for_pages)




async def fetch(session, url):
    async with session.get(url=url, headers=HEADERS) as response:
        soup = BeautifulSoup(await response.text(), 'lxml')
        tag_url = soup.select(".b-product-card.js-stats-box.js-mi-autoheight-section-item")
        urls = ["https://mi-shop.com" + link.get("href") for link in tag_url]
        return urls


async def scroll_page():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for page in range(1, count_pages + 1): 
            if page == 1:
                url = base_url
            else:
                url = f"https://mi-shop.com/catalog/audio/?PAGEN_1={page}"
            tasks.append(asyncio.create_task(fetch(session, url)))
        res = await asyncio.gather(*tasks)
    flat_urls = sum(res, [])  # Объединяем вложенные списки
    return flat_urls



#def scroll_page(browser):
#    while True: 
#        try:  
#            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#            time.sleep(2)
#            tag_url = browser.find_elements(By.CSS_SELECTOR, ".b-product-card.js-stats-box.js-mi-autoheight-section-item") 
#            urls = [link.get_attribute("href") for link in tag_url]
#            element = browser.find_element(By.CSS_SELECTOR, ".btn.btn--white.b-catalog__btn")
#           time.sleep(0.5)
#           ActionChains(browser).move_to_element(element).click().perform()
#            time.sleep(2)
#        except NoSuchElementException:
#            return urls        
    #browser.quit()


async def fetch1(session, url):
    async with session.get(url=url, headers=HEADERS) as response:
        soup = BeautifulSoup(await response.text(), 'lxml')
        try:
            name = (soup.select_one(".b-product-info__title.b-product-info__title--compare"))
            price = (soup.select_one(".b-product-info__price-new"))
            img_tag = (soup.select_one("div.b-slider-images picture img"))
            if img_tag and img_tag.has_attr("src"):
                img_url = urljoin(url, img_tag["src"])
                async with session.get(img_url) as img_response:
                    image = await img_response.read()
            else:
                image = "Нет картинки"
            article_tag = (soup.select_one(".b-article"))
            color = (soup.select_one(".b-product-info__stat-color.is-active img"))
            name = name.get_text(strip=True)
            price = price.get_text(strip=True) if price else "Нет в наличие"
            article = ''.join(filter(str.isdigit, article_tag.get_text(strip=True))) if article_tag else "00000"
            color = color['alt'] if color else "error"
            return (name, price, image, color, article)
        except Exception as e:
            print(f"Error: {e}")
        

async def main1(urls): 
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = asyncio.create_task(fetch1(session, url))
            tasks.append(task)
        res = await asyncio.gather(*tasks)
    return res



def main_async():
    start_time = time.time()
    #global browser
    entry_id = add_category_stats(today, product_count)
    urls = asyncio.run(scroll_page())
    results = asyncio.run(main1(urls))
    #browser.quit()
    add_products(entry_id, results)
    close_db()
    end_time = time.time()
    time_work = end_time - start_time
    print(f"Парсинг занял: {time_work:.2f} секунд")


