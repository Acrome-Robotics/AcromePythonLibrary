import enum
import struct
from crccheck.crc import Crc32Mpeg2 as CRC32
import time
import serial

Index = enum.IntEnum('Index', [
	'Header',
	'DeviceID',
	'PackageSize',
	'Command',
	'SoftwareVersion',
	'HardwareVersion',
	'ErrorCount',
	'CurrentPosition',
	'CurrentSpeed',
	'CurrentAcceleration',
	'LimitSwitchStatus',
	'BusVoltage',
	'V5Voltage',
	'GoalPositionSpeed',
	'PositionTolerance',
	'SpeedTolerance',
	'MinSpeed',
	'MaxSpeed',
	'MinPosition',
	'MaxPosition',
	'MotionProfile',
	'Baudrate',
	'Jerk',
	'TorqueEn',
	'PIOMode0',
	'PIOMode1',
	'PIOMode2',
	'PIOMode3',
	'PIOMode4',
	'PIOMode5',
	'PIOMode6',
	'PIOData0',
	'PIOData1',
	'PIOData2',
	'PIOData3',
	'PIOData4',
	'PIOData5',
	'PIOData6',
	'ExternalEncoder',
	'CRCValue',
], start=0)

class Commands(enum.IntEnum):
	PING = 0x00,
	READ = 0x01,
	WRITE = 0x02,
	REBOOT = 0x10,
	EEPROM_WRITE = 0x20,
	BL_JUMP = 0x30,
	ACK = 0x80,
	WRITE_ACK = 0x80 | 0x02,
	EEPROM_WRITE_ACK = 0x20 | 0x02,

class _Data():
	def __init__(self, index, var_type, rw=True, value = 0):
		self.__index = index
		self.__type = var_type
		self.__size  = struct.calcsize(self.__type)
		self.__value = value
		self.__rw = rw

	def value(self, value=None):
		if value is None:
			return self.__value
		elif self.__rw:
			self.__value = struct.unpack('<' + self.__type, struct.pack('<' + self.__type, value))[0]

	def index(self) ->enum.IntEnum:
		return self.__index

	def size(self) -> int:
		return self.__size
	
	def type(self) -> str:
		return self.__type

