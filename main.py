#!/usr/bin/python
import cv2 
from letterClassifier import LetterClassifier 
import configparser

config = configparser.ConfigParser()
config.read("settings.ini")
sizeReduction = config.getfloat('General', 'ImageSizeReduction', fallback=.25)
vc = cv2.VideoCapture(0)
classifier = LetterClassifier()

while True:
    _, im = vc.read()
    height, width = im.shape[:2]
    newWidth = round(sizeReduction * width)
    newHeight = round(sizeReduction * height)
    res = cv2.resize(im, ( newWidth, newHeight))
    cv2.imshow('Original', res)
    # Read image
    #im = cv2.imread("letterS.png", cv2.IMREAD_GRAYSCALE)
    print(classifier.getLetterFromImage(res))

    cv2.waitKey(1)