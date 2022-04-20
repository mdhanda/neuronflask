import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


def search_and_download(driver_path: str, count=10):

    with webdriver.Chrome(service = Service(driver_path)) as wd:
        res = fetch_details(count, wd=wd, sleep_between_interactions=0.5)


def fetch_details(count_to_fetch: int, wd: webdriver, sleep_between_interactions: int = 1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

        # build the google query

    search_url = URL_TO_SCRAP

    # load the page
    wd.get(search_url)

    image_urls = set()
    data_count = 0
    results_start = 0
    while data_count < count_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        #search_results = wd.find_elements(by=By.CSS_SELECTOR, value="Course_course-card__1_V8S Course_card__2uWBu card")
        search_results = wd.find_elements(by=By.CLASS_NAME, value="Course_flex__3ZrIo flex")
        number_results = len(search_results)
        print(search_results)
        print(f"Found: {number_results} search results.")

    return number_results

DRIVER_PATH = r'D:\DS\Misc\chromedriver.exe'
URL_TO_SCRAP = 'http://courses.ineuron.ai'

search_and_download(driver_path=DRIVER_PATH, count=20)