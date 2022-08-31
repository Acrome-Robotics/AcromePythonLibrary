import sys
import getopt
from flask import Flask, request, Response
from acrome.motion import AutoStewart
from acrome.autocontrol import PID
from threading import Thread
from queue import Queue, Empty
import json

def __get_arguments():
    sp = baud = wsp = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:b:p:')
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-s":
            sp = str(arg)
        elif opt == '-b':
            baud = int(arg)
        elif opt == '-p':
            wsp = int(arg)
    
    if sp is None:
        sp = '/dev/serial0'
    
    if baud is None:
        baud = 115200
    
    if wsp is None:
        wsp = 5000
    
    return sp, baud, wsp

if __name__ == '__main__':
    __INTERVAL = 0.008

    last_telemetry = {'position':[0] * 6, 'imu':[0]*3}
    
    sp, baud, wsp = __get_arguments()

    param_q = Queue()
    pos_q = Queue()
    sp_q = Queue()
    dev = AutoStewart(portname=sp, baudrate=baud, interval = __INTERVAL)
    
    def process_loop(sp_q:Queue, param_q:Queue, pos_q:Queue, port = '/dev/serial0', baudrate=115200):
        while True:
            try:
                params = param_q.get_nowait()
                dev.set_mechanical_constants(**dict(params['mechanical_constants']))
                dev.set_motor_limits(**(params['motor_limits']))
                map(PID.set_gains, dev.control, params['gains'])
            except Empty:
                pass

            try:
                sp = sp_q.get_nowait()
                dev.enable(sp['enable'])
                dev.update_setpoint(sp['motors'])
            except Empty:
                pass
            
            dev.iter_control()
            while True:
                try:
                    pos_q.get_nowait()
                except Empty:
                    pos_q.put_nowait({'position':dev.position, 'imu':dev.imu})
                    break

    def update_setpoint():
        if request.method == 'POST':
            mot_vals = dev.inverse_kinematics(**(json.loads(request.data))['setpoint'])
            en = (json.loads(request.data))['enable']
            #Validate given setpoints against available workspace
            if any([mt < 0 for mt in mot_vals]):
                return Response(status=422)
            
            sp_q.put_nowait({'enable':en, 'motors':mot_vals})
            return Response(status=200)

    def generate_trajectory():
        if request.method == 'POST':
            mot_vals = dev.inverse_kinematics(**(json.loads(request.data)['setpoint']))
            en = (json.loads(request.data))['enable']
            for mv in mot_vals:
                if mv > 4095 or mv < 0:
                    return Response(status=422)
            
            traj = dev.generate_trajectory(get_telemetry().json['position'], mot_vals, json.loads(request.data)['duration'])
            for point in traj:
                sp_q.put({'enable' : en, 'motors' : list(point)})
            return Response(status=200)

    def get_telemetry():
        global last_telemetry
        try:
            telemetry = pos_q.get_nowait()
            last_telemetry = telemetry
        except Empty:
            telemetry = last_telemetry
            pass
        
        return Response(json.dumps(telemetry), status=200, mimetype='application/json')
        
    def update_params():
        if request.method == 'POST':
            params = json.loads(request.data)
            try:
                _ =params['mechanical_constants']
                _ =params['motor_limits']
                _ =params['gains']
                param_q.put_nowait(params)
                return Response(status=200)
            except KeyError:
                return Response(status=422)

    def clear_motion():
        if request.method == 'POST':
            while True:
                try:
                    _ = sp_q.get_nowait()
                except Empty:
                    break
            sp_q.put({'enable':False, 'motors':[0]*6})
            return Response(status=200)

    control_process = Thread(target=process_loop, args=[sp_q, param_q, pos_q, sp, baud], daemon=True)
    control_process.start()

    app = Flask(__name__)
    app.add_url_rule('/update/setpoint', 'update_setpoint', update_setpoint, methods=['POST'])
    app.add_url_rule('/update/trajectory', 'generate_trajectory', generate_trajectory, methods=['POST'])
    app.add_url_rule('/telemetry', 'get_telemetry', get_telemetry)
    app.add_url_rule('/update/clear', 'clear_motion', clear_motion, methods=['POST'])
    app.add_url_rule('/update/params', 'update_params', update_params, methods=['POST'])

    app.run(host='0.0.0.0', port=wsp, debug=False)

