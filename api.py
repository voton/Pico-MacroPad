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
    for item in DATA:
        if type(DATA[item]) == dict:
            for x in DATA[item]:
                for y in range(len(DATA[item][x])):
                    DATA[item][x][y] = getattr(board, f"GP{DATA[item][x][y]}", None)
        else:
            if type(DATA[item][0]) == list:
                for x in range(len(DATA[item])):
                    for y in range(len(DATA[item][x])):
                        DATA[item][x][y] = getattr(board, f"GP{DATA[item][x][y]}", None)
            else:
                for x in range(len(DATA[item])):
                    DATA[item][x] = getattr(board, f"GP{DATA[item][x]}", None)
    return DATA

def initButtons(GPIO):
    BTN = []
    for PIN in GPIO:
        temp = digitalio.DigitalInOut(PIN)
        temp.direction = digitalio.Direction.INPUT
        temp.pull = digitalio.Pull.DOWN

        BTN.append(temp)

    return BTN

def initMatrix(GPIO):
    matrix = keypad.KeyMatrix(
        column_pins=(GPIO['columns']),
        row_pins=(GPIO['rows']),
    )

    return matrix

def initEncoders(GPIO):
    ENC = []
    for PIN in GPIO:
        ENC.append([[0, 0], rotaryio.IncrementalEncoder(PIN[0], PIN[1])])

    return ENC

def keyboard():
    return Keyboard(usb_hid.devices)

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

class MacroBoard:
    def __init__(self):
        self.GPIO = loadGPIO()
        self.BIND = loadConfig('bind/default')

        self.BUTTON = initButtons(self.GPIO['buttons'])
        self.MATRIX = initMatrix(self.GPIO['matrix'])
        self.ENCODER = initEncoders(self.GPIO['encoders'])

    def CheckMatrix(self):
        matrix = self.MATRIX.events.get()
        if matrix:
            key = matrix.key_number
            try: 
                bind = self.BIND['matrix'][key]
                if bind['on_press']:
                    if matrix.pressed: Press(bind)
                else:
                    if matrix.released: Press(bind)
            except(KeyError, IndexError): print("Button is unset")

    def CheckEncoders(self):
        for x in range(len(self.ENCODER)):
            POS = self.ENCODER[x][0]
            ENC = self.ENCODER[x][1]
            try:
                BIND = self.BIND['encoders'][x]

                POS[1] = ENC.position
                if POS[0] != POS[1]:
                    if POS[0] > POS[1]: Press(BIND['left'])
                    if POS[0] < POS[1]: Press(BIND['right'])
                    POS[0] = POS[1]

                    print(POS)
            except(KeyError, IndexError): pass
        
        BTN = self.BUTTON
        for x in range(len(BTN)):
            if BTN[x].value:
                try: 
                    Press(self.BIND['encoders'][x]['click'])
                    time.sleep(.5)
                except(KeyError, IndexError): print("Button is unset")