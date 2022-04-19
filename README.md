# Overview

This library provides easy-to-use Python modules for interacting with Acrome Robotics products.

# Modules 

## **Controller Module**

This module provides a hardware abstraction layer between Acrome Controller board and application code and enables users to develop their own applications without hassle of implementing a communication protocol or struggling with any timing requirements. This module also provides safety limitations for Acrome Robotics products and users don't have to worry about any mechanical or electrical limit of the products while working on their application code.

The controller module provides 6 different classes  for interacting with 5 different products and the Acrome Controller board itself.

- ## Controller Class

    This class provides an interface with the Acrome Controller board. For basic communication checks and configuration via 4 different methods.

    * #### `__init__(self, portname="/dev/serial0", baudrate=115200)`
        
        **`Return:`** *None*
        
        This is the constructor of the Controller class.
        
        `portname` argument is the serial/COM port of the host computer which is connected to the Acrome Controller board. Since the board is designed with Raspberry Pi in mind, default portname is `/dev/serial0` to provide out of the box support for Raspberry Pi.

        `baudrate` argument must not be changed by the user since different baudrates are not supported by the hardware, yet.

    * #### `ping(self)` 

        **`Return:`** *boolean*

        This method provides a basic ping functionality between the board and the host computer as the name suggests. If the communication succeeded method returns true, otherwise false.
    * #### `reboot(self)`

        **`Return:`** *None*
        
        This method immediately reboots the Acrome Controller board when called.

    * #### `enter_bootloader(self)`
    
        **`Return:`** *None*
        
        When this method called, the Acrome Controller board boots into the embedded bootloader to provide a firmware update. When bootloader activated, the board does not respond to any other command rather than specific instruction for bootloader operation.

    * #### `get_board_info(self)`

        **`Return:`** *dict*

        This method returns a dictionary that contains information about the underlaying hardware configuration and status. Since gathering that information interrupts the any other operation at the hardware, calling it in any control loop might affect the system performance and should be avoided.


- ## OneDOF Class

    This class provides an interface with the Acrome Controller board. For basic communication checks and configuration via 4 different methods.

    * #### `__init__(self, portname="/dev/serial0", baudrate=115200)`
        
        **`Return:`** *None*
        
        This is the constructor of the OneDOF class. Please refer to the Controller class constructor for argument descriptions.

    * #### `set_speed(self, speed)`

        **`Return:`** *None*

        This method provides an interface to set speed of the OneDOF motor. Available range is from -1000 to 1000.

    * #### `enable(self)`
        **`Return:`** *None*

        This method enables the power stage of the OneDOF motor and should be called prior to setting speed.

    * #### `reset_encoder_mt(self)`
        **`Return:`** *None*

        This method resets the encoder of the DC motor on the OneDOF.

    * #### `reset_encoder_shaft(self)`
        **`Return:`** *None*

        This method resets the encoder on the shaft of OneDOF.

    * #### `update(self)`
        **`Return:`** *None*

        This method syncronizes the variables both on host computer and hardware side. Should be called prior to read of any attribute or called after any write/set operation to make latest values available immediately.

    * #### `motor_enc`

        This attribute returns the current value of encoder on the DC motor.
        
        > **Note:** This attribute might be always 0 according to your product configuration.

    * #### `shaft_enc`

        This attribute returns the current value of encoder on the OneDOF shaft.
        
    * #### `imu`
        
        This attribute returns the current roll, pitch and yaw values in degrees in a form of Python list.

        > **Note:** This attribute is only available on the product that shipped with an BNO055 Absolute Orientation Sensor. Products with MPU6050 IMU is not supported yet and will return 0.

- ## BallBeam Class

    This class provides an interface with Ball and Beam via Acrome Controller.

    * #### `__init__(self, portname="/dev/serial0", baudrate=115200)`
        
        **`Return:`** *None*
        
        This is the constructor of the OneDOF class. Please refer to the Controller class constructor for argument descriptions.
    * #### `set_servo(self, servo)`

        **`Return:`** *None*

        This method provides an interface to set angle of the servo motor on Ball and Beam. Available range is from -1000 to 1000.

    * #### `update(self)`
        **`Return:`** *None*

        This method syncronizes the variables both on host computer and hardware side. Should be called prior to read of any attribute or called after any write/set operation to make latest values available immediately.

    * #### `position`

        This attribute returns the current value of the ball position on the beam.
