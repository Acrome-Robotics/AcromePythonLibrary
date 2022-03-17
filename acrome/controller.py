import serial
from crccheck.crc import Crc32Mpeg2 as CRC32
import struct
class Controller():
    _HEADER = 0x55
    _ID_INDEX = 1

    def __init__(self, portname="/dev/serial0"):
        self.ph = serial.Serial(port=portname, baudrate=115200, timeout=0.1)
    
    def _write(self, data):
        self.ph.write(data)
    
    def _read(self, byte_count):
        data = self.ph.read(byte_count)
        if data[0] == self.__class__._HEADER:
            if self._crc32(data[:-4]) == data[-4:]:
                return data
        return None

    def _crc32(self, data):
        return CRC32.calc(data).to_bytes(4, 'little')

class OneDOF(Controller):
    _DEVID = 0xBA
    _EN_MASK = 1 << 0
    _ENC1_RST_MASK = 1 << 1
    _ENC2_RST_MASK = 1 << 2
    _RECEIVE_COUNT = 16
    _MAX_SPEED_ABS = 1000

    def __init__(self, portname="/dev/serial0"):
        super().__init__(portname=portname)
        self.config = 0
        self.speed = 0
        self.angle = 0
        self.motor_enc = 0
        self.shaft_enc = 0
        self.imu = [0,0,0]

    def set_speed(self, speed):
        if speed != 0:
            self.speed = speed if abs(speed) <= self.__class__._MAX_SPEED_ABS else self.__class__._MAX_SPEED_ABS * (speed / abs(speed))
        else:
            self.speed = speed

    def enable(self, en):
        self.config = (self.config & ~self.__class__._EN_MASK) | (en & self.__class__._EN_MASK)

    def reset_encoder_mt(self):
        self.config |= self.__class__._ENC1_RST_MASK

    def reset_encoder_shaft(self):
        self.config |= self.__class__._ENC2_RST_MASK
    
    def write(self):
        data = struct.pack("<BBBh", self.__class__._HEADER, self.__class__._DEVID, self.config, self.speed)
        data += self._crc32(data)
        super()._write(data)
        self.config &= self.__class__._EN_MASK

    def read(self):
        data = super()._read(self.__class__._RECEIVE_COUNT)
        if data is not None:
            if data[self.__class__._ID_INDEX] == self.__class__._DEVID:
                self.motor_enc = struct.unpack("<H", data[2:4])[0]
                self.shaft_enc = struct.unpack("<H", data[4:6])[0]
                self.imu[0] = struct.unpack("<h", data[6:8])[0]
                self.imu[1] = struct.unpack("<h", data[8:10])[0]
                self.imu[2] = struct.unpack("<h", data[10:12])[0]

class BallBeam(Controller):
    _DEVID = 0xBB
    _MAX_SERVO_ABS = 1000
    _RECEIVE_COUNT = 8

    def __init__(self, portname="/dev/serial0"):
        super().__init__(portname=portname)
        self.position = 0
        self.servo = 0
    
    def set_servo(self, servo):
        if servo != 0:
            self.servo = servo if abs(servo) <= self.__class__._MAX_SERVO_ABS else self.__class__._MAX_SERVO_ABS * (servo / abs(servo))
        else:
            self.servo = servo
    
    def write(self):
        data = struct.pack("<BBh", self.__class__._HEADER, self.__class__._DEVID, self.servo)
        data += self._crc32(data)
        super()._write(data)
    
    def read(self):
        data = super()._read(self.__class__._RECEIVE_COUNT)
        if data is not None:
            if data[self.__class__._ID_INDEX] == self.__class__._DEVID:
                self.position = struct.unpack("<h", data[2:4])[0]

class BallBalancingTable(Controller):
    _DEVID = 0xBC
    _MAX_SERVO_ABS = 1000
    _RECEIVE_COUNT = 10

    def __init__(self, portname="/dev/serial0"):
        super().__init__(portname=portname)
        self.servo = [0,0]
        self.position = [0,0]

    def set_servo(self, x, y):
        if x != 0:
            self.servo[0] = x if abs(x) <= self.__class__._MAX_SERVO_ABS else self.__class__._MAX_SERVO_ABS * (x / abs(x))
        else:
            self.servo[0] = x

        if y != 0:
            self.servo[1] = y if abs(x) <= self.__class__._MAX_SERVO_ABS else self.__class__._MAX_SERVO_ABS * (y / abs(y))
        else:
            self.servo[1] = y

    def write(self):
        data = struct.pack("<BBhh", self.__class__._HEADER, self.__class__._DEVID, self.servo[0], self.servo[1])
        data += self._crc32(data)
        super()._write(data)

    def read(self):
        data = super()._read(self.__class__._RECEIVE_COUNT)
        if data is not None:
            if data[self.__class__._ID_INDEX] == self.__class__._DEVID:
                self.position = list(struct.unpack("<hh", data[2:6]))

class Delta(Controller):
    _DEVID = 0xBD
    _MAX_MT_ABS = 1000
    _RECEIVE_COUNT = 12
    
    def __init__(self, portname="/dev/serial0"):
        super().__init__(portname=portname)
        self.magnet = 0
        self.motors = [0] * 3
        self.position = [0] * 3

    def pick(self, magnet):
        self.magnet = magnet & 0x01

    def set_motors(self, motors):
        if len(motors) != 3:
            raise Exception("Motors variable must have length of 6")
        
        for i, motor in enumerate(motors):
            if motor != 0:
                self.motors[i] = motor if abs(motor) <= self.__class__._MAX_MT_ABS else self.__class__._MAX_MT_ABS * (motor / abs(motor))
            else:
                self.motors[i] = 0

    def write(self):
        data = struct.pack("<BBBhhh", self.__class__._HEADER, self.__class__._DEVID, self.magnet, *self.motors)
        data += self._crc32(data)
        super()._write(data)

    def read(self):
        data = super()._read(self.__class__._RECEIVE_COUNT)
        if data is not None:
            if data[self.__class__._ID_INDEX] == self.__class__._DEVID:
                self.position = list(struct.unpack("<HHH", data[2:8]))


class Stewart(Controller):
    _DEVID = 0xBE
    _MAX_MT_ABS = 1000
    _RECEIVE_COUNT = 24

    def __init__(self, portname="/dev/serial0"):
        super().__init__(portname=portname)
        self._en = 0
        self.motors = [0] * 6
        self.position = [0] * 6
        self.imu = [0] * 3

    def enable(self, en):
        self._en = en & 0x01

    def set_motors(self, motors):
        if len(motors) != 6:
            raise Exception("Motors variable must have length of 6")
        
        for i, motor in enumerate(motors):
            if motor != 0:
                self.motors[i] = motor if abs(motor) <= self.__class__._MAX_MT_ABS else self.__class__._MAX_MT_ABS * (motor / abs(motor))
            else:
                self.motors[i] = 0

    def write(self):
        data = struct.pack("<BBBhhhhhh", self.__class__._HEADER, self.__class__._DEVID, self._en, *self.motors)
        data += self._crc32(data)
        super()._write(data)

    def read(self):
        data = super()._read(self.__class__._RECEIVE_COUNT)
        if data is not None:
            if data[self.__class__._ID_INDEX] == self.__class__._DEVID:
                self.position = list(struct.unpack("<HHHHHH", data[2:14]))
                self.imu = list(struct.unpack("<hhh", data[14:20]))