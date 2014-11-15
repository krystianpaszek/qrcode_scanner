print "Importing libraries..."
import sys
#to działa typowo u mnie, nie powinno to tak wyglądać :P
sys.path.append('/usr/local/lib/python2.7/site-packages')
import zbar
import cv2
from PIL import Image
#ImageOps w sumie nie jest potrzebne, używałem tego do debugu
import PIL.ImageOps
import time
import thread

print "Creating window..."
cv2.namedWindow("preview")
vc = cv2.VideoCapture(0)

if vc.isOpened():
    #pierwszy odczyt, nie wiem w sumie po co jest osobno od całej pętli
    #można spróbować się tego pozbyć
    rval, frame = vc.read()
else:
    rval = False

print "Creating scanner object..."
scanner = zbar.ImageScanner()
scanner.parse_config('enable')
#konwersja z przedziwnego BGR którym posługuje się OpenCV
rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#konwersja na PIL Image którym posługuje się zbar
#.convert('L') chyba przekonwertowuje na odcienie szarości, ważne by zbar dobrze odczytywał
i = Image.fromarray(rgb, 'RGB').convert('L')

def process_image():
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    i = Image.fromarray(rgb, 'RGB').convert('L')
    width, height = i.size
    raw = i.tostring()
    #stworzenie obiektu do odczytania z wszystkich zgromadzonych danych
    image = zbar.Image(width, height, 'Y800', raw)
    #skanowanie obrazu
    scanner.scan(image)
    #i wypisanie zakodowanych treści
    for symbol in image:
        print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
    del(image)


print "Starting capture..."
while rval:
    #multithreading taki trudny
    #dzięki temu podgląd mamy na żywo, a przetwarzanie jest w tle
    thread.start_new_thread(process_image, ())
    cv2.imshow("preview", frame)
    rval, frame = vc.read()
    key = cv2.waitKey(20)
    if key == 27:
        print "Stopping capture"
        break
    #time.sleep(1)

cv2.destroyWindow("preview")