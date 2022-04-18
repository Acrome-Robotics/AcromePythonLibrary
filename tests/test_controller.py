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
        self.assertEqual(controller.Controller()._readbus(6), bytes([0x55, 0x00, 87, 115, 157, 198]))

    def test_write(self): #Placeholder test since it is just a wrapper
        self.assertTrue(True) 

    def test_reboot(self):
        with patch.object(controller.Controller, '_writebus') as wr:
            controller.Controller().reboot()
            wr.assert_called_once_with(bytes([0x55, 0xFC, 0x1, 0x0, 0x0, 0x0, 0x0, 0xA3, 0x41, 0x95, 0xD2]))
    
    def test_enter_bootloader(self):
        with patch.object(controller.Controller, '_writebus') as wr:
            controller.Controller().enter_bootloader()
            wr.assert_called_once_with(bytes([0x55, 0xFC, 0x2, 0x0, 0x0, 0x0, 0x0, 0x34, 0xE9, 0x82, 0x9]))

    def test_ping(self):
        self.mock.return_value.read.return_value = bytes([0x55, 0x0, 0x57, 0x73, 0x9D, 0xC6])
        with patch.object(controller.Controller, '_writebus') as wr:
            self.assertTrue(controller.Controller().ping())
            wr.assert_called_once_with(bytes([0x55, 0x0, 0x57, 0x73, 0x9D, 0xC6]))

    def test_get_status(self):
        self.mock.return_value.read.return_value = bytes([0x55, 0xFC, 0x0, 0x1, 0x0, 0x0, 0x0, 0x1, 0x1, 0x0, 0x15, 0x0, 0x0, 0x0, 0x0, 0xF1, 0x79, 0xD6, 0x6F])
        with patch.object(controller.Controller, '_writebus') as wr:
            st = controller.Controller().get_board_info()
            wr.assert_called_once_with(bytes([0x55, 0xFC, 0x0, 0x0, 0x0, 0x0, 0x0, 0x2E, 0x26, 0x98, 0x9B]))
        
        self.assertTrue(isinstance(st, dict))
        self.assertEqual(len(st.keys()), len(controller.Controller()._STATUS_KEY_LIST))
        self.assertTrue(list(st.keys()).sort() == controller.Controller()._STATUS_KEY_LIST.sort())
        self.assertTrue(st['EEPROM'] == True)
        self.assertTrue(st['IMU'] == False)
        self.assertTrue(st['Touchscreen Serial'] == True)
        self.assertTrue(st['Touchscreen Analog'] == False)
        self.assertTrue(st['Delta'] == True)
        self.assertTrue(st['Software Version'] == '0.1.0')
        self.assertTrue(st['Hardware Version'] == '1.1.0')

    def test_update(self):
        self.assertRaises(NotImplementedError, controller.Controller().update)