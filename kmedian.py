# first test k median method
# to be updated later to match mesh
# algorithm from CMPT459 
import cv2 
import numpy as np
import os, os.path
import random
import copy

maxNeighbour = 10 # num of max randomly chosen pairs of non mediod and mediod
numlocal = 10 # number of initial points to attempt to select
k = 6

# temp example:

data = [2,2,2,2,3,14,14,15,16,27,28,28,28,29,39,40,40,4,42,44,64,64,66,67,100,101,111]
print(len(data))
rdata = random.sample(data, len(data))
print(rdata)

def distance(item1,item2):
    return abs(item1-item2)

#------


def reAssignClusters(clusters):
    k = len(clusters)
    centroids = [[0 for i in range(1)] for j in range(k)]
    for i in range(k):
        centroids[i][0] = clusters[i][0]

    return assignClusters(k,centroids,data)

        

def assignClusters(k,centroids,data):
    #remove duplicates of centroid and data
    tmpdata = copy.deepcopy(data)
    for i in centroids:
        tmpdata.remove(i[0])



    clusters = centroids
    # for each object in data assign it to nearest cluster


    for j in range(len(tmpdata)): # for each data
        minCost = 999
        c = 0
        for i in range(k):
            cost = distance(tmpdata[j],clusters[i][0])
            
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
        count = count+distance(cluster[0],cluster[i])
    return count


def totalDistance(clusters):
    cnum = len(clusters)
    count = 0
    for i in range(cnum):
        count = count+singleTotalDistance(clusters[i])
    return count


def kmedian(k, dist, data):






    bestTD = 999999999
    bestClusters = []
    for r in range(numlocal):
        print('-----------------------------------------')

        # randomly select k parts as centroid
        centroids = [[0 for i in range(1)] for j in range(k)]
        # sample k values
        rdata = random.sample(data, k)
        for i in range(k):
            centroids[i][0] = rdata[i]


        print ('centroids:')
        print (centroids)

        clusters = assignClusters(k,centroids,data)


        #TD = # total distance of clustering
        TD = totalDistance(clusters)

        print('TD = ',TD)
        
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

            clustersTemp = reAssignClusters(clustersTemp)


            TDswap = totalDistance(clustersTemp)
            print('TD = ',TD)
            print('TDswap = ',TDswap)

            # if new assignment gives lower cost, update cluster
            if TDswap<TD:
                print(TD-TDswap)
                print(clustersTemp)
                clusters = clustersTemp
                TD = TDswap
            else:
                i=i+1
        if TD < bestTD:
            bestTD = TD
            bestClusters = clusters
        

    print('================================')
    print('bestTD = ',bestTD)
    print('bestclusters: ')
    print(bestClusters)

    return 


    

kmedian(k,2,rdata)

