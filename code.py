import time

import board
import keypad
import rotaryio
import digitalio

import usb_hid
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard import Keyboard

def convert_GPIO(data):
    if type(data[0]) == list:
        for x in range(len(data)):
            for y in range(len(data[x])):
                data[x][y] = getattr(board, f"GP{data[x][y]}", None)
    else:
        for x in range(len(data)):
            data[x] = getattr(board, f"GP{data[x]}", None)

    return data

GPIO = [[19, 20, 21],
        [[0, 1, 2, 3], [16, 17, 18]],
        [[14, 15], [12, 13], [10, 11]]]

GPIO_ENC = convert_GPIO(GPIO[2])
GPIO_MTX = convert_GPIO(GPIO[1])
GPIO_BTN = convert_GPIO(GPIO[0])

ENC = []
POS = []
for x in GPIO_ENC: 
    ENC.append(rotaryio.IncrementalEncoder(x[0], x[1]))
    POS.append([0, 0])

BTN = []
for x in GPIO_BTN:
    temp = digitalio.DigitalInOut(x)
    temp.direction = digitalio.Direction.INPUT
    temp.pull = digitalio.Pull.DOWN

    BTN.append(temp)

MTX = keypad.KeyMatrix(
    column_pins=(GPIO_MTX[0]),
    row_pins=(GPIO_MTX[1]),
)

while True:
    event = MTX.events.get()
    if event:
        print(event)

    for x in range(len(ENC)):
        POS[x][1] = ENC[x].position
        if POS[x][0] != POS[x][1]:
            if POS[x][0] > POS[x][1]:
                print("-1")
            if POS[x][0] < POS[x][1]:
                print("+1")
            
            POS[x][0] = POS[x][1]
            print(POS[x][0])

    for x in BTN:
        if x.value:
            print(x)
            time.sleep(.5)
    
    time.sleep(.1)