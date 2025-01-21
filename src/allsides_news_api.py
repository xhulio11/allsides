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
    

    def __init__(self,):
        pass 

    def create_url(self, code=None, query_parameter=None):
        
        # Set the proper url based on the selection of Main topics (WORLD, BUISNESS, ...) or sections (POLITICS, SPORTS ..)
        try: 
            # Check the topic to be used
            if code in TOPICS: 
                url = ALLSIDES_NEWS_URL + '/topics/' + code 
                return url 
        except:
            print("ERROR: Some variable is not defined properly for the creation of the url")


    def get_news_by_topic(self, topic="politics"):
        # Get News by main provided topics in google news site 
        url = self.create_url(code=topic, query_parameter=self.query)


        """
        list: news_by_topic
        
        This list will contain in every positin a dictionary of reated news 
        [
        {"title 1": "https://news.google.com/...", "title 2": "https://news.google.com/..."}, 
        {"title 3": "https://news.google.com/...", "title 4": "https://news.google.com/..."}, 
        ...]
        
        """
        news_by_topic = [None for _ in entries]

        for i, entry in enumerate(entries): 

            # Get main title and the url 
            title = entry['title']
            
            url = entry["links"][0]['href']
            
            # Add the first article in the current position
            news_by_topic[i] = {url:title}

            # Parse the html content to extract the other related news 
            # Get the key:summary which is html content
            summary = entry['summary']
            
            # Create a BeautifulSoup instant to parse 
            content = BeautifulSoup(summary, 'html.parser')
            
            # Every li tag contains href: link, target: title 
            a_tags = content.find_all('a')
            j = 0 
            for a_tag in a_tags:

                # Get url and title of current article 
                url = a_tag.get('href')
                title = a_tag.get_text(strip=True)  # Extracts the text content

                # Add it in the dictionary 
                news_by_topic[i][url] = title 

        return news_by_topic


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
    
        