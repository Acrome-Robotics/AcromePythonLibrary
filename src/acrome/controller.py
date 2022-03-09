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
            if self._crc32(data[:-4]) == struct.unpack("<I", data[-4:]):
                return data
        return None

    def _crc32(self, data):
        return CRC32.calc(data).to_bytes(4, 'little')
