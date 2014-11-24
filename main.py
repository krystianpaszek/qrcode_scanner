print "Importing libraries..."
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
import zbar
import cv2
from PIL import Image, ImageDraw
import time
import thread
import copy
import numpy as np
import os
from scipy import ndimage

print "Creating window..."
cv2.namedWindow("preview")
cv2.namedWindow("rotated")
vc = cv2.VideoCapture(0)

if vc.isOpened():
    rval, frame = vc.read()
else:
    rval = False
roi = frame
cv2.moveWindow("preview", 0+50, 0)
cv2.moveWindow("rotated", frame.shape[1]+50, 0)

print "Creating scanner object..."
scanner = zbar.ImageScanner()
scanner.parse_config('enable')

location = [(0,0),(0,0),(0,0),(0,0)]
counter = 0
message = ""

def process_image():
    global location, counter, message
    #konwersja z przedziwnego BGR ktorym posluguje sie OpenCV
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #konwersja na PIL Image ktorym posluguje sie zbar
    #.convert('L') przekonwertowuje na odcienie szarosci, wazne by zbar dobrze odczytywal
    i = Image.fromarray(rgb, 'RGB').convert('L')
    width, height = i.size
    raw = i.tostring()
    #stworzenie obiektu do odczytania z wszystkich zgromadzonych danych
    image = zbar.Image(width, height, 'Y800', raw)
    #skanowanie obrazu
    scanner.scan(image)
    #i wypisanie zakodowanych tresci
    if len(image.symbols) == 0:
        counter = counter + 1
    else:
        counter = 0
    if counter == 5:
        counter = 0
        location = [(0,0),(0,0),(0,0),(0,0)];
    for symbol in image:
        #print 'zbar', symbol.type, 'symbol', '"%s"' % symbol.data
#        if message != symbol.data:
#            message = symbol.data
#            print "Decoded: " + message
        location = symbol.location
    
    rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
    i = Image.fromarray(rgb, 'RGB').convert('L')
    width, height = i.size
    raw = i.tostring()
    image = zbar.Image(width, height, 'Y800', raw)
    scanner.scan(image)
    
    for symbol in image:
        #print 'crop + zbar', symbol.type, 'symbol', '"%s"' % symbol.data
        #        if message != symbol.data:
        #            message = symbol.data
        #            print "Decoded: " + message
        location = symbol.location
    del(image)

def show_rotated():
    global roi
    rotated = ndimage.rotate(new, angle)
    gray2 = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)
    blackwhite = cv2.threshold(gray2, thresh, 255, cv2.THRESH_BINARY)[1]
    contours2, hierarchy2 = cv2.findContours(blackwhite,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    areas2 = [cv2.contourArea(c) for c in contours2]
    if (len(contours2) > 0):
        max_index2 = np.argmax(areas2)
        cnt2=contours2[max_index2]
        x, y, w, h = cv2.boundingRect(cnt2)
        roi = rotated[y:y+h, x:x+w]
        #cv2.rectangle(rotated, (x,y), (x+w, y+h), (0,255,0), 2)
    cv2.imshow("rotated", roi)


print "Starting capture...\n\n\n"
while rval:
    rval, frame = vc.read()
    thread.start_new_thread(process_image, ())
    frame_to_display = copy.copy(frame)
    test_frame = copy.copy(frame)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thresh = 200
    im_bw = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY)[1]
    contours, hierarchy = cv2.findContours(im_bw,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    if (len(contours)>0):
        global new
        areas = [cv2.contourArea(c) for c in contours]
        max_index = np.argmax(areas)
        cnt=contours[max_index]
        rect = cv2.minAreaRect(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        new = frame[y:y+h, x:x+w]
        angle = rect[2]
    #box = cv2.cv.BoxPoints(rect)
    #box = np.int0(box)
    #cv2.drawContours(test_frame, contours, max_index, (0,255,0), 3)
    #cv2.drawContours(test_frame, [box], 0, (0,255,0), 3)
    dst = cv2.cornerHarris(im_bw, 2, 3, 0.04)
    dst = cv2.dilate(dst, None)
    color = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    color[dst>0.01*dst.max()] = [0,0,255]
    cv2.rectangle(frame_to_display,location[0],location[2],(0,255,0),3)
    thread.start_new_thread(show_rotated, ())
    cv2.imshow("preview", test_frame)
    key = cv2.waitKey(20)
    if key == 27:
        print "\n\n\nStopping capture"
        break
    if key == 32:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        i = Image.fromarray(rgb, 'RGB').convert('L')
        cv2.imwrite('savedimage.jpg', frame)

cv2.destroyWindow("preview")
