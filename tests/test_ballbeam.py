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
        self.bb = controller.BallBeam()

    def tearDown(self):
        pass

    def test_set_servo_valid_values(self):
        for servo in range(-1000,1000+1):
            self.bb.set_servo(servo)
            self.assertEqual(self.bb.servo, servo)
        
    def test_set_speed_invalid_values(self):
        self.bb.set_servo(99999999)
        self.assertEqual(self.bb.servo, 1000)

        self.bb.set_servo(-99999999)
        self.assertEqual(self.bb.servo, -1000)

    def test_write(self):
        self.bb.set_servo(700)
        
        with patch.object(controller.Controller, '_write') as wr:
            self.bb.write()
        
        wr.assert_called_once_with(bytes([0x55, 0xBB, 0xBC, 0x2, 0xA6, 0x10, 0x6E, 0xF3]))

    def test_read(self):
        #POS 1028
        self.mock.return_value.read.return_value = bytes([0x55, 0xBB, 0x4, 0x4, 0xEB, 0x6B, 0xDE, 0xD1])

        self.bb.read()

        self.assertEqual(self.bb.position, 1028)