import pygame
from InputPyGameGenericJoystick import *
from ObjectMotion import *

class XBox360Joypad(PyGameJoystickController):

    def __init__(self, joystick_handle, joystick_name=__name__):
        super(XBox360Joypad,self).__init__(joystick_handle,joystick_name)

    def get_motion(self, motion_type = MTYPE_CARSTEER):
        """
        by default return car type motions
        joystick can do all motion types maybe?
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
