from acrome import controller
from acrome import autocontrol
import time
import queue
class AutoOneDOF(controller.OneDOF):
    def __init__(self, interval=0.004, *args, **kwargs):
        self.__interval = interval
        self.control = [autocontrol.PID()] * 1
        self.control[0].set_gains({'ff':750, 'kp':0.9, 'kd':0.1, 'ki':0.01, 'antiwindup':30, 'deadband':(0,0)})
        for ctrl in self.control:
            ctrl.set_interval(self.__interval)
        super().__init__(*args, **kwargs)
        self.update()
    
    def iter_control(self):
        _time0 = time.time()
        self.control[0].set_input(self.shaft_enc)
        self.set_speed(self.control[0].calculate())
        self.update()
        sleep_time = self.__interval - (time.time() - _time0)
        time.sleep(sleep_time if sleep_time > 0 else 0)
    
    def update_setpoint(self, val):
        self.control[0].setpoint(val)

class AutoBallBeam(controller.BallBeam):
    def __init__(self, interval = 0.004, *args, **kwargs):
        self.__interval = interval
        self.control = [autocontrol.PID()] * 1
        self.control[0].set_gains({'ff':0, 'kp':0.35, 'kd':0.15, 'ki':0.1, 'antiwindup':30, 'deadband':(0,0)})
        self.control[0].config_filter(20, 'error')
        self.control[0].config_filter(20, 'derivative')
        for ctrl in self.control:
            ctrl.set_interval(self.__interval)
        super().__init__(*args, **kwargs)
        self.update()
    
    def iter_control(self):
        _time0 = time.time()
        self.control[0].set_input(self.position)
        self.set_servo(self.control[0].calculate())
        self.update()
        sleep_time = self.__interval - (time.time() - _time0)
        time.sleep(sleep_time if sleep_time > 0 else 0)
    
    def update_setpoint(self, val):
        self.control[0].setpoint(val)

class AutoBallBalancingTable(controller.BallBalancingTable):
    def __init__(self, interval=0.004, *args, **kwargs):
        self.__interval = interval
        self.control = [autocontrol.PID()] * 2

        self.control[0].set_gains({'ff':0, 'kp':1.7, 'kd':0.5, 'ki':0.5, 'antiwindup':30, 'deadband':(0,0)})
        self.control[0].config_filter(20, 'derivative')

        self.control[1].set_gains({'ff':0, 'kp':1.7, 'kd':0.5, 'ki':0.5, 'antiwindup':30, 'deadband':(0,0)})
        self.control[1].config_filter(20, 'derivative')

        for ctrl in self.control:
            ctrl.set_interval(self.__interval)
        super().__init__(*args, **kwargs)
        self.update()
    
    def iter_control(self):
        _time0 = time.time()
        self.control[0].set_input(self.position[0])
        self.control[1].set_input(self.position[1])
        self.set_servo(self.control[0].calculate(), self.control[1].calculate())
        self.update()
        sleep_time = self.__interval - (time.time() - _time0)
        time.sleep(sleep_time if sleep_time > 0 else 0)
    
    def update_setpoint(self, val):
        map(autocontrol.PID.setpoint, self.control, val)

class AutoDelta(controller.Delta):
    def __init__(self, interval=1, *args, **kwargs):
        self.__interval = interval
        self.control = [autocontrol.PID()] * 3
        
        map(autocontrol.PID.set_gains, self.control, [{'ff':0, 'kp':1, 'kd':0, 'ki':0, 'antiwindup':0, 'deadband':(0,0)}]*3)
        
        for ctrl in self.control:
            ctrl.set_interval(self.__interval)
        
        super().__init__(*args, **kwargs)
        self.update()

    def iter_control(self):
        _time0 = time.time()
        map(autocontrol.PID.set_input, self.control, self.position)
        self.set_motors([control.calculate() for control in self.control])
        self.update()
        sleep_time = self.__interval - (time.time() - _time0)
        time.sleep(sleep_time if sleep_time > 0 else 0)
    
    def update_setpoint(self, val):
        map(autocontrol.PID.setpoint, self.control, val)

class AutoStewart(controller.Stewart):
    def __init__(self, interval=1, *args, **kwargs):
        self.__interval = interval
        self.control = [autocontrol.PID()] * 6
        
        map(autocontrol.PID.set_gains, self.control, [{'ff':300, 'kp':0.25, 'kd':0, 'ki':0, 'antiwindup':0, 'deadband':(0,0)}]*6)
        
        for ctrl in self.control:
            ctrl.set_interval(self.__interval)
        
        super().__init__(*args, **kwargs)
        self.update()

    def iter_control(self):
        _time0 = time.time()
        map(autocontrol.PID.set_input, self.control, self.position)
        self.set_motors([control.calculate() for control in self.control])
        self.update()
        sleep_time = self.__interval - (time.time() - _time0)
        time.sleep(sleep_time if sleep_time > 0 else 0)
    
    def update_setpoint(self, val):
        map(autocontrol.PID.setpoint, self.control, val)

