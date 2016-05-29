from nltk.corpus import sentiwordnet as swn
from predictor import StaticPredictor
from utilities import loadScraperDataFromFile
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as plt
import numpy as np
import os
from srs import settings

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
        try:
            res = swn.senti_synsets(w)
            pos_score += res[0]._pos_score
            neg_score += res[0]._neg_score
            num_valid_word += 1
        except:
            pass
            
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
    score_dict = defaultdict(list)
    for ls in prodReview:
        ls.static_aspect = staticPredictor.predict(ls) # predict the static aspect
        sentence_score(ls)
        for ft in aspect_list_useful:
            if ft == ls.static_aspect:
                score_dict[ft].append(ls.score)

    return score_dict 

# function for setting the colors of the box plots pairs
def set_box_color(bp, color):
    plt.setp(bp['boxes'], color=color)
    plt.setp(bp['whiskers'], color=color,alpha=0)
    plt.setp(bp['caps'], color=color,alpha=0)
    plt.setp(bp['medians'], color=color,alpha=0)

def box_plot(prod1score,filename,prod1ID):
    ticks = prod1score.keys()
    
    prod1score_list = []
    for ft in ticks:
        prod1score_list.append(prod1score[ft])

    plt.figure(figsize=(7, 7))

    bpl = plt.boxplot(prod1score_list, positions=np.array(xrange(len(ticks)))*2.0, sym='', widths=0.6)
    set_box_color(bpl, '#D7191C') # colors are from http://colorbrewer2.org/

    plt.plot([], c='#D7191C', label=prod1ID)
    plt.legend()

    locs, labels = plt.xticks(xrange(0, len(ticks) * 2, 2), ticks)
    plt.xlim(-2, len(ticks)*2)
    plt.setp(labels, rotation=90)
    plt.axhline(y=0.0,xmin=0,xmax=3,c="blue",linewidth=0.5,zorder=0)
    plt.tight_layout()
    plt.savefig(filename)

def box_plot_compare(prod1score,prod2score,filename,prod1ID,prod2ID):
    ticks = prod1score.keys()
    
    prod1score_list = []
    for ft in ticks:
        prod1score_list.append(prod1score[ft])

    prod2score_list = []
    for ft in ticks:
        prod2score_list.append(prod2score[ft])

    plt.figure(figsize=(7, 7))

    bpl = plt.boxplot(prod1score_list, positions=np.array(xrange(len(ticks)))*2.0-0.4, sym='', widths=0.6)
    bpr = plt.boxplot(prod2score_list, positions=np.array(xrange(len(ticks)))*2.0+0.4, sym='', widths=0.6)
    set_box_color(bpl, '#D7191C') # colors are from http://colorbrewer2.org/
    set_box_color(bpr, '#2C7BB6')

    plt.plot([], c='#D7191C', label=prod1ID)
    plt.plot([], c='#2C7BB6', label=prod2ID)
    plt.legend()

    locs, labels = plt.xticks(xrange(0, len(ticks) * 2, 2), ticks)
    plt.xlim(-2, len(ticks)*2)
    plt.setp(labels, rotation=90)
    # plt.ylim(-0.5, 0.5)
    plt.axhline(y=0.0,xmin=0,xmax=3,c="blue",linewidth=0.5,zorder=0)
    plt.tight_layout()
    plt.savefig(filename)

def swnModel(params_filename, wordlist_filename, figure_file_path, prod1ID, prod2ID=None):
    staticPredictor = StaticPredictor()
    staticPredictor.loadParams(params_filename)
    staticPredictor.loadWordListDict(wordlist_filename)

    prod1_data_file_dir = os.path.join(
        settings['scraper_data'], 
        prod1ID + '.txt')
    prod1Review = loadScraperDataFromFile(prod1_data_file_dir)
    prod1score = get_prod_score(prod1Review,staticPredictor)
    
    if prod2ID == None:
        box_plot(prod1score,figure_file_path,prod1ID)
    else:
        prod2_data_file_dir = os.path.join(
            settings['scraper_data'], 
            prod2ID + '.txt')
        prod2Review = loadScraperDataFromFile(prod2_data_file_dir)
        prod2score = get_prod_score(prod2Review,staticPredictor)
        box_plot_compare(prod1score,prod2score,figure_file_path,prod1ID,prod2ID)

    return prod1score
    
def main(prod1ID):
    params_filename = 'lambda_opt_regu2.txt'
    wordlist_filename = 'wordlist_dict_1.txt'

    plot_folder = settings['sentiment_plot']
    figure_file_path = os.path.join(plot_folder, prod1ID + '_boxplot.png')
    return swnModel(params_filename,wordlist_filename,figure_file_path,prod1ID)

