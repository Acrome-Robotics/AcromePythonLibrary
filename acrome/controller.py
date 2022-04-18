import serial
from crccheck.crc import Crc32Mpeg2 as CRC32
import struct
class Controller():
    _HEADER = 0x55
    _ID_INDEX = 1
    _DEVID = 0xFC
    _CMD_NULL = 0
    _CMD_REBOOT = (1 << 0)
    _CMD_BL = (1 << 1)
    _PINGID = 0
    _STATUS_KEY_LIST = ['EEPROM', 'IMU', 'Touchscreen Serial', 'Touchscreen Analog', 'Delta', 'Software Version', 'Hardware Version']

    def __init__(self, portname="/dev/serial0", baudrate=115200):
        self.ph = serial.Serial(port=portname, baudrate=baudrate, timeout=0.1)
    
    def _writebus(self, data):
        self.ph.write(data)
    
    def _readbus(self, byte_count):
        data = self.ph.read(byte_count)
        if len(data) > 0:
            if data[0] == self.__class__._HEADER:
                if self._crc32(data[:-4]) == data[-4:]:
                    return data
        return None

    def reboot(self):
        data = 0
        data = struct.pack("<BBBI", self.__class__._HEADER, self.__class__._DEVID, self.__class__._CMD_REBOOT, data)
        data += self._crc32(data)
        self._writebus(data)

    def enter_bootloader(self):
        data = 0
        data = data = struct.pack("<BBBI", self.__class__._HEADER, self.__class__._DEVID, self.__class__._CMD_BL, data)
        data += self._crc32(data)
        self._writebus(data)

    def ping(self):
        data = struct.pack("<BB", self.__class__._HEADER, self.__class__._PINGID)
        data += self._crc32(data)
        self._writebus(data)
        r = self._readbus(6)
        if r is not None:
            if r[self.__class__._ID_INDEX] == self.__class__._PINGID:
                return True    
        return False

    def get_board_info(self):
        data = 0
        data = struct.pack("<BBBI", self.__class__._HEADER, self.__class__._DEVID, self.__class__._CMD_NULL, data)
        data += self._crc32(data)
        self._writebus(data)
        r = self._readbus(19)
        st = dict([])
        if r is not None:
            for pos, key in enumerate(self.__class__._STATUS_KEY_LIST):
                st[key] = bool((r[10] & (1 << pos)) >> pos)
            ver = list(r)[2:5]
            st['Software Version'] = "{0}.{1}.{2}".format(*ver[::-1])
            ver = list(r)[6:9]
            st['Hardware Version'] = "{0}.{1}.{2}".format(*ver[::-1])
            return st
        return None
    
    def _crc32(self, data):
        return CRC32.calc(data).to_bytes(4, 'little')
    
    def update(self):
        if self.__class__ is not Controller:
            self._write()
            return self._read()
        else:
            raise NotImplementedError

class OneDOF(Controller):
    _DEVID = 0xBA
    _EN_MASK = 1 << 0
    _ENC1_RST_MASK = 1 << 1
    _ENC2_RST_MASK = 1 << 2
    _RECEIVE_COUNT = 22
    _MAX_SPEED_ABS = 1000

    def __init__(self, portname="/dev/serial0", baudrate=115200):
        super().__init__(portname=portname, baudrate=baudrate)
        self.__config = 0
        self.__speed = 0
        self.angle = 0
        self.motor_enc = 0
        self.shaft_enc = 0
        self.imu = [0,0,0]

    def set_speed(self, speed):
        if speed != 0:
            self.__speed = speed if abs(speed) <= self.__class__._MAX_SPEED_ABS else self.__class__._MAX_SPEED_ABS * (speed / abs(speed))
        else:
            self.__speed = speed

    def enable(self, en):
        self.__config = (self.__config & ~self.__class__._EN_MASK) | (en & self.__class__._EN_MASK)

    def reset_encoder_mt(self):
        self.__config |= self.__class__._ENC1_RST_MASK

    def reset_encoder_shaft(self):
        self.__config |= self.__class__._ENC2_RST_MASK
    
    def _write(self):
        data = struct.pack("<BBBh", self.__class__._HEADER, self.__class__._DEVID, self.__config, self.__speed)
        data += self._crc32(data)
        super()._writebus(data)
        self.__config &= self.__class__._EN_MASK

    def _read(self):
        data = super()._readbus(self.__class__._RECEIVE_COUNT)
        if data is not None:
            if data[self.__class__._ID_INDEX] == self.__class__._DEVID:
                self.motor_enc = struct.unpack("<H", data[2:4])[0]
                self.shaft_enc = struct.unpack("<H", data[4:6])[0]
                self.imu = list(struct.unpack("<fff", data[6:18]))

