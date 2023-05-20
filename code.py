import api

device = api.MacroBoard()
keyboard = api.keyboard()

while True:
    device.CheckMatrix()
    device.CheckEncoders()