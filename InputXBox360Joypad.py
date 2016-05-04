'''
A class overloading the Generic joypad class, specifically for the XBox 360 Joypad
Tested with wired and wireless XBox 360 Joypads on a Raspberry Pi B (V1)
Your milage may vary
'''

import pygame
from InputPyGameGenericJoystick import *
from ObjectMotion import *

class XBox360Joypad(PyGameJoystickController):

    def __init__(self, joystick_handle, joystick_name=__name__):
        super(XBox360Joypad,self).__init__(joystick_handle,joystick_name)

    def get_motion(self, motion_type = MTYPE_CARSTEER):
        """
        Return motion, by default this produces a car motion using the analogue sticks like Gran Tourismo (steering
        left stick, accel/brake on right stick. It can also produce tank steer by using the sticks as tank controls.
        """

        if (motion_type == MTYPE_CARSTEER) or (motion_type == MTYPE_COMPASS):
            axis0 = self.check_axis(0)
            axis1 = self.check_axis(5)

            amt = AnalogMotionTranslator(__name__, -self.axis_deadzone[0], self.axis_deadzone[0], -self.axis_deadzone[1], self.axis_deadzone[1])
            loco = amt.get_motion(motion_type, axis0, axis1)

            # logging.debug("Joystick: " + self.__name + " x:" + str(x0) + " y:" + str(y0))
            return loco

        elif motion_type == MTYPE_TANKSTEER:
            axis1 = self.check_axis(1)
            axis3 = self.check_axis(4)

            amt = AnalogMotionTranslator(__name__,-self.axis_deadzone[1],self.axis_deadzone[1],-self.axis_deadzone[3],self.axis_deadzone[3])
            loco = amt.get_motion(motion_type, axis1, axis3)

            # logging.debug("Joystick: " + self.__name + " y0:" + str(y0) + " y1:" + str(y1))
            return loco
