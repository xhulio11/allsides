from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from newspaper import Article
import newspaper 
from bs4 import BeautifulSoup
from constants import * 
import json
import time
import urllib3
from datetime import datetime 
from colorama import Fore, Style

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


    def normalize_date(self, date_str):
        # Remove unwanted characters and extra spaces
        date_str = date_str.strip().replace('\n', '').replace('Posted on AllSides', '').strip()
        
        # Replace ordinal suffixes (st, nd, rd, th) with an empty string
        date_str = date_str.replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')
        
        # Parse the date string into a datetime object
        date_obj = datetime.strptime(date_str, '%B %d, %Y')
        
        # Format the datetime object into a normalized date string (YYYY-MM-DD)
        normalized_date = date_obj.strftime('%Y-%m-%d')
        
        return normalized_date
    
    
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
            found = any(url_bias['url'] == item[1] for item in all_urls[url_bias['bias']])
            if not found:
                all_urls[url_bias["bias"]].append((url_bias['date'], url_bias['url']))
        
        for div in center: 
            a_tag = div.find("a")
            url_bias = self.get_article_url(intermidiate_url=a_tag['href'])
            time.sleep(0.5)
            # url_bias['bias'] == "Center"
            # Check if the string matches any value in position 0

            found = any(url_bias['url'] == item[1] for item in all_urls[url_bias['bias']])
            if not found:
                all_urls[url_bias["bias"]].append((url_bias['date'], url_bias['url']))
        
        for div in right: 
            a_tag = div.find("a")
            url_bias = self.get_article_url(intermidiate_url=a_tag['href'])
            time.sleep(0.5)
            # url_bias['bias'] == "Lean Right" || "Right"
            found = any(url_bias['url'] == item[1] for item in all_urls[url_bias['bias']])
            if not found:
                all_urls[url_bias["bias"]].append((url_bias['date'], url_bias['url']))
        
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

        # Get Date 
        article_date = allsides_html.find('div', class_="article-posted-date")
        date = article_date.get_text()

        # Get bias 
        bias_element = allsides_html.find('span', class_="media-bias-name")
        bias = bias_element.find('a').get_text() 

        # Get article url 
        url_div = allsides_html.find('div', class_="read-more-story")
        url = url_div.find('a')["href"]

        return {"date":self.normalize_date(date),"url":url, "bias":bias}


    def read_articles(self, urls, driver, write_json=False, force_all_articles = False, hard_check_article=True):

        failed_articles_urls = []
        counter_passed_articles = 0
        counter_all_articles = 0
        with open('articles.json', 'w', encoding='UTF-8') as file: 
            articles_content = []
            print("Trying newspaper3k Api ...\n")
            for key, value in urls.items(): 
                # Getting the number of all articles
                counter_all_articles += len(value)

                for url in value:
                    # Simple approach 
                    try:
                        article = Article(url=url[1], language='en')
                        article.download()
                        article.parse() 

                    except newspaper.article.ArticleException:
                        print(f"Article {Fore.RED}FAILED{Style.RESET_ALL}:", url[1])
                        failed_articles_urls.append(url)
                        continue 
                    print(f"Article {Fore.GREEN}PASSED{Style.RESET_ALL}:", url[1])
                    # Get the content of the article 
                    artilce_title = article.title
                    article_text = article.text
                    articles_content.append({"date":url[0],"article":artilce_title + '\n' + article_text,"bias":key, "url":url[1]})
                    counter_passed_articles += 1 
                
            print(f"\n{Fore.GREEN}PASSED{Style.RESET_ALL} Articles:{Fore.GREEN}{counter_passed_articles}{Style.RESET_ALL}/{Fore.RED}{counter_all_articles}{Style.RESET_ALL}")
                    
            if force_all_articles:
                print("\nTrying Selenium and Webroswer ...\n")
                counter_passed_articles = 0
                counter_all_articles = len(failed_articles_urls)
                for url in failed_articles_urls: 
                    
                    #Using the browser for the failed urls with simple aproach 
                    try:
                        # Get content using browser 
                        driver.get(url[1]) 
                        try:                                
                            # Wait for the page to fully load 
                            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))  # Wait for the body tag
                        
                        except TimeoutError: 
                            print(f"{Fore.RED}TimeoutError{Style.RESET_ALL} - No Body tag found:",url[1])
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
                        if hard_check_article:
                            # Return a tuple (bool, message)
                            hard_check = self.hard_check_article(article)

                            if not hard_check[0]:
                                print(f"Article {Fore.RED}FAILED - {hard_check[1]}{Style.RESET_ALL}:{url[1]}")
                                continue 

                    except TimeoutException:
                        # Selenium-specific timeout
                        print(f"{Fore.RED}TimeoutException {Style.RESET_ALL}: {url[1]}")
                        continue

                    except urllib3.exceptions.ReadTimeoutError:
                        # Lower-level read timeout from urllib3
                        print(f"{Fore.RED}ReadTimeoutError{Style.RESET_ALL}: {url[1]}")
                        continue

                    except Exception as e:
                        print(f"An error occurred while loading the page: {e}")
                        # json.dump(articles_content, file, ensure_ascii=False, )
                        continue 

                    # Get the content of the article 
                    print(f"Article {Fore.GREEN}PASSED:{Style.RESET_ALL}", url[1])
                    artilce_title = article.title
                    article_text = article.text
                    articles_content.append({"date":url[0],"article":artilce_title + '\n' + article_text,"bias":key, "url":url[1]})
                    counter_passed_articles += 1
                    
                print(f"\n{Fore.GREEN}PASSED{Style.RESET_ALL} Articles:{Fore.GREEN}{counter_passed_articles}{Style.RESET_ALL}/{Fore.RED}{counter_all_articles}{Style.RESET_ALL}")

                    

            # Writing every article collected 
            json.dump(articles_content, file, indent=4)
            
        return articles_content
    

    def hard_check_article(self, article): 

        message = ""
        # Title check
        if not article.title or len(article.title.strip()) < 5:
            message = "Missing or invalid title"
            return (False, message)

        # Length check
        if len(article.text) < 100:
            message = "Content too short"
            print(article.text)
            return (False, message)
        
        # Paragraph structure
        paragraphs = article.text.split("\n")
        if len([p for p in paragraphs if len(p.split()) > 10]) < 2:
            message="Insufficient paragraph structure"
            return (False, message)

        # Media-only check
        if article.movies and len(article.text) < 100:
            message="Media-only content"
            return (False, message)
        
        return (True, message)
    