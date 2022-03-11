import unittest
import unittest.mock
from unittest.mock import patch
from acrome import controller

class TestBallBalancingTable(unittest.TestCase):
    def setUp(self) -> None:
        patcher = patch("acrome.controller.serial.Serial", autospec=True)
        self.mock = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock.reset_mock()
        self.bbt = controller.BallBalancingTable()

    def tearDown(self):
        pass

    def test_set_servo_valid_values(self):
        x = 0
        y = 0
        
        for x in range(-self.bbt.__class__._MAX_SERVO_ABS,self.bbt.__class__._MAX_SERVO_ABS+1):
            self.bbt.set_servo(x, y)
            self.assertEqual(self.bbt.servo, [x,y])
        
        for y in range(-self.bbt.__class__._MAX_SERVO_ABS,self.bbt.__class__._MAX_SERVO_ABS+1):
            self.bbt.set_servo(x, y)
            self.assertEqual(self.bbt.servo, [x,y])
        
    def test_set_speed_invalid_values(self):
        self.bbt.set_servo(99999, 99999)
        self.assertEqual(self.bbt.servo, [self.bbt.__class__._MAX_SERVO_ABS,self.bbt.__class__._MAX_SERVO_ABS])

        self.bbt.set_servo(-99999, -99999)
        self.assertEqual(self.bbt.servo, [-self.bbt.__class__._MAX_SERVO_ABS,-self.bbt.__class__._MAX_SERVO_ABS])

    def test_write(self):
        self.bbt.set_servo(700,300)
        
        with patch.object(controller.Controller, '_write') as wr:
            self.bbt.write()
        
        wr.assert_called_once_with(bytes([0x55, 0xBC, 0xBC, 0x2, 0x2C, 0x1, 0xD1, 0x42, 0xB3, 0x11]))

    def test_read(self):
        #POS 250,715
        self.mock.return_value.read.return_value = bytes([0x55, 0xBC, 0xFA, 0x0, 0xCB, 0x2, 0x7, 0x35, 0x1B, 0xDA])

        self.bbt.read()

        self.assertEqual(self.bbt.position, [250,715])