from ObjectMotion import *
import time
import logging
from Helpers import *
import nxt, thread
from OutputRobotBase import *


class LegoNXT(BluetoothRobotBase):
    speed_default = 75
    speed_max = 100
    speed_min = 5

    def __init__(self, bluetooth_address):
        super(LegoNXT,self).__init__(bluetooth_address)
        self._name = 'Lego Mindstorms NXT Brick'
        self._brick = None
        self._hardware_motion_type = MTYPE_UNDEFINED
        self._motor_a = None
        self._motor_b = None
        self._motor_c = None
        self._motor_a_speed_last = 0
        self._motor_b_speed_last = 0
        self._motor_c_speed_last = 0

    def connect(self, hardware_motion_type = MTYPE_TANKSTEER):
        connection_attempt_count = 0
        connection_retry = False

        self._supported_motion_types.append(hardware_motion_type)

        while connection_attempt_count < LegoNXT.maximum_retry_count:
            self.report_connection_attempt()

            try:
                connection_attempt_count += 1
                self._brick = nxt.locator.find_one_brick(host=self._bluetooth_address, debug=True, method=nxt.locator.Method(usb=False, bluetooth=True, fantomusb=False))
                self._connection_success = True
            except Exception as ex:
                self.report_connection_fail_retry(connection_attempt_count, LegoNXT.maximum_retry_count)
                time.sleep(2)
                connection_retry = True
                pass

            if not connection_retry:
                # exit loop
                break
        # end loop

        if connection_retry:
            # looks like it all went bad
            self._connection_success = False
            raise RobotNotConnected('Bluetooth connection failed.', self)

        self.report_connection_success()

        self._hardware_motion_type = hardware_motion_type
        self._motor_a = nxt.Motor(self._brick, nxt.PORT_A)
        self._motor_b = nxt.Motor(self._brick, nxt.PORT_B)
        self._motor_c = nxt.Motor(self._brick, nxt.PORT_C)
        self._motor_a_speed_last = 0
        self._motor_b_speed_last = 0
        self._motor_c_speed_last = 0

    def disconnect(self):
        if self._connection_success:
            self._brick = None

    def stop(self):
        if self._connection_success:
            self.output_motion(ObjectMotion(MTYPE_UNDEFINED, DDIR_STATIONARY))

    def output_motion(self, object_motion):
        # if object_motion.motion_type != MTYPE_TANKSTEER:
        #     raise RobotBadMotionInstruction("")

        direction = object_motion.direction
        speed = object_motion.speed

        nxtspeed = LegoNXT.speed_default

        if speed == -1:
            nxtspeed = LegoNXT.speed_default
        else:
            if (speed > 0) and (speed<=1):
                nxtspeed = int(speed * LegoNXT.speed_max)

        if nxtspeed < LegoNXT.speed_min:
            nxtspeed = LegoNXT.speed_min
        elif nxtspeed > LegoNXT.speed_max:
            nxtspeed = LegoNXT.speed_max

        motor_speed_a = 0
        motor_speed_b = 0

        if direction == DDIR_AHEADLEFT:
            motor_speed_a = 50
            motor_speed_b = 100
        elif direction == DDIR_AHEADRIGHT:
            motor_speed_a = 100
            motor_speed_b = 50
        elif direction == DDIR_AHEAD:
            motor_speed_a = 100
            motor_speed_b = 100
        elif direction == DDIR_LEFT:
            motor_speed_a = -100
            motor_speed_b = 100
        elif direction == DDIR_RIGHT:
            motor_speed_a = 100
            motor_speed_b = -100
        elif direction == DDIR_REVERSELEFT:
            motor_speed_a = -50
            motor_speed_b = -100
        elif direction == DDIR_REVERSERIGHT:
            motor_speed_a = -100
            motor_speed_b = -50
        elif direction == DDIR_REVERSE:
            motor_speed_a = -100
            motor_speed_b = -100
        elif direction == DDIR_STATIONARY:
            motor_speed_a = 0
            motor_speed_b = 0

        motor_speed_a = int(motor_speed_a * (float(nxtspeed) / float(LegoNXT.speed_max)))
        motor_speed_b = int(motor_speed_b * (float(nxtspeed) / float(LegoNXT.speed_max)))

        # if (self._motor_a_speed_last != motor_speed_a) or (self._motor_b_speed_last != motor_speed_b):
        #     logging.debug(self.name + " output_motion a:" + str(motor_speed_a) + " b:" + str(motor_speed_b))

        degrees = 45

        if motor_speed_a != 0:
            if self._motor_a_speed_last != motor_speed_a:
                self.__turn_motor(self._motor_a, motor_speed_a, degrees)
        else:
            self.__stop_motor(self._motor_a, None)

        if motor_speed_b != 0:
            if self._motor_b_speed_last != motor_speed_b:
                self.__turn_motor(self._motor_b, motor_speed_b, degrees)
        else:
            self.__stop_motor(self._motor_b, None)

        self._motor_a_speed_last = motor_speed_a
        self._motor_b_speed_last = motor_speed_b


    def __turn_motor(self, motor, power, degrees):
        # if(power!=0) and (degrees!=0):
        #     motor.weak_turn(power, degrees)
        logging.debug(self.name + ' Motor: ' + str(motor.port) + " Power:" + str(power) + " Degrees:" + str(degrees))
        if(power != 0) and (degrees != 0):
            motor.run(power)

    def __stop_motor(self, motor, *args):
        motor.idle()

    def test_motors(self):
        self.__turn_motor(self._motor_a,100,360)
        time.sleep(1)
        self.__stop_motor(self._motor_a)
        time.sleep(1)
        self.__turn_motor(self._motor_a,-100,360)
        time.sleep(1)
        self.__stop_motor(self._motor_a)
        time.sleep(1)
        self.__turn_motor(self._motor_b,100,360)
        time.sleep(1)
        self.__stop_motor(self._motor_b)
        time.sleep(1)
        self.__turn_motor(self._motor_b,-100,360)
        time.sleep(1)
        self.__stop_motor(self._motor_b)
        time.sleep(1)

    def test_motors_quick(self):
        self.__turn_motor(self._motor_a,100,30)
        time.sleep(1)
        self.__stop_motor(self._motor_a)
        self.__turn_motor(self._motor_a,-100,30)
        time.sleep(1)
        self.__stop_motor(self._motor_a)
        self.__turn_motor(self._motor_b,100,30)
        time.sleep(1)
        self.__stop_motor(self._motor_b)
        self.__turn_motor(self._motor_b,-100,30)
        time.sleep(1)
        self.__stop_motor(self._motor_b)
