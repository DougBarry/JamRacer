import bluetooth
from ObjectMotion import *
import time
import logging
from Helpers import *
from OutputRobotBase import *
from random import  randint

class iRacer(BluetoothRobotBase):
    speed_default = 8
    speed_max = 15
    speed_min = 4
    maximum_retry_count = 5

    def __init__(self,bluetooth_address):
        super(iRacer,self).__init__(bluetooth_address)
        self._name = "iRacer"


    def connect(self):
        connection_attempt_count = 0
        connection_retry = False

        while connection_attempt_count < iRacer.maximum_retry_count:
            self.report_connection_attempt()

            try:
                connection_attempt_count += 1
                port = connection_attempt_count
                self._bluetooth_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                self._bluetooth_socket.bind(("", port))    # python 2.7 fix
                self._bluetooth_socket.connect((self._bluetooth_address, port))
                self._connection_success = True
            except Exception as ex:
                self.report_connection_fail_retry(connection_attempt_count, iRacer.maximum_retry_count)
                logging.debug(ex)
                self._bluetooth_socket = None
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
            raise RobotCommunicationError('Bluetooth connection failed ', self)

        self.report_connection_success()


    def disconnect(self):
        if self._connection_success:
            self.stop()
            self._bluetooth_socket.close()
            self._bluetooth_socket = None


    def stop(self):
        if self._connection_success:
            self.output_motion(ObjectMotion(MTYPE_CARSTEER, DDIR_STATIONARY))


    def output_motion(self, object_motion):
        self.__send_motion(object_motion.direction, object_motion.speed)


    def __send_motion(self,direction,speed = -1):
        # if not self.__connectionSuccess:
            # raise DaguCarNotConnected

        action_code = "0x00"

        carspeed = iRacer.speed_default

        if speed == -1:
            carspeed = iRacer.speed_default
        else:
            if (speed > 0) and (speed<=1):
                carspeed = int(speed * iRacer.speed_max)

        if carspeed < iRacer.speed_min:
            carspeed = iRacer.speed_min
        elif carspeed > iRacer.speed_max:
            carspeed = iRacer.speed_max

        if (direction == DDIR_AHEADLEFT):
            action_code = add_hex2("0x50",hex(carspeed))
        #    # 0x5X for left forward. 0x51 very slow. 0x5F fastest
#            sock.send('\x5A')

        if (direction == DDIR_AHEADRIGHT):
            action_code = add_hex2("0x60",hex(carspeed))
        #    # 0x6X for right forward. 0x11 very slow. 0x1F fastest
#            sock.send('\x6A')

        if (direction == DDIR_AHEAD):
            action_code = add_hex2("0x10",hex(carspeed))
        #    # 0x1X for straight forward. 0x11 very slow. 0x1F fastest
#            sock.send('\x1A')

        if (direction == DDIR_REVERSELEFT):
            action_code = add_hex2("0x70",hex(carspeed))
        #    # 0x7X for left backwards. 0x71 very slow. 0x7F fastest
#            sock.send('\x7A')

        if (direction == DDIR_REVERSERIGHT):
            action_code = add_hex2("0x80",hex(carspeed))
        #    # 0x8X for right backwards. 0x81 very slow. 0x8F fastest
#            sock.send('\x8A')

        if (direction == DDIR_REVERSE):
            action_code = add_hex2("0x20",hex(carspeed))
        #    # 0x2X for straight backward. 0x21 very slow. 0x2F fastest
#            sock.send('\x2A')

        if (direction == DDIR_STATIONARY):
        #    #stop
            action_code = "0x00"

        # add action and speed together
        action_to_send = action_code.replace("0x","").decode('hex')

        try:
            self._bluetooth_socket.send(action_to_send)
        except:
            # error communicating with dagu car!
            raise RobotCommunicationError("Error sending action to bluetooth_socket: ", action_to_send, self)
