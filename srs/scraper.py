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
from database import has_product_id, upsert_contents_for_product_id,has_review_id


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

    def process_reviews(self, rs, checker, item_id):
        """
        Inputs: Amazon Reviews object, and a filehandle.
        Output: Returns number of reviews processed. Writes reviews to file.
        """

        sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

        count = 0
        output_str = ""
        contents = []
        review_ids = []
        ratings =[]
        for r in rs.full_reviews():
            try:
                if self.debug:
                    logging.debug(
                        "{} | {} | {}".format(
                            r.id, r.date, self._encode_safe(
                                r.text)))
                if r.text != "None":
                    if checker: # if we need to check reviewID 
                        if has_review_id(item_id,r.id):
                            print 'scraped review is passed as it is in db'
                            continue 
                        else: 
                            count += 1
                            sentenceContent_list = getSentencesFromReview(self._encode_safe(r.text))
                            print "First sentence: " + sentenceContent_list[0]
                            for content in sentenceContent_list:
                                contents.append(content)
                            review_ids.append(r.id)
                            ratings.append(float(r.rating)*5) # rating directly from API is normalized to 1
                    else: #don't need to check reviewID
                        count += 1
                        sentenceContent_list = getSentencesFromReview(self._encode_safe(r.text))
                        print "First sentence: " + sentenceContent_list[0]
                        for content in sentenceContent_list:
                            contents.append(content)
                        review_ids.append(r.id)
                        ratings.append(float(r.rating)*5) # rating directly from API is normalized to 1
            except:
                logging.warn(
                    'Encoding problem with review {}'.format(
                        r.id))

        return count, contents, review_ids, ratings

    def scrape_reviews(self, item_id, checker=False):
        """
        Fetches reviews for the Amazon product with the specified ItemId. 
        """

        start = time.time()
        p = self.amzn.lookup(ItemId=item_id)
        rs = self.amzn.reviews(URL=p.reviews_url)
        count = 0
        page_count = 0
        contents = []
        review_ids =[]
        ratings = []
        while True:
            page_count += 1
            result_tup = self.process_reviews(rs,checker,item_id)
            count += result_tup[0]
            contents.extend(result_tup[1])
            review_ids.extend(result_tup[2])
            ratings.extend(result_tup[3])

            rs = self.amzn.reviews(URL=rs.next_page_url)
            if not rs.next_page_url:
                result_tup = self.process_reviews(rs,checker,item_id)
                count += result_tup[0]
                contents.extend(result_tup[1])
                review_ids.extend(result_tup[2])
                ratings.extend(result_tup[3])
                break
            print "page_count: {0}".format(page_count)

            # if page_count%3 == 0:
            #     print "page_count%3 == 0: {0}".format(page_count)
            #     upsert_contents_for_product_id(item_id, contents)
                
        end = time.time()
        logging.info(
            "Collected {} reviews for item {} in {} seconds".format(
                count,
                item_id,
                end -
                start))
        return contents,review_ids,ratings

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

def getWebPage(productID):
    from lxml import html
    import requests
    from fake_useragent import UserAgent #install at: https://pypi.python.org/pypi/fake-useragent
    from time import sleep
    import random
    url = "http://www.amazon.com/dp/" + productID
    print "Processing: " + url
    ua = UserAgent()
    headers = {
        # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        'User-Agent': ua.random}
        # get user agent: http://www.whoishostingthis.com/tools/user-agent/ 
        # or generate random one: https://pypi.python.org/pypi/fake-useragent
    page = requests.get(url, headers=headers)
    while True:
        sleep(int(random.random()*2+1)) # this is important not to be identified as Amazon
        try: 
            doc = html.fromstring(page.content)
            return doc
        except Exception as e:
            print e

def scrape_reviews_hard(productID,checker=False):
    '''
    This method scraps directly from website and does not need userID or the AmazonScrape object
    However, it can only scrape the 5 top ranked review. 
    '''
    try: 
        doc = getWebPage(productID)
        XPATH_RATINGS = '//div[contains(@id, "rev-dpReviewsMostHelpfulAUI")]/div/div/a/i/span//text()'
        XPATH_REVIEWS_BODY = '//div[contains(@id, "revData-dpReviewsMostHelpfulAUI")]/div//text()'
        XPATH_REVIEWS_IDS = '//div[contains(@id, "rev-dpReviewsMostHelpfulAUI")]/a[2]/@id'
        RAW_RATINGS = doc.xpath(XPATH_RATINGS)
        ratings = [x[:3] for x in RAW_RATINGS] #remove the rest of the string 
        RAW_REVIEWS_BODY = doc.xpath(XPATH_REVIEWS_BODY)
        RAW_REVIEWS_IDS = doc.xpath(XPATH_REVIEWS_IDS)
        review_ids = [x[:x.index(".")] for x in  RAW_REVIEWS_IDS] #remove the rest of the string 
        REVIEWS_BODY = ' '.join(RAW_REVIEWS_BODY).strip() if RAW_REVIEWS_BODY else None            
        reviews_text  = REVIEWS_BODY.encode('utf-8')
        contents = getSentencesFromReview(reviews_text.decode('utf-8'))

        if checker:
            for i in range(len(review_ids)):
                ind_new_review = []
                if not has_review_id(productID,review_ids[i]):
                    ind_new_review.append(i)
            if len(ind_new_review)>0:
                print('new reviews available from scrape_reviews_hard')
                contents = [contents[j] for j in ind_new_review]
                review_ids = [review_ids[j] for j in ind_new_review]
                ratings = [ratings[j] for j in ind_new_review]
                print review_ids

        return contents,review_ids,ratings
    except: 
        return scrape_reviews_hard(productID,checker)

def scrape_number_review(productID):
    '''
    return total number of reviews 
    '''
    try: 
        doc = getWebPage(productID)
        XPATH_TOTAL_REVIEW = '//div[contains(@id, "averageCustomerReviews")]/span[3]/a/span/text()'
        RAW_TOTAL_REVIEW = doc.xpath(XPATH_TOTAL_REVIEW)
        ind = RAW_TOTAL_REVIEW[0].index('c')

        number_review = RAW_TOTAL_REVIEW[0][:ind-1] # example: 1,029 customer reviews 
        return int(number_review.replace(',', '')) 
    except: 
        # reinitiate if failed
        print 'scraper failed, reinitiate'
        return scrape_number_review(productID)

def main(amazonScraper, product_id, checker=False):
    number_review = scrape_number_review(product_id)
    if has_product_id(product_id):
        print "{0} is already scraped...scrape for more".format(product_id)
        # scrape contents while checking for conflict review 
        checker = True

    try: 
        contents,review_ids,ratings = amazonScraper.scrape_reviews(product_id,checker)
        return contents,review_ids,ratings,number_review
    except:
        # backup scraper 
        print 'Amazon API failed. Scrape the hard way!'
        contents,review_ids,ratings = scrape_reviews_hard(product_id,checker)
        return contents,review_ids,ratings,number_review


if __name__ == "__main__":
    # function testing 
    productID = 'B00THKEKEQ' # B00I8BICB2 sony a6000 with 686 reviews,B00T85PH2Y,B00HZE2PYI,B00C7NX884
    a = createAmazonScraper()   
    result = main(a,productID)
    print result
    print scrape_number_review(productID)
    # print scrape_reviews_hard(productID)