#-*- coding: utf-8 -*-
#!/usr/bin/env python
from configparser import ConfigParser, ExtendedInterpolation
import sys
import amazon_scraper
import time
import datetime
import logging.config
import os.path
from utilities import getSentencesFromReview, Sentence, Review, Product, loadScraperDataFromDB
import nltk
from srs import settings
from database import has_product_id, upsert_contents_for_product_id


class AmazonReviewScraper:

    def __init__(self, access_key, 
        secret_key, assoc_tag, logger=None, debug=False):
        self.amzn = amazon_scraper.AmazonScraper(
            access_key,
            secret_key,
            assoc_tag)
        self.logger = logger or logging.getLogger(__name__)
        logging.config.fileConfig(
            os.path.join(
                settings["scraper_data"],
                "logging.ini"))
        self.debug = debug

    def _encode_safe(self, s):
        if s:
            return s.encode('utf-8')
        else:
            return ""

    def process_reviews(self, rs):
        """
        Inputs: Amazon Reviews object, and a filehandle.
        Output: Returns number of reviews processed. Writes reviews to file.
        """

        sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

        count = 0
        output_str = ""
        contents = []
        for r in rs.full_reviews():
            count += 1
            
            try:
                if self.debug:
                    logging.debug(
                        "{} | {} | {}".format(
                            r.id, r.date, self._encode_safe(
                                r.text)))
                if r.text != "None":
                    sentenceContent_list = getSentencesFromReview(self._encode_safe(r.text))
                    print "First sentence: " + sentenceContent_list[0]
                    for content in sentenceContent_list:
                        contents.append(content)
            except:
                logging.warn(
                    'Encoding problem with review {}'.format(
                        r.id))
        
        return count, contents

    def scrape_reviews(self, item_id):
        """
        Fetches reviews for the Amazon product with the specified ItemId. 
        """

        start = time.time()
        p = self.amzn.lookup(ItemId=item_id)
        rs = self.amzn.reviews(URL=p.reviews_url)
        count = 0
        page_count = 0
        contents = []
        while True:
            page_count += 1
            result_tup = self.process_reviews(rs)
            count += result_tup[0]
            contents.extend(result_tup[1])
            rs = self.amzn.reviews(URL=rs.next_page_url)
            if not rs.next_page_url:
                result_tup = self.process_reviews(rs)
                count += result_tup[0]
                contents.extend(result_tup[1])
                break
            print "page_count: {0}".format(page_count)
            if page_count%3 == 0:
                print "page_count%3 == 0: {0}".format(page_count)
                upsert_contents_for_product_id(item_id, contents)
        end = time.time()
        logging.info(
            "Collected {} reviews for item {} in {} seconds".format(
                count,
                item_id,
                end -
                start))
        return contents

def getAmazomConfidentialKeys():
    conf_file = os.path.join(
                settings["scraper_data"],
                "amazon.ini")
    conf = ConfigParser(interpolation=ExtendedInterpolation())
    try:
        conf.read(conf_file)
    except:
        sys.exit('Cannot read configuration file %s; exiting.' % conf_file)
    try:
        # str() is used to avoid HMAC-related unicode error
        AMAZON_ACCESS_KEY = str(conf.get('amazon', 'AMAZON_ACCESS_KEY'))
        AMAZON_SECRET_KEY = str(conf.get('amazon', 'AMAZON_SECRET_KEY'))
        AMAZON_ASSOC_TAG = str(conf.get('amazon', 'AMAZON_ASSOC_TAG'))
    except:
        sys.exit("Bad configuration file; exiting.")

    return AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG

def createAmazonScraper():
    AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG = \
    getAmazomConfidentialKeys()
    
    a = AmazonReviewScraper(
        AMAZON_ACCESS_KEY,
        AMAZON_SECRET_KEY,
        AMAZON_ASSOC_TAG,
        debug=False)
    return a

def scrape_reviews_hard(productID):
    '''
    This method scraps directly from website and does not need userID or the AmazonScrape object
    However, it can only scrape the 5 top ranked review. 
    '''
    from lxml import html
    import requests
    from time import sleep
    from fake_useragent import UserAgent
    import random
    
    url = "http://www.amazon.com/dp/" + productID
    print "Processing: " + url
    ua = UserAgent()
    headers = {
        # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        'User-Agent': ua}
        # get user agent: http://www.whoishostingthis.com/tools/user-agent/ 
        # or generate random one: https://pypi.python.org/pypi/fake-useragent
    page = requests.get(url, headers=headers)
    while True:
        sleep(int(random.random()*2+1)) # this is important not to be identified as Amazon
        try:
            doc = html.fromstring(page.content)
            XPATH_NAME = '//h1[@id="title"]//text()'
            XPATH_RATINGS = '//div[contains(@id, "rev-dpReviewsMostHelpfulAUI")]/div/div/a/i/span//text()'
            XPATH_REVIEWS_TITLE = '//div[contains(@id, "rev-dpReviewsMostHelpfulAUI")]/div/div/a[2]//text()'
            XPATH_REVIEWS_BODY = '//div[contains(@id, "revData-dpReviewsMostHelpfulAUI")]/div//text()'

            RAW_NAME = doc.xpath(XPATH_NAME)
            RAW_RATINGS = doc.xpath(XPATH_RATINGS)
            RAW_REVIEWS_TITLE = doc.xpath(XPATH_REVIEWS_TITLE)
            RAW_REVIEWS_BODY = doc.xpath(XPATH_REVIEWS_BODY)

            NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
            RATINGS = ' , '.join(RAW_RATINGS).strip() if RAW_RATINGS else None
            REVIEWS_TITLE = ' , '.join(RAW_REVIEWS_TITLE).strip() if RAW_REVIEWS_TITLE else None
            REVIEWS_BODY = '. '.join(RAW_REVIEWS_BODY).strip() if RAW_REVIEWS_BODY else None
            
            reviews_text  = REVIEWS_BODY.encode('utf-8')
            sentences = getSentencesFromReview(reviews_text.decode('utf-8'))

            return sentences

        except Exception as e:
            print e



def main(amazonScraper, productID):

    if not has_product_id(productID):
        contents = amazonScraper.scrape_reviews(productID)
        return contents
    else:
        print "{0} is already scraped and has reviews stored.".format(productID)
        contents, _, _ = loadScraperDataFromDB(productID)
        return contents


if __name__ == "__main__":

    productID = 'B00C7NX884' # B00I8BICB2 sony a6000 with 686 reviews,B00T85PH2Y
    a = createAmazonScraper()   
    content = main(a,productID)
    # sentences = scrape_reviews_hard(productID)
    # print sentences


    # p = a.amzn.lookup(ItemId=productID)
    # rs = p.reviews()
    # for r in rs.full_reviews():
    #     print r.text

    # content = main(a, productID)
    # print content
