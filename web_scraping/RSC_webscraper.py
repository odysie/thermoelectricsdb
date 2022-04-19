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
        
        base_path = os.path.dirname(__file__) + '/Articles/RSC/'

        if self.open_access:
            base_path = os.path.dirname(__file__) + '/Articles/RSC_OA/'

        
        for doi, URLandJournal in self.doisAndHTMLs.items():
            downloadURL = URLandJournal[0]
            journal = URLandJournal[1].replace(' ','_') + '/'
            download_path = os.path.join(base_path, journal)

            if not os.path.exists(download_path):
                os.makedirs(download_path)

            with open((download_path) + "article-{}.html".format(doi.replace('/', '-')), 'wb') as f:
                article = urllib.request.urlopen(downloadURL).read()
                f.write(article)
