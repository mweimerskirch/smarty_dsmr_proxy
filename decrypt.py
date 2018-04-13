import serial
import binascii
import argparse

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import (
    Cipher, algorithms, modes
)
from cryptography.exceptions import InvalidTag


class SerialBuffer(object):
    def __init__(self):
        self.STATE_IGNORING = 0
        self.STATE_STARTED = 1
        self.STATE_HAS_SYSTEM_TITLE_LENGTH = 2
        self.STATE_HAS_SYSTEM_TITLE = 3
        self.STATE_HAS_SYSTEM_TITLE_SUFFIX = 4
        self.STATE_HAS_DATA_LENGTH = 5
        self.STATE_HAS_SEPARATOR = 6
        self.STATE_HAS_FRAME_COUNTER = 7
        self.STATE_HAS_PAYLOAD = 8
        self.STATE_HAS_GCM_TAG = 9
        self.STATE_DONE = 10

        self._args = {"key": ""}

        self._connection = None

        self._state = self.STATE_IGNORING
        self._buffer = ""
        self._buffer_length = 0
        self._next_state = 0

        self._system_title = b""
        self._system_title_length = 0

        self._data_length_bytes = b""
        self._data_length = 0

        self._frame_counter = b""

        self._payload = b""

        self._gcm_tag = b""

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            'key',
            help="Decryption key")
        self._args = parser.parse_args()

        serial_buffer.connect()
        while True:
            serial_buffer.process()

    def connect(self):
        try:
            self._connection = serial.Serial(
                port="/dev/ttyUSB0",
                baudrate=115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
            )
        except (serial.SerialException, OSError) as err:
            print("ERROR")

    def process(self):
        try:
            raw_data = self._connection.read()
        except serial.SerialException:
            return

        hex = binascii.hexlify(raw_data)
        if (self._state == self.STATE_IGNORING):
            if (hex == b'db'):
                self._state = self.STATE_STARTED
                self._buffer = b""
                self._buffer_length = 1
                self._system_title_length = 0
                self._system_title = b""
                self._data_length = 0
                self._data_length_bytes = b""
                self._frame_counter = b""
                self._payload = b""
                self._gcm_tag = b""
            else:
                return
        elif self._state == self.STATE_STARTED:
            self._state = self.STATE_HAS_SYSTEM_TITLE_LENGTH
            self._system_title_length = int(hex, 16)
            self._buffer_length = self._buffer_length + 1
            self._next_state = 2 + self._system_title_length  # start bytes + system title length
        elif self._state == self.STATE_HAS_SYSTEM_TITLE_LENGTH:
            if self._buffer_length > self._next_state:
                self._system_title += hex
                # print("System title")
                # print(self._system_title)
                self._state = self.STATE_HAS_SYSTEM_TITLE
                self._next_state = self._next_state + 2  # read two more bytes
            else:
                self._system_title += hex
        elif self._state == self.STATE_HAS_SYSTEM_TITLE:
            self._next_state = self._next_state + 1
            self._state = self.STATE_HAS_SYSTEM_TITLE_SUFFIX  # Ignore separator byte
        elif self._state == self.STATE_HAS_SYSTEM_TITLE_SUFFIX:
            if self._buffer_length > self._next_state:
                self._data_length_bytes += hex
                self._data_length = int(self._data_length_bytes, 16)
                self._state = self.STATE_HAS_DATA_LENGTH
            else:
                self._data_length_bytes += hex
        elif self._state == self.STATE_HAS_DATA_LENGTH:
            self._state = self.STATE_HAS_SEPARATOR  # Ignore separator byte
            self._next_state = self._next_state + 1 + 4  # separator byte + 4 bytes for framecounter
        elif self._state == self.STATE_HAS_SEPARATOR:
            if self._buffer_length > self._next_state:
                self._frame_counter += hex
                print("Framecounter")
                print(self._frame_counter)
                self._state = self.STATE_HAS_FRAME_COUNTER
                self._next_state = self._next_state + self._data_length - 17
            else:
                self._frame_counter += hex
        elif self._state == self.STATE_HAS_FRAME_COUNTER:
            if self._buffer_length > self._next_state:
                self._payload += hex
                # print("Payload")
                # print(self._payload)
                self._state = self.STATE_HAS_PAYLOAD
                self._next_state = self._next_state + 12
            else:
                self._payload += hex
        elif self._state == self.STATE_HAS_PAYLOAD:
            if self._buffer_length > self._next_state:
                self._gcm_tag += hex
                # print("GCM Tag")
                # print(self._gcm_tag)
                self._state = self.STATE_DONE
            else:
                self._gcm_tag += hex

        self._buffer += hex
        self._buffer_length = self._buffer_length + 1

        if self._state == self.STATE_DONE:
            # print(self._buffer)
            self.analyze()
            self._state = self.STATE_IGNORING

    def analyze(self):
        key = binascii.unhexlify(self._args.key)
        aad = binascii.unhexlify("3000112233445566778899AABBCCDDEEFF")

        try:
            decryption = self.decrypt(
                key,
                aad
            )
            print(decryption)
        except InvalidTag:
            print("ERROR: Invalid Tag.")

    def decrypt(self, key, additional_data):
        iv = binascii.unhexlify(self._system_title + self._frame_counter)
        payload = binascii.unhexlify(self._payload)
        gcm_tag = binascii.unhexlify(self._gcm_tag)

        decryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, gcm_tag, 12),
            backend=default_backend()
        ).decryptor()

        decryptor.authenticate_additional_data(additional_data)

        return decryptor.update(payload) + decryptor.finalize()


if __name__ == '__main__':
    serial_buffer = SerialBuffer()
    serial_buffer.main()
