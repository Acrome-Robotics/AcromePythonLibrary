from acrome import controller

dev = controller.Stewart("COM8", baudrate=115200)


while True:
    dev.update()