#!/bin/bash

#$ -l h_rt=02:00:00
#$ -l mem_total=2G
#$ -l normal
#$ -pe singlenode 1
#$ -N training

TRAINING_LOG_FOLDER=training_results
VERSION_NUM=3

python predictor.py -vn $VERSION_NUM > $TRAINING_LOG_FOLDER/training_$VERSION_NUM.out