class BallBeam(Controller):
    _DEVID = 0xBB
    _MAX_SERVO_ABS = 1000
    _RECEIVE_COUNT = 8

    def __init__(self, portname="/dev/serial0", baudrate=115200):
        super().__init__(portname=portname, baudrate=baudrate)
        self.position = 0
        self.__servo = 0
    
    def set_servo(self, servo):
        if servo != 0:
            self.__servo = servo if abs(servo) <= self.__class__._MAX_SERVO_ABS else self.__class__._MAX_SERVO_ABS * (servo / abs(servo))
        else:
            self.__servo = servo
    
    def _write(self):
        data = struct.pack("<BBh", self.__class__._HEADER, self.__class__._DEVID, self.__servo)
        data += self._crc32(data)
        super()._writebus(data)
    
    def _read(self):
        data = super()._readbus(self.__class__._RECEIVE_COUNT)
        if data is not None:
            if data[self.__class__._ID_INDEX] == self.__class__._DEVID:
                self.position = struct.unpack("<h", data[2:4])[0]

class BallBalancingTable(Controller):
    _DEVID = 0xBC
    _MAX_SERVO_ABS = 1000
    _RECEIVE_COUNT = 10

    def __init__(self, portname="/dev/serial0", baudrate=115200):
        super().__init__(portname=portname, baudrate=baudrate)
        self.__servo = [0,0]
        self.position = [0,0]

    def set_servo(self, x, y):
        if x != 0:
            self.__servo[0] = x if abs(x) <= self.__class__._MAX_SERVO_ABS else self.__class__._MAX_SERVO_ABS * (x / abs(x))
        else:
            self.__servo[0] = x

        if y != 0:
            self.__servo[1] = y if abs(x) <= self.__class__._MAX_SERVO_ABS else self.__class__._MAX_SERVO_ABS * (y / abs(y))
        else:
            self.__servo[1] = y

    def _write(self):
        data = struct.pack("<BBhh", self.__class__._HEADER, self.__class__._DEVID, self.__servo[0], self.__servo[1])
        data += self._crc32(data)
        super()._writebus(data)

    def _read(self):
        data = super()._readbus(self.__class__._RECEIVE_COUNT)
        if data is not None:
            if data[self.__class__._ID_INDEX] == self.__class__._DEVID:
                self.position = list(struct.unpack("<hh", data[2:6]))

class Delta(Controller):
    _DEVID = 0xBD
    _MAX_MT_POS = 810
    _MIN_MT_POS = 310
    _RECEIVE_COUNT = 12
    
    def __init__(self, portname="/dev/serial0", baudrate=115200):
        super().__init__(portname=portname, baudrate=baudrate)
        self.__magnet = 0
        self.__motors = [0] * 3
        self.position = [0] * 3

    def pick(self, magnet):
        self.__magnet = magnet & 0x01

    def set_motors(self, motors):
        if len(motors) != 3:
            raise Exception("Motors variable must have length of 6")
        
        for i, motor in enumerate(motors):
            if motor <= self.__class__._MAX_MT_POS and motor >= self.__class__._MIN_MT_POS:
                self.__motors[i] = motor
            else: 
                if motor >= self.__class__._MAX_MT_POS:
                    self.__motors[i] = self.__class__._MAX_MT_POS
                else:
                    self.__motors[i] = self.__class__._MIN_MT_POS

    def _write(self):
        data = struct.pack("<BBBhhh", self.__class__._HEADER, self.__class__._DEVID, self.__magnet, *self.__motors)
        data += self._crc32(data)
        super()._writebus(data)

    def _read(self):
        data = super()._readbus(self.__class__._RECEIVE_COUNT)
        if data is not None:
            if data[self.__class__._ID_INDEX] == self.__class__._DEVID:
                self.position = list(struct.unpack("<HHH", data[2:8]))

class Stewart(Controller):
    _DEVID = 0xBE
    _MAX_MT_ABS = 1000
    _RECEIVE_COUNT = 30

    def __init__(self, portname="/dev/serial0", baudrate=115200):
        super().__init__(portname=portname, baudrate=baudrate)
        self.__en = 0
        self.__motors = [0] * 6
        self.position = [0] * 6
        self.imu = [0] * 3

    def enable(self, en):
        self.__en = en & 0x01

    def set_motors(self, motors):
        if len(motors) != 6:
            raise Exception("Motors variable must have length of 6")
        
        for i, motor in enumerate(motors):
            if motor != 0:
                self.__motors[i] = motor if abs(motor) <= self.__class__._MAX_MT_ABS else self.__class__._MAX_MT_ABS * (motor / abs(motor))
            else:
                self.__motors[i] = 0

    def _write(self):
        data = struct.pack("<BBBhhhhhh", self.__class__._HEADER, self.__class__._DEVID, self.__en, *self.__motors)
        data += self._crc32(data)
        super()._writebus(data)

    def _read(self):
        data = super()._readbus(self.__class__._RECEIVE_COUNT)
        if data is not None:
            if data[self.__class__._ID_INDEX] == self.__class__._DEVID:
                self.position = list(struct.unpack("<HHHHHH", data[2:14]))
                self.imu = list(struct.unpack("<fff", data[14:26]))
