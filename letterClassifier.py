import cv2
import numpy as np
import configparser

class LetterClassifier:
    def __init__(self):
        self.__config = configparser.ConfigParser()
        self.__updateValues()
        self.__errorNoLetterFound = 'n/a'

    def __hasBlack (self,matrix, threshold):
        height, width = matrix.shape
        totalAmount = 0
        blackAmount = 0
        for y in range(height):
            for x in range(width):
                #print (matrix[y, x], end=' ')
                if(matrix[y, x] == 0):
                    blackAmount = blackAmount + 1
                totalAmount = totalAmount + 1
            #print()

        if(blackAmount > totalAmount * threshold / 100):
            return True
        else:
            return False

    def __updateValues(self):
        self.__config.read('settings.ini')
        self.__heightWidthRatioLow = self.__config.getfloat('LetterDetection', 'HeightWidthRatioLowLimit', fallback=.78)
        self.__heightWidthRatioHigh = self.__config.getfloat('LetterDetection', 'HeightWidthRatioHighLimit', fallback=.83)
        self.__heightWidthRatioTolerance = self.__config.getfloat('LetterDetection', 'PercentHeightWidthTolerance', fallback=10)
        self.__blackSectionPercent = self.__config.getfloat('LetterDetection', 'BlackThresholdSectionPercent', fallback=10)
        self.__blackLowLimit = self.__config.getfloat('LetterDetection', 'ImageBlackLowLimit', fallback=200)
        self.__blackHighLimit = self.__config.getfloat('LetterDetection', 'ImageBlackHighLimit', fallback=255)
        self.__lineIdentifierWidth = self.__config.getfloat('LetterDetection', 'LineIdentifierrWidth', fallback=3)
        self.__minAreaLetter = self.__config.getfloat('LetterDetection', 'MinAreaLetter', fallback=5)

    def getLetterFromImage(self, im):

        self.__updateValues()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        im_thresh = cv2.inRange(gray, self.__blackLowLimit, self.__blackHighLimit)
        heightOriginal, widthOriginal = im_thresh.shape
        areaOriginal = heightOriginal * widthOriginal
        _, contours, hierarchy = cv2.findContours(im_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        counter = 0
        rects = []
        for cnt in contours:
            rect = cv2.boundingRect(cnt)
            x, y, w, h = rect
            #Area filter
            if (w * h  / areaOriginal)  > (self.__minAreaLetter / 100) and w * h  / areaOriginal < 1:
                #print("Counter: {} \t\%area: {} \tThresh: {}".format(counter, w * h / areaOriginal, self.__minAreaLetter / 100))
                counter = counter + 1
                rects.append(cv2.boundingRect(cnt))

        if counter >= 1:

            #Ratio filter
            ratioFilteredRects = []
            for rectCand in rects:
                x,y,w,h = rectCand
                ratio = w/h
                higherThanLower = ratio > (self.__heightWidthRatioLow) #- self.__heightWidthRatioLow * (self.__heightWidthRatioTolerance / 100))
                lowerThanHigher = ratio < (self.__heightWidthRatioHigh )#+ self.__heightWidthRatioHigh * (self.__heightWidthRatioTolerance / 100))
                if higherThanLower and lowerThanHigher:
                    ratioFilteredRects.append(rectCand)
                    x,y,w,h = rectCand
                    #cv2.rectangle(im_thresh,(x,y),(x+w,y+h),0,1)
            rect = rects[0]

            if len(ratioFilteredRects) == 0:
                return (self.__errorNoLetterFound)

            if len(ratioFilteredRects) >= 1:
                rect = ratioFilteredRects[0]
            

            x,y,w,h = rect

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
            #print("Upper: {}\tMiddle: {}\tLower: {}".format(upperIsBlack, middleIsBlack,lowerIsBlack ))
            if isS:
                return ("S")
            elif isH :
                return ("H")
            elif isU:
                return ("U")
    
        return (self.__errorNoLetterFound)