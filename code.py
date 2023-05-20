import api
import time

device = api.MacroBoard('bind/default')
keyboard = api.keyboard()

brush = 0

while True:
    device.CheckMatrix()
    device.CheckEncoders()
    
    BTN = device.listButtons()
    for num in range(len(BTN)):
        if BTN[num].value:
            if num == 2:                
                if brush == 0: api.Press(['press', 'b'])
                elif brush == 1: api.Press(['press', 'z'])
                else: api.Press(['press', 'e'])

                brush += 1
                if brush > 2: brush = 0

                print(brush)

            time.sleep(.2)
    