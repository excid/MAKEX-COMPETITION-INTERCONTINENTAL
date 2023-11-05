# REAL CODE V.2
# libraries (DO NOT TOUCH)
import novapi
from mbuild import gamepad
from mbuild.encoder_motor import encoder_motor_class
from mbuild import power_expand_board
from mbuild.ranging_sensor import ranging_sensor_class
from mbuild.smartservo import smartservo_class
from mbuild import power_manage_module 

##          ##           ##

# settings
encoderSpeedDivider = 2         # set encoder speed **divider** / the more value = the slower
DC_DefaultSpeed = 100           # set DC motor default speed
servoDefaultSpeed = 10          # set MANUAL servo default speed (rotation per minute)

# flag DC settings
flagEncoderSpeedDivider = 10    # set power of flag DC motor speed
flagStopPower = 1              # set power of flag DC motor when control isn't pressed

# servo settings
shooterServoResetDegree = 115        # shooter position servo degree
shooterServoResetSpeed = 100         # speed in RPM
shooterServoResetMultiplier = 1.07   

# brushless settings # set brushless speed (1 -> FASTEST, 4 -> SLOWEST)
brushlessSpeed1 = 60            # number 4
brushlessSpeed2 = 100           # number 1
brushlessCooldown = 0.4         # delay between brushless and above DC

# sensitivities
pivotSensitivity = 75           # right joystick
                  
                                   # ยกธง (M6)
                                   # ล้อ (M1-M4) 
# button settings
autoStateKey = "L2"                # automatic state key
autoCancelKey = "R2"               # automatic cancel key
button1 = "L1"                     # สายพานขึ้น (DC5-DC6, DC7-DC8)
button2 = "R1"                     # สายพานลง (DC5-DC6, DC7-DC8)
button3 = "Up"                     # สลิงขึ้น (DC3)
button4 = "Down"                       # สลิงลง (DC3)
button5 = "Left"                   # หนีบออก (DC2)
button6 = "Right"                  # หนีบเข้า (DC2)
button7 = "N2"                     # ที่ยิงยกลง servo1 (M5)
button8 = "N3"                     # ที่ยิงยกขึ้น servo1 (M5)
button11 = "N4"                    # ยิงเร็ว (BL1-BL2, DC1, DC4)
button12 = "N1"                    # ยิงช้า (BL1-BL2, DC1, DC4)

##### PROGRAMMER ZONE #####

# variables
automaticState = False
isAutoPressed = False

# gyro


# class definitions
encoder1 = encoder_motor_class("M1", "INDEX1")
encoder2 = encoder_motor_class("M2", "INDEX1")
encoder3 = encoder_motor_class("M3", "INDEX1")
encoder4 = encoder_motor_class("M4", "INDEX1")
sensor = ranging_sensor_class("PORT1", "INDEX1")
servo1 = smartservo_class("M5", "INDEX1")
flagEncoder = encoder_motor_class("M6", "INDEX1")

# encoder control function
def encoderControl(divider:float): # check!
    vertical = -gamepad.get_joystick("Ly")
    horizontal = gamepad.get_joystick("Lx")
    pivot = gamepad.get_joystick("Rx")

    encoder1.set_power(-((pivot if (pivot>pivotSensitivity or pivot < -pivotSensitivity) else 0) + vertical + (horizontal*1.65 if (horizontal > 90 or horizontal < -90) else horizontal)) / divider)
    encoder2.set_power((-(pivot if (pivot>pivotSensitivity or pivot < -pivotSensitivity) else 0) + vertical - (horizontal*1.65 if (horizontal > 90 or horizontal < -90) else horizontal)) / divider)
    encoder3.set_power(-((pivot if (pivot>pivotSensitivity or pivot < -pivotSensitivity) else 0) + vertical - (horizontal*1.65 if (horizontal > 90 or horizontal < -90) else horizontal)) / divider)
    encoder4.set_power((-(pivot if (pivot>pivotSensitivity or pivot < -pivotSensitivity) else 0) + vertical + (horizontal*1.65 if (horizontal > 90 or horizontal < -90) else horizontal)) / divider)

# stop encoder
def robotStop():
    encoder1.set_power(0)
    encoder2.set_power(0)
    encoder3.set_power(0)
    encoder4.set_power(0)

# brushless control function
def brushlessPower(speed:float):
    power_expand_board.set_power("BL1", speed)
    power_expand_board.set_power("BL2", speed)

# control shooter
def brushlessControl(key1:str, key2:str, speed1:float, speed2:float):
    if gamepad.is_key_pressed(key1):
        brushlessPower(speed1)
        if novapi.timer() >= brushlessCooldown:
            power_expand_board.set_power("DC4", 100)
            power_expand_board.set_power("DC1", -100)
    elif gamepad.is_key_pressed(key2):
        brushlessPower(speed2)
        if novapi.timer() >= brushlessCooldown:
            power_expand_board.set_power("DC4", 100)
            power_expand_board.set_power("DC1", -100)
    else:
        power_expand_board.stop("BL1")
        power_expand_board.stop("BL2")
        power_expand_board.stop("DC4")
        power_expand_board.stop("DC1")
        novapi.reset_timer()
        

