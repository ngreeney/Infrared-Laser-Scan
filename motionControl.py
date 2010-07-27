import visa as v
import numpy as np
import time as time

#Made for the Newport ESP300 motion controller
#other commands for controller are found in section 3 of the ESP300 Users Manual

def setupMotor():
    motor=v.SerialInstrument("ASRL1",baud_rate=19200)    
    setZeroLoc(motor)
    return motor


def moveTo(motor,x,y):
    #turns motors on
    motor.write("1MO")
    motor.write("2MO")
    
    #moves to absolute location x,y
    motor.write("1PA"+np.str(x))
    motor.write("2PA"+np.str(y))

#    #moves to relative location x,y
#    motor.write("1PR"+np.str(x))
#    motor.write("2PR"+np.str(y))

    #wait for motor to stop
    while motor.ask("1MD?")==0 or motor.ask("2MD?")==0:
        time.sleep(0.01)
    return

#sets current location to be 0.0 for both axis
def setZeroLoc(motor):
    motor.write("1DH")
    motor.write("2DH")
    return

#don't forget to close access to serial connections 
#or connection will be lost till the computer is restarted
def close(motor):
    motor.close()
    return