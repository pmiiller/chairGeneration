# generates clusterings of parts based on the k medians method
# algorithm from CMPT459 
import cv2 
import numpy as np
import os, os.path
import random
import copy
import pickle

from main import calculateDeformationCost # import cost function from main

from main import loadTemplates

# num of max randomly chosen pairs of non mediod and mediod
# max number of meaningless tries
maxNeighbour = 10 
numlocal = 5 # number of initial points to attempt to select
k = 12 




def reAssignClusters(clusters,data):
    k = len(clusters)
    centroids = [[0 for i in range(1)] for j in range(k)]
    for i in range(k):
        centroids[i][0] = clusters[i][0]
        
    return assignClusters(k,centroids,data)

        

def assignClusters(k,centroids,data):
    #remove duplicates of centroid and data
    tmpdata = copy.deepcopy(data)

    for i in centroids:
        tmp = [m for m in tmpdata if (m.dir != i[0].dir or m.obj !=i[0].obj )]
        tmpdata = tmp


    #print(tmpdata)
    #print('tmpdata len = ',len(tmpdata))
    #print('data len = ',len(data))
    clusters = centroids
    # for each object in data assign it to nearest cluster


    for j in range(len(tmpdata)): # for each data
        minCost = 999
        c = 0
        for i in range(k):
            cost = calculateDeformationCost(tmpdata[j],clusters[i][0])
            
            if cost<minCost:
                minCost = cost
                c = i
                #print('cost=',cost,' c=',c,' minCost = ',minCost)
        clusters[c].append(tmpdata[j])

            

    return clusters


def singleTotalDistance(cluster):
    clen = len(cluster)
    count = 0
    for i in range(1,clen-1):
        count = count+calculateDeformationCost(cluster[0],cluster[i])
    return count


def totalDistance(clusters):
    cnum = len(clusters)
    count = 0
    for i in range(cnum):
        count = count+singleTotalDistance(clusters[i])
    return count




def kmedian(k, data):

    bestTD = 999999999
    bestClusters = []
    
    for r in range(numlocal):
        print('producing cluster--------------------------')

        # randomly select k parts as centroid and cluster
        centroids = [[0 for i in range(1)] for j in range(k)]
        # sample k values
        rdata = random.sample(data, k)
        for i in range(k):
            centroids[i][0] = rdata[i]
        clusters = assignClusters(k,centroids,data)


        #TD = # total distance of clustering
        TD = totalDistance(clusters)
        #print('TD = ',TD)
        
        i=0
        while i<maxNeighbour:
            # choosing a random cluster medoid and non medoid
            randk = random.randint(0,k-1)
            medoid = clusters[randk][0]
            randi = random.randint(0,len(clusters[randk])-1)
            nonMedoid = clusters[randk][randi]


            # calculate swap cost of switching medoid and non medoid
            clustersTemp = copy.deepcopy(clusters)
            clustersTemp[randk][0] = nonMedoid
            clustersTemp[randk][randi] = medoid

            clustersTemp = reAssignClusters(clustersTemp,data)


            TDswap = totalDistance(clustersTemp)
            #print('TD = ',TD,' TDswap = ',TDswap)


            # if new assignment gives lower cost, update cluster
            if TDswap<TD:
                #print('cost is improved by: ',TD-TDswap)
                clusters = clustersTemp
                TD = TDswap
            else:
                i=i+1
        print('the cost of this cluster is:',TD)
        if TD < bestTD:
            bestTD = TD
            bestClusters = clusters
        

    print('================================')
    print('best Total Distance = ',bestTD)


    print('Finished creating clusters')
    clustering = reAssignClusters(bestClusters,data)

    return clustering


# ========================DONE DEFINING FCN

templates = []
parts = []

  
loadedTemplates = loadTemplates()
templates = loadedTemplates[0]
parts = loadedTemplates[1]

print('the length of parts is: ',len(parts))


clusterings = kmedian(k,parts)



with open("clusterings", 'wb') as f:
    pickle.dump(clusterings, f)

with open("clusterings", 'rb') as f:
    aaa = pickle.load(f)


