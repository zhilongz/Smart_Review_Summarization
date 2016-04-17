#!/bin/bash

#$ -o training.out
#$ -e training.err
#$ -l h_rt=02:00:00
#$ -l mem_total=2G
#$ -l normal
#$ -pe singlenode 1
#$ -N training

python predictor.py 