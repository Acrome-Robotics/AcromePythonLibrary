import unittest
import unittest.mock
from unittest.mock import patch
from acrome import controller

class TestOneDOF(unittest.TestCase):
    def setUp(self) -> None:
        patcher = patch("acrome.controller.serial.Serial", autospec=True)
        self.mock = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock.reset_mock()
        self.dof = controller.OneDOF()

    def tearDown(self):
        self.dof.__init__()

    def test_set_speed_valid_values(self):
        for speed in range(-1000,1000+1):
            self.dof.set_speed(speed)
            self.assertEqual(self.dof.speed, speed)

    def test_set_speed_invalid_values(self):
        self.dof.set_speed(99999999)
        self.assertEqual(self.dof.speed, 1000)

        self.dof.set_speed(-99999999)
        self.assertEqual(self.dof.speed, -1000)

    def test_set_enable(self):
        first_config = self.dof.config
        self.dof.enable(1)
        self.assertEqual(self.dof.config, first_config | self.dof.__class__._EN_MASK)

    def test_reset_enable(self):
        self.dof.config |= self.dof._EN_MASK
        first_config = self.dof.config
        self.dof.enable(False)
        self.assertEqual(self.dof.config, first_config & ~self.dof._EN_MASK)
        
    def test_reset_encoder(self):
        first_config = self.dof.config
        self.dof.reset_encoder_mt()
        self.assertEqual(self.dof.config, first_config | self.dof._ENC1_RST_MASK)
        self.dof.config = 0
        
        first_config = self.dof.config
        self.dof.reset_encoder_shaft()
        self.assertEqual(self.dof.config, first_config | self.dof._ENC2_RST_MASK)
    
    def test_write(self):
        self.dof.enable(1)
        self.dof.set_speed(500)
        self.dof.reset_encoder_mt()
        
        with patch.object(controller.Controller, '_write') as wr:
            self.dof.write()
        
        wr.assert_called_once_with(bytes([0x55, 0xBA, 0x03, 0xF4, 0x01, 0x2A, 0x64, 0xAE, 0xE5]))

        self.assertEqual(self.dof.config, self.dof._EN_MASK)
        
    def test_read(self):
        #ENC1 27381
        #ENC2 1998
        #IMU 117.4, 32.2, 258.8
        self.mock.return_value.read.return_value = bytes([0x55, 0xBA, 0xF5, 0x6A, 0xCE, 0x7, 0xCD, 0xCC, 0xEA, 0x42, 0xCD, 0xCC, 0x0, 0x42, 0x66, 0x66, 0x81, 0x43, 0xF1, 0x92, 0x3C, 0xCE])

        self.dof.read()

        self.assertEqual(self.dof.motor_enc, 27381)
        self.assertEqual(self.dof.shaft_enc, 1998)
        for i, val in enumerate([117.4, 32.2, 258.8]):
            self.assertAlmostEqual(self.dof.imu[i], val, places=2)
