import os
from serial import Serial

class Connection(object):
    def __init__(self):
        self.tty = self._find_tty('tty.usbmodem')
        self.ser = Serial(self.tty, timeout=0.05)

    def _find_tty(self, prefix):
        for file in os.listdir('/dev'):
            if file.startswith(prefix):
                return '/dev/' + file

    def _read_to_empty(self):
        lines = []
        while True:
            lines.append(self.ser.readline().rstrip('\r\n'))
            if not self.ser.inWaiting():
                break

        return lines

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        if self.ser:
            self.ser.close()
            self.ser = None

    def writeline(self, line):
        self.ser.write(line + '\r')

    def readline(self):
        return self.ser.readline().rstrip('\r\n')

    def readall(self):
        return self._read_to_empty()

