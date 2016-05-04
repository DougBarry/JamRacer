from ObjectMotion import *
import logging

class RobotBaseException(Exception):
    pass

class RobotBadMotionInstruction(RobotBaseException):
    pass

class RobotCommunicationError(RobotBaseException):
    pass

class RobotNotConnected(RobotCommunicationError):
    pass


class RobotBase(object):
    speed_default = 50
    speed_max = 100
    speed_min = 1
    maximum_retry_count = 5

    def __init__(self):
        self._name = "Robot device"
        self._connection_success = False
        self._speed = 0
        self._supported_motion_types=[]

    def __report_initialisation(self):
        logging.debug("Robot initialised: " + self.name)

    @property
    def name(self):
        return self._name

    @property
    def supported_motion_types(self):
        return self._supported_motion_types

    def connect(self,maximumRetryCount=50):
        raise NotImplemented()

    def disconnect(self):
        raise NotImplemented()

    def report_connection_attempt(self):
        logging.info(self.name + ' connection attempt')

    def report_connection_fail_retry(self, connection_attempt_count, maximum_retry_count):
        logging.info(self.name + ' connection error, retrying (' + str(connection_attempt_count) + '/' + str (maximum_retry_count)+ ')')

    def report_connection_success(self):
        logging.info(self.name + ' connection success')

    def stop(self):
        raise NotImplemented()

    def output_motion(self, object_motion):
        raise NotImplemented()


class BluetoothRobotBase(RobotBase):

    def __init__(self,bluetooth_address):
        super(BluetoothRobotBase, self).__init__()
        self._name = 'Bluetooth Robot device'
        self._bluetooth_socket = None
        self._bluetooth_address = bluetooth_address

    def __report_initialisation(self):
        logging.debug('Bluetooth Robot initialised: ' + self.name)

    @property
    def name(self):
        return self._name + ' ' + self._bluetooth_address

    @property
    def bluetooth_address(self):
        return self._bluetooth_address

    def connect(self,maximumRetryCount=50):
        raise NotImplemented()

