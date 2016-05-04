'''
A class for generic USB gamepads, as provided by the PyGame library, overloading the ControllerBase class.
'''

import pygame
from ObjectMotion import *
from InputControllerBase import *

class JoystickNotConnectedException(Exception):
    pass

class PyGameJoystickController(ControllerBase):

    def __init__(self, joystick_handle, joystick_name=__name__):
        super(PyGameJoystickController,self).__init__([MTYPE_CARSTEER,MTYPE_TANKSTEER,MTYPE_COMPASS], joystick_name)
        self.controller_name = joystick_name
        self.controller_handle = joystick_handle
        for indx in range(self.controller_handle.get_numaxes()):
            self.axis_deadzone.append(PyGameJoystickController.default_axis_deadzone_size)

    def get_motion(self, motion_type = MTYPE_CARSTEER):
        """
        Return motion. By default return Car motion types, but support others
        If a button is depressed, speed boost is supported
        """

        direction = DDIR_STATIONARY
        speed = -1

        if (motion_type == MTYPE_CARSTEER) or (motion_type == MTYPE_COMPASS):
            axis0 = self.check_axis(0)
            axis1 = self.check_axis(1)

            amt = AnalogMotionTranslator(-self._axis_deadzone[0], self._axis_deadzone[0], -self._axis_deadzone[1], self._axis_deadzone[1])
            direction = amt.get_direction(motion_type, axis0, axis1)

            # logging.debug("Joystick: " + self.__name + " x:" + str(x0) + " y:" + str(y0))

        elif motion_type == MTYPE_TANKSTEER:
            axis1 = self.check_axis(1)
            axis3 = self.check_axis(3)

            amt = AnalogMotionTranslator(-self._axis_deadzone[1],self._axis_deadzone[1],-self._axis_deadzone[3],self._axis_deadzone[3])
            direction = amt.get_direction(motion_type, axis1, axis3)

            # logging.debug("Joystick: " + self.__name + " y0:" + str(y0) + " y1:" + str(y1))

        if self.check_button(5) or self.check_button(6) or self.check_button(7) or self.check_button(8):
            # speed boost
            speed = 2

        return ObjectMotion(self.name, motion_type, direction, speed)
            
    def check_axis(self, p_axis):
        if self.controller_handle is not None:
            if p_axis < self.controller_handle.get_numaxes():
                return self.controller_handle.get_axis(p_axis)
 
        return 0
 
    def check_button(self, p_button):
        if self.controller_handle is not None:
            if p_button < self.controller_handle.get_numbuttons():
                return self.controller_handle.get_button(p_button)
 
        return False
 
    def check_hat(self, p_hat):
        if self.controller_handle is not None:
            if p_hat < self.controller_handle.get_numhats():
                return self.controller_handle.get_hat(p_hat)
 
        return (0, 0)
