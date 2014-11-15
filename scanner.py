import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')

from sys import argv
import zbar
from PIL import Image
import glob

#if len(argv) < 2: exit(1)

# create a reader
scanner = zbar.ImageScanner()

# configure the reader
scanner.parse_config('enable')

# obtain image data
for filename in glob.glob('*.jpg'):
    print filename
    #pil = Image.open(argv[1]).convert('L')
    pil = Image.open(filename).convert('L')
    width, height = pil.size
    raw = pil.tostring()

    # wrap image data
    image = zbar.Image(width, height, 'Y800', raw)

    # scan the image for barcodes
    scanner.scan(image)
    #print dir(image)

    # extract results
    for symbol in image:
        # do something useful with results
        #print dir(symbol)
        print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
        print symbol.location, symbol.quality, symbol.count, symbol.components

# clean up
del(image)
