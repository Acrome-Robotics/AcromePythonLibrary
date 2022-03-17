import unittest
import unittest.mock
from unittest.mock import patch
from acrome import controller

class TestBallBeam(unittest.TestCase):
    def setUp(self) -> None:
        patcher = patch("acrome.controller.serial.Serial", autospec=True)
        self.mock = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock.reset_mock()
        self.delta = controller.Delta()

    def tearDown(self):
        pass

    def test_set_servo_valid_values(self):
        for mt in range(-self.delta.__class__._MAX_MT_ABS, self.delta.__class__._MAX_MT_ABS+1):
            self.delta.set_motors([mt] * 3)
            self.assertEqual(self.delta.motors, [mt] * 3)
        
    def test_set_speed_invalid_values(self):
        self.delta.set_motors([99999] * 3)
        self.assertEqual(self.delta.motors, [self.delta.__class__._MAX_MT_ABS] * 3)

        self.delta.set_motors([-99999] * 3)
        self.assertEqual(self.delta.motors, [-self.delta.__class__._MAX_MT_ABS] * 3)

    def test_write(self):
        self.delta.pick(True)
        self.delta.set_motors([100,-200,300])
        
        with patch.object(controller.Controller, '_write') as wr:
            self.delta.write()
        
        wr.assert_called_once_with(bytes([0x55, 0xBD, 0x1, 0x64, 0x0, 0x38, 0xFF, 0x2C, 0x1, 0x71, 0x95, 0x1, 0x89]))

    def test_read(self):
        #POS 317,656,1721
        self.mock.return_value.read.return_value = bytes([0x55, 0xBD, 0x3D, 0x1, 0x90, 0x2, 0xB9, 0x6, 0x1D, 0xCB, 0x83, 0xD6])
    
        self.delta.read()

        self.assertEqual(self.delta.position, [317,656,1721])