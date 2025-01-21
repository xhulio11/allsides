from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from newspaper import Article
from bs4 import BeautifulSoup
import requests
import feedparser
import json
import time


# Set up Selenium options
chrome_options = Options()
service = Service('C:\\Users\\xhuli\\OneDrive\\Desktop\\Thesis\\chromedriver-win64\\chromedriver.exe')  # Path to GeckoDriver
chrome_options.add_argument('--disable-notifications')
# chrome_options.add_argument('--headless')
chrome_options.add_argument(r"--user-data-dir=C:\Users\xhuli\AppData\Local\Google\Chrome\User Data")  # Root directory for Chrome user data
chrome_options.add_argument(r"--profile-directory=Profile 1")  # The profile folder you created

# Initialize WebDriver for Firefox
driver = webdriver.Chrome(service=service, options=chrome_options)
# Get content using browser 

url = "https://www.allsides.com/topics/politics"
driver.get(url) 


# Wait for the page to fully load 
WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))  # Wait for the body tag


# Get the page source
page_content = driver.page_source

page = BeautifulSoup(page_content,"html.parser")
# page = page.prettify()
# print(page)
# with open("page.html", "w",encoding='utf-8') as file: 
#     file.write(page)

div_left = page.find_all("div", class_="news-item left")
div_center = page.find_all("div", class_="news-item center")
div_right = page.find_all("div", class_="news-item right")

print(len(div_left))