class Premium():
	_BATCH_ID = 254
	def __init__(self, ID) -> bool:
		self.__ack_size = 0
		self.vars = [
			_Data(Index.Header, 'B', False, 0x55),
			_Data(Index.DeviceID, 'B'),
			_Data(Index.PackageSize, 'B'),
			_Data(Index.Command, 'B'),
			_Data(Index.SoftwareVersion, 'I'),
			_Data(Index.HardwareVersion, 'I'),
			_Data(Index.ErrorCount, 'I'),
			_Data(Index.CurrentPosition, 'I'),
			_Data(Index.CurrentSpeed, 'I'),
			_Data(Index.CurrentAcceleration, 'I'),
			_Data(Index.LimitSwitchStatus, 'B'),
			_Data(Index.BusVoltage, 'H'),
			_Data(Index.V5Voltage, 'H'),
			_Data(Index.GoalPositionSpeed, 'I'),
			_Data(Index.PositionErrorTolerance, 'I'),
			_Data(Index.SpeedErrorTolerance, 'I'),
			_Data(Index.MinSpeed, 'I'),
			_Data(Index.MaxSpeed, 'I'),
			_Data(Index.MinPosition, 'I'),
			_Data(Index.MaxPosition, 'I'),
			_Data(Index.MotionProfile, 'B'),
			_Data(Index.Baudrate, 'I'),
			_Data(Index.Jerk, 'I'),
			_Data(Index.TorqueEn, 'B'),
			_Data(Index.PIOMode0, 'B'),
			_Data(Index.PIOMode1, 'B'),
			_Data(Index.PIOMode2, 'B'),
			_Data(Index.PIOMode3, 'B'),
			_Data(Index.PIOMode4, 'B'),
			_Data(Index.PIOMode5, 'B'),
			_Data(Index.PIOMode6, 'B'),
			_Data(Index.PIOData0, 'I'),
			_Data(Index.PIOData1, 'I'),
			_Data(Index.PIOData2, 'I'),
			_Data(Index.PIOData3, 'I'),
			_Data(Index.PIOData4, 'I'),
			_Data(Index.PIOData5, 'I'),
			_Data(Index.PIOData6, 'I'),
			_Data(Index.ExternalEncoder, 'I'),
			_Data(Index.CRCValue, 'I')
		]

		if ID > 253 or ID < 0:
			raise ValueError("Device ID can not be higher than 253 or lower than 0!")
		else:
			self.vars[Index.DeviceID].value(ID)

	def get_ack_size(self):
		return self.__ack_size

	def set_variables(self, index_list=[], value_list=[], ack=False):
		#Set command to write/write_ack
		self.vars[Index.Command].value(Commands.WRITE_ACK if ack else Commands.WRITE)
		
		fmt_str = '<' + ''.join([var.type() for var in self.vars[:4]])
		for index, value in zip(index_list, value_list):
			self.vars[int(index)].value(value)
			fmt_str += 'B' + self.vars[int(index)].type()

		self.__ack_size = struct.calcsize(fmt_str)

		#Create a list of id-value pairs and convert them to a byte-array
		struct_out = list(struct.pack(fmt_str, *[*[var.value() for var in self.vars[:4]], *[val for pair in zip(index_list, [self.vars[int(index)].value() for index in index_list]) for val in pair]]))
		
		struct_out[int(Index.PackageSize)] = len(struct_out) + self.vars[Index.CRCValue].size()
		self.vars[Index.CRCValue].value(CRC32.calc(struct_out))
		
		return bytes(struct_out) + struct.pack('<' + self.vars[Index.CRCValue].type(), self.vars[Index.CRCValue].value())
	
	def get_variables(self, index_list=[]):
		#Set command to Read
		self.vars[Index.Command].value(Commands.READ)
		
		#Constant Registers
		fmt_str = '<' + ''.join([var.type() for var in self.vars[:4]])
		
		#Update format string
		for _ in index_list:
			fmt_str += 'B'

		self.__ack_size = struct.calcsize(fmt_str + self.vars[Index.CRCValue].type()) + struct.calcsize(''.join([self.vars[idx].type() for idx in index_list]))

		#Populate actual string
		struct_out = list(struct.pack(fmt_str, *[*[var.value() for var in self.vars[:4]], *[int(index) for index in index_list]]))
		
		#Populate actual package size
		struct_out[int(Index.PackageSize)] = len(struct_out) + self.vars[Index.CRCValue].size()
		
		#Calculate CRC
		self.vars[Index.CRCValue].value(CRC32.calc(struct_out))

		#Append CRC and return
		return bytes(struct_out) + struct.pack('<' + self.vars[Index.CRCValue].type(), self.vars[Index.CRCValue].value())
	
	def reboot(self):
		self.vars[Index.Command].value(Commands.REBOOT)
		fmt_str = '<' + ''.join([var.type() for var in self.vars[:4]])
		struct_out = list(struct.pack(fmt_str, *[var.value() for var in self.vars[:4]]))
		struct_out[int(Index.PackageSize)] = len(struct_out) + self.vars[Index.CRCValue].size()
		self.__ack_size = 0
		return bytes(struct_out) + struct.pack('<' + self.vars[Index.CRCValue].type(), self.vars[Index.CRCValue].value())
	
	def EEPROM_write(self, ack=False):
		self.vars[Index.Command].value(Commands.EEPROM_WRITE_ACK if ack else Commands.EEPROM_WRITE)
		fmt_str = '<' + ''.join([var.type() for var in self.vars[:4]])
		struct_out = list(struct.pack(fmt_str, *[var.value() for var in self.vars[:4]]))
		struct_out[int(Index.PackageSize)] = len(struct_out) + self.vars[Index.CRCValue].size()
		self.vars[Index.CRCValue].value(CRC32.calc(struct_out))
		self.__ack_size = struct.calcsize(fmt_str.join(['B' + var.type() for var in self.vars[4:]])) + struct.calcsize(fmt_str + self.vars[Index.CRCValue].type())
		return bytes(struct_out) + struct.pack('<' + self.vars[Index.CRCValue].type(), self.vars[Index.CRCValue].value())
	
	def ping(self):
		self.vars[Index.Command].value(Commands.PING)
		fmt_str = '<' + ''.join([var.type() for var in self.vars[:4]])
		struct_out = list(struct.pack(fmt_str, *[var.value() for var in self.vars[:4]]))
		struct_out[int(Index.PackageSize)] = len(struct_out) + self.vars[Index.CRCValue].size()
		self.vars[Index.CRCValue].value(CRC32.calc(struct_out))
		self.__ack_size = struct.calcsize(fmt_str + self.vars[Index.CRCValue].type())
		return bytes(struct_out) + struct.pack('<' + self.vars[Index.CRCValue].type(), self.vars[Index.CRCValue].value())

