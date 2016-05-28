from flask import Flask, url_for, request, redirect, render_template, send_file
from srs.scraper import main as scraper_main
from srs.scraper import isProductScraped
from srs.swnModel import main as swnModel_main
from srs import settings
import os
import json

app = Flask(__name__)

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/scrape_reviews', methods=['GET', 'POST'])
def scrape_reviews():
	if request.method == 'POST':
		product_id = request.form["product_id"]
		print 'product_id is ' + product_id

		scrapeFlag = True
		if isProductScraped(product_id):
			print "scraped before for {0}".format(product_id)
			scrapeFlag = False
		
		# scrap data
		if scrapeFlag:
			scraper_main(product_id)
		
		return product_id
	else:
		return render_template('home.html')

@app.route('/srs_result/<product_id>')
def showResultWithProductId(product_id): #B00HZE2PYI
	
	ft_score, _ = swnModel_main(product_id)
	return render_template('srs_result_bar.html', ft_score=json.dumps(ft_score))

@app.route('/srs_result_box/<product_id>')
def showBoxResultWithProductId(product_id): #B00HZE2PYI
	
	_, ft_scorelist = swnModel_main(product_id)

	return render_template('srs_result_box.html', ft_scorelist=json.dumps(ft_scorelist))


if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=80)