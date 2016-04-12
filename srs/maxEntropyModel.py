# -*- coding: utf-8 -*-
"""
Created on Sat Mar 19 10:46:46 2016

@author: zhilong21, kehang
"""

import numpy as np
from scipy.optimize import minimize 
from nltk.tokenize import sent_tokenize, word_tokenize
import re
from nltk.stem import SnowballStemmer
from utilities import Sentence


def loadDynamicAspectList():
    #load a list of features words extracted and acts as the dynamic aspect. The length of this list will determine the size of the model
    dynamic_aspect_list = [u'camera', u'pictur', u'batteri', u'qualiti', \
    u'zoom', u'shot', u'time', u'lif', u'photo', u'featur', u'memori', \
    u'card', u'imag', u'review', u'flash', \
    u'resolut', u'set', u'cabl', u'problem', u'screen', \
    u'adapt', u'size', u'photograph', \
    u'light', u'softwar', u'pic', u'screen', u'price', u'mode', \
    u'scene', u'color', u'point', u'angl',u'button', u'port']
    return dynamic_aspect_list

def eval_f_vec(sentence): 
    """
    sentence: a single labelled sentence obj 
    returns a vector of length len(dynamic_aspect_list)
    """
    dynamic_aspect_list = loadDynamicAspectList()   

    word_list = []
    if sentence.tokens != []:
        word_list = sentence.tokens
    else:
        # process sentence to a list of word without punctuation and number
        word_list = word_tokenize(sentence.content)
        punctuation = re.compile(r'[-.?!,":;()|0-9]') # remove these punctuations and number 
        word_list = [punctuation.sub("", word) for word in word_list]  
        word_list = filter(None, word_list) #filters empty 
        # stem process for word_list
        stemmer = SnowballStemmer('english')
        for i in range(len(word_list)):
            word = word_list[i]
            stemmedWord = stemmer.stem(word)
            word_list[i] = stemmedWord

        sentence.tokens = word_list

    len_word = max(len(word_list),1)*1.0;
    
    f_vec = []
    for w in dynamic_aspect_list:
        f_vec.append(word_list.count(w)/len_word)
    
    return f_vec
        
def cond_prob(lam_vec,static_aspect_list,sentence, isTraining=True): 
    """ 
    lam_vec: lambda as a vector  
    static_aspect_list: list of all static features 
    sentence: input sentence 
        
    returns the conditional probability for all class (a vector)
    """
    f = eval_f_vec(sentence)
    f_len = len(f)

    numerators = []
    deno = 0.0
    if isTraining:
        labeled_aspect = sentence.labeled_aspects
        for aspect0 in static_aspect_list:
            numerator = 1
            if aspect0 == labeled_aspect:
                labeled_aspect_idx = static_aspect_list.index(labeled_aspect) 
                numerator = np.exp(np.inner(lam_vec[labeled_aspect_idx*f_len:(labeled_aspect_idx+1)*f_len],f))
            numerators.append(numerator)
            deno += numerator
    else:
        for aspect_idx in range(len(static_aspect_list)):
            numerator = np.exp(np.inner(lam_vec[aspect_idx*f_len:(aspect_idx+1)*f_len],f))
            numerators.append(numerator)
            deno += numerator

    cp = []
    for numerator in numerators:
        cp.append(numerator/deno)

    return cp 

def loss_func(lam_vec,static_aspect_list,ls_list):
    """ 
    loss function
    First argument is parameter vector to be optimized  
    """ 

    loss = 0
    for ls in ls_list: 
        f = eval_f_vec(ls)
        f_len = len(f)
        
        labeled_aspect_idx = 0
        deno = 0
        for aspect_idx in range(len(static_aspect_list)):
            c = static_aspect_list[aspect_idx]
            if c == ls.labeled_aspects:
                labeled_aspect_idx = static_aspect_list.index(c)
                deno = deno + np.exp(np.inner(lam_vec[labeled_aspect_idx*f_len:(labeled_aspect_idx+1)*f_len],f))
            deno = deno + 1
        
        loss_sent = np.inner(lam_vec[labeled_aspect_idx*f_len:(labeled_aspect_idx+1)*f_len],f) - np.log(deno)
        loss = loss + loss_sent

    print loss*(-1)    
    return loss*(-1)

def train(static_aspect_list,ls_list,lambda_len):
    """ optimization by minimizing the loss function returns lambda* """
    lambda_guess = np.random.rand(lambda_len)*0.1
    res = minimize(loss_func, lambda_guess, args=(static_aspect_list,ls_list), method='BFGS', options={'gtol': 1e-3, 'disp': True})
    return res
    """
    see for list of method: http://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.optimize.minimize.html
    """

def loadTrainingData():
    import os
    static_traning_data_dir = os.path.abspath('static_training_data/')
    sentences = []
    for data_file in os.listdir(static_traning_data_dir):
        if data_file.endswith('labeled.txt'):
            sentences.extend(load_labelled_sent(os.path.join(static_traning_data_dir, data_file)))
    return sentences

def load_labelled_sent(file_name): 
    with open(file_name) as f:
        ls_list =[]
        for line in f.readlines():
            line_splitted = line.split('***')
            ls_list.append(Sentence(content=line_splitted[1],labeled_aspects=line_splitted[0]))
    return ls_list 

def main():
    # load a list of features words extracted and acts as the dynamic aspect. The length of this list will determine the size of the model
    dynamic_aspect_list = loadDynamicAspectList()

    # load a list of classes (static aspect)
    static_aspect_list = ['price','pictures','video','zoom','size','design','battery','screen','detection','ease of use','quality','other features','no feature']
    
    # load labeled sentences as a list of labeled_sent
    ls_list = load_labelled_sent('static_training_data/B00B7O2Z42_labeled.txt')
    
    # train 

    n = len(dynamic_aspect_list)*len(static_aspect_list)
    res = train(static_aspect_list,ls_list[:180],n)
    
    lambda_star = res.x 
    print 'The lambda is: \n'
    print lambda_star
    
    #load unlabeled testing data (TBD) 
    uls_list = ls_list[180:]    
    
    #validation 
    correct = 0.0
    for uls in uls_list:
        cp = cond_prob(lambda_star,static_aspect_list,uls, isTraining=False)
        predicted_class_index = cp.index(max(cp)) 
        if static_aspect_list[predicted_class_index] == uls.labeled_aspects:
            correct += 1
    
    class_error = 1.0 - correct/len(uls_list)
    print 'The classification error is: %.2f' % (class_error)

def testcase():
    # load a list of classes (static aspect)
    static_aspect_list = ['price','pictures','video','zoom','size','design','battery','screen','detection','ease of use','quality','other features','no feature']
    
    # load labeled sentences as a list of labeled_sent
    ls_list = load_labelled_sent('static_training_data/B00B7O2Z42_labeled.txt')
    print loadDynamicAspectList()
    print eval_f_vec(ls_list[1])
    print static_aspect_list[1]
    print len(ls_list)

if __name__ == '__main__':
    testcase()

    
    
