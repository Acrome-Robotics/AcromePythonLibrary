from acrome.premium import *
import math

port = "COM6"
m = Master(port)


m.attach(Premium(0))
print(Index.MaxSpeed)
m.set_variables(0, [[Index.TorqueEn, 1]])

for i in range(0,200):
    #m.set_variables(0, [(i, 0)])
    m.set_variables(0, [[Index.GoalSpeed, i*300]])
    print(i*300)
    time.sleep(0.05)

time.sleep(10)

for i in range(200,0,-1):
    m.set_variables(0, [[Index.GoalSpeed, i*300]])
    print(i*300)
    time.sleep(0.05)

m.set_variables(0, [[Index.GoalSpeed, 0]])