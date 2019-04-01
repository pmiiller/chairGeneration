# generate new positive and negative chair data
import cv2 
import numpy as np
import os, os.path
import random

from makePositive import makePositiveData
from makeNegative import makeNegativeData
  
generatePositive = 50 # generate generatePositive*3 images
generateNegative = 100 # generate generateNegative*3 images

indir = '..\LeChairs\chairs-data\positive'

# get random number of a set of front, side and top images
def makeRandNum():

    list = os.listdir(indir) 
    number_files = len(list)

    number_sets = number_files/3

    setNum = random.randint(0,number_sets)
    return setNum


    

for x in range(generatePositive):
    print('generating positive case number ',x*3)
    num = makeRandNum()
    makePositiveData(x,num,indir)
    
for i in range(generateNegative):
    print('generating negative case number ',i*3)
    num = makeRandNum()
    makeNegativeData(i,num,indir)

