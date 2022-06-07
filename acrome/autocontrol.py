class MovingAverage():
    def __init__(self, size):
        self.__array = [0]*size
        self.__iter = 0
        self.__output = 0
    
    def apply(self, val):
        out = self.__output - self.__array[self.__iter]/len(self.__array)
        self.__array[self.__iter] = float(val)
        self.__output = out + self.__array[self.__iter]/len(self.__array)
        self.__iter = (self.__iter + 1) % len(self.__array)
        return self.__output

class PID():
    def __init__(self):
        self.__output = 0
        self.__input = 0
        self.__setpoint = 0
        self.__error = 0
        self.__previous_error = 0
        self.__cumulative_error = 0
        self.__kp = 0
        self.__ki = 0
        self.__kd = 0
        self.__ff = 0
        self.__proportional_term = 0
        self.__integral_term = 0
        self.__derivative_term = 0
        self.__error_deadband = (0, 0)
        self.__interval = 1
        self.__antiwindup = 0
        self.__error_filter = MovingAverage(1)
        self.__derivative_filter = MovingAverage(1)
        self.__reached = False

    def __call__(self):
        return self.calculate()

    def set_interval(self, interval):
        self.__interval = interval

    def config_filter(self, size, stage='error', filter_type='mavg'):
        if stage == 'error':
            if filter_type == 'mavg':
                self.__error_filter = MovingAverage(size)
            else:
                raise ValueError(f"Filter type {filter_type} is not valid!")
        elif stage == 'derivative':
            if filter_type == 'mavg':
                self.__derivative_filter = MovingAverage(size)
            else:
                raise ValueError(f"Filter type {filter_type} is not valid!")

    def set_gains(self, gains:dict):
        self.__ff = gains.get('ff')
        self.__kp = gains.get('kp')
        self.__ki = gains.get('ki')
        self.__kd = gains.get('kd')
        self.__error_deadband = gains.get('deadband')
        self.__antiwindup = gains.get('antiwindup')

    def set_input(self, input):
        self.__input = input

    def calculate(self):
        self.__reached = False
        self.__error = self.__error_filter.apply(self.__setpoint - self.__input)
        if self.__error > 0:
            if ((self.__error_deadband[0] > self.__error)  or (self.__error < self.__error_deadband[1])):
                self.__reached = True
                return 0
        else:
            if ((self.__error_deadband[0] < self.__error)  or (self.__error > self.__error_deadband[1])):
                self.__reached = True
                return 0

            self.__proportional_term = self.__kp * self.__error

            self.__derivative_term = self.__derivative_filter.apply(self.__kd * (self.__error - self.__previous_error) / self.__interval)
            self.__previous_error = self.__error

            self.__cumulative_error += self.__error
            if ((-self.__antiwindup <= self.__cumulative_error <= self.__antiwindup) or self.__antiwindup == 0):
                self.__integral_term = self.__cumulative_error * self.__ki
            else:
                self.__integral_term = self.__cumulative_error / abs(self.__cumulative_error) * self.__antiwindup * self.__ki

            self.__output = self.__ff + self.__proportional_term + self.__derivative_term + self.__integral_term

        return self.__output
    
    def setpoint(self, setpoint):
        self.__setpoint = setpoint

