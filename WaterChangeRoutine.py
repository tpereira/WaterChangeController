# Water change routine 16 May 2021 Tushar P

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

ReservoirCheckEnabled = "N"

S1Pin = 11 #Drain Pump
S2Pin = 12 #RO Reservoir Pump
S3Pin = 13 #Well Water Solenoid
S4Pin = 7  #Reserved - Maybe for RO filter later

L1Pin = 16 #High Water Tank Level
L2Pin = 18 #Low Water Tank Level
L3Pin = 22 #Low RO Reservoir Level

#TimeOuts in seconds
DrainTimeOut = 900
ROPumpTimeOut = 600
WellWaterDelay = 1200

print ("Started Water Change Routine")

GPIO.setup(S1Pin, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(S2Pin, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(S3Pin, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(S4Pin, GPIO.OUT, initial=GPIO.HIGH)

GPIO.output(S1Pin, GPIO.HIGH)
GPIO.output(S2Pin, GPIO.HIGH)
GPIO.output(S3Pin, GPIO.HIGH)
GPIO.output(S4Pin, GPIO.HIGH)

GPIO.setup(L1Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(L2Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(L3Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

L1PinState = GPIO.input(L1Pin)
L2PinState = GPIO.input(L2Pin)
L3PinState = GPIO.input(L3Pin)

print ("ReservoirCheckEnabled", ReservoirCheckEnabled)
print ("L1PinState", L1PinState)
print ("L2PinState", L2PinState)
print ("L3PinState", L3PinState)

try:
    #Check water in Reservoir
    if ReservoirCheckEnabled == "Y":
        if L3PinState == True:
            print ("RO Reservoir water level too low. Exiting ...")
            exit()

    print ("Detected sufficient water in RO Reservoir. Continuing ...")

    print ("Starting drain pump")
    GPIO.output(S1Pin, GPIO.LOW)

    Timeout = DrainTimeOut

    while True:
        Timeout = Timeout - 1
        time.sleep(1)
        L2PinState = GPIO.input(L2Pin)
        print ("L2PinState",L2PinState,"Timeout",Timeout)

        if Timeout == 0:
            #print ("Timeout Exceeded. Exiting ...")
            GPIO.output(S1Pin, GPIO.HIGH)
            raise ValueError("Timeout Exceeded. Exiting ...")

        if L2PinState == True:
            print ("Low Water Tank Level Reached")
            GPIO.output(S1Pin, GPIO.HIGH)
            break

    time.sleep(5)
    print ("Stage 1 complete")
    print ("Stage 2 started")

    print ("Starting RO pump")
    GPIO.output(S2Pin, GPIO.LOW)

    time.sleep(1)
    print ("Starting Well water solenoid")
    GPIO.output(S3Pin, GPIO.LOW)

    Timeout = ROPumpTimeOut

    while True:
        Timeout = Timeout - 1
        time.sleep(1)
        L1PinState = GPIO.input(L1Pin)
        print ("L1PinState",L1PinState,"Timeout",Timeout)

        if Timeout == 0:
            #print ("Timeout Exceeded. Exiting ...")
            GPIO.output(S2Pin, GPIO.HIGH)
            GPIO.output(S3Pin, GPIO.HIGH)
            raise ValueError("Timeout Exceeded. Exiting ...")
            
        if L1PinState == False:
            print ("High Water Tank Level Reached")
            GPIO.output(S2Pin, GPIO.HIGH)
            break

    print ("Stage 2 completed")

    print ("Stage 3 started. Continuing Well water for ",WellWaterDelay," seconds more ...")
    time.sleep(WellWaterDelay)
    GPIO.output(S3Pin, GPIO.HIGH)
    print ("Stage 3 complete. Stopped Well water solenoid")

    print ("Water change routine successfully completed")

except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    print("Keyboard interrupt")

except ValueError as e:
    print("Error")
    print(e)
    exit()
   
finally:
    print("Cleaning up") 
    GPIO.cleanup()


