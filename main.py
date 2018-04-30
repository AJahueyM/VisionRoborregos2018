#!/usr/bin/python

# Standard imports
import cv2
import numpy as np;

# Read image
im = cv2.imread("letterS.png", cv2.IMREAD_GRAYSCALE)
im_thresh = cv2.inRange(im, 200, 255)

_, contours, hierarchy = cv2.findContours(im_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

counter = 0
rects = []
for cnt in contours:
    counter = counter + 1
    rects.append(cv2.boundingRect(cnt))
    x,y,w,h = rects[len(rects) - 1]
    cv2.rectangle(im_thresh,(x,y),(x+w,y+h),0,1)

#TODO Saber cual de todas estas es la letra que queremos, recomiendo usar relacion de height / width
x,y,w,h = rects[1]
letter = im_thresh[y:y+h, x:x+w]

print(letter)



print(counter)
cv2.imshow("letter", letter)
cv2.imshow("image_invr", im_thresh)

cv2.waitKey(0)