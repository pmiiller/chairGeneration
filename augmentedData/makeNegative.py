# reading a set of images from positive set and output negative cases
# implemented:
#   - random cut in image
# can be improved:
#   - replace part of image with random part of other images
import cv2 
import numpy as np
import os, os.path
import random



def makeNegativeData(outputNumber,setNumber,indir):

    # Reading input image from positive set 

    setNum = int(setNumber)

    imgFile1 = indir + '\\' +str(setNum*3+1)+'.bmp'
    imgFile2 = indir + '\\' +str(setNum*3+2)+'.bmp'
    imgFile3 = indir + '\\' +str(setNum*3+3)+'.bmp'


    img1 = cv2.imread(imgFile1, 0)
    img2 = cv2.imread(imgFile2, 0)
    img3 = cv2.imread(imgFile3, 0)



    height = np.size(img1, 0) #224
    width = np.size(img1, 1) #224

    #print('height = ',height,'width = ',width)



    # modify front view:

    randX1 = random.randint(int(width/4),int(width/2))
    randX2 = random.randint(int(width/2),int(width*3/4))
    randY1 = random.randint(height/4,height/2)
    randY2 = random.randint(height/2,height*3/4)


    cv2.rectangle(img1, (randX1, randY1), (randX2,randY2), (255,255,255), -2)
    #cv2.imshow('Front', img1)


    # modify side view:

    randX1 = random.randint(int(width/4),int(width/2))
    randX2 = random.randint(int(width/2),int(width*3/4))
    randY1 = random.randint(height/4,height/2)
    randY2 = random.randint(height/2,height*3/4)


    cv2.rectangle(img2, (randX1, randY1), (randX2,randY2), (255,255,255), -2)
    #cv2.imshow('Side', img2)


    # modify top view: 

    randX1 = random.randint(int(width/4),int(width/2))
    randX2 = random.randint(int(width/2),int(width*3/4))
    randY1 = random.randint(height/4,height/2)
    randY2 = random.randint(height/2,height*3/4)


    cv2.rectangle(img3, (randX1, randY1), (randX2,randY2), (255,255,255), -2)
    #cv2.imshow('Top', img3)



    # outputting images

    outputNum = outputNumber*3+1 

    outFile1 = 'output\\negative\\img'+ str(outputNum)+ '.bmp'
    outFile2 = 'output\\negative\\img'+ str(outputNum+1)+ '.bmp'
    outFile3 = 'output\\negative\\img'+ str(outputNum+2)+ '.bmp'

    cv2.imwrite(outFile1,img1)
    cv2.imwrite(outFile2,img2)
    cv2.imwrite(outFile3,img3)

      
    #cv2.waitKey(0)
    return

