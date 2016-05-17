from flask import Flask, url_for, request, redirect, render_template, send_file
from srs.scraper import main as scraper_main
from srs.swnModel import swnModel

app = Flask(__name__)

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/scrape_reviews', methods=['GET', 'POST'])
def scrape_reviews():
	if request.method == 'POST':
		product_id = request.form["product_id"]
		print 'product_id is ' + product_id

		scraper_main(product_id)

		# prepare static predictor params  
		params_file = '../srs/predictor_data/lambda_opt_regu2.txt'
		wordlist_dict_path = '../srs/predictor_data/wordlist_dict_1.txt'
		
		# sentiment analysis and plot
		plot_folder = "../srs/sentiment_plot/"
		figure_filename = plot_folder + product_id + '_boxplot.png'
		swnModel(params_file,wordlist_dict_path,figure_filename,product_id)

		return product_id
	else:
		return render_template('home.html')

@app.route('/srs_result/<product_id>')
def showResultWithProductId(product_id): #B00HZE2PYI
    plot_file = "../srs/sentiment_plot/%s_boxplot.png" % product_id
    return send_file(plot_file, mimetype='image/png')



if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=80)