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
        self.dev = controller.Delta()

    def tearDown(self):
        pass

    def test_set_motors_valid_values(self):
        for mt in range(self.dev.__class__._MIN_MT_POS, self.dev.__class__._MAX_MT_POS):
            self.dev.set_motors([mt] * 3)
            self.assertEqual(self.dev._Delta__motors, [mt] * 3)
        
    def test_set_motors_invalid_values(self):
        self.dev.set_motors([99999] * 3)
        self.assertEqual(self.dev._Delta__motors, [self.dev.__class__._MAX_MT_POS] * 3)

        self.dev.set_motors([-99999] * 3)
        self.assertEqual(self.dev._Delta__motors, [self.dev.__class__._MIN_MT_POS] * 3)

    def test_pick(self):
        self.dev.pick(True)
        self.assertTrue(self.dev._Delta__magnet == 1)
        self.dev.pick(False)
        self.assertTrue(self.dev._Delta__magnet == 0)

    def test_write(self):
        self.dev.pick(True)
        self.dev.set_motors([400, 500, 600])
        
        with patch.object(controller.Controller, '_writebus') as wr:
            self.dev._write()
        
        wr.assert_called_once_with(bytes([0x55, 0xBD, 0x1, 0x90, 0x1, 0xF4, 0x1, 0x58, 0x2, 0x27, 0xA7, 0x2C, 0x7A]))                     

    def test_read(self):
        #POS 317,656,1721
        self.mock.return_value.read.return_value = bytes([0x55, 0xBD, 0x3D, 0x1, 0x90, 0x2, 0xB9, 0x6, 0x1D, 0xCB, 0x83, 0xD6])
    
        self.dev._read()

        self.assertEqual(self.dev.position, [317,656,1721])
    
    def test_update(self):
        
        with patch.object(self.dev.__class__, '_write') as wr:
            self.dev.update()
            wr.assert_called()

        with patch.object(self.dev.__class__, '_read') as rd:
            self.dev.update()
            rd.assert_called()
            
