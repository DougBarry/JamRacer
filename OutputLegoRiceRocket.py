from OutputLegoMindstormsNXT import *

class RiceRocket(LegoNXT):

    def __init__(self, bluetooth_address):
        super(RiceRocket,self).__init__(bluetooth_address)
        self._name = 'THE RICE ROCKET'
        self._hardware_motion_type = MTYPE_TANKSTEER

    # overriding the output motion method as the rice rocket has reverse motors
    def output_motion(self, object_motion, speed=None):
        # if object_motion.motion_type != MTYPE_TANKSTEER:
        #     raise RobotBadMotionInstruction("")

        direction = object_motion.direction
        if speed is None:
            speed = LegoNXT.speed_default

        # some kind of percentage speed thing needed here

        motor_speed_a = 0
        motor_speed_b = 0

        if direction == DDIR_AHEADLEFT:
            motor_speed_a = -50
            motor_speed_b = -100
        elif direction == DDIR_AHEADRIGHT:
            motor_speed_a = -100
            motor_speed_b = -50
        elif direction == DDIR_AHEAD:
            motor_speed_a = -100
            motor_speed_b = -100
        elif direction == DDIR_LEFT:
            motor_speed_a = 100
            motor_speed_b = -100
        elif direction == DDIR_RIGHT:
            motor_speed_a = -100
            motor_speed_b = 100
        elif direction == DDIR_REVERSELEFT:
            motor_speed_a = 50
            motor_speed_b = 100
        elif direction == DDIR_REVERSERIGHT:
            motor_speed_a = 100
            motor_speed_b = 50
        elif direction == DDIR_REVERSE:
            motor_speed_a = 100
            motor_speed_b = 100
        elif direction == DDIR_STATIONARY:
            motor_speed_a = 0
            motor_speed_b = 0

        if (self._motor_a_speed_last != motor_speed_a) or (self._motor_b_speed_last != motor_speed_b):
            logging.debug(self.name + " Motor A change:" + str(motor_speed_a) + " Motor B change:" + str(motor_speed_b))

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