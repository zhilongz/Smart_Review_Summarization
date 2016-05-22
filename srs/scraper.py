#-*- coding: utf-8 -*-
#!/usr/bin/env python
from configparser import ConfigParser, ExtendedInterpolation
import sys
import amazon_scraper
import time
import datetime
import logging.config
import os.path
from utilities import getSentencesFromReview, Sentence, Review, Product
import nltk
from srs import settings


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

    def process_reviews(self, rs, filename):
        """
        Inputs: Amazon Reviews object, and a filehandle.
        Output: Returns number of reviews processed. Writes reviews to file.
        """

        sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

        count = 0
        output_str = ""
        reviews = []
        with open(filename, "a") as fh:
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
                        sentences = []
                        for content in sentenceContent_list:
                            fh.write(content + '\n')
                            sentence = Sentence(content=content)
                            sentences.append(sentence)
                        review = Review(sentences=sentences)
                        reviews.append(review)
                except:
                    logging.warn(
                        'Encoding problem with review {}'.format(
                            r.id))
        
            

        return count, reviews

    def fetch_reviews(self, item_id, filename=None):
        """
        Fetches reviews for the Amazon product with the specified ItemId. 
        """
        if not filename:
            filename = os.path.join(
                settings["scraper_data"], 
                item_id + '.txt')

        start = time.time()
        p = self.amzn.lookup(ItemId=item_id)
        rs = self.amzn.reviews(URL=p.reviews_url)
        count = 0
        reviews = []
        while True:
            result_tup = self.process_reviews(rs, filename)
            count += result_tup[0]
            reviews.extend(result_tup[1])
            rs = self.amzn.reviews(URL=rs.next_page_url)
            if not rs.next_page_url:
                result_tup = self.process_reviews(rs, filename)
                count += result_tup[0]
                reviews.extend(result_tup[1])
                break
        end = time.time()
        logging.info(
            "Collected {} reviews for item {} in {} seconds".format(
                count,
                item_id,
                end -
                start))
        return reviews

def isProductScraped(productID):

    scraper_data_folder = settings["scraper_data"]
    target_data_file_path = os.path.join(scraper_data_folder,
                productID + ".txt")

    if not os.path.exists(target_data_file_path):
        return False
    else:
        line_count = 0
        with open(target_data_file_path, 'r') as f:
            for line in f:
                line_count += 1
                return True
        if line_count == 0:
            return False


def main(productID):
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

    a = AmazonReviewScraper(
        AMAZON_ACCESS_KEY,
        AMAZON_SECRET_KEY,
        AMAZON_ASSOC_TAG,
        debug=False)
    reviews = a.fetch_reviews(productID)
    product = Product(name=productID, reviews=reviews)
    print len(product.reviews)


if __name__ == "__main__":

    productID = 'B00I8BICB2' # sony a6000 with 686 reviews
    main(productID)
