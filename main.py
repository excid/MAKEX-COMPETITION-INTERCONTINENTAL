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

# button settings
autoStateKey = "L2"                # automatic state key
button1 = "L1"                     # สายพานขึ้น
button2 = "R1"                     # สายพานลง
button3 = "Up"                     # สลิงขึ้น
button4 = "Down"                   # สลิงลง
button5 = "Left"                   # หนีบเข้า
button6 = "Right"                  # หนีบออก
button7 = "R2"                     # ยกธงขึ้น
button8 = "N2"                     # ที่ยิงยกขึ้น
button9 = "N3"                     # ที่ยิงยกลง
button10 = "+"                     # กวาดบอล / recycle เข้า
button11 = "≡"                     # กวาดบอล / recycle ออก                    
button12 = "N4"                    # ยิงเร็ว
button13 = "N1"                    # ยิงช้า

# brushless settings
brushlessSpeed1 = 100           # set brushless speed (1 -> FASTEST, 4 -> SLOWEST)
brushlessSpeed2 = 50


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

# encoder control function
def encoderControl(divider:float): # check!
    horizontal = gamepad.get_joystick("Lx")
    vertical = -gamepad.get_joystick("Ly")
    pivot = gamepad.get_joystick("Rx")

    encoder1.set_power((pivot + vertical + horizontal) / divider)
    encoder2.set_power(-(-pivot + vertical - horizontal) / divider)
    encoder3.set_power((pivot + vertical - horizontal) / divider)
    encoder4.set_power(-(-pivot + vertical + horizontal) / divider)

def encoderMove(statusEncoder1:int, statusEncoder2:int, statusEncoder3:int, statusEncoder4:int, speed:float, time:float): # time in seconds
    encoder1.set_power(statusEncoder1*speed)
    encoder2.set_power(statusEncoder2*speed)
    encoder3.set_power(statusEncoder3*speed)
    encoder4.set_power(statusEncoder4*speed)
    time.sleep(time)
    encoder1.set_power(0)
    encoder2.set_power(0)
    encoder3.set_power(0)
    encoder4.set_power(0)

# brushless control function
def brushlessPower(speed:float):
    power_expand_board.set_power("BL1", speed)
    power_expand_board.set_power("BL2", speed)

def brushlessControl(key1:str, key2:str, speed1, speed2): # check!
    if gamepad.is_key_pressed(key1):
        brushlessPower(speed1)
    elif gamepad.is_key_pressed(key2):
        brushlessPower(speed2)
    else:
        power_expand_board.stop("BL1")
        power_expand_board.stop("BL2")

# DC control function
def DC_Control(key1, key2, key3, key4, key5, key6, key7, speed): #add ...keyN
    if gamepad.is_key_pressed(key1):
        power_expand_board.set_power("DC4", speed)
        power_expand_board.set_power("DC5", speed)
        power_expand_board.set_power("DC6", speed)
        power_expand_board.set_power("DC7", speed)
        power_expand_board.set_power("DC8", speed)
    elif gamepad.is_key_pressed(key2):
        power_expand_board.set_power("DC4", -speed)
        power_expand_board.set_power("DC5", -speed)
        power_expand_board.set_power("DC6", -speed)
        power_expand_board.set_power("DC7", -speed)
        power_expand_board.set_power("DC8", -speed)
    elif gamepad.is_key_pressed(key3):
        power_expand_board.set_power("DC3", speed)
    elif gamepad.is_key_pressed(key4):
        power_expand_board.set_power("DC3", -speed)
    elif gamepad.is_key_pressed(key5):
        power_expand_board.set_power("DC2", speed)
    elif gamepad.is_key_pressed(key6):
        power_expand_board.set_power("DC2", -speed)
    elif gamepad.is_key_pressed(key7):
        power_expand_board.set_power("DC1", -speed)
    else:
        power_expand_board.stop("DC1")
        power_expand_board.stop("DC2")
        power_expand_board.stop("DC3")
        power_expand_board.stop("DC4")
        power_expand_board.stop("DC5")
        power_expand_board.stop("DC6")
        power_expand_board.set_power("DC7", 1)
        power_expand_board.stop("DC8")

# servo control function
def servoControl(servoName, key1:str, key2:str, speed:float):
    if gamepad.is_key_pressed(key1):
        servoName.set_power(speed)
    elif gamepad.is_key_pressed(key2):
        servoName.set_power(-speed)
    else:
        servoName.set_power(0)
        
# automatic stage function
def automaticStage():
    brushlessPower(20)
    automaticState=False

# loop (main)
while True:
    try:
        if (not automaticState):
            if (gamepad.is_key_pressed(autoStateKey)) and (not isAutoPressed):
                automaticState = True
            else:
                encoderControl(encoderSpeedDivider)
                DC_Control(button1, button2, button3, button4, button5, button6, button7, DC_DefaultSpeed)
                servoControl(servo1, button8, button9, servoDefaultSpeed)
                servoControl(servo2, button10, button11, servoDefaultSpeed)
                brushlessControl(button12, button13, brushlessSpeed1, brushlessSpeed2)

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