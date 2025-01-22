from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from newspaper import Article
from bs4 import BeautifulSoup
from constants import * 
import json
import time
import urllib3

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

        all_urls = {"Lean Left":[], "Left":[], "Center":[], "Lean Right":[], "Right":[]}

        # Loop through each column and extract intermidiate url 
        for div in left: 
            a_tag = div.find("a")
            url_bias = self.get_article_url(intermidiate_url=a_tag['href'])
            time.sleep(0.5)

            # url_bias['bias'] == "Lean Left" || "Left"
            if url_bias['url'] not in all_urls[url_bias["bias"]]:
                all_urls[url_bias["bias"]].append(url_bias['url'])
        
        for div in center: 
            a_tag = div.find("a")
            url_bias = self.get_article_url(intermidiate_url=a_tag['href'])
            time.sleep(0.5)
            # url_bias['bias'] == "Center"
            if url_bias['url'] not in all_urls[url_bias["bias"]]:
                all_urls[url_bias["bias"]].append(url_bias['url'])
        
        for div in right: 
            a_tag = div.find("a")
            url_bias = self.get_article_url(intermidiate_url=a_tag['href'])
            time.sleep(0.5)
            # url_bias['bias'] == "Lean Right" || "Right"
            if url_bias['url'] not in all_urls[url_bias["bias"]]:
                all_urls[url_bias["bias"]].append(url_bias['url'])
        
        return all_urls
    

    def get_article_url(self, intermidiate_url): 
        """
            This fucntion takes as input: intermidate url 
            Return the article url and the political bias: {"url":"http:/.....", "bias"="Lean Left"}
        """
        self.driver.get(intermidiate_url)
 
        # Wait for the page to fully load 
        WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        # Get the page source
        allsides = self.driver.page_source

        allsides_html = BeautifulSoup(allsides,"html.parser")

        # Get bias 
        bias_element = allsides_html.find('span', class_="media-bias-name")
        bias = bias_element.find('a').get_text() 

        # Get article url 
        url_div = allsides_html.find('div', class_="read-more-story")
        url = url_div.find('a')["href"]

        return {"url":url, "bias":bias}


    def read_articles(self, urls, driver, write_json=False, max_topics = 10, hard_check_article=True):


        with open('articles.json', 'w', encoding='UTF-8') as file: 
            articles_content = []
            for key, value in urls.items(): 
                
                for url in value:

                    try:
                        # Get content using browser 
                        driver.get(url) 
                        
                        try:                                
                            # Wait for the page to fully load 
                            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))  # Wait for the body tag
                        
                        except TimeoutError: 
                            print("No Body tag found")
                            continue

                        # Add a delay to mimic human behavior
                        time.sleep(2) 

                        # Get the page source
                        page_content = driver.page_source

                        # Use newspaper3k to parse the article text
                        article = Article('')
                        article.set_html(page_content)
                        article.parse()
                    # Check articles validity 
                        if hard_check_article and not self.hard_check_article(article): 
                            continue 
                    except TimeoutException:
                        # Selenium-specific timeout
                        print(f"Selenium TimeoutException for URL: {url}. Skipping...")
                        continue

                    except urllib3.exceptions.ReadTimeoutError:
                        # Lower-level read timeout from urllib3
                        print(f"urllib3 ReadTimeoutError for URL: {url}. Skipping...")
                        continue

                    except Exception as e:
                        print(f"An error occurred while loading the page: {e}")
                        json.dump(articles_content, file, ensure_ascii=False, )
                        return 

                    # Get the content of the article 
                    artilce_title = article.title
                    article_text = article.text
                    articles_content.append([artilce_title + '\n' + article_text, key])
                    
                    # Mimic human behavior 
                    time.sleep(2)
            
            json.dump(articles_content, file, indent=4)
            
        return articles_content
    
    def hard_check_article(self, article): 
        
        print("1.Checking Articles Validity")

        # Title check
        if not article.title or len(article.title.strip()) < 5:
            print("2.Missing or invalid title")
            return False

        # Length check
        if len(article.text) < 100:
            print("2.Content too short")
            print(article.text)
            return False

        # Keyword filtering (check for terms like "terms of use", "cookies", etc.)
        disallowed_keywords = [
            "terms of use", "privacy policy", "cookies", 
            "about us", "contact us", "login", "sign up"
        ]
        if any(keyword.lower() in article.text.lower() for keyword in disallowed_keywords):
            print("2. Disallowed content keywords found")
            return False

        # Boilerplate or repetitive content check
        if len(set(article.text.split())) / len(article.text.split()) < 0.5:
            print("2. High repetition or boilerplate content detected")
            return False
        
        # Paragraph structure
        paragraphs = article.text.split("\n")
        if len([p for p in paragraphs if len(p.split()) > 10]) < 2:
            print("2.Insufficient paragraph structure")
            return False

        # Media-only check
        if article.movies and len(article.text) < 100:
            print("2.Media-only content")
            return False

        # If all checks pass
        print("2.Valid article")
        return True
    