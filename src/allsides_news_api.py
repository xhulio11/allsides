from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from newspaper import Article
from bs4 import BeautifulSoup
import requests
from constants import * 
import feedparser
import json
import time


class AllSidesNews():
    

    def __init__(self, driver): 
        self.driver = driver

    
    def create_url(self, topic=None):
        
        # Set the proper url based on the selection of Main topics (WORLD, BUISNESS, ...) or sections (POLITICS, SPORTS ..)
        try: 
            # Check the topic to be used
            if topic in TOPICS: 
                url = ALLSIDES_NEWS_URL + '/topics/' + topic 
                return url 
        except:
            print("ERROR: Some variable is not defined properly for the creation of the url")


    def get_news_by_bias(self, topic="politics"):
        
        # Create url based on given topic 
        base_url = self.create_url(topic=topic) 
        
        # Get Page content 
        self.driver.get(base_url) 

        # Wait for the page to fully load 
        WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        # Get the page source
        allsides = self.driver.page_source

        allsides_html = BeautifulSoup(allsides,"html.parser")

        # Get political column names 
        political_columns = allsides_html.find("div", class_="news-trio")

        # Retrieve left, center, and right divs which contain the ulrs for the source  
        left = political_columns.find_all("div", class_="news-item left")
        center = political_columns.find_all("div", class_="news-item center")
        right = political_columns.find_all("div", class_="news-item right")

        all_urls = {"left":[], "center":[], "right":[]}

        # Loop through each column and extract intermidiate url 
        for div in left: 
            a_tag = div.find("a")
            all_urls["left"].append(a_tag["href"])
        
        for div in center: 
            a_tag = div.find("a")
            all_urls["center"].append(a_tag["href"])
        
        for div in right: 
            a_tag = div.find("a")
            all_urls["right"].append(a_tag["href"])
        


        return all_urls
    


    def get_article_url(self, intermidiate_url): 
        """
            This fucntion takes as input: intermidate url 
            Return the article url and the political bias: {"url":"http:/.....", "bias"="Lean Left"}
        """
        
         
    def read_articles(self, topics, driver, write_json=False, max_topics = 10):

        articles_by_topic = []

        with open('articles.json', 'w', encoding='UTF-8') as file: 
            
            for counter, topic in enumerate(topics):
                
                articles_content = []

                for url in topic:

                    # Get content using browser 
                    driver.get(url) 

                    try:
                        # Wait for the page to fully load 
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))  # Wait for the body tag

                        # Add a delay to mimic human behavior
                        time.sleep(2) 

                        # Get the page source
                        page_content = driver.page_source

                        # Use newspaper3k to parse the article text
                        article = Article('')
                        article.set_html(page_content)
                        article.parse()
                    
                    except TimeoutException:
                        print("An error occurred while loading the page: Page load timed out.")
                        # continue to the other url 
                        continue 

                    except Exception as e:
                        print(f"An error occurred while loading the page: {e}")
                        json.dump(articles_by_topic, file, ensure_ascii=False, )
                        return 

                    # Get the content of the article 
                    artilce_title = article.title
                    article_text = article.text
                    articles_content.append(artilce_title + '\n' + article_text)
                    
                    # Mimic human behavior 
                    time.sleep(10)
                                
                articles_by_topic.append(articles_content)

                # This counter is used to keep track of max number of news retrieved 
                counter += 1 

                if counter == max_topics:
                    if write_json: 
                        json.dump(articles_by_topic, file, ensure_ascii=False) # Store the content in a file                   
                    driver.quit() # quit the browswer 
                    break 
            
        return articles_by_topic
    
        