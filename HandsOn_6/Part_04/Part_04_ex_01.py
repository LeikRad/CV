# Visual Computing
# Image Processing Module
#
# Image Resizing and Pixelation
#
# SSS, v 1.0, Nov 2022

import cv2
import skimage
from sklearn.cluster import KMeans
from numpy import linalg as LA
import numpy as np



def colorClustering(idx, img, k):
    clusterValues = []
    for _ in range(0, k):
        clusterValues.append([])

    for r in range(0, idx.shape[0]):
        for c in range(0, idx.shape[1]):
            clusterValues[idx[r][c]].append(img[r][c])

    imgC = np.copy(img)

    clusterAverages = []
    for i in range(0, k):
        clusterAverages.append(np.average(clusterValues[i], axis=0))

    for r in range(0, idx.shape[0]):
        for c in range(0, idx.shape[1]):
            imgC[r][c] = clusterAverages[idx[r][c]]

    return imgC


def segmentImgClrRGB(img, k):
    imgC = np.copy(img)

    h = img.shape[0]
    w = img.shape[1]

    imgC.shape = (img.shape[0] * img.shape[1], 3)

    # 5. Run k-means on the vectorized responses X to get a vector of labels (the clusters);
    #
    kmeans = KMeans(n_clusters=k, random_state=0).fit(imgC).labels_

    # 6. Reshape the label results of k-means so that it has the same size as the input image
    #   Return the label image which we call idx
    kmeans.shape = (h, w)

    return kmeans


def kMeansImage(image, k):
    idx = segmentImgClrRGB(image, k)
    return colorClustering(idx, image, k)

############################################################

img = cv2.imread("paddington.png")


cv2.imshow('first', img)


cv2.waitKey(0)