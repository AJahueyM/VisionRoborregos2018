#!/usr/bin/python
import cv2 
import letterClassifier as lc

# Read image
im = cv2.imread("letterU.png", cv2.IMREAD_GRAYSCALE)

print(lc.getLetterFromImage(im))

cv2.waitKey(0)