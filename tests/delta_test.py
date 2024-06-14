from acrome import controller



dev = controller.Delta("COM27", baudrate=115200)




dev.set_motors([10,10,10])
dev.update()