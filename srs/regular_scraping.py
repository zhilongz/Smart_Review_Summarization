from amazon.api import AmazonAPI
from scraper import getAmazomConfidentialKeys, createAmazonScraper
from database import has_product_id
from srs_local import fill_in_db
import time

def getTopProductIDs(keywords="camera", searchIndex='Electronics'):
	AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG = \
	getAmazomConfidentialKeys()

	amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)
	products = amazon.search(Keywords=keywords, SearchIndex=searchIndex)

	productIDs = []
	for i, product in enumerate(products):
		productIDs.append(product.asin)

	return productIDs

def regularScraping():
	a = createAmazonScraper()
	productIDs = getTopProductIDs()
	for productID in productIDs:
		print "Scraping reviews for {0}".format(productID)
		new_productID = fill_in_db(a, productID)
		if new_productID:
			time.sleep(7200)

if __name__ == '__main__':
	regularScraping()
        