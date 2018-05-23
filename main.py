#!/usr/bin/python
import cv2 
from letterClassifier import LetterClassifier 
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import configparser

config = configparser.ConfigParser()
config.read("settings.ini")
sizeReduction = config.getfloat('General', 'ImageSizeReduction', fallback=.25)
classifier = LetterClassifier()
cv2.namedWindow('Original',cv2.WINDOW_NORMAL)
cv2.namedWindow('Thresh',cv2.WINDOW_NORMAL)
camera = PiCamera()
camera.resolution = (160, 128)
time.sleep(1)
camera.start_preview()
camera.awb_mode = 'off'
camera.awb_gains = (1.8, 1.5)
camera.shutter_speed = 20000
camera.exposure_mode = 'off'
camera.vflip = True
rawCapture = PiRGBArray(camera)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array
	print(classifier.getLetterFromImage(image))
	# show the frame
	cv2.imshow("Original", image)
	key = cv2.waitKey(1) & 0xFF
 
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
 
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
camera.close()