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
import json


def loadWordListDict(wordlist_dict_path):
    wordlist_dict = json.load(open(wordlist_dict_path, 'r'))

    return wordlist_dict

def eval_f_vec(sentence, wordlist_dict): 
    """
    sentence: a single labelled sentence obj 
    returns a vector of length len(wordlist_dict)
    """
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
            try:
                stemmedWord = stemmer.stem(word)
            except:
                print word
            word_list[i] = stemmedWord

        sentence.tokens = word_list

    len_word = max(len(word_list),1)*1.0;
    
    f_vec = []
    static_aspect_list = sorted(wordlist_dict.keys())
    for key in static_aspect_list:
        count = 0
        for represent_word in wordlist_dict[key]:
            count += word_list.count(represent_word)
        f_vec.append(count/len_word)
    
    return f_vec
        
def cond_prob(lam_vec, wordlist_dict, static_aspect_list,sentence, isTraining=True): 
    """ 
    lam_vec: lambda as a vector  
    static_aspect_list: list of all static features 
    sentence: input sentence 
        
    returns the conditional probability for all class (a vector)
    """
    f = eval_f_vec(sentence, wordlist_dict)
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

def loss_func(lam_vec,wordlist_dict, static_aspect_list,ls_list):
    """ 
    loss function
    First argument is parameter vector to be optimized  
    """ 

    loss = 0
    for ls in ls_list: 
        f = eval_f_vec(ls, wordlist_dict)
        f_len = len(f)
        
        labeled_aspect_idx = 0
        deno = 0
        for aspect_idx in range(len(static_aspect_list)):
            c = static_aspect_list[aspect_idx]
            if c == ls.labeled_aspects:
                labeled_aspect_idx = static_aspect_list.index(c)
                deno = deno + np.exp(np.inner(lam_vec[labeled_aspect_idx*f_len:(labeled_aspect_idx+1)*f_len],f))
            else:
                deno = deno + 1
        
        loss_sent = np.inner(lam_vec[labeled_aspect_idx*f_len:(labeled_aspect_idx+1)*f_len],f) - np.log(deno)
        loss = loss + loss_sent

    regularization_term = 0
    for lam in lam_vec:
        regularization_term += abs(lam)
    regularization_term = regularization_term*1e-1


    print loss*(-1) + regularization_term   
    return loss*(-1) + regularization_term

def generateInitialGuess(lambda_len, static_aspect_list_len=None):
    if static_aspect_list_len:
        lambda_guess = np.zeros(lambda_len)
        for i in range(static_aspect_list_len):
            diagonal_idx = i + static_aspect_list_len*i
            lambda_guess[diagonal_idx] = np.random.randn()
    else:
        lambda_guess = np.random.rand(lambda_len)

    return lambda_guess

def train(wordlist_dict, static_aspect_list,ls_list,lambda_len):
    """ optimization by minimizing the loss function returns lambda* """
    lambda_guess = generateInitialGuess(lambda_len, len(static_aspect_list))
    res = minimize(loss_func, lambda_guess, args=(wordlist_dict, static_aspect_list,ls_list), \
        method='BFGS', options={'gtol': 1e-2, 'disp': True, 'maxiter': 300})
    return res
    """
    see for list of method: http://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.optimize.minimize.html
    """

    
    