# control flag DC
def flagDC_Control(stop_power:float):
    flagEncoder.set_power(gamepad.get_joystick("Ry")/flagEncoderSpeedDivider if gamepad.get_joystick("Ry")!=0 else stop_power) 

# control all DC
def DC_Control(key1:str, key2:str, key3:str, key4:str, key5:str, key6:str, speed:float):
    if gamepad.is_key_pressed(key1):
        power_expand_board.set_power("DC5", speed)
        power_expand_board.set_power("DC6", speed)
        power_expand_board.set_power("DC7", -speed)
        power_expand_board.set_power("DC8", -speed)
    elif gamepad.is_key_pressed(key2):
        power_expand_board.set_power("DC5", -speed)
        power_expand_board.set_power("DC6", -speed)
        power_expand_board.set_power("DC7", speed)
        power_expand_board.set_power("DC8", speed)
    elif gamepad.is_key_pressed(key3):
        power_expand_board.set_power("DC3", -speed)
    elif gamepad.is_key_pressed(key4):
        power_expand_board.set_power("DC3", speed)
    elif gamepad.is_key_pressed(key5):
        power_expand_board.set_power("DC2", speed)
    elif gamepad.is_key_pressed(key6):
        power_expand_board.set_power("DC2", -speed)
    else:
        power_expand_board.stop("DC2")
        power_expand_board.stop("DC3")
        power_expand_board.stop("DC5")
        power_expand_board.stop("DC6")
        power_expand_board.stop("DC7")
        power_expand_board.stop("DC8")

# servo control function
def servoControl(servoName, key1:str, key2:str, speed:float):
    if gamepad.is_key_pressed(key1):
        servoName.set_power(speed)
    elif gamepad.is_key_pressed(key2):
        servoName.set_power(-speed)
    else:
        servoName.set_power(0)

#  reset servo position
def servoReset(servoName, key1:str, degree:float, speed:float):
    if gamepad.is_key_pressed(key1):
        servoName.move_to(degree, speed)
        
# manual stage function
def manualStage():
    encoderControl(encoderSpeedDivider)
    DC_Control(button1, button2, button3, button4, button5, button6, DC_DefaultSpeed)
    brushlessControl(button11, button12, brushlessSpeed1, brushlessSpeed2)
    servoReset(servo1, button7, shooterServoResetDegree, shooterServoResetSpeed)
    servoReset(servo1, button8, shooterServoResetDegree*shooterServoResetMultiplier, shooterServoResetSpeed)
    flagDC_Control(flagStopPower)

# automatic stage function
def autoReset():
    robotStop()
    novapi.reset_timer()

# auto stage wait
def autoWait(time:float):
    autoReset()
    while novapi.timer() <= time and(not gamepad.is_key_pressed(autoCancelKey)):
        pass

# auto stage transition        
def autoTrans():
    autoReset()
    autoWait(1)

# automatic stage (MODIFY THIS VERYYYYYYYYYYYYYYYYYYYY NECCESSARY)
def automaticStage():
    power_expand_board.set_power("DC5", 100)
    power_expand_board.set_power("DC6", 100)  
    power_expand_board.set_power("DC7", -100)
    power_expand_board.set_power("DC8", -100)

    while novapi.timer() <= 2 and(not gamepad.is_key_pressed(autoCancelKey)):
        encoder1.set_power(30)
        encoder2.set_power(-30)
        encoder3.set_power(30)
        encoder4.set_power(-30)


    while (not gamepad.is_key_pressed(autoCancelKey) and (automaticState or power_manage_module.is_auto_mode())):
        power_expand_board.set_power("DC5", 100)
        power_expand_board.set_power("DC6", 100)
        power_expand_board.set_power("DC7", -100)
        power_expand_board.set_power("DC8", -100)
        
    '''autoTrans()

    while novapi.timer() <= 0.5 and(not gamepad.is_key_pressed(autoCancelKey)):
        encoder1.set_power(-100)
        encoder2.set_power(-100)
        encoder3.set_power(-100)
        encoder4.set_power(-100)

    autoTrans()

    while novapi.timer() <= 2.2 and(not gamepad.is_key_pressed(autoCancelKey)):
        encoder1.set_power(20)
        encoder2.set_power(-20)
        encoder3.set_power(20)
        encoder4.set_power(-20)

    autoReset()'''

    '''while novapi.timer() <= 0.8 and(not gamepad.is_key_pressed(autoCancelKey)):
        encoder1.set_power(20)
        encoder2.set_power(20)
        encoder3.set_power(20)
        encoder4.set_power(20)
    
    autoReset()
    autoWait(1)

    while novapi.timer() <= 2 and(not gamepad.is_key_pressed(autoCancelKey)):
        brushlessPower(100)
        power_expand_board.set_power("DC4", -100)
        power_expand_board.set_power("DC1", -100)'''
    
# loop (main)
while True:
    if not automaticState and not power_manage_module.is_auto_mode():
        manualStage()
        if gamepad.is_key_pressed(autoStateKey) and not isAutoPressed:
            automaticState = True

    elif (automaticState or power_manage_module.is_auto_mode()) and not isAutoPressed:  
        automaticStage()
        autoTrans()
        isAutoPressed = True
        automaticState = False
    else:
        manualStage()