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
        self.dev = controller.BallBalancingTable()

    def tearDown(self):
        pass

    def test_set_servo_valid_values(self):
        x = 0
        y = 0
        
        for x in range(-self.dev.__class__._MAX_SERVO_ABS,self.dev.__class__._MAX_SERVO_ABS+1):
            self.dev.set_servo(x, y)
            self.assertEqual(self.dev._BallBalancingTable__servo, [x,y])
        
        for y in range(-self.dev.__class__._MAX_SERVO_ABS,self.dev.__class__._MAX_SERVO_ABS+1):
            self.dev.set_servo(x, y)
            self.assertEqual(self.dev._BallBalancingTable__servo, [x,y])
        
    def test_set_speed_invalid_values(self):
        self.dev.set_servo(99999, 99999)
        self.assertEqual(self.dev._BallBalancingTable__servo, [self.dev.__class__._MAX_SERVO_ABS,self.dev.__class__._MAX_SERVO_ABS])
        
        for m in self.dev._BallBalancingTable__servo:
            self.assertIsInstance(m, int)

        self.dev.set_servo(-99999, -99999)
        self.assertEqual(self.dev._BallBalancingTable__servo, [-self.dev.__class__._MAX_SERVO_ABS,-self.dev.__class__._MAX_SERVO_ABS])
        for m in self.dev._BallBalancingTable__servo:
            self.assertIsInstance(m, int)

    def test_write(self):
        self.dev.set_servo(700,300)
        
        with patch.object(controller.Controller, '_writebus') as wr:
            self.dev._write()
        
        wr.assert_called_once_with(bytes([0x55, 0xBC, 0xBC, 0x2, 0x2C, 0x1, 0xD1, 0x42, 0xB3, 0x11]))

    def test_read(self):
        #POS 250,715
        self.mock.return_value.read.return_value = bytes([0x55, 0xBC, 0xFA, 0x0, 0xCB, 0x2, 0x7, 0x35, 0x1B, 0xDA])

        self.dev._read()

        self.assertEqual(self.dev.position, [250,715])

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
            