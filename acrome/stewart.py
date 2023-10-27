import serial
from crccheck.crc import Crc32Mpeg2 as CRC32
import struct
from stm32loader.main import main as stm32loader_main
import tempfile
import requests
import hashlib
from packaging.version import parse as parse_version


class UnsupportedFirmware(Exception):
    pass


class UnsupportedHardware(Exception):
    pass


class StewartStepper():
    _HEADER = 0x55
    _CMD_ID_INDEX = 2
    _CFG_DEVID = 0xBE
    _CMD_NULL = 0
    _CMD_PING = 0x01
    _CMD_GENERAL_CALL = 0x02
    _CMD_CALIB = 0x04
    _CMD_SET_REF = 0x03
    _CMD_REBOOT = (1 << 6)
    _CMD_BL = (1 << 7)

    def __init__(self, portname="/dev/serial0", baudrate=115200):
        self.__ph = serial.Serial(port=portname, baudrate=baudrate, timeout=0.1)
        self.__en = 0
        self.status = 0
        self.__motors = [0] * 6
        self.position = [0] * 6
        self.imu = [0] * 3

    def __del__(self):
        try:
            if self.__ph.isOpen():
                self.__ph.flush()
                self.__ph.flushInput()
                self.__ph.flushOutput()
                self.__ph.close()
        except AttributeError:
            pass
        except Exception as e:
            raise e

    def _writebus(self, data):
        self.__ph.write(data)

    def _readbus(self, byte_count):
        data = self.__ph.read(byte_count)
        if len(data) == byte_count:
            if data[0] == self.__class__._HEADER and data[1] == self.__class__._CFG_DEVID:
                if self._crc32(data[:-4]) == data[-4:]:
                    return data
        return None

    def _crc32(self, data):
        return CRC32.calc(data).to_bytes(4, 'little')

    def reboot(self):
        data = 0
        data = struct.pack("<BBBI", self.__class__._HEADER, self.__class__._CFG_DEVID, self.__class__._CMD_REBOOT, data)
        data += self._crc32(data)
        self._writebus(data)

    def enter_bootloader(self):
        data = 0
        data = data = struct.pack("<BBBI", self.__class__._HEADER, self.__class__._CFG_DEVID, self.__class__._CMD_BL, data)
        data += self._crc32(data)
        self._writebus(data)

    def ping(self):
        data = struct.pack("<BBB", self.__class__._HEADER, self.__class__._CFG_DEVID, self.__class__._CMD_PING)
        data += self._crc32(data)
        self._writebus(data)
        r = self._readbus(7)
        if r is not None:
            if r[self.__class__._CMD_ID_INDEX] == self.__class__._CMD_PING:
                return True
        return False

    def set_motors(self, motors):
        if len(motors) != 6:
            raise Exception("Argument motors must have length of 6")

        for i, motor in enumerate(motors):
            if motor != 0:
                self.__motors[i] = int(motor)

    def get_motors(self):
        return self.__motors

    def enable(self, en):
        self.__en = (self.__en & ~0x01) | (en & 0x01)

    def update(self):
        data = struct.pack("<BBBBiiiiii", self.__class__._HEADER, self.__class__._CFG_DEVID, self.__class__._CMD_GENERAL_CALL, self.__en, *self.__motors)
        data += self._crc32(data)
        self._writebus(data)
        r = self._readbus(44)
        if r is not None:
            if r[self.__class__._CMD_ID_INDEX] == self.__class__._CMD_GENERAL_CALL:
                data = list(struct.unpack("<BBBBiiiiiifffI", r))
                self.status = data[3]
                self.position = data[4:10]
                self.imu = data[10:13]
                return True
        return False

    def calibrate(self):
        data = struct.pack("<BBB", self.__class__._HEADER, self.__class__._CFG_DEVID, self.__class__._CMD_CALIB)
        data += self._crc32(data)
        self._writebus(data)
        r = self._readbus(44)
        if r is not None:
            if r[self.__class__._CMD_ID_INDEX] == self.__class__._CMD_GENERAL_CALL:
                data = list(struct.unpack("<BBBBiiiiiifffI", r))
                self.status = data[3]
                self.position = data[4:10]
                self.imu = data[10:13]
                return True
        return False

    def reference(self):
        data = struct.pack("<BBB", self.__class__._HEADER, self.__class__._CFG_DEVID, self.__class__._CMD_SET_REF)
        data += self._crc32(data)
        self._writebus(data)
        r = self._readbus(44)
        if r is not None:
            if r[self.__class__._CMD_ID_INDEX] == self.__class__._CMD_GENERAL_CALL:
                data = list(struct.unpack("<BBBBiiiiiifffI", r))
                self.status = data[3]
                self.position = data[4:10]
                self.imu = data[10:13]
                return True
        return False
