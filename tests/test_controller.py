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
    
    @patch('acrome.controller.serial.Serial')    
    def test_read(self, mock_serial):
        mock_serial.return_value.read.return_value = bytes([0x55, 0x00, 87, 115, 157, 198])
        self.assertEqual(controller.Controller()._read(6), bytes([0x55, 0x00, 87, 115, 157, 198]))
