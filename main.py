import cv2 
from letterClassifier import LetterClassifier 
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import configparser
import time
import RPi.GPIO as GPIO

print("Roborregos Delta | Robocup 2018 - Maze Junior Vision ")

#cv2.namedWindow('Original',cv2.WINDOW_NORMAL)
#cv2.namedWindow('Thresh',cv2.WINDOW_NORMAL)

config = configparser.ConfigParser()
config.read("settings.ini")

xSize = config.getint('General', 'ImageSizeX', fallback=80)
ySize = config.getint('General', 'ImageSizeY', fallback=64)
shutterSpeed = config.getint('General', 'ShutterSpeed', fallback = 3000)
awR = config.getfloat('General', 'AWGainR', fallback=1.6)
awB = config.getfloat('General', 'AWGainB', fallback = 1.9)

heightStartPercent = config.getfloat('General', 'HeightStartDivisionPercent', fallback=20) / 100
heightEndPercent = config.getfloat('General', 'HeightEndDivisionPercent', fallback=80) / 100
widthDistancePercent = config.getfloat('General', 'DistanceCenterWidthDvisionPercent', fallback=20) / 100

heightStartDivision = round(ySize * heightStartPercent)
heightEndDivision = round(ySize * heightEndPercent)
widthDistanceDivision = round(xSize * widthDistancePercent)
midPointImage = round(xSize / 2)

hFlip = config.getboolean('General', 'HFlip', fallback=True)
vFlip = config.getboolean('General', 'VFlip', fallback=True)
classifier = LetterClassifier()

camera = PiCamera()
camera.resolution = (xSize, ySize)
time.sleep(1)
camera.start_preview()
camera.awb_mode = 'off'
camera.awb_gains = (awR, awB)
camera.shutter_speed = shutterSpeed
camera.exposure_mode = 'off'
camera.hflip = hFlip
camera.vflip = vFlip
rawCapture = PiRGBArray(camera)

sLetterPin = config.getint('General', 'SLetterPin', fallback=10)
uLetterPin = config.getint('General', 'ULetterPin', fallback=11)
hLetterPin = config.getint('General', 'HLetterPin', fallback=12)
directionLetterPin = config.getint('General', 'DirectionLetterPin', fallback=13)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(sLetterPin, GPIO.OUT)
GPIO.setup(uLetterPin, GPIO.OUT)
GPIO.setup(hLetterPin, GPIO.OUT)
GPIO.setup(directionLetterPin, GPIO.OUT)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	image = frame.array
	leftMirror = image[heightStartDivision : heightEndDivision, 0: midPointImage - widthDistanceDivision]
	rightMirror = image[heightStartDivision : heightEndDivision, midPointImage + widthDistanceDivision : xSize]
	cv2.rectangle(image, (0, heightStartDivision), (midPointImage - widthDistanceDivision, heightEndDivision), (0,0,255))
	cv2.rectangle(image, (midPointImage + widthDistanceDivision, heightStartDivision), (xSize, heightEndDivision), (0,0,255))

	leftLetter = classifier.getLetterFromImage(leftMirror)
	rightLetter = classifier.getLetterFromImage(rightMirror)
	#print("Left: {}\t Right:{}".format(leftLetter, rightLetter))
	#cv2.imshow("Original", image)


	if leftLetter != classifier.errorNoLetterFound:
		GPIO.output(directionLetterPin, 0)
		if leftLetter == classifier.sLetterFound:
			GPIO.output(sLetterPin, 1)
			GPIO.output(uLetterPin, 0)
			GPIO.output(hLetterPin, 0)
		elif leftLetter == classifier.uLetterFound:
			GPIO.output(sLetterPin, 0)
			GPIO.output(uLetterPin, 1)
			GPIO.output(hLetterPin, 0)
		elif leftLetter == classifier.hLetterFound:
			GPIO.output(sLetterPin, 0)
			GPIO.output(uLetterPin, 0)
			GPIO.output(hLetterPin, 1)
	elif rightLetter != classifier.errorNoLetterFound:
		GPIO.output(directionLetterPin, 1)
		if rightLetter == classifier.sLetterFound:
			GPIO.output(sLetterPin, 1)
			GPIO.output(uLetterPin, 0)
			GPIO.output(hLetterPin, 0)
		elif rightLetter == classifier.uLetterFound:
			GPIO.output(sLetterPin, 0)
			GPIO.output(uLetterPin, 1)
			GPIO.output(hLetterPin, 0)
		elif rightLetter == classifier.hLetterFound:
			GPIO.output(sLetterPin, 0)
			GPIO.output(uLetterPin, 0)
			GPIO.output(hLetterPin, 1)
	else:
		GPIO.output(directionLetterPin, 0)
		GPIO.output(sLetterPin, 0)
		GPIO.output(uLetterPin, 0)
		GPIO.output(hLetterPin, 0)

	key = cv2.waitKey(1) & 0xFF
 
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
 
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
camera.close()