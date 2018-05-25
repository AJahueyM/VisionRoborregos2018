#!/usr/bin/python
import cv2 
from letterClassifier import LetterClassifier 
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import configparser
import time

current_milli_time = lambda: int(round(time.time() * 1000))

config = configparser.ConfigParser()
config.read("settings.ini")

xSize = config.getint('General', 'ImageSizeX', fallback=80)
ySize = config.getint('General', 'ImageSizeY', fallback=64)
shutterSpeed = config.getint('General', 'ShutterSpeed', fallback = 20000)
aw1 = config.getfloat('General', 'AWGain1', fallback=1.8)
aw2 = config.getfloat('General', 'AWGain2', fallback = 1.5)

classifier = LetterClassifier()
#cv2.namedWindow('Original',cv2.WINDOW_NORMAL)
#cv2.namedWindow('Thresh',cv2.WINDOW_NORMAL)
camera = PiCamera()
camera.resolution = (xSize, ySize)
time.sleep(1)
camera.start_preview()
camera.awb_mode = 'off'
camera.awb_gains = (aw1, aw2)
camera.shutter_speed = shutterSpeed
camera.exposure_mode = 'off'
camera.vflip = True
rawCapture = PiRGBArray(camera)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	config.read("settings.ini")
	aw1 = config.getfloat('General', 'AWGain1', fallback=1.8)
	aw2 = config.getfloat('General', 'AWGain2', fallback = 1.5)
	shutterSpeed = config.getint('General', 'ShutterSpeed', fallback = 20000)
	camera.awb_gains = (aw1, aw2)
	camera.shutter_speed = shutterSpeed

	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array
	print(classifier.getLetterFromImage(image))
	# show the frame
	#cv2.imshow("Original", image)
	key = cv2.waitKey(1) & 0xFF
 
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
 
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
camera.close()