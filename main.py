# libraries
import novapi
from mbuild import gamepad
from mbuild.encoder_motor import encoder_motor_class
from mbuild import power_expand_board
from mbuild.ranging_sensor import ranging_sensor_class
from mbuild.smartservo import smartservo_class


# settings
encoderSpeedDivider = 6         # set encoder speed **divider** / the more value = the slower
DC_DefaultSpeed = 100           # set DC motor default speed
servoDefaultSpeed = 10          # set MANUAL servo default speed (rotation per minute)
servoDefaultDegree = 5          # set MANUAL servo default degree
autoStateKey = "L2"             # automatic state key

# brushless settings
brushlessSpeed1 = 100           # set brushless speed (1 -> FASTEST, 4 -> SLOWEST)
brushlessSpeed2 = 75
brushlessSpeed3 = 50
brushlessSpeed4 = 25


##### PROGRAMMER ZONE #####

# variables
timer = 0
automaticState = False
isAutoPressed = False

# class definitions
encoder1 = encoder_motor_class("M1", "INDEX1")
encoder2 = encoder_motor_class("M2", "INDEX1")
encoder3 = encoder_motor_class("M3", "INDEX1")
encoder4 = encoder_motor_class("M4", "INDEX1")
sensor = ranging_sensor_class("PORT1", "INDEX1")
servo1 = smartservo_class("M1", "INDEX1")
servo2 = smartservo_class("M2", "INDEX1")

# automatic stage function
def automaticStage():
    # # things
    automaticState=False

# encoder control function
def encoderControl(divider:float): # check!
    horizontal = gamepad.get_joystick("Lx")
    vertical = -gamepad.get_joystick("Ly")
    pivot = gamepad.get_joystick("Rx")

    encoder1.set_power((pivot + vertical + horizontal) / divider)
    encoder2.set_power(-(-pivot + vertical - horizontal) / divider)
    encoder3.set_power((pivot + vertical - horizontal) / divider)
    encoder4.set_power(-(-pivot + vertical + horizontal) / divider)

# brushless control function
def brushlessPower(speed:float):
    power_expand_board.set_power("BL1", speed)
    power_expand_board.set_power("BL2", speed)

def brushlessControl(key1:str, key2:str, key3:str, key4:str): # check!
    if gamepad.is_key_pressed(key1):
        brushlessPower(brushlessSpeed1)
    elif gamepad.is_key_pressed(key2):
        brushlessPower(brushlessSpeed2)
    elif gamepad.is_key_pressed(key3):
        brushlessPower(brushlessSpeed3)
    elif gamepad.is_key_pressed(key4):
        brushlessPower(brushlessSpeed4)
    else:
        power_expand_board.stop("BL1")
        power_expand_board.stop("BL2")

# DC control function
def DC_Control(key1:str, key2:str, speed:float): #add ...keyN
    if gamepad.is_key_pressed(key1):
        power_expand_board.set_power("DC5", speed)
        power_expand_board.set_power("DC6", speed)
        power_expand_board.set_power("DC7", speed)
        power_expand_board.set_power("DC8", speed)
    elif gamepad.is_key_pressed(key2):
        power_expand_board.set_power("DC5", -speed)
        power_expand_board.set_power("DC6", -speed)
        power_expand_board.set_power("DC7", -speed)
        power_expand_board.set_power("DC8", -speed)
    else:
        power_expand_board.stop("DC5")
        power_expand_board.stop("DC6")
        power_expand_board.stop("DC7")
        power_expand_board.stop("DC8")

# servo control function
def servoControl(servoName, key1:str, key2:str, degree:float, speed:float):
    if gamepad.is_key_pressed(key1):
        servoName.set_power(speed)
        #servoName.move(degree, speed)
    elif gamepad.is_key_pressed(key2):
        servoName.set_power(-speed)
        #servoName.move(-degree, speed)
    else:
        servoName.set_power(0)

# loop (main)
while True:
    try:
        if (not automaticState):
            if (gamepad.is_key_pressed(autoStateKey)) and (not isAutoPressed):
                automaticState = True
            else:
                servoControl(servo1, "Up", "Down", servoDefaultDegree, servoDefaultSpeed)
                encoderControl(encoderSpeedDivider)
                DC_Control("L1", "R1", DC_DefaultSpeed)
                brushlessControl("N4", "N3", "N2", "N1")
        else:
            timer = novapi.timer()
            if timer <= 30:
                automaticStage()
                isAutoPressed=True
            else:
                automaticState = False
                isAutoPressed=True

    except: # IF CODE RETURNS ERROR
        brushlessPower(30)