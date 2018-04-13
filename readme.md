In the future, this piece of code will act as a "proxy" between the Luxembourgish "Smarty" meters and existing open source software that analyse DSMR telegrams. E.g. [dsmr_parser](https://github.com/ndokter/dsmr_parser).
This is currently only a proof of concept that only prints out the DSMR telegrams but doesn't forward them yet.

* I run this on a Raspberry Pi Zero W that I have connected to my "Smarty" meter using a serial-to-USB cable. The serial-to-usb device is supposed to be accessible under /dev/ttyUSB0
* You need to install the "cryptography" and "serial" libraries for Python. Ubuntu/Debian: ``sudo apt-get install python3-cryptography python3-serial``
* Ask you energy provider for your decryption key
* Then, run the following on the command line and watch the telegrams appear on screen: ``python3 decrypt.py KEY`` (with "KEY" being your decryption key)
* Push CTRL+C to exit