print "Importing libraries..."
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
import zbar
import cv2
from PIL import Image, ImageDraw
import time
import thread
import copy

print "Creating window..."
cv2.namedWindow("preview")
vc = cv2.VideoCapture(0)

if vc.isOpened():
    rval, frame = vc.read()
else:
    rval = False

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
        #print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
        if message != symbol.data:
            message = symbol.data
            print "Decoded: " + message
        location = symbol.location
    del(image)


print "Starting capture...\n\n\n"
while rval:
    rval, frame = vc.read()
    frame_to_display = copy.copy(frame)
    #dzieki temu podglad mamy na zywo, a przetwarzanie jest w tle
    thread.start_new_thread(process_image, ())
    cv2.rectangle(frame_to_display,location[0],location[2],(0,255,0),3)
    cv2.imshow("preview", frame_to_display)
    key = cv2.waitKey(20)
    if key == 27:
        print "\n\n\nStopping capture"
        break

cv2.destroyWindow("preview")
