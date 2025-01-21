from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import sys
import os

# Add the absolute path of the src directory to sys.path
sys.path.append(os.path.abspath("/home/xhulio/Desktop/Thesis/GNews/src"))
from allsides_news_api import *


# Set up Selenium options
chrome_options = Options()
service = Service('C:\\Users\\xhuli\\OneDrive\\Desktop\\Thesis\\chromedriver-win64\\chromedriver.exe')  # Path to GeckoDriver
chrome_options.add_argument('--disable-notifications')
chrome_options.add_argument(r"--user-data-dir=C:\Users\xhuli\AppData\Local\Google\Chrome\User Data")  # Root directory for Chrome user data
chrome_options.add_argument(r"--profile-directory=Profile 1")  # The profile folder you created

# Initialize WebDriver for Firefox
driver = webdriver.Chrome(service=service, options=chrome_options)
google_api = GoNews(language='greek', country='Greece')

a = google_api.get_news_by_topic(topic='POLITICS')
b = google_api.read_articles(a, driver, write_json=True, max_topics=1)