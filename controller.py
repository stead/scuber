import time

# constants
K_P = 0.5
K_I = 0.0
K_D = 0.0

K_HEADING = 1.0
K_SPEED = 0.1
LATERAL_OFFSET = -29

class Controller(object):
    def __init__(self):
        self._integrated_error = 0
        self._last_timestamp = float(time.clock())
        self._last_error = 0

    # TODO: Communicate to motor here
    def output_to_motor(self, percent_l, percent_r):
        print "LOut = %d\tROut=%d" % (percent_l, percent_r)

    def update_controller(self, speed_heading):
        target_speed, current_error = speed_heading

        # Heading PID
        current_timestamp = float(time.clock())
        delta_t = current_timestamp - self._last_timestamp

        self._integrated_error = self._integrated_error + delta_t * current_error
        delta_error = (current_error - self._last_error) / delta_t
        target_heading = K_P * current_error + K_I * self._integrated_error + K_D * delta_error
        print "TargetHeading= %f" % target_heading

        # update values for next loop iteration
        self._last_timestamp = current_timestamp
        self._last_error = current_error

        # translate heading and speed to motor outputs
        output_l, output_r = self.ConvertSpeedAndHeadingToMotorOutput(target_heading, target_speed)

        self.output_to_motor(output_l, output_r)

    def ConvertSpeedAndHeadingToMotorOutput(self, target_speed, target_heading):
        # solve system:
        # output_r - output_l = target_heading * K_HEADING / target_speed
        # output_r + output_l = target_speed * K_SPEED

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

        print("output_l: %f\t output_r: %f" % (output_l, output_r))

        return (output_l, output_r)
