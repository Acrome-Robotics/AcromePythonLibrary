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

