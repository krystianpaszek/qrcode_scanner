qrcode_scanner
==============

Simple QR code decoding program that takes input from your device's built-in camera. Written in Python, uses zbar for decoding and OpenCV for image capture.

main.py is, well, main program. Run it without arguments, it will launch live preview of your camera stream and will output to stdout every qrcode it will decode.

scanner.py is a helper program that reads all .jpg files in folder and tries to decode them, displaying info to stdout.
