import cv2
import numpy as np
import configparser

class LetterClassifier:
    def __init__(self):
        self.__config = configparser.ConfigParser()
        self.__updateValues()
        self.errorNoLetterFound = "n/a"
        self.sLetterFound = "S"
        self.hLetterFound = "H"
        self.uLetterFound = "U"

    def __hasBlack (self,matrix, threshold):
        height, width = matrix.shape
        totalAmount = 0
        blackAmount = 0
        for y in range(height):
            for x in range(width):
                if(matrix[y, x] == 0):
                    blackAmount = blackAmount + 1
                totalAmount = totalAmount + 1

        return (blackAmount > totalAmount * threshold / 100)
           

    def __updateValues(self):
        self.__config.read('settings.ini')
        self.__heightWidthRatioLow = self.__config.getfloat('LetterDetection', 'HeightWidthRatioLowLimit', fallback=.78)
        self.__heightWidthRatioHigh = self.__config.getfloat('LetterDetection', 'HeightWidthRatioHighLimit', fallback=.83)
        self.__blackSectionPercent = self.__config.getfloat('LetterDetection', 'BlackThresholdSectionPercent', fallback=10)
        self.__blackLowLimit = self.__config.getfloat('LetterDetection', 'ImageBlackLowLimit', fallback=200)
        self.__blackHighLimit = self.__config.getfloat('LetterDetection', 'ImageBlackHighLimit', fallback=255)
        self.__lineIdentifierWidth = self.__config.getfloat('LetterDetection', 'LineIdentifierrWidth', fallback=3)
        self.__minAreaLetter = self.__config.getfloat('LetterDetection', 'MinAreaLetter', fallback=5)
        self.__maxAreaLetter = self.__config.getfloat('LetterDetection', 'MaxAreaLetter', fallback=30)

    def getLetterFromImage(self, im):
        #self.__updateValues()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        im_thresh = cv2.threshold(gray, self.__blackLowLimit, self.__blackHighLimit, cv2.THRESH_BINARY)[1]
        #cv2.imshow("Thresh", im_thresh)
        heightOriginal, widthOriginal = im_thresh.shape
        areaOriginal = heightOriginal * widthOriginal
        _, contours, hierarchy = cv2.findContours(im_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        rects = []
        for cnt in contours:
            rect = cv2.boundingRect(cnt)
            x, y, w, h = rect
            #Area filter
            if (w * h  / areaOriginal)  > (self.__minAreaLetter / 100) and (w * h  / areaOriginal) < (self.__maxAreaLetter / 100):
                rects.append(cv2.boundingRect(cnt))

        if len(rects) >= 1:

            #Ratio filter
            ratioFilteredRects = []
            for rectCand in rects:
                x,y,w,h = rectCand
                ratio = w/h
                higherThanLower = ratio > self.__heightWidthRatioLow
                lowerThanHigher = ratio < self.__heightWidthRatioHigh
                if higherThanLower and lowerThanHigher:
                    ratioFilteredRects.append(rectCand)
                    cv2.rectangle(im, (x, y), (x+w, y+h), (250,0,0))         
           
            rect = rects[0]

            if len(ratioFilteredRects) == 0:
                return (self.errorNoLetterFound)

            if len(ratioFilteredRects) >= 1:
                rect = ratioFilteredRects[0]
                x,y,w,h = rect
                areaOld = w * h
                for rectA in ratioFilteredRects:
                    x,y,w,h = rectA
                    areaNew = w * h
                    if areaNew < areaOld:
                        areaOld = areaNew
                        rect = rectA
            

            x,y,w,h = rect
            cv2.rectangle(im, (x, y), (x+w, y+h), (0,255,0))         
            #cv2.imshow('Original', im)
            letter = im_thresh[y:y+h, x:x+w]

            height, width = letter.shape
            letterMidpoint = round(width/2)

            #Dividir imagen en 3 grandes secciones
            heightSection = round(height / 3)
            widthSection = self.__lineIdentifierWidth
            widthStart = round(letterMidpoint - widthSection/2)
            widthEnd = round(letterMidpoint + widthSection/2)

            upperLetter = letter[0:heightSection, widthStart:widthEnd]
            middleLetter = letter[heightSection:heightSection*2, widthStart:widthEnd] 
            lowerLetter = letter[heightSection*2:heightSection*3, widthStart:widthEnd]

            #Porcentaje de la imagen que tiene que ser negra para ser considerada como negra
            upperIsBlack = self.__hasBlack(upperLetter, self.__blackSectionPercent)
            middleIsBlack = self.__hasBlack(middleLetter, self.__blackSectionPercent)
            lowerIsBlack = self.__hasBlack(lowerLetter, self.__blackSectionPercent)

            isS = (upperIsBlack & middleIsBlack) & lowerIsBlack
            isH = (not upperIsBlack & middleIsBlack) & (not lowerIsBlack)
            isU = (not upperIsBlack & (not middleIsBlack)) & lowerIsBlack

            if isS:
                return (self.sLetterFound)
            elif isH :
                return (self.hLetterFound)
            elif isU:
                return (self.uLetterFound)
        return (self.errorNoLetterFound)