"""
Define Webscrapers to download articles from different Publishers.
Currently scrapers defined for:
    - Elsevier
    - RSC
    - Springer Open Access

:code author: Pankaj Kumar (pk503@cam.ac.uk)
"""

import os
import sys
import json
import requests
import urllib.request
import re
import pprint
from chemdataextractor.scrape.pub.rsc import RscSearchScraper
from selenium import webdriver


class Els_scraper:
    """Class used to scrape Elsevier articles.


    Finds DOIs of articles corresponding to the user's search criteria. 
    The articles resulting from the search can be downloaded. This only works if 
    a correct API key is used. To register for an API key, visit the Elsevier Developer website.

    Args:
        search_query (str): Keywords to search for an article
        search_date (str): Search for articles published in this year
        num_articles (int): Number of articles to search for
        search_journal (str): Specifies which journal to search in (default=None)

    Attributes: 
        api_key: String that is required to access Elsevier API
        search_data: Dictionary containing search criteria
        headers: Dictionary required to request article data from Elsevier API, contains API key and content type
        url: String of the base URL required to request article data
        dois: List containing article DOIs that match search criteria
        article_ID: Identifier used to name the downloaded articles
    """
    
    def __init__(self, search_query, search_date, num_articles, search_journal=None):

        self.api_key = '15dd914e62bef9bde40fb5992f26e7d8' #oddy api key

        self.search_data = {
            'qs' : search_query,
            'pub' : search_journal,
            'date' : search_date,
            'display' : {
                'show' : num_articles,
                'offset' : 0
                }
        }

        self.headers = {
            'x-els-apikey': self.api_key,
            'Content-Type': 'application/json'  
            }

        self.base_url = 'https://api.elsevier.com/content/search/sciencedirect'
        self.dois = []
        self.article_ID = 0
        
    
    def article_search(self):
        """Uses search criteria to find list of corresponding articles

        Returns:
            article_list: Dictionary containing all responses of the search with relevant article information
        """
        print(self.search_data)

        response = requests.put(self.base_url, data=json.dumps(self.search_data), headers=self.headers)
        if response:
            response = response.text.replace('false', 'False').replace('true', 'True')
            search_result = eval(response) #convert the response string to python dictionary
            return search_result

        else:
            print("Error with status code: {} - {}".format(response,response.text))
            sys.exit()
        
    
    def get_dois(self):
        """Extracts the DOIs from the article_list

        Returns:
            self.dois: List containing all DOIs
        """
        articles = self.article_search()['results']
        for article in articles:
            if 'doi' in article:
                self.dois.append(article['doi'])
        #print(self.dois)
        return self.dois

    def article_downloader(self, yop, model_name='unspecified'):
        """Saves articles to ./downloaded_articles/Elsevier where ./ is the path of webscraper.py
        """
        #oddy edited to save folders per year of publication (yop)

        self.yop = yop

        download_path = os.path.join("/Users/ody/Desktop/BERT/2ELS", 'Elsevier_' + model_name + '_' + str(yop) + '/')
        print(download_path)


        if not os.path.exists(download_path):
            os.makedirs(download_path)

        for doi in self.dois:
            doi = doi.replace('/','-')
            with open(download_path + 'article-{}.xml'.format(doi), 'w+', encoding='utf-8') as f:
                download_url = 'https://api.elsevier.com/content/article/doi/{}'.format(doi)
                f.write(requests.get(download_url, headers={'x-els-apikey': self.api_key}).text)
        
    def debug_doi_request(self):
        """Prints HTML link used to find DOIs 
        """
        doi_response = requests.Request('PUT',url=self.base_url, data=json.dumps(self.search_data), headers=self.headers)
        doi_link = doi_response.prepare()
        print(doi_link.url)
        
            
