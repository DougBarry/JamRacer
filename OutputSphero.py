import bluetooth
from ObjectMotion import *
import JamRacerConfig
from Helpers import *
import logging
import time
import SpheroRequest
import struct
from OutputRobotBase import *
from random import randint

class SpheroColour(object):
    r=255
    g=255
    b=255
    
    def __init__(self,r,g,b):
        self.r = int(r)
        self.g = int(g)
        self.b = int(b)
        
    @property
    def red(self):
        return self.r
    
    @property
    def green(self):
        return self.g

    @property
    def blue(self):
        return self.b

        
class Sphero(BluetoothRobotBase):
    speed_default = 0x40
    maximum_retry_count = 50
    
    def __init__(self,bluetooth_address):
        super(Sphero,self).__init__(bluetooth_address)
        self.__robotName = "Sphero"
        self.streamNumPackets = 16
        self.dev = 0x00
        self.seq = 0x00

    def connect(self):
        connection_attempt_count = 0
        connection_retry = False

        while connection_attempt_count < Sphero.maximum_retry_count:
            self.report_connection_attempt()

            try:
                connection_attempt_count += 1
                port = randint(1,31)
                self._bluetooth_socket = None
                self._bluetooth_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                self._bluetooth_socket.bind(("", port))    # python 2.7 fix
                self._bluetooth_socket.connect((self._bluetooth_address, port))
                self._connection_success = True
            except:
                self.report_connection_fail_retry(connection_attempt_count, Sphero.maximum_retry_count)
                logging.debug(ex.args)
                time.sleep(1)
                connection_retry = True
                pass

            if not connection_retry:
                # exit loop
                break
        # end loop

        if connection_retry == True:
            # looks like it all went bad
            self._connection_success = False
            raise RobotCommunicationError('Bluetooth connection failed.', self)

        self.report_connection_success()


    def disconnect(self):
        if self._connection_success:
            self._bluetooth_socket.close()

    def __write(self, packet):
    
        try:
            self._bluetooth_socket.send(str(packet))
            self.seq += 1
            if self.seq == 0xFF:
                self.seq = 0x00

            header = struct.unpack('5B', self._bluetooth_socket.recv(5))
            body = self._bluetooth_socket.recv(header[-1])

            response = packet.response(header, body)

            if response.success:
                return response
            else:
                raise RobotCommunicationError('request failed (request: %s:%s, response: %s:%s)' % (header, repr(body), response.header, repr(response.body)))
        except RobotCommunicationError as ex:
            logging.debug(ex)
            pass

    def __prep_str(self, s):
        """ Helper method to take a string and give a array of "bytes" """
        return [ord(c) for c in s]

    # CORE COMMANDS

    def ping(self):
        return self.__write(SpheroRequest.Ping(self.seq))

    def set_rgb(self, colour):
        persistant = False
        logging.debug("Sphero: " + self._bluetooth_address + " setting colour to " + hex(colour.red) + hex(colour.green) + hex(colour.blue))
        return self.__write(SpheroRequest.SetRGB(self.seq, int(colour.red), int(colour.green), int(colour.blue), 0x01 if persistant else 0x00))

    # def set_rgb(self, r, g, b, persistant=False):
        # return self.write(request.SetRGB(self.seq, r, g, b, 0x01 if persistant else 0x00))

    def get_rgb(self):
        return self.__write(SpheroRequest.GetRGB(self.seq))

    def get_version(self):
        raise NotImplementedError

    def get_device_name(self):
        # GET_DEVICE_NAME is not really part of the api, 
        # it has changed to GET_BLUETOOTH_INFO.
        # Which returns both name and Bluetooth mac address.
        return self.get_bluetooth_info().name

    def set_device_name(self, newname):
        """ Sets internal device name. (not announced bluetooth name).
        requires utf-8 encoded string. """
        return self.__write(SpheroRequest.SetDeviceName(self.seq, *self.__prep_str(newname)))

    def get_bluetooth_info(self):
        return self.__write(SpheroRequest.GetBluetoothInfo(self.seq))

    def set_auto_reconnect(self):
        raise NotImplementedError

    def get_auto_reconnect(self):
        raise NotImplementedError

    def get_power_state(self):
        raise NotImplementedError

    def set_power_notification(self):
        raise NotImplementedError

    def sleep(self, wakeup=0, macro=0, orbbasic=0):
        return self.__write(SpheroRequest.Sleep(self.seq, wakeup, macro, orbbasic))

    def get_voltage_trip_points(self):
        raise NotImplementedError

    def set_voltage_trip_points(self):
        raise NotImplementedError

    def set_inactivity_timeout(self):
        raise NotImplementedError

    def jump_to_bootloader(self):
        raise NotImplementedError

    def perform_level_1_diagnostics(self):
        raise NotImplementedError

    def perform_level_2_diagnostics(self):
        raise NotImplementedError

    def clear_counters(self):
        raise NotImplementedError

    def set_time_value(self):
        raise NotImplementedError

    def poll_packet_times(self):
        raise NotImplementedError

    # SPHERO COMMANDS

    def set_heading(self, value):
        """value can be between 0 and 359"""
        return self.__write(SpheroRequest.SetHeading(self.seq, value))

    def set_stabilization(self, state):
        return self.__write(SpheroRequest.SetStabilization(self.seq, state))

    def set_rotation_rate(self, val):
        """value ca be between 0x00 and 0xFF:
            value is a multiplied with 0.784 degrees/s except for:
            0   --> 1 degrees/s
            255 --> jumps to 400 degrees/s
        """
        return self.__write(SpheroRequest.SetRotationRate(self.seq, val))

    def set_application_configuration_block(self):
        raise NotImplementedError

    def get_application_configuration_block(self):
        raise NotImplementedError

    def reenable_demo_mode(self):
        raise NotImplementedError

    def get_chassis_id(self):
        raise NotImplementedError

    def set_chassis_id(self):
        raise NotImplementedError

    def self_level(self):
        raise NotImplementedError

    def set_data_streaming(self):
        raise NotImplementedError

    def configure_collision_detection(self):
        raise NotImplementedError

    def set_back_led_output(self, value):
        """value can be between 0x00 and 0xFF"""
        return self.__write(SpheroRequest.SetBackLEDOutput(self.seq, value))

    def roll(self, heading, state=1):
        """
        speed can have value between 0x00 and 0xFF
        heading can have value between 0 and 359

        """

        myspeed = self.defaultSpeed

        if (self._speed >= 0) and (self._speed <= 0xFF):
            myspeed = self._speed

        logging.debug("Sphero roll dir %i " % heading)
        logging.debug("Sphero roll speed %i " % myspeed)
        return self.__write(SpheroRequest.Roll(self.seq, myspeed, heading, state))

    def roll(self, speed, heading, state=1):
        """
        speed can have value between 0x00 and 0xFF
        heading can have value between 0 and 359

        """
        logging.debug("Sphero roll dir %i " % heading)
        logging.debug("Sphero roll speed %i " % speed)
        return self.__write(SpheroRequest.Roll(self.seq, speed, heading, state))

    def stop(self):
        return self.roll(0,0)

    def sendMotion(self,loco):
        self.SendMotion(loco,self.speed)

    def output_motion(self, motion, speed):
        if not self._connection_success:
            return

        logging.debug("Sphero try dir: " + str(motion.direction))
        logging.debug("Sphero try speed: " + str(speed))

        if motion.direction == DDIR_STATIONARY:
            self.roll(0,0)
        else:
            self.roll(speed, motion.direction)


    def setBackLED(self,intensity):
        return self.__write(SpheroRequest.SetBackLEDOutput(self.seq, intensity))
        # return self.sendCommand(0x02, 0x21, 0x04, 0x02, intensity)

    def rotateHeadingBy(self,heading):
        return self.__write(SpheroRequest.SetHeading(self.seq, (heading >> 8), (heading & 0xff)))

    # def setMotorPowers(self,p1,p2):
        # dir1 = 0x01
        # dir2 = 0x01
        # m1 = p1
        # m2 = p2

        # if (p1 < 0):
            # m1 = p1 * -1
            # dir1 = 0x02

        # if (p2 < 0):
            # m1 = p2 * -1
            # dir2 = 0x02

        # return sendCommand(0x02, 0x33, 0x0B, 0x05, dir1, m1, dir2, m2)

    # def stop(self,coast):
        # coastval = 0x00
        # if coast:
            # coastval = 0x03
        # return sendCommand(0x02, 0x33, 0x0C, 0x05, coastval, 0x00, coastval, 0x00)

    # def setStabilization(self,enable):
        # enableval = 0x00
        # if enable:
            # enable = 0x01
        # return sendCommand(0x02, 0x33, 0x0A, 0x05, 0x04, 0x00, 0x04, 0x00)<<4 | sendCommand(0x02, 0x02, 0x09, 0x02, enableval)

    # def setStreamingData(self,freq,frames_per_sample,mask):
        # streamingParams.count = 0
        # streamingParams.freq = freq
        # streamingParams.frames_per_sample = frames_per_sample
        # streamingParams.mask = mask

        # return sendCommand(0x02, 0x11, 0x07, 0x0A, (400/freq) >> 8, (400/freq), frames_per_sample >> 8, frames_per_sample, char(mask >> 24), char(mask >> 16), char(mask >> 8), char(mask), streamingParams.numOfPackets)

    # def getOptionFlags(self):
        # return sendCommand(0x02, 0x36, 0x08, 0x01)

