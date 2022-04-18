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
        self.dev = controller.BallBeam()

    def tearDown(self):
        pass

    def test_set_servo_valid_values(self):
        for servo in range(-1000,1000+1):
            self.dev.set_servo(servo)
            self.assertEqual(self.dev._BallBeam__servo, servo)
        
    def test_set_servo_invalid_values(self):
        self.dev.set_servo(99999999)
        self.assertEqual(self.dev._BallBeam__servo, 1000)

        self.dev.set_servo(-99999999)
        self.assertEqual(self.dev._BallBeam__servo, -1000)

    def test_write(self):
        self.dev.set_servo(700)
        
        with patch.object(controller.Controller, '_writebus') as wr:
            self.dev._write()
        
        wr.assert_called_once_with(bytes([0x55, 0xBB, 0xBC, 0x2, 0xA6, 0x10, 0x6E, 0xF3]))

    def test_read(self):
        #POS 1028
        self.mock.return_value.read.return_value = bytes([0x55, 0xBB, 0x4, 0x4, 0xEB, 0x6B, 0xDE, 0xD1])

        self.dev._read()

        self.assertEqual(self.dev.position, 1028)
    
    def test_update(self):
        self.dev.update()
        
        with patch.object(self.dev.__class__, '_write') as wr:
            self.dev._write()
            wr.assert_called()

        with patch.object(self.dev.__class__, '_read') as rd:
            self.dev._read()
            rd.assert_called()
            