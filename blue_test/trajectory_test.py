
from acrome.premium import *
import math
import time
import numpy as np

port = "COM6"
m = Master(port)


m.attach(Premium(0))

m.set_variables(0, [[Index.TorqueEn, 1]])


def generate_trajectory(first_pos:list, second_pos:list, duration):
        return list(np.linspace(start=first_pos, stop=second_pos, num=int(duration / 0.005), endpoint=True))


print(generate_trajectory(0, 100, 10))

for i in generate_trajectory(0, 100, 10):
        m.set_variables(0, [[Index.GoalPosition, int(i)*1000]])

