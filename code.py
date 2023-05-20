import time
import json

import board
import keypad
import rotaryio
import digitalio

import usb_hid
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard import Keyboard

def loadConfig(file):
    file = open(f'config/{file}.json')
    config = json.load(file)
    file.close()

    return config

def loadGPIO():
    DATA = loadConfig('GPIO')
    print(DATA['matrix'])

    GPIO_ENC = convertGPIO(DATA['encoders'])
    GPIO_MTX = convertGPIO([DATA['matrix']['columns'], DATA['matrix']['rows']])
    GPIO_BTN = convertGPIO(DATA['buttons'])

    return GPIO_ENC, GPIO_MTX, GPIO_BTN
def convertGPIO(data):
    if type(data[0]) == list:
        for x in range(len(data)):
            for y in range(len(data[x])):
                data[x][y] = getattr(board, f"GP{data[x][y]}", None)
    else:
        for x in range(len(data)):
            data[x] = getattr(board, f"GP{data[x]}", None)

    return data


def Press(data):
    MODE = data['mode']
    KEYS = data['keys']

    if MODE == 'press':
        for KEY in KEYS:
            keys = f"Keycode.{KEY}"
            ExecPress(keys)

    if MODE == 'combo':
        TEMP = []
        for KEY in KEYS: 
            TEMP.append(f"Keycode.{KEY}")
        
        keys = ', '.join(TEMP)
        ExecPress(keys)
    
    if MODE == 'write':
        for LETTER in KEYS:
            KEY = LETTER.upper()
            KEY = KEY.replace(' ', 'SPACE')

            keys = f"keycode.{KEY}"
            ExecPress(keys)
def ExecPress(keys):
        exec(f"keyboard.press({keys})")
        exec(f"time.sleep(.01)")
        exec(f"keyboard.release({keys})")
        exec(f"time.sleep(.01)")

GPIO_ENC, GPIO_MTX, GPIO_BTN = loadGPIO()
BINDS = loadConfig('bind/default')

print(BINDS)

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

keyboard = Keyboard(usb_hid.devices)

while True:
    event = MTX.events.get()
    if event:
        key = event.key_number
        bind = BINDS['matrix'][key]
        if bind['on_press']:
            if event.pressed:
                Press(bind)
        else:
            if event.released:
                Press(bind)

    for x in range(len(ENC)):
        bind = BINDS['encoders'][x]
        
        POS[x][1] = ENC[x].position
        if POS[x][0] != POS[x][1]:
            if POS[x][0] > POS[x][1]:
                print("-1")
                Press(bind['left'])
            if POS[x][0] < POS[x][1]:
                print("+1")
                Press(bind['right'])
            
            POS[x][0] = POS[x][1]

    for x in range(len(BTN)):
        if BTN[x].value:
            bind = BINDS['encoders'][x]['click']
            Press(bind)

            time.sleep(.5)
    
    time.sleep(.1)