class Master():
	def __init__(self, portname, baudrate=115200):
		self.__driver_list = [Premium(255)] * 256
		if baudrate > 9500000 or baudrate < 1200:
			raise ValueError("Baudrate must be in range of 1200 to 9.5M")
		else:
			self.__baudrate = baudrate
			self.__ph = serial.Serial(port=portname, baudrate=self.__baudrate, timeout=0.01)

	def __del__(self):
		try:
			self.__ph.close()
		except:
			pass

	def __write_bus(self, data):
		self.__ph.write(data)
		time.sleep(10/self.__baudrate)

	def __read_bus(self, size) -> bytes:
		return self.__ph.read(size=size)

	def attach(self, premium):
		self.__driver_list[premium.vars[Index.DeviceID].value()] = premium

	def parse_received(self, data):
		id = data[Index.DeviceID]
		data = data[4:-4]
		fmt_str = '<'

		i = 0
		while i < len(data):
			fmt_str += 'B' + self.__driver_list[id].vars[data[i]].type()
			i += self.__driver_list[id].vars[data[i]].size() + 1

		unpacked = list(struct.unpack(fmt_str, data))
		grouped = zip(*(iter(unpacked),) * 2)
		for group in grouped:
			self.__driver_list[id].vars[group[0]].value(group[1])

	def set_variables(self, id, idx_val_pairs=[], ack=False) -> list:
		index_list = [pair[0] for pair in idx_val_pairs]
		value_list = [pair[1] for pair in idx_val_pairs]
		self.__write_bus(self.__driver_list[id].set_variables(index_list, value_list, ack))
		if ack:
			if self.__read_ack(id):
				return [self.__driver_list[id].vars[index].value() for index in index_list]
		return [None]

	def get_variables(self, id, index_list) -> list:
		self.__write_bus(self.__driver_list[id].get_variables(index_list))
		if self.__read_ack(id):
			return [self.__driver_list[id].vars[index].value() for index in index_list]
		else:
			return [None]

	def __read_ack(self, id) -> bool:
		ret = self.__read_bus(self.__driver_list[id].get_ack_size())
		if len(ret) == self.__driver_list[id].get_ack_size():
			if (CRC32.calc(ret[:-4]) == struct.unpack('<I', ret[-4:])[0]):
				if ret[int(Index.PackageSize)] > 8:
					self.parse_received(ret)
					return True
				else:
					return True
			else:
				return False
		else:
			return False

	def reboot(self, id):
		self.__write_bus(self.__driver_list[id].reboot())

	def EEPROM_write(self, id, ack=False):
		index_list = [int(index) for index in Index]
		self.__write_bus(self.__driver_list[id].EEPROM_write(ack))
		if ack:
			if self.__read_ack(id):
				return [self.__driver_list[id].vars[index].value() for index in index_list]
		return [None]

	def ping(self, id):
		self.__write_bus(self.__driver_list[id].ping())
		if self.__read_ack(id):
			return True
