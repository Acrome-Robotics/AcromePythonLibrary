import unittest
import unittest.mock
from unittest.mock import patch
from acrome import controller

class TestStewartEncoder(unittest.TestCase):
    def setUp(self) -> None:
        patcher = patch("acrome.controller.serial.Serial", autospec=True)
        self.mock = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock.reset_mock()
        self.mock.return_value.read.return_value = bytes([0x55, 0xFC, 0x0, 0x5, 0x1, 0x0, 0x0, 0x2, 0x1, 0x0, 0xFF, 0x0, 0x0, 0x0, 0x0, 0x8, 0xDB, 0x8B, 0xBE])
        self.dev = controller.StewartEncoder()
        self.mock.reset_mock()

    def tearDown(self):
        pass

    def test_enable(self):
        self.dev.enable(True)
        self.assertTrue(self.dev._StewartEncoder__en)
        self.assertIsInstance(self.dev._StewartEncoder__en, int)

        self.dev.enable(False)
        self.assertFalse(self.dev._StewartEncoder__en)
        self.assertIsInstance(self.dev._StewartEncoder__en, int)
        
        self.dev.enable(3)
        self.assertTrue(self.dev._StewartEncoder__en)
        self.assertIsInstance(self.dev._StewartEncoder__en, int)

        self.dev.enable(4)
        self.assertFalse(self.dev._StewartEncoder__en)
        self.assertIsInstance(self.dev._StewartEncoder__en, int)

    def test_set_motors_valid_values(self):
        for mt in range(-self.dev.__class__._MAX_MT_ABS, self.dev.__class__._MAX_MT_ABS+1):
            self.dev.set_motors([mt] * 6)
            self.assertEqual(self.dev._StewartEncoder__motors, [mt] * 6)
        
        for m in self.dev._StewartEncoder__motors:
            self.assertIsInstance(m, int)
        
    def test_set_motors_invalid_values(self):
        self.dev.set_motors([99999] * 6)
        self.assertEqual(self.dev._StewartEncoder__motors, [self.dev.__class__._MAX_MT_ABS] * 6)
        for m in self.dev._StewartEncoder__motors:
            self.assertIsInstance(m, int)

        self.dev.set_motors([-99999] * 6)
        self.assertEqual(self.dev._StewartEncoder__motors, [-self.dev.__class__._MAX_MT_ABS] * 6)
        
        for m in self.dev._StewartEncoder__motors:
            self.assertIsInstance(m, int)

    def test_write(self):
        self.dev.enable(True)
        self.dev.set_motors([100,-200,300,-400,500,-600])
        
        with patch.object(controller.Controller, '_writebus') as wr:
            self.dev._write()
        
        wr.assert_called_once_with(bytes([0x55, 0xC0, 0x1, 0x64, 0x0, 0x38, 0xFF, 0x2C, 0x1, 0x70, 0xFE, 0xF4, 0x1, 0xA8, 0xFD, 0xD6, 0xB5, 0x88, 0x14]))

    def test_read(self):
        #POS 50,63,85,117,756,3721
        self.mock.return_value.read.return_value = bytes([0x55, 0xC0, 0x32, 0x0, 0x3F, 0x0, 0x55, 0x0, 0x75, 0x0, 0xF4, 0x2, 0x89, 0xE, 0x9A, 0x99, 0xCC, 0x42, 0x9A, 0x19, 0x59, 0x43, 0x33, 0xF3, 0xB3, 0x43, 0xB8, 0xE6, 0x40, 0x3])
    
        self.dev._read()

        self.assertEqual(self.dev.position, [50,63,85,117,756,3721])
        for i, val in enumerate([102.3, 217.1, 359.9]):
            self.assertAlmostEqual(self.dev.imu[i], val, places=2)

    def test_update(self):
        
        with patch.object(self.dev.__class__, '_write') as wr:
            self.dev.update()
            wr.assert_called()

        with patch.object(self.dev.__class__, '_read') as rd:
            self.dev.update()
            rd.assert_called()

    def test_reboot(self):
        with patch.object(controller.Controller, '_writebus') as wr:
            self.dev.reboot()
            wr.assert_called_once_with(bytes([0x55, 0xFC, 0x1, 0x0, 0x0, 0x0, 0x0, 0xA3, 0x41, 0x95, 0xD2]))
    
    def test_enter_bootloader(self):
        with patch.object(controller.Controller, '_writebus') as wr:
            self.dev.enter_bootloader()
            wr.assert_called_once_with(bytes([0x55, 0xFC, 0x2, 0x0, 0x0, 0x0, 0x0, 0x34, 0xE9, 0x82, 0x9]))

    def test_ping(self):
        self.mock.return_value.read.return_value = bytes([0x55, 0x0, 0x57, 0x73, 0x9D, 0xC6])
        with patch.object(controller.Controller, '_writebus') as wr:
            self.assertTrue(self.dev.ping())
            wr.assert_called_once_with(bytes([0x55, 0x0, 0x57, 0x73, 0x9D, 0xC6]))

    def test_get_status(self):
        self.mock.return_value.read.return_value = bytes([0x55, 0xFC, 0x0, 0x1, 0x0, 0x0, 0x0, 0x1, 0x1, 0x0, 0x15, 0x0, 0x0, 0x0, 0x0, 0xF1, 0x79, 0xD6, 0x6F])
        with patch.object(controller.Controller, '_writebus') as wr:
            st = self.dev.get_board_info()
            wr.assert_called_once_with(bytes([0x55, 0xFC, 0x0, 0x0, 0x0, 0x0, 0x0, 0x2E, 0x26, 0x98, 0x9B]))

    def test_hw_version_enforce(self):
        self.mock.return_value.read.return_value = bytes([0x55, 0xFC, 0x0, 0x5, 0x1, 0x0, 0x0, 0x1, 0x1, 0x0, 0xFF, 0x0, 0x0, 0x0, 0x0, 0x56, 0xBE, 0x69, 0x52])
        with self.assertRaises(controller.UnsupportedHardware):
            controller.StewartEncoder()
    
    def test_fw_version_enforce(self):
        self.mock.return_value.read.return_value = bytes([0x55, 0xFC, 0x0, 0x4, 0x1, 0x0, 0x0, 0x2, 0x1, 0x0, 0xFF, 0x0, 0x0, 0x0, 0x0, 0xE, 0x38, 0x7D, 0xB9])
        with self.assertRaises(controller.UnsupportedFirmware):
            controller.StewartEncoder()
    
    def test_reset_encoder_all(self):
        self.dev.reset_encoder()
        self.assertEqual(self.dev._StewartEncoder__en, 0b111111 << 2)
        self.assertIsInstance(self.dev._StewartEncoder__en, int)
    
    def test_reset_encoder_multi(self):
        self.dev.reset_encoder([1,3,5])
        self.assertEqual(self.dev._StewartEncoder__en, 0b010101 << 2)
        self.assertIsInstance(self.dev._StewartEncoder__en, int)
        