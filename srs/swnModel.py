from nltk.corpus import sentiwordnet as swn
from predictor import StaticPredictor
from utilities import loadTrainingData
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np 

def sentence_score(ls):
    '''
    input type sentence
    this method estimate a score for the sentence based on the swn model 
    '''
    from nltk.tokenize import word_tokenize
    import re
    word_list = word_tokenize(ls.content)
    punctuation = re.compile(r'[-.?!,":;()|0-9]') # remove these punctuations and number 
    word_list = [punctuation.sub("", word) for word in word_list]  
    word_list = filter(None, word_list) #filters empty         
    ls.tokens = word_list

    pos_score = 0.0
    neg_score = 0.0
    num_valid_word = 0.1
    for w in word_list:
        res = swn.senti_synsets(w)
        if res: # if not empty 
            pos_score += res[0]._pos_score
            neg_score += res[0]._neg_score
            num_valid_word += 1
    ls.score = (pos_score - neg_score)/num_valid_word
    
    """
    documentation on swn: http://www.nltk.org/_modules/nltk/corpus/reader/sentiwordnet.html
    """

def get_prod_score(prodReview,staticPredictor):
	'''
	prodReview: a list of sentence object
	staticPredictor object
	return a list of individual score sorted for each static aspect via a dictionary
	'''
	aspect_list_useful = staticPredictor.staticAspectList[:-1]
	myDic = defaultdict(list)
	for ls in prodReview:
		ls.static_aspect = staticPredictor.predict(ls)
		sentence_score(ls)
		for ft in aspect_list_useful:
	            if ft == ls.static_aspect:
	                myDic[ft].append(ls.score)

	myList = []
	for ft in aspect_list_useful:
		myList.append(myDic[ft])

	return myList 

# function for setting the colors of the box plots pairs
def set_box_color(bp, color):
    plt.setp(bp['boxes'], color=color)
    plt.setp(bp['whiskers'], color=color,alpha=0)
    plt.setp(bp['caps'], color=color,alpha=0)
    plt.setp(bp['medians'], color=color,alpha=0)


staticPredictor = StaticPredictor()
params_file = 'predictor_data/lambda_opt_regu2.txt'
staticPredictor.loadParams(params_file)
wordlist_dict_path = 'predictor_data/wordlist_dict_1.txt'
staticPredictor.loadWordListDict(wordlist_dict_path)
# staticPredictor.loadStaticAspectList(static_aspect_list_file)

#load reviews 
static_training_data_dir = 'static_training_data/'
allReviews = loadTrainingData(static_training_data_dir)
prod1Review = allReviews[0:600]
prod2Review = allReviews[601:1200]

prod1Dic = get_prod_score(prod1Review,staticPredictor)
prod2Dic = get_prod_score(prod2Review,staticPredictor)

ticks = staticPredictor.staticAspectList[:-1]

plt.figure(figsize=(7, 7))

bpl = plt.boxplot(prod1Dic, positions=np.array(xrange(len(prod1Dic)))*2.0-0.4, sym='', widths=0.6)
#bpr = plt.boxplot(prod2Dic, positions=np.array(xrange(len(prod2Dic)))*2.0+0.4, sym='', widths=0.6)
set_box_color(bpl, '#D7191C') # colors are from http://colorbrewer2.org/
#set_box_color(bpr, '#2C7BB6')

plt.plot([], c='#D7191C', label='Product 1')
#plt.plot([], c='#2C7BB6', label='Product 2')
plt.legend()

locs, labels = plt.xticks(xrange(0, len(ticks) * 2, 2), ticks)
plt.xlim(-2, len(ticks)*2)
plt.setp(labels, rotation=90)
#plt.ylim(-0.5, 0.5)
plt.axhline(y=0.0,xmin=0,xmax=3,c="blue",linewidth=0.5,zorder=0)
plt.tight_layout()
plt.savefig('boxcompare1.png')


