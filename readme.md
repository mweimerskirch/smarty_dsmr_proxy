# Decrypter and proxy for Luxembourgish "Smarty" meters

This piece of code acts as a "proxy" between the Luxembourgish "Smarty" meters and existing open source software that analyse DSMR telegrams. E.g. [dsmr_parser](https://github.com/ndokter/dsmr_parser).

I run this on a Raspberry Pi Zero W that I have connected to my "Smarty" meter using a serial-to-USB cable.

## Before you start

* You need to install the "cryptography" and "serial" libraries for Python. Ubuntu/Debian: ``sudo apt-get install python3-cryptography python3-serial``
* Ask you energy provider for your decryption key
* You might need to install "socat" for the examples below. Ubuntu/Debian: ``sudo apt-get install socat``

## Test if everything works

* Run the following on the command line and watch the telegrams appear on screen: ``python3 decrypt.py KEY`` (with "KEY" being your decryption key)
* If the serial-to-usb cable is not accessible under /dev/ttyUSB0, you can use the "--serial-input-port" argument to specify which path to read from.
* Push CTRL+C to exit

## To connect your smart meter to dsmr_parser (or a Home Assistant instance) that runs remotely

Start socat to get a virtual serial port that is forwarded to a TCP connection on port 2001.
**Please be aware that this way, the data from your smart meter is available unencrypted on your network!**
```
socat -d -d pty,raw,echo=0 TCP-LISTEN:2001,reuseaddr
```

The output should look as follows. 
```
2018/04/13 20:30:00 socat[1301] N PTY is /dev/pts/2
2018/04/13 20:30:00 socat[1301] N listening on AF=2 0.0.0.0:2001
(...)
```

Using the given port name, you can now start the proxy with the "--serial-output-port" argument (with the port name from the previous output).
```
python3 decrypt.py KEY --serial-output-port=/dev/pts/2
```

You can now configure dsmr_parser (or your Home Assistant instance) to use a TCP connection to the current device on port 2001.

## To connect your smart meter to dsmr_reader, dsmr_parser (or a Home Assistant instance) that runs on the same machine

Start socat to get a virtual serial port that is connected to a second virtual serial port.
```
socat -d -d pty,raw,echo=0 pty,raw,echo=0
```

The output should look as follows. 
```
2018/04/13 20:30:00 socat[1301] N PTY is /dev/pts/2
2018/04/13 20:30:00 socat[1301] N PTY is /dev/pts/3
(...)
```

Using the given port name, you can now start the proxy with the "--serial-output-port" argument (with the first port name from the previous output).
```
python3 decrypt.py KEY --serial-output-port=/dev/pts/2
```

You can now configure dsmr_reader, dsmr_parser (or your Home Assistant instance) to connect to the second port from the previous output (in this example /dev/pts/3).

## Further information

* [DSMR Component for Home Assistant](https://www.home-assistant.io/components/sensor.dsmr/)
* [DSMR Parser](https://github.com/ndokter/dsmr_parser), the library used by Home Assistant to read meter data
* [DSMR Reader](http://dsmr-reader.readthedocs.io/en/latest/), stand-alone utility to log and view your energy consumption
* [P1 Port Specification for Luxembourg's "Smarty" electricity meter](https://smarty.creos.net/wp-content/uploads/P1PortSpecification.pdf), the reference document for this library. It describes how the encryption on top of the DSMR standard works.
