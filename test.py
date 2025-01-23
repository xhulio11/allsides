from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import sys 
import os 


# Add the absolute path of the src directory to sys.path
sys.path.append(os.path.abspath("/home/xhulio/Desktop/Thesis/AllSides/src"))
from allsides_news_api import *

# Set up Selenium options
chrome_options = Options()
#service = Service('C:\\Users\\xhuli\\OneDrive\\Desktop\\Thesis\\chromedriver-win64\\chromedriver.exe')  # Path to GeckoDriver
service = Service('/home/xhulio/Downloads/chromedriver-linux64/chromedriver')  # Path to ChromeDriver
chrome_options.add_argument('--disable-notifications')
# chrome_options.add_argument('--headless')
chrome_options.add_argument(r"--user-data-dir=/home/xhulio/.config/google-chrome/")  # Root directory for Chrome user data
chrome_options.add_argument(r"--profile-directory=Profile 1")  # The profile folder you created

# Initialize WebDriver for Firefox
driver = webdriver.Chrome(service=service, options=chrome_options)
# Get content using browser 

all_sides_api = AllSidesNews(driver)

urls = all_sides_api.get_news_by_bias(topic="politics")

with open("article_urls.json", "w") as file: 
    json.dump(urls, file, indent=4)
# with open("article_urls_backup.json", "w") as file: 
#     json.dump(urls, file, indent=4)

# with open("article_urls.json", "r", encoding="utf-8") as file: 
#     data = json.load(file)

# articles = all_sides_api.read_articles(data, driver, write_json=True, max_topics = 10)