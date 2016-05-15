from flask import Flask, url_for, request, redirect, render_template
from srs.scraper import main as scraper_main

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

		return str(12)
	else:
		return render_template('home.html')



if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=80)