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

#odczyt pierwszej klatki
if vc.isOpened():
    rval, frame = vc.read()
else:
    rval = False
#ustawienie okien
cv2.moveWindow("preview", 0+50, 0)
cv2.moveWindow("rotated", frame.shape[1]+50, 0)

print "Creating scanner object..."
scanner = zbar.ImageScanner()
scanner.parse_config('enable')

zbar_decoded_count = 0
crop_decoded_count = 0
message, zbar_string, crop_string = "", "", ""

def process_image():
    global zbar_string, crop_string
    global message, zbar_decoded_count, crop_decoded_count
    #przetworzenie obrazu do zdekodowania przez zbar
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    i = Image.fromarray(rgb, 'RGB').convert('L')
    width, height = i.size
    raw = i.tostring()
    image = zbar.Image(width, height, 'Y800', raw)
    scanner.scan(image)
    for symbol in image:
        zbar_decoded_count = zbar_decoded_count + 1
        message = symbol.data
    
    #reczne wycinanie kodu z obrazu
    #przetworzenie obrazu do rozpoznania krawedzi
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thresh = 200
    im_bw = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY)[1]
    contours, hierarchy = cv2.findContours(im_bw,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    new = np.zeros((1,1,3), np.uint8)
    angle = 0
    if (len(contours)>0):
        areas = [cv2.contourArea(c) for c in contours]
        max_index = np.argmax(areas)
        cnt=contours[max_index]
        rect = cv2.minAreaRect(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        new = frame[y:y+h, x:x+w]
        angle = rect[2]
    
    #jesli wykryto i zapisano kod do nowej tablicy
    #wyswietl wyciety obszar i wyslij go do dekodera
    if np.any(new != 0):
        rgb2 = cv2.cvtColor(show_rotated(new,angle), cv2.COLOR_BGR2RGB)
        i2 = Image.fromarray(rgb2, 'RGB').convert('L')
        width, height = i2.size
        raw2 = i2.tostring()
        image2 = zbar.Image(width, height, 'Y800', raw2)
        scanner.scan(image2)
        
        for symbol in image2:
            crop_decoded_count = crop_decoded_count + 1

    zbar_string = "zbar: " + str(zbar_decoded_count)
    crop_string = "crop: " + str(crop_decoded_count)
    del(image)

def show_rotated(new2, angle2):
    #obroc fragment obrazu z kodem i wytnij z niego juz tylko sam kod
    roi = np.zeros((1,1,3), np.uint8)
    if angle2 != 0:
        rotated = ndimage.rotate(new2, angle2)
        gray2 = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)
        thresh = 200
        blackwhite = cv2.threshold(gray2, thresh, 255, cv2.THRESH_BINARY)[1]
        contours2, hierarchy2 = cv2.findContours(blackwhite,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        areas2 = [cv2.contourArea(c) for c in contours2]
        if (len(contours2) > 0):
            max_index2 = np.argmax(areas2)
            cnt2=contours2[max_index2]
            x, y, w, h = cv2.boundingRect(cnt2)
            roi = rotated[y:y+h, x:x+w]
        else:
            roi = np.zeros((1,1,3), np.uint8)
    cv2.imshow("rotated", roi)
    return roi


print "Starting capture..."
frame_counter = 0
while rval:
    #petla programu
    frame_counter = frame_counter + 1
    rval, frame = vc.read()
    frame_to_display = copy.copy(frame)
    #zbadaj krawedzie by podswietlic kod na podgladzie
    gray = cv2.cvtColor(frame_to_display, cv2.COLOR_BGR2GRAY)
    thresh = 200
    im_bw = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY)[1]
    contours, hierarchy = cv2.findContours(im_bw,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    if (len(contours)>0):
        areas = [cv2.contourArea(c) for c in contours]
        max_index = np.argmax(areas)
        cnt=contours[max_index]
        rect = cv2.minAreaRect(cnt)
        box = cv2.cv.BoxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(frame_to_display, contours, max_index, (0,255,0), 3)
    
    #rozpocznij nowy watek ktory przetworzy przechwycona klatke
    thread.start_new_thread(process_image, ())

    #wyswietlanie informacji
    cv2.putText(frame_to_display, "frame: " + str(frame_counter), (50,25), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), thickness=1)
    cv2.putText(frame_to_display, message, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), thickness=1)
    cv2.putText(frame_to_display, zbar_string, (50,75), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), thickness=1)
    cv2.putText(frame_to_display, crop_string, (50,100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), thickness=1)
    cv2.imshow("preview", frame_to_display)

    #obsluga klawiszy
    key = cv2.waitKey(20)
    if key == 27 or frame_counter == 500:
        print "Stopping capture."
        break
    if key == 32:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        i = Image.fromarray(rgb, 'RGB').convert('L')
        cv2.imwrite('savedimage.jpg', frame)

cv2.destroyWindow("preview")
print "\n\nResults:"
print "zbar:", zbar_decoded_count
print "crop:", crop_decoded_count
