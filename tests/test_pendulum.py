import unittest
import unittest.mock
from unittest.mock import patch
from acrome import controller


class TestPendulum(unittest.TestCase):
    def setUp(self) -> None:
        patcher = patch("acrome.controller.serial.Serial", autospec=True)
        self.mock = patcher.start()
        self.addCleanup(patcher.stop)
        self.dev = controller.Pendulum()
        self.mock.reset_mock()

    def tearDown(self):
        pass

    def test_set_motor_valid_values(self):
        for speed in range(-1000, 1000+1):
            self.dev.set_motor(speed)
            self.assertEqual(self.dev._Pendulum__motor, speed)

        self.assertTrue(isinstance(self.dev._Pendulum__motor, int))

    def test_set_motor_invalid_values(self):
        self.dev.set_motor(99999999)
        self.assertEqual(self.dev._Pendulum__motor, self.dev.__class__._MAX_MT_SPEED)
   
        self.assertTrue(isinstance(self.dev._Pendulum__motor, int))

        self.dev.set_motor(-99999999)
        self.assertEqual(self.dev._Pendulum__motor, self.dev.__class__._MIN_MT_SPEED)

        self.assertTrue(isinstance(self.dev._Pendulum__motor, int))

    def test_set_enable(self):
        first_config = self.dev._Pendulum__config
        self.dev.enable(1)
        self.assertEqual(self.dev._Pendulum__config, first_config | self.dev.__class__._EN_MASK)
        self.assertTrue(isinstance(self.dev._Pendulum__config, int))

    def test_reset_enable(self):
        self.dev._Pendulum__config |= self.dev._EN_MASK
        first_config = self.dev._Pendulum__config
        self.dev.enable(False)
        self.assertEqual(self.dev._Pendulum__config, first_config & ~self.dev._EN_MASK)
        self.assertTrue(isinstance(self.dev._Pendulum__config, int))
        
    def test_reset_encoder(self):
        first_config = self.dev._Pendulum__config
        self.dev.reset_encoder_mt()
        self.assertEqual(self.dev._Pendulum__config, first_config | self.dev._ENC1_RST_MASK)
        self.assertTrue(isinstance(self.dev._Pendulum__config, int))
        self.dev._Pendulum__config = 0
    
    def test_write(self):
        self.dev.enable(1)
        self.dev.set_motor(500)
        self.dev.reset_encoder_mt()
        
        with patch.object(controller.Controller, '_writebus') as wr:
            self.dev._write()
        
        wr.assert_called_once_with(bytes([0x55, 0xBF, 0x03, 0xF4, 0x01, 0x98, 0xB2, 0x36, 0x45]))

        self.assertEqual(self.dev._Pendulum__config, self.dev._EN_MASK | self.dev._ENC1_RST_MASK)
        
    def test_read(self):
        #POS 3063
        #ENC 1636
        self.mock.return_value.read.return_value = bytes([0x55, 0xBF, 0xF7, 0x0B, 0x64, 0x06, 0xD3, 0xE7, 0x7E, 0x58])

        self.dev._read()

        self.assertEqual(self.dev.position, 3063)
        self.assertEqual(self.dev.encoder, 1636)
    
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
            
