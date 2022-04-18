import unittest
import unittest.mock
from unittest.mock import patch
from acrome import controller

class TestStewart(unittest.TestCase):
    def setUp(self) -> None:
        patcher = patch("acrome.controller.serial.Serial", autospec=True)
        self.mock = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock.reset_mock()
        self.stw = controller.Stewart()

    def tearDown(self):
        pass

    def test_enable(self):
        self.stw.enable(True)
        self.assertTrue(self.stw._en)

        self.stw.enable(False)
        self.assertFalse(self.stw._en)
        
        self.stw.enable(3)
        self.assertTrue(self.stw._en)

        self.stw.enable(4)
        self.assertFalse(self.stw._en)

    def test_set_motors_valid_values(self):
        for mt in range(-self.stw.__class__._MAX_MT_ABS, self.stw.__class__._MAX_MT_ABS+1):
            self.stw.set_motors([mt] * 6)
            self.assertEqual(self.stw.motors, [mt] * 6)
        
    def test_set_motors_invalid_values(self):
        self.stw.set_motors([99999] * 6)
        self.assertEqual(self.stw.motors, [self.stw.__class__._MAX_MT_ABS] * 6)

        self.stw.set_motors([-99999] * 6)
        self.assertEqual(self.stw.motors, [-self.stw.__class__._MAX_MT_ABS] * 6)

    def test_write(self):
        self.stw.enable(True)
        self.stw.set_motors([100,-200,300,-400,500,-600])
        
        with patch.object(controller.Controller, '_writebus') as wr:
            self.stw._write()
        
        wr.assert_called_once_with(bytes([0x55, 0xBE, 0x1, 0x64, 0x0, 0x38, 0xFF, 0x2C, 0x1, 0x70, 0xFE, 0xF4, 0x1, 0xA8, 0xFD, 0x52, 0x9A, 0xEF, 0xB7]))

    def test_read(self):
        #POS 50,63,85,117,756,3721
        self.mock.return_value.read.return_value = bytes([0x55, 0xBE, 0x32, 0x0, 0x3F, 0x0, 0x55, 0x0, 0x75, 0x0, 0xF4, 0x2, 0x89, 0xE, 0x9A, 0x99, 0xCC, 0x42, 0x9A, 0x19, 0x59, 0x43, 0x33, 0xF3, 0xB3, 0x43, 0x90, 0xC5, 0xF0, 0x59])
    
        self.stw._read()

        self.assertEqual(self.stw.position, [50,63,85,117,756,3721])
        for i, val in enumerate([102.3, 217.1, 359.9]):
            self.assertAlmostEqual(self.stw.imu[i], val, places=2)
        