"""
Define Webscrapers to download articles from different Publishers.
Currently scrapers defined for:
    - Elsevier
    - RSC

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

        self.api_key = '' # please provide your key

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

    def article_downloader(self, yop):
        """Saves articles to ./Articles/ELS/{year_of_publication} where ./ is the path of this script
        """

        self.yop = yop

        download_path = os.path.join(os.path.dirname(__file__), "Articles", "ELS", str(yop))
        print(download_path)

        if not os.path.exists(download_path):
            os.makedirs(download_path)

        for doi in self.dois:
            doi = doi.replace('/', '-')
            with open(os.path.join(download_path, 'article-{}.xml'.format(doi)), 'w+', encoding='utf-8') as f:
                download_url = 'https://api.elsevier.com/content/article/doi/{}'.format(doi)
                f.write(requests.get(download_url, headers={'x-els-apikey': self.api_key}).text)

    def debug_doi_request(self):
        """Prints HTML link used to find DOIs
        """
        doi_response = requests.Request('PUT', url=self.base_url, data=json.dumps(self.search_data),
                                        headers=self.headers)
        doi_link = doi_response.prepare()
        print(doi_link.url)

