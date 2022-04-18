import unittest
import unittest.mock
from unittest.mock import patch
from acrome import controller

class TestDelta(unittest.TestCase):
    def setUp(self) -> None:
        patcher = patch("acrome.controller.serial.Serial", autospec=True)
        self.mock = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock.reset_mock()
        self.delta = controller.Delta()

    def tearDown(self):
        pass

    def test_set_motors_valid_values(self):
        for mt in range(self.delta.__class__._MIN_MT_POS, self.delta.__class__._MAX_MT_POS):
            self.delta.set_motors([mt] * 3)
            self.assertEqual(self.delta.motors, [mt] * 3)
        
    def test_set_motors_invalid_values(self):
        self.delta.set_motors([99999] * 3)
        self.assertEqual(self.delta.motors, [self.delta.__class__._MAX_MT_POS] * 3)

        self.delta.set_motors([-99999] * 3)
        self.assertEqual(self.delta.motors, [self.delta.__class__._MIN_MT_POS] * 3)

    def test_write(self):
        self.delta.pick(True)
        self.delta.set_motors([400, 500, 600])
        
        with patch.object(controller.Controller, '_writebus') as wr:
            self.delta._write()
        
        wr.assert_called_once_with(bytes([0x55, 0xBD, 0x1, 0x90, 0x1, 0xF4, 0x1, 0x58, 0x2, 0x27, 0xA7, 0x2C, 0x7A]))                     

    def test_read(self):
        #POS 317,656,1721
        self.mock.return_value.read.return_value = bytes([0x55, 0xBD, 0x3D, 0x1, 0x90, 0x2, 0xB9, 0x6, 0x1D, 0xCB, 0x83, 0xD6])
    
        self.delta._read()

        self.assertEqual(self.delta.position, [317,656,1721])
