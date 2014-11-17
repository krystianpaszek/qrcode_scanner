print "Importing libraries..."
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
import zbar
import cv2
from PIL import Image, ImageDraw
import time
import thread

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

def process_image():
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
    for symbol in image:
        print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
    del(image)


print "Starting capture..."
while rval:
    #multithreading taki trudny
    #dzieki temu podglad mamy na zywo, a przetwarzanie jest w tle
    rval, frame = vc.read()
    thread.start_new_thread(process_image, ())
    cv2.imshow("preview", frame)
    key = cv2.waitKey(20)
    if key == 27:
        print "Stopping capture"
        break

cv2.destroyWindow("preview")
