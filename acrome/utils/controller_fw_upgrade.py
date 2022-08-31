from acrome.controller import *

print("\nDevice will enter to the bootloader.") 
print("DO NOT DISCONNECT POWER FROM THE DEVICE SINCE IT MAY BRICK YOUR DEIVCE!\n")

print("Press any key to continue or CTRL + C to cancel")

input()

dev = Controller()

if (not dev.ping()):
	print("Could not reach to the Acrome Controller Board. Check your serial connection.")
	exit(-1)
else:
	dev.get_board_info() #Trigger update of board info
	print("Received ping reply. Proceeding with firmware upgrade.")
	print("Current firmware version is: ", dev.get_board_info()['Software Version'], '\n')

print("Latest available firmware version is", dev.get_latest_version())
if(dev.fetch_fw_binary()):
	print("\nFirmware file successfully fetched from repository!")

while not dev.ping():
	pass
dev.enter_bootloader()
dev.update_fw_binary()

print("Firmware update is completed. Please reset the Acrome Controller by pressing the reset button or disconnecting and reconnecting power.")
