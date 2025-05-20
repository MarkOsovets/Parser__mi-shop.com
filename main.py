from bs4 import BeautifulSoup
import requests
import lxml
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import aiohttp
import asyncio
import time

chrome_path = "/usr/bin/google-chrome-stable"

options = Options()
options.binary_location = chrome_path
options.add_experimental_option("prefs", {
    "profile.managed_default_content_settings.images": 2
#    "profile.managed_default_content_settings.stylesheet": 2,
#    "profile.managed_default_content_settings.geolocation":2,
#    "profile.managed_default_content_settings.javascript": 1 # 1 - разрешить, 2 - блокировать
#    "profile.managed_default_content_settings.media_stream": 2,
})


url='https://mi-shop.com/catalog/audio/'
browser = webdriver.Chrome(options=options)
browser.get(url)



response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')


def scroll_page(browser):
    while True: 
        try:  
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            tag_url = browser.find_elements(By.CSS_SELECTOR, ".b-product-card.js-stats-box.js-mi-autoheight-section-item") 
            urls = [link.get_attribute("href") for link in tag_url]
            element = browser.find_element(By.CSS_SELECTOR, ".btn.btn--white.b-catalog__btn")
            time.sleep(0.5)
            ActionChains(browser).move_to_element(element).click().perform()
            time.sleep(2)
        except NoSuchElementException:
            return urls        
    #browser.quit()


async def fetch(session, url):
    async with session.get(url=url) as response:
        soup = BeautifulSoup(await response.text(), 'lxml')
        try:
            name = (soup.select_one(".b-product-info__title.b-product-info__title--compare"))
            price = (soup.select_one(".b-product-info__price-new"))
            battery = (soup.select_one(".b-product-info__stat-line"))
            article_tag = (soup.select_one(".b-article"))
            color = (soup.select_one(".b-product-info__stat-color.is-active img"))
            number_review = (soup.select_one(".b-product-info__link.b-product-info__link--review.no-wrap.js-review-count-string"))
            name = name.get_text(strip=True)
            price = price.get_text(strip=True) if price else "Нет в наличие"
            battery = battery.get_text(strip=True) if battery else "ERORR"
            article = ''.join(filter(str.isdigit, article_tag.get_text(strip=True))) if article_tag else "000000"
            color = color['alt'] if color else "ERORR"
            number_review = number_review.get_text(strip=True) if number_review else "ERORR"
            return (name, price, battery, color, article)
        except Exception as e:
            print(f"Error: {e}")
        

async def main1(urls): 
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = asyncio.create_task(fetch(session, url))
            tasks.append(task)
        res = await asyncio.gather(*tasks)
    return res

def add_db(results):
    db = sqlite3.connect("bd.db")
    cursor = db.cursor()
    with open('db.sql', mode='r') as f:
        cursor.executescript(f.read())
    db.commit()

    for name, price, battery, color, article in results:
        cursor.execute(
            "INSERT INTO Products (name, price) VALUES (?, ?)",
            (name, price)
        )
        product_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO Specifications (product_id, battery, color, article) VALUES (?, ?, ?, ?)",
            (product_id, battery, color, article)
        )
    db.commit()
    db.close()


def main():
    global browser
    urls = scroll_page(browser)
    results = asyncio.run(main1(urls))
    browser.quit()
    add_db(results)

if __name__ == "__main__":
    main()
