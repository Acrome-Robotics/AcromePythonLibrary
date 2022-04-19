# Overview

This library provides easy-to-use Python modules for interacting with Acrome Robotics products.

# Modules 

## **Controller Module**

This module provides a hardware abstraction layer between Acrome Controller board and application code and enables users to develop their own applications without hassle of implementing a communication protocol or struggling with any timing requirements. This module also provides safety limitations for Acrome Robotics products and users don't have to worry about any mechanical or electrical limit of the products while working on their application code.

The controller module provides 6 different classes  for interacting with 5 different products and the Acrome Controller board itself.

- ## Controller Class

    This class provides an interface with the Acrome Controller board. For basic communication checks and configuration via 4 different methods.

    * ### `__init__(self, portname="/dev/serial0", baudrate=115200)`
        
        **`Return:`** *None*
        
        This is the constructor of the Controller class.
        
        `portname` argument is the serial/COM port of the host computer which is connected to the Acrome Controller board. Since the board is designed with Raspberry Pi in mind, default portname is `/dev/serial0` to provide out of the box support for Raspberry Pi.

        `baudrate` argument must not be changed by the user since different baudrates are not supported by the hardware, yet.

    * ### `ping(self)` 

        **`Return:`** *boolean*

        This method provides a basic ping functionality between the board and the host computer as the name suggests. If the communication succeeded method returns true, otherwise false.
    * ### `reboot(self)`

        **`Return:`** *None*
        
        This method immediately reboots the Acrome Controller board when called.

    * ### `enter_bootloader(self)`
    
        **`Return:`** *None*
        
        When this method called, the Acrome Controller board boots into the embedded bootloader to provide a firmware update. When bootloader activated, the board does not respond to any other command rather than specific instruction for bootloader operation.

    * ### `get_board_info(self)`

        **`Return:`** *dict*

        This method returns a dictionary that contains information about the underlaying hardware configuration and status. Since gathering that information interrupts the any other operation at the hardware, calling it in any control loop might affect the system performance and should be avoided.