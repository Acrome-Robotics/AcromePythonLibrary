import struct
from crccheck.crc import Crc32Mpeg2 as CRC



pkg = struct.pack("<BBhhh", 0x55, 0xBD, *[317,656,1721])
pkg += CRC.calc(pkg).to_bytes(4, 'little')

hex_lst = [ hex(i)[0:2] + hex(i)[2:].upper() for i in list(pkg) ]

print(*hex_lst, sep=', ')
