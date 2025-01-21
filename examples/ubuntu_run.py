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

service = Service('/home/xhulio/Downloads/chromedriver-linux64/chromedriver')  # Path to ChromeDriver
chrome_options.add_argument('--disable-notifications')
chrome_options.add_argument(r"--user-data-dir=/home/xhulio/.config/google-chrome/")  # Root directory for Chrome user data
chrome_options.add_argument(r"--profile-directory=Profile 1")  # The profile folder you created

# Initialize WebDriver for Chrome 
driver = webdriver.Chrome(service=service, options=chrome_options)
google_api = GoNews(language='english', country='United States')

url_news = google_api.get_news_by_topic(topic='POLITICS')
content = google_api.read_articles(url_news, driver, write_json=True, max_topics=1)