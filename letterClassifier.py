import cv2
import numpy as np

def hasBlack (matrix, threshold):
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


def getLetterFromImage(im):
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

    height, width = letter.shape
    letterMidpoint = round(width/2)

    #Dividir imagen en 3 grandes secciones
    heightSection = round(height / 3)
    widthSection = 3
    widthStart = round(letterMidpoint- widthSection/2)
    widthEnd = round(letterMidpoint + widthSection/2)

    upperLetter = letter[0:heightSection, widthStart:widthEnd]
    middleLetter = letter[heightSection:heightSection*2, widthStart:widthEnd] 
    lowerLetter = letter[heightSection*2:heightSection*3, widthStart:widthEnd]

    #Porcentaje de la imagen que tiene que ser negra para ser considerada como negra
    threshold = 10

    upperIsBlack = hasBlack(upperLetter, threshold)
    middleIsBlack = hasBlack(middleLetter, threshold)
    lowerIsBlack = hasBlack(lowerLetter, threshold)

    isS = (upperIsBlack & middleIsBlack) & lowerIsBlack
    isH = (not upperIsBlack & middleIsBlack) & (not lowerIsBlack)
    isU = (not upperIsBlack & (not middleIsBlack)) & lowerIsBlack
    if isS:
        return ("S")
    elif isH :
        return ("H")
    elif isU:
        return ("U")
    else:
        print("No se pudo identificar, tratando como U")
        return ("U")