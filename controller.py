import time

def GetTestLateralOffset():
	return -29

def OutputToMotor(percentL, percentR):
	print "LOut = %d\tROut=%d" % (percentL, percentR)
	
# constants
Kp = 0.5
Ki = 0.0
Kd = 0.0

kHeading = 1.0
kSpeed = 0.1

integratedError = 0
lastTimestamp = float(time.clock())
lastError = 0
	
def StartController():
	global integratedError
	global lastTimestamp
	global lastError
	
	integratedError = 0
	lastTimestamp = float(time.clock())
	lastError = 0

def UpdateController(i):
	global integratedError
	global lastTimestamp
	global lastError
	
	# Heading PID
	#currentError = GetTestLateralOffset()
	currentError = i
	currentTimestamp = float(time.clock())
	deltaT = currentTimestamp - lastTimestamp
	
	integratedError = integratedError + deltaT*currentError
	deltaError = (currentError - lastError) / deltaT
	targetHeading = Kp*currentError + Ki*integratedError + Kd*deltaError
	print "TargetHeading= %f" % targetHeading
	
	# update values for next loop iteration
	lastTimestamp = currentTimestamp
	lastError = currentError
	
	# determine desired Speed
	#speed = constant # Or slow down when approaching intersections
	targetSpeed = 2.0 # ft/s
	
	# translate heading and speed to motor outputs
	outputR, outputL = ConvertHeadingAndSpeedToMotorOutput(targetHeading, targetSpeed)

def ConvertHeadingAndSpeedToMotorOutput(targetHeading, targetSpeed):
	# solve system:
	# outputR - outputL = targetHeading * kHeading / targetSpeed
	# outputR + outputL = targetSpeed * kSpeed
	
	outputR = kSpeed * targetSpeed
	outputL = kSpeed * targetSpeed
	
	headingCorrectionFactor = abs(targetHeading * kHeading / targetSpeed)
	headingSign = 1.0
	if targetHeading < 0:
		headingSign = -1.0
	# limit headingCorrection to 1/2 base output
	headingCorrectionFactor = headingSign * min(headingCorrectionFactor, outputR/2.0)
	
	#print("base output: %f\t heading correct: %f" % (outputR, headingCorrectionFactor))
		
	outputR = outputR - headingCorrectionFactor
	outputL = outputL + headingCorrectionFactor
	
	print("outputR: %f\t outputL: %f" % (outputR, outputL))
	
	# check bounds
	#outputR = min(max(0,outputR), 1)
	#outputL = min(max(0,outputL), 1)
	
	return (outputR, outputL)
