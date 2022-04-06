import unittest
from unittest.mock import patch
from acrome import controller

class TestController(unittest.TestCase):
    def setUp(self):
        patcher = patch("acrome.controller.serial.Serial", autospec=True)
        self.mock = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock.reset_mock()

    def test_crc32(self):
        self.assertEqual(controller.Controller()._crc32([0x55, 0xAA, 123, 321]), bytes([81, 232, 252, 34]))
      
    def test_read(self):
        self.mock.return_value.read.return_value = bytes([0x55, 0x00, 87, 115, 157, 198])
        self.assertEqual(controller.Controller()._read(6), bytes([0x55, 0x00, 87, 115, 157, 198]))

    def test_write(self): #Placeholder test since it is just a wrapper
        self.assertTrue(True) 

    def test_reboot(self):
        with patch.object(controller.Controller, '_write') as wr:
            controller.Controller().reboot()
            wr.assert_called_once_with(bytes([0x55, 0xFC, 0x1, 0x0, 0x0, 0x0, 0x0, 0xA3, 0x41, 0x95, 0xD2]))
    