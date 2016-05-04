import logging

class ControllerBase(object):
    default_axis_deadzone_size = 0.4

    def __init__(self, supported_motion_outputs, controller_name = "Generic Input device"):
        if not isinstance(supported_motion_outputs,list):
            raise Exception("supported_motion_outputs is not a list")
        self.controller_supported_motion_outputs = supported_motion_outputs
        self.axis_deadzone = []
        self.controller_name = controller_name
        self.__report_initialisation()

    def __report_initialisation(self):
        logging.debug("Controller initialised: " + self.name)

    def update(self):
        raise NotImplemented()

    @property
    def name(self):
        return self.controller_name

    @property
    def number(self):
        return self.joynumber

    @property
    def handle(self):
        return self.joyhandle

    @property
    def supported_motion_outputs(self):
        return self.controller_supported_motion_outputs

    def get_direction(self, motion_type):
        raise NotImplementedError()

    def check_axis(self, p_axis):
        raise NotImplementedError()

    def check_button(self, p_button):
        raise NotImplementedError()

    def check_hat(self, p_hat):
        raise NotImplementedError()