class Rsc_scraper:
    """Class used to scrape RSC articles.

    
    Uses methods defined in ChemDataExtractor version 2 which is provided by the group
    and does not have a public release as of 28/01/2020. Also requires a webdriver since RSC 
    does not provide an API (Gecko driver for Mozilla Firefox used here). 

    Gecko driver - https://github.com/mozilla/geckodriver/releases 

    Args:
        search_query (str): Keywords to search for
        search_pages (int): Number of pages to scrape (default=1)

    Attributes:
        dois: List containing the DOIs of the articles found
        download_urls: List containing the corresponding download links for the articles
        article_ID: Identifier used to name the downloaded articles
        


    """

    # oddy added open_access to Rsc_scraper's initialisation. Within its get_dois function, there is an
    # RscSearchScraper.run(...). So, a new variable open_access is added to run, and self.open_access (from
    # Rsc_scraper's initialisation) is passed to it. run(...) belongs to SearchScraper, the parent class
    # from which RscSearchScraper inherits from. Within it, run calls perform_search(...), which is the function
    # which gives the url to search for. I have added an open_access variable to it as well, which adds the necessary
    # extension to the url, which should yield open access results. Note that perform_search is a function of
    # SearchScraper, which is overriden in RscSearchScraper, and takes an extra argument, called driver,
    # so u need to pass open_acess=open_access to the calling of perform_search.

    def __init__(self, search_query, search_pages=1, open_access=False):
        self.search_query = search_query
        self.search_pages = search_pages
        self.dois = []
        self.journals = []
        self.doisAndHTMLs = {}
        self.open_access = open_access


    def get_dois(self):
        """Finds DOIs using function defined in CDE v2
        

        Uses the search criteria to find the DOIs of articles over the defined number 
        of pages and appends these to a list containing all found article DOIs.

        """
        #oddy added open_access variable
        rsc_scraped = RscSearchScraper().run(self.search_query, page=self.search_pages) #removed the passing of open_access parameter?
        articles = rsc_scraped.serialize()

        for article in articles:            
            self.dois.append([article['doi'], article['journal']])

        
        
    def get_download_urls(self):
        """Finds the download URL for each DOI

        Requires get_dois() to be ran before using.
        Using the Gecko web driver, the HTML of an article is found by using the DOI api
        which upon request will return metadata including the article link. 
        
        """
        for doi_and_journal in self.dois:
            doi = doi_and_journal[0]
            journal = doi_and_journal[1]

            response = requests.get('https://www.doi.org/' + doi, headers= { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'})
            download_url = re.findall(r'https://pubs.rsc.org/en/content/articlehtml/.*?"', response.text)
            download_urls = download_url[0].strip('"')
            self.doisAndHTMLs.update({doi : [download_urls,journal]})
            
    def article_downloader(self):
        """Saves articles to ./Articles/RSC where ./ is the path of webscraper.py


        Requires get_download_urls() to be ran before using. 
        """
        
        base_path = os.path.dirname(__file__) + '/downloaded_articles/RSC_new/'
        # manually oddy
        base_path = "/Users/ody/Desktop/BERT/2RSC"

        if self.open_access:
            base_path = os.path.dirname(__file__) + '/downloaded_articles/RSC_new_OA/'
            # manually oddy
            base_path = "/Users/ody/Desktop/BERT/2RSC_OA"


        
        for doi, URLandJournal in self.doisAndHTMLs.items():
            downloadURL = URLandJournal[0]
            journal = URLandJournal[1].replace(' ','_') + '/'
            download_path = os.path.join(base_path, journal)

            if not os.path.exists(download_path):
                os.makedirs(download_path)

            with open((download_path) + "article-{}.html".format(doi.replace('/', '-')), 'wb') as f:
                article = urllib.request.urlopen(downloadURL).read()
                f.write(article)


class Springer_scraper:
    """Class used to scrape Springer articles.


    Finds DOIs of articles corresponding to the user's search criteria. This scraper is limited to 
    only Open Access articles. The doi and full text html can be found for articles matching the 
    search criteria. 

    Args:
        search_query (str): Keywords to search for an article
        search_date (str): Search for articles published in this year
        num_articles (int): Number of articles to search for

    Attributes: 
        api_key: String that is required to access Springer API
        search_data: Dictionary containing search criteria
        url: String of the base URL required to request article metadata
        doisAndHTMLs: Dictionary containing dois and the corresponding fulltext html
    """

    def __init__(self, search_query, num_articles, search_date=None):
        self.api_key = '4ee9cc09a97ae4420cbcc1ba9acf1587'
        self.base_url = 'http://api.springernature.com/meta/v2/json'
        self.search_data = {
            'q' : '(keyword:{} openaccess:true year:{})'.format(search_query,search_date),
            'api_key' : self.api_key,
            'p' : num_articles,
        }
        self.articles = None
        self.doisAndHTMLs = {}

    def article_search(self):
        """Searches for article using search criteria


        Saves the articles found during the search if a response is successful, else
        the error code is printed to the user. Status code (403) and (404) are common
        error codes, these respectively stand for forbidden and not found.
        """
        response = requests.get(self.base_url, params=self.search_data)
        if response:
            article_list = eval(response.text)
            self.articles = article_list['records']                    

        else: 
            print("Error with status code: {} - {}".format(response,response.text))
            sys.exit()
                      
            
    def get_fulltextHTMLs(self):
        """Gets the full text HTMLs of the articles

        Searches for the HTML links to the full text of each article in self.articles.
        The link is then saved to a dictionary with the DOI as the key and the HTML as the value.

        Requires article_search() to be ran prior to this function.
        """
        for article in self.articles:
            url_list = article['url']
            doi = article['identifier']
            doi = doi.strip('doi:').replace('/','_')
            html_url = [html for html in url_list if html['format']=='html']
            if not html_url:
                pass
            else:
                html_url = html_url[0]['value']
                self.doisAndHTMLs.update({doi : html_url})

    def article_downloader(self):
        """Saves articles to ./Articles/Springer/ where ./ is the path of webscraper.py

        Each article has an ID which is the DOI. Requires get_fulltextHTMLs() to be ran prior to this function.
        """
        download_path = os.path.dirname(__file__) + '/downloaded_articles/Springer/'
        
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        for doi, downloadURL in self.doisAndHTMLs.items():
            article = urllib.request.urlopen(downloadURL).read()
            with open(download_path + 'article-{}.html'.format(doi), 'wb') as f:
                f.write(article)

    def debug_request(self):
        """Prints URL that is trying to be opened in article_search()
        """
        r = requests.Request('GET',url=self.base_url, params=self.search_data)
        prep = r.prepare()
        print (self.base_url)
        print(prep.url)

            
