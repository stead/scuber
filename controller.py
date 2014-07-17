import comms
import time

# constants
K_P = 0.5
K_I = K_P / 3.0
K_D = 0.0

K_HEADING = 1.0
K_SPEED = 0.1
LATERAL_OFFSET = -29

class Controller(object):
    def __init__(self):
        self._integrated_error = 0
        self._last_timestamp = float(time.clock())
        self._last_error = 0
        self._controller_debug = True
        self._conn = comms.Connection()
        self._write("import board; board.run()")
        self._write("c 30 40")

    def output_to_motor(self, percent_l, percent_r):
        left_int = min(int(percent_l * 100.0), 100)
        right_int = min(int(percent_r * 100.0), 100)
        self._write("m %d %d" % (left_int, right_int,))

    def close(self):
        self._conn.close()

    def _write(self, stmt):
        self._conn.writeline(stmt)
        print "\n".join(self._conn.readall())

    def update_controller(self, speed_heading, resetIDTerm=False):
        current_error, target_speed  = speed_heading

        # Heading PID
        current_timestamp = float(time.clock())
        delta_t = current_timestamp - self._last_timestamp

        self._integrated_error = self._integrated_error + delta_t * current_error
        delta_error = (current_error - self._last_error) / delta_t
        target_heading = K_P * current_error + K_I * self._integrated_error + K_D * delta_error
        
        # safety check to avoid I-term/D-term windup
        if (delta_t > 1.0):
            resetIDTerm = True
        if (resetIDTerm):
            self._integrated_error = 0
            delta_error = 0
        
        if (self._controller_debug):
            print "lineOffset= %.3f, TargetHeading= %.3f" % (current_error, target_heading)
            print "P%%= %.2f, I%%= %.2f, D%%= %.2f, " % ((K_P*current_error / target_heading), (K_I*self._integrated_error / target_heading), (K_D*delta_error / target_heading))

        # update values for next loop iteration
        self._last_timestamp = current_timestamp
        self._last_error = current_error

        # translate heading and speed to motor outputs
        if target_speed == 0:
            output_l, output_r = 0.0, 0.0
        else:
            output_r = K_SPEED * target_speed
            output_l = K_SPEED * target_speed

            heading_correction_factor = abs(target_heading * K_HEADING / target_speed)
            heading_sign = 1.0
            if target_heading < 0:
                heading_sign = -1.0
            # limit heading_correction_factor to 1/2 base output
            heading_correction_factor = heading_sign * min(heading_correction_factor, output_r/2.0)

            output_r = output_r - heading_correction_factor
            output_l = output_l + heading_correction_factor

        if (self._controller_debug):
            print("output_l: %f\t output_r: %f" % (output_l, output_r))
            print("")

        return (output_l, output_r)
