# reading a set of images from positive set and output a positive set of images
# implemented:
#   - erode and dilate through open cv methods
# can be improved:
#   - scaling
#   - rotating

import cv2 
import numpy as np
import os, os.path
import random


def makePositiveData(outputNumber,setNumber,indir):
  
    # Reading random input image from positive set ============================

    setNum = int(setNumber)

    
    imgFile1 = indir + '\\' +str(setNum*3+1)+'.bmp'
    imgFile2 = indir + '\\' +str(setNum*3+2)+'.bmp'
    imgFile3 = indir + '\\' +str(setNum*3+3)+'.bmp'


    img1 = cv2.imread(imgFile1, 0)
    img2 = cv2.imread(imgFile2, 0)
    img3 = cv2.imread(imgFile3, 0)

    # Taking a matrix of size 5 as the kernel =============================
    #kernel = np.ones((5,5), np.uint8)
    kernel = np.ones((5,5), np.uint8) 
      
    # The first parameter is the original image, 
    # kernel is the matrix with which image is  
    # convolved and third parameter is the number  
    # of iterations, which will determine how much  
    # you want to erode/dilate a given image.

    num = random.randint(0,2)
    if num == 1:
        #print('making erotion of image') # made thick
        processedImg1 = cv2.erode(img1, kernel, iterations=1)
        processedImg2 = cv2.erode(img2, kernel, iterations=1)
        processedImg3 = cv2.erode(img3, kernel, iterations=1)
    else:
        #print('making dilation of image') # made thin
        processedImg1 = cv2.dilate(img1, kernel, iterations=1)
        processedImg2 = cv2.dilate(img2, kernel, iterations=1)
        processedImg3 = cv2.dilate(img3, kernel, iterations=1) 
      
    #cv2.imshow('Front', processedImg1) 
    #cv2.imshow('Side', processedImg2) 
    #cv2.imshow('Top', processedImg3)  


    outputNum = outputNumber*3+1 

    outFile1 = 'output\\positive\\img'+ str(outputNum)+ '.bmp'
    outFile2 = 'output\\positive\\img'+ str(outputNum+1)+ '.bmp'
    outFile3 = 'output\\positive\\img'+ str(outputNum+2)+ '.bmp'

    cv2.imwrite(outFile1,processedImg1)
    cv2.imwrite(outFile2,processedImg2)
    cv2.imwrite(outFile3,processedImg3)

      
    #cv2.waitKey(0)

    return

