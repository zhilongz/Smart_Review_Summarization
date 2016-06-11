from pymongo import MongoClient
from srs import settings
import os

def connect_to_db():
	client = MongoClient('localhost', 27017)
	db = client['srs']
	return client, db

def disconnect_db(client):
	client.close()

def load_db_from_files():
	client, db = connect_to_db()
	product_collection = db.product_collection

	# read files in scraper_data
	scraper_data = settings['scraper_data']
	for file0 in os.listdir(scraper_data):
		if file0.endswith('.txt'):
			product_id = file0[:-4]
			contents = []
			with open(os.path.join(scraper_data, file0), 'r') as file0_open:
				for line in file0_open:
					# get contents for each product
					contents.append(line)

			# create a document to insert
			product_document = {
			"product_id":product_id,
			"contents": contents,
			"ft_score": {},
			"ft_senIdx": {}
			}
			
			# insert
			product_collection.save(product_document)

	disconnect_db(client)

def has_product_id(product_id):
	client, db = connect_to_db()
	query_res = list(db.product_collection.find({"product_id": product_id}))
	disconnect_db(client)
	
	return len(query_res) > 0

def select_for_product_id(product_id):
	client, db = connect_to_db()
	query_res = list(db.product_collection.find({"product_id": product_id}))
	disconnect_db(client)

	return query_res

def insert_for_product_id(product_id, contents, ft_score=None, ft_senIdx=None):
	if ft_score is None:
		ft_score = {}
	if ft_senIdx is None:
		ft_senIdx = {}

	# create a document to insert
	product_document = {
	"product_id":product_id,
	"contents": contents,
	"ft_score": ft_score,
	"ft_senIdx": ft_senIdx
	}

	client, db = connect_to_db()
	product_collection = db.product_collection

	# insert
	product_collection.save(product_document)
	client.close()

def upsert_contents_for_product_id(product_id, contents, ft_score=None, ft_senIdx=None):
	if ft_score is None:
		ft_score = {}
	if ft_senIdx is None:
		ft_senIdx = {}

	client, db = connect_to_db()
	product_collection = db.product_collection

	query = {"product_id": product_id}
	update_field = {
	"contents": contents,
	"ft_score": ft_score, 
	"ft_senIdx":ft_senIdx
	}
	product_collection.update(query, {"$set": update_field}, True)

	client.close()

def update_for_product_id(product_id, ft_score, ft_senIdx):

	client, db = connect_to_db()
	product_collection = db.product_collection

	query = {"product_id": product_id}
	update_field = {"ft_score": ft_score, "ft_senIdx":ft_senIdx}
	product_collection.update(query, {"$set": update_field}, True)

	client.close()


if __name__ == '__main__':
	load_db_from_files()

