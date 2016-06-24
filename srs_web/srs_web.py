from flask import Flask, url_for, request, redirect, render_template, send_file
from srs.sentiment_plot import sentimentBoxPlot, sentimentBoxPlot_Compare
from srs.srs_local import fill_in_db
from srs.utilities import loadScraperDataFromDB
from srs.scraper import createAmazonScraper
import json
import numpy as np

from bokeh.embed import file_html, components

app = Flask(__name__)

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/scrape_reviews', methods=['GET', 'POST'])
def scrape_reviews():
	if request.method == 'POST':
		product_id = request.form["product_id"]
		product_id2 = request.form["product_id2"]
		if not product_id2:		
			print 'product_id is ' + product_id			
			a = createAmazonScraper()
			fill_in_db(a, product_id)
			return str(product_id)
		else:
			print 'product_id are ' + product_id	+ ' and '+ product_id2
			a = createAmazonScraper()
			fill_in_db(a, product_id)
			fill_in_db(a, product_id2)
			return str(product_id) + "&" + str(product_id2)

	else:
		return render_template('home.html')

@app.route('/srs_result/<product_id>')
def showResultWithProductId(product_id): #B00HZE2PYI
	
	_, ft_score_dict, _ = loadScraperDataFromDB(product_id)
	ft_score_ave = []
	for ft in ft_score_dict:
		average_score = np.mean(np.array(ft_score_dict[ft]))
		ft_score_ave.append({"feature": ft, "score":average_score})

	return render_template('srs_result_bar.html', ft_score_ave=json.dumps(ft_score_ave))

@app.route('/srs_result_box/<product_id>')
def showBoxResultWithProductId(product_id): #B00HZE2PYI
	
	_, ft_score_dict, _ = loadScraperDataFromDB(product_id)
	ft_scorelist = []
	for ft in ft_score_dict:
		ft_scorelist.append([ft, ft_score_dict[ft]])

	return render_template('srs_result_box.html', ft_scorelist=json.dumps(ft_scorelist))

@app.route('/srs_result_box_bokeh/<product_id>')
def showBokehBoxResultWithProductId(product_id):
	# generate data for plotting

@app.route('/srs_result_box_bokeh/<product_id>&<product_id2>')
def showBokehBoxResultWithTwoProductIds(product_id, product_id2):
	# generate data for plotting
	_, ft_score_dict, _ = loadScraperDataFromDB(product_id)
	_, ft_score_dict2, _ = loadScraperDataFromDB(product_id2)

	# do plotting
	plots = sentimentBoxPlot_Compare(ft_score_dict, ft_score_dict2)

	# create the HTML elements to pass to template
	figJS,figDivs = components(plots)
	return render_template('srs_result_box_bokeh.html', figJS=figJS,figDiv=figDivs[0],figDiv2=figDivs[1])

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=80)