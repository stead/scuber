import pyb
import sys

class Scuber(object):
    def __init__(self, freq=50, limit=200):
        self.left = pyb.Pin('X1', pyb.Pin.OUT_PP)
        self.left_led = pyb.LED(1)
        self.right = pyb.Pin('X2', pyb.Pin.OUT_PP)
        self.right_led = pyb.LED(2)
        self.left_level = 0
        self.left_threshold = 0
        self.right_level = 0
        self.right_threshold = 0
        self.counter = 0
        self.timer = pyb.Timer(1)
        self.timer.init(freq=freq * limit)
        self.limit = limit
        self.max_power = limit / 2
        self.calib = (0, 100)

    def start(self):
        self.set_power(0)
        self.timer.callback(self.timer_callback)

    def stop(self):
        self.timer.callback(None)
        self.left.low()
        self.right.low()
        self.set_power(0)

    def timer_callback(self, t):
        self.counter += 1
        if self.counter >= self.limit:
            self.counter = 0

            if self.left_level > 0:
                self.left.high()
                self.left_led.on()

            if self.right_level > 0:
                self.right.high()
                self.right_led.on()

        if self.counter == self.left_threshold:
            self.left.low()
            self.left_led.off()
        if self.counter == self.right_threshold:
            self.right.low()
            self.right_led.off()

    def _set_level(self, level):
        calibrated = int(self.calib[0] + (level * (self.calib[1] - self.calib[0])) / 100.0)
        return level, int(calibrated * self.max_power / 100)

    def set_power(self, left_power, right_power = None):
        if right_power is None:
            right_power = left_power
        assert 0 <= left_power <= 100 and 0 <= right_power <= 100, (
                'power values must be between 0 and 100 (left: %r, right: %r)' %
                (left_power, right_power))

        self.left_level, self.left_threshold = self._set_level(left_power)
        self.right_level, self.right_threshold = self._set_level(right_power)

    def _ok_value(self):
        return 'OK %d,%d -> %d,%d' % (
                self.left_level,
                self.right_level,
                self.left_threshold,
                self.right_threshold)

    def process_line(self, line):
        assert line, 'Expecting line as input'

        elements = line.lower().split()
        length = len(elements)

        if elements[0] in ('m', 'move'):
            assert length == 3 or length == 2, (
                    'Expecting one or two arguments to move command')
            l = int(elements[1])
            if length == 2:
                self.set_power(l)
            else:
                r = int(elements[2])
                self.set_power(l, r)

            return self._ok_value()

        elif elements[0] in ('s', 'stop'):
            self.set_power(0)
            return self._ok_value()

        elif elements[0] in ('c', 'calib', 'calibrate'):
            assert length == 3, 'Expecting two arguments to calibrate command'
            low, high = int(elements[1]), int(elements[2])
            assert 0 <= low < high, 'low must be >= 0 and less than high value'
            assert low < high <= 100, 'high must be <= 100 and greater than low value'
            self.calib = (low, high)
            self.set_power(self.left_level, self.right_level)
            return ("# calibrate %d %d\n" % self.calib) + self._ok_value()

        elif elements[0] in ('t', 'status'):
            return self._ok_value()

        elif elements[0] in ('h', 'help'):
            return """# Usage:
#  m|move <power>            Set power on both wheels to <power>
#  m|move <left> <right>     Set power on left and right wheels to <left> and <right>
#
#  s|stop                    Stop - equivalent to 'm 0'
#
#  c|calib <low> <high>      Set calibration values, this allows mapping power values for move
#                            from 0-100 onto 'low' - 'high'
#
#  t|status                  Get the current power for each wheel
#
#  x|exit                    Exits the process, stops listening on STDIN
#
#  h|help                    Display this message
OK"""


        elif elements[0] in ('x', 'exit', 'q', 'quit'):
            self.set_power(0)
            return 'EXIT'

        else:
            assert False, 'Unknown command %r' % line


def run():
    scuber = Scuber()
    scuber.start()
    ret = 'ACK'
    while ret != 'EXIT':
        try:
            line = sys.stdin.readline()
            line = line[:-1]
            ret = scuber.process_line(line) if len(line) else 'ACK'
        except Exception as e:
            ret = 'ERROR ' + str(e)

        print(ret)

    scuber.stop()
