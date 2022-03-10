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
            self.speed = speed if abs(speed) <= 1000 else 1000 * (speed / abs(speed))
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
                self.motor_enc = struct.unpack("<H", data[2:4])
                self.shaft_enc = struct.unpack("<H", data[4:6])
                self.imu[0] = struct.unpack("<h", data[6:8])
                self.imu[0] = struct.unpack("<h", data[8:10])
                self.imu[0] = struct.unpack("<h", data[10:12])
