from acrome import controller
from acrome import autocontrol
import time
import math
import numpy as np

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
        for control, value in zip(self.control, val):
            control.setpoint(value)

class AutoDelta(controller.Delta):
    def __init__(self, interval=1, *args, **kwargs):
        self.__interval = interval
        self.control = [autocontrol.PID()] * 3
        
        for control in self.control:
            control.set_gains({'ff':0, 'kp':1.0, 'kd':0.00, 'ki':0, 'antiwindup':0, 'deadband':(0,0)})
        
        for ctrl in self.control:
            ctrl.set_interval(self.__interval)
        
        super().__init__(*args, **kwargs)
        self.update()

    def iter_control(self):
        _time0 = time.time()

        for control, position in zip(self.control, self.position):
            control.set_input(position)

        self.set_motors([control.calculate() for control in self.control])
        self.update()
        sleep_time = self.__interval - (time.time() - _time0)
        time.sleep(sleep_time if sleep_time > 0 else 0)
    
    def update_setpoint(self, val):
        for control, value in zip(self.control, val):
            control.setpoint(value)

class AutoStewart(controller.Stewart):
    def __init__(self, interval=1, *args, **kwargs):
        self.__interval = interval
        self.control = [autocontrol.PID()] * 6
        self.__pos_min = [0] * 6
        self.__pos_max = [4095] * 6
        
        self.__tradius = 130
        self.__bradius = 170

        #Angles between first and second motors
        self.__tangle = math.radians(25)
        self.__bangle = math.radians(90)

        self.__toffset = 62
        self.__boffset = 57

        self.__leg_len_extended = 598
        self.__leg_len_retracted = 394.8
        
        for control in self.control:
            control.set_gains({'ff':0, 'kp':1, 'kd':0, 'ki':0, 'antiwindup':0, 'deadband':(0,0)})
        
        for ctrl in self.control:
            ctrl.set_interval(self.__interval)
        
        super().__init__(*args, **kwargs)
        self.update()

    def iter_control(self):
        _time0 = time.time()
        for control, pos in zip(self.control, self.position):
            control.set_input(pos)
        self.set_motors([control.calculate() for control in self.control])
        self.update()
        sleep_time = self.__interval - (time.time() - _time0)
        time.sleep(sleep_time if sleep_time > 0 else 0)
    
    def update_setpoint(self, val):
        for control, value in zip(self.control, val):
            control.setpoint(value)

    def set_mechanical_constants(self, top_radius, bottom_radius, top_offset, bottom_offset, top_angle, bottom_angle, extended_leg_length, retracted_leg_length):
        self.__tradius = top_radius
        self.__bradius = bottom_radius

        #Angles between first and second motors
        self.__tangle = math.radians(top_angle)
        self.__bangle = math.radians(bottom_angle)

        self.__toffset = top_offset
        self.__boffset = bottom_offset

        self.__leg_len_extended = extended_leg_length
        self.__leg_len_retracted = retracted_leg_length

    def set_motor_limits(self, pos_min, pos_max):
        if len(pos_min) == 6 and len(pos_max) == 6:
            self.__pos_min = [pos if pos < 4096 and pos > 0 else 0 for pos in pos_min]
            self.__pos_max = [pos if pos < 4096 and pos > 0 else 4095 for pos in pos_max]

    def inverse_kinematics(self, x, y, z, roll, pitch, yaw):
        __axis_remap = lambda x, y, z, roll, pitch, yaw : (-y, x, z, -pitch, roll, -yaw)
        rot_x = lambda angle : np.array([[1,0,0],[0, math.cos(angle), -math.sin(angle)], [0, math.sin(angle), math.cos(angle)]])
        rot_y = lambda angle : np.array([[math.cos(angle),0,math.sin(angle)],[0, 1, 0], [-math.sin(angle), 0, math.cos(angle)]])
        rot_z = lambda angle : np.array([[math.cos(angle), -math.sin(angle), 0],[math.sin(angle), math.cos(angle), 0],[0,0,1]])

        mm2raw = lambda mm, pos_max, pos_min : (mm * (pos_max - pos_min) / (self.__leg_len_extended - self.__leg_len_retracted))

        x,y,z,roll,pitch,yaw = (__axis_remap(x,y,z,roll,pitch,yaw))

        roll, pitch, yaw = (math.radians(roll), math.radians(pitch), math.radians(yaw))

        bottom_mt_coords = np.empty(shape=(6,3), dtype=np.float32)
        platform_mt_coords = np.empty(shape=(6,3), dtype=np.float32)

        bottom_mt_coords[0] = [self.__bradius *  -math.sin((2*math.pi / 3 - self.__bangle)/2), self.__bradius *  math.cos((2*math.pi / 3 - self.__bangle)/2), self.__boffset]
        bottom_mt_coords[1] = np.transpose(np.matmul(rot_z(self.__bangle), np.vstack(bottom_mt_coords[0])))
        bottom_mt_coords[5] = np.transpose(np.matmul(rot_z(-2 * math.pi / 3), np.vstack(bottom_mt_coords[1])))
        bottom_mt_coords[3] = np.transpose(np.matmul(rot_z(-2 * math.pi / 3), np.vstack(bottom_mt_coords[5])))
        bottom_mt_coords[4] = np.transpose(np.matmul(rot_z(-2 * math.pi / 3), np.vstack(bottom_mt_coords[0])))
        bottom_mt_coords[2] = np.transpose(np.matmul(rot_z(-2 * math.pi / 3), np.vstack(bottom_mt_coords[4])))

        platform_mt_coords[0] = [self.__tradius *  -math.sin((2*math.pi / 3 - self.__tangle)/2), self.__tradius *  math.cos((2*math.pi / 3 - self.__tangle)/2), 0]
        platform_mt_coords[1] = np.transpose(np.matmul(rot_z(self.__tangle), np.vstack(platform_mt_coords[0])))
        platform_mt_coords[5] = np.transpose(np.matmul(rot_z(-2 * math.pi / 3), np.vstack(platform_mt_coords[1])))
        platform_mt_coords[3] = np.transpose(np.matmul(rot_z(-2 * math.pi / 3), np.vstack(platform_mt_coords[5])))
        platform_mt_coords[4] = np.transpose(np.matmul(rot_z(-2 * math.pi / 3), np.vstack(platform_mt_coords[0])))
        platform_mt_coords[2] = np.transpose(np.matmul(rot_z(-2 * math.pi / 3), np.vstack(platform_mt_coords[4])))

        rotation_matrix = np.matmul(np.matmul(rot_x(roll), rot_y(pitch)), rot_z(yaw))
        rpy_offset = np.transpose(np.matmul(rotation_matrix, [0,0,self.__toffset]))
        platform_mt_coords = [np.add(np.matmul(rotation_matrix, np.transpose(pcoord)), [x,y,z]) for pcoord in platform_mt_coords]
        platform_joint_coords = [np.subtract(pcoord, rpy_offset) for pcoord in platform_mt_coords]

        vectorel_length = [np.linalg.norm(jcoord-bcoord) - self.__leg_len_retracted for jcoord, bcoord in zip(platform_joint_coords, bottom_mt_coords) ]

        return list(map(mm2raw, vectorel_length, self.__pos_max, self.__pos_min))
    
    def generate_trajectory(self, first_pos:list, second_pos:list, duration):
        return list(np.linspace(start=first_pos, stop=second_pos, num=int(duration / self.__interval), endpoint=True))
        