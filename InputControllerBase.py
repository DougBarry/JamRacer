'''
Base class for input method implimentations. This is inherited and overloaded by input method children such as The Wii
Fit Board or the Generic USB Joysitck (provided through PyGame)
'''

import logging

class ControllerBase(object):
    '''
    Controller Base class.
    A generous default deadzone is defined here.
    '''
    default_axis_deadzone_size = 0.4

    def __init__(self, supported_motion_outputs, controller_name = "Generic Input device"):
        if not isinstance(supported_motion_outputs,list):
            raise Exception("supported_motion_outputs is not a list")
        self.controller_supported_motion_outputs = supported_motion_outputs
        self.axis_deadzone = []
        self.controller_name = controller_name
        self.__report_initialisation()

    def __report_initialisation(self):
        '''
        Log successful completion of constructor
        :return:
        '''
        logging.debug("Controller initialised: " + self.name)

    def update(self):
        '''
        To be overloaded
        :return:
        '''
        raise NotImplemented()

    @property
    def name(self):
        '''
        Return human readable string relating to controller
        :return:
        '''
        return self.controller_name

    @property
    def number(self):
        '''
        If this controller is of an enumerable type such as USB gamepads, return the number
        :return:
        '''
        return self.joynumber

    @property
    def handle(self):
        '''
        If this controller is of an enumerable type such as USB gamepads, return the PyGame reference for direct access
        :return:
        '''
        return self.joyhandle

    @property
    def supported_motion_outputs(self):
        '''
        Can this input device report angles, cardinal directions, or some other type of direction or instruction
        :return:
        '''
        return self.controller_supported_motion_outputs

    def get_direction(self, motion_type):
        '''
        If this controller can provide a direction (0-359 degrees), return it
        :return:
        '''
        raise NotImplementedError()

    def check_axis(self, p_axis):
        '''
        Update (poll) the value for device axes if it has any
        :return:
        '''
        raise NotImplementedError()

    def check_button(self, p_button):
        '''
        Update (poll) the value for device buttons if it has any
        :return:
        '''
        raise NotImplementedError()

    def check_hat(self, p_hat):
        '''
        Update (poll) the value for device hats if it has any
        :return:
        '''
        raise NotImplementedError()
