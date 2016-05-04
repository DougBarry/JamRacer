'''
A class overloading the Generic joypad class, for a specific type of gamepad
'''

from ObjectMotion import *
from InputPyGameGenericJoystick import *

class TrustUSBJoypadController(PyGameJoystickController):
    default_axis_deadzone_size = 0.4

    def __init__(self, joystick_handle, joystick_name=__name__):
        super(TrustUSBJoypadController, self).__init__(joystick_handle, joystick_name)

    def get_motion(self, motion_type = MTYPE_CARSTEER):
        """
        by default return car type motions
        joystick can do all motion types maybe?
        """

        direction = DDIR_STATIONARY
        speed = -1

        # for i in range(self.controller_handle.get_numaxes()):
        #     logging.debug("Axis["+str(i)+"="+str(self.check_axis(i)))

        if (motion_type == MTYPE_CARSTEER) or (motion_type == MTYPE_COMPASS):
            axis0 = self.check_axis(0)
            axis3 = self.check_axis(3)

            amt = AnalogMotionTranslator(-self.axis_deadzone[0], self.axis_deadzone[0], -self.axis_deadzone[1], self.axis_deadzone[1])
            direction = amt.get_direction(motion_type, axis0, axis3)

            # logging.debug("Joystick: " + self.__name + " x:" + str(x0) + " y:" + str(y0))

        elif motion_type == MTYPE_TANKSTEER:
            axis1 = self.check_axis(1)
            axis3 = self.check_axis(3)

            amt = AnalogMotionTranslator(-self.axis_deadzone[1],self.axis_deadzone[1],-self.axis_deadzone[3],self.axis_deadzone[3])
            direction = amt.get_direction(motion_type, axis1, axis3)

            # logging.debug("Joystick: " + self.__name + " y0:" + str(y0) + " y1:" + str(y1))

        if self.check_button(5) or self.check_button(6) or self.check_button(7) or self.check_button(8):
            # speed boost
            speed = 1

        return ObjectMotion(self.name,motion_type,direction,speed)