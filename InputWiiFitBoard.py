'''
A class providing an input object for the Nintendo Wii Fit Balance Board over Bluetooth
This class is an amalgomation over several years from many many sources.
I have modified it to work and tested it with Python 2.7 on Bluez5 on Raspbian on a Raspberry Pi B (V1) only.
Your milage may vary.

A non-comprehensive list of sources and inspiration:
https://www.mattcutts.com/blog/linux-wii-balanceboard/
https://www.stavros.io/posts/your-weight-online/
https://dani33l.wordpress.com/2012/11/11/using-python-with-balance-board-ubuntu/
https://github.com/abstrakraft/cwiid
http://conoroneill.net/controlling-an-i-racer-rc-car-using-a-wii-balance-board-and-raspberry_pi/

From here on, 'WFB' is used to refer to the physical Nintendo Wii Fit Board

'''

from ObjectMotion import *
#import ObjectMotion
import JamRacerConfig
import logging
import time
import bluetooth
from InputControllerBase import*
import threading

WII_CONTINUOUS_REPORTING = "04"  # Easier as string with leading zero

WII_COMMAND_LIGHT = 11
WII_COMMAND_REPORTING = 12
WII_COMMAND_REQUEST_STATUS = 15
WII_COMMAND_REGISTER = 16
WII_COMMAND_READ_REGISTER = 17

WII_INPUT_STATUS = 20
WII_INPUT_READ_DATA = 21

WII_EXTENSION_8BYTES = 32

WII_BUTTON_DOWN_MASK = 8

WIIFIT_TOP_RIGHT = 0
WIIFIT_BOTTOM_RIGHT = 1
WIIFIT_TOP_LEFT = 2
WIIFIT_BOTTOM_LEFT = 3

WIIFIT_BLUETOOTH_NAME = 'Nintendo RVL-WBC-01'

WIIFIT_STATUS_CONNECTING = 'Connecting'
WIIFIT_STATUS_CONNECTED = 'Connected'
WIIFIT_STATUS_DISCONNECTING = 'Disconnecting'
WIIFIT_STATUS_DISCONNECTED = 'Disconnected'

class WiiFitBoardEvent:
    '''
    Class for passing events relating to the WFB around
    '''
    def __init__(self, topLeft, topRight, bottomLeft, bottomRight, buttonPressed, buttonReleased):

        self.topLeft = topLeft
        self.topRight = topRight
        self.bottomLeft = bottomLeft
        self.bottomRight = bottomRight
        self.buttonPressed = buttonPressed
        self.buttonReleased = buttonReleased
        #convenience value
        self.totalWeight = topLeft + topRight + bottomLeft + bottomRight


#Usefull for error handling
class WiiFitBoardNotConnected(Exception):
    pass

class WiiFitBoardCommunicationError(Exception):
    pass

#Main Class
class WiiFitBoard(ControllerBase):
    '''
    Main Class, defining some default calibrations relating to my board in particular.
    I have not found a way of causing the WFB to reliably go into calibration mode and update the values in
    its EEPROM. I have had to make do with occasionally hooking it up to a real Wii and using the Wii Fit disc.
    Connecting to the Wii Fit board is conveluted, involving pressing the boards red pairing button when this routine
    first attempts to connect to it. Every time. I have been unable to cause it to pair properly without this action.
    '''
    maximum_connect_retry_count = 5
    '''Number of times to retry connecting'''

    minimum_active_mass = 3
    '''Any detected mass less than this is ignored, such as the weight of a single foot resting atop on a bent knee'''
    minimum_lean_ratio_f = 1.3
    minimum_lean_ratio_b = 2.7
    minimum_lean_ratio_l = 1.7
    minimum_lean_ratio_r = 1.7

    # used to detect only one foot or manual pressing
    maximum_lean_ratio = 10

    def __init__(self,bluetooth_address):
        '''Construction of the object, fill in default values to help us later'''
        self._bluetooth_address = bluetooth_address
        self._calibration = []
        self._calibration_requested = False
        self._device_led = False
        self._button_depressed = False
        for i in xrange(3):
            self._calibration.append([])
            for j in xrange(4):
                self._calibration[i].append(10000)  # high dummy value so events with it don't register

        self._last_event = WiiFitBoardEvent(0, 0, 0, 0, False, False)
        self._receive_socket = None
        self._control_socket = None
        self._last_board_event = None
        self._last_motion_data = None
        self._board_event_lock = threading.Lock()
        self.__set_status(WIIFIT_STATUS_DISCONNECTED)
        self._connection_success = False
        self.controller_name = "Wii Fit Board"

    @property
    def name(self):
        '''Override parent property such that the BT address is also returned'''
        return self.controller_name + ' ' + self._bluetooth_address

    def connect(self):
        '''Attempt to connect to the board'''

        if self._bluetooth_address is None:
            #Error handling
            raise WiiFitBoardCommunicationError("Bluetooth MAC Address not set")

        self.__set_status(WIIFIT_STATUS_CONNECTING)

        # Attempt to connect to Wii balance board over bluetooth, failure is non-fatal
        connection_attempt_count = 0
        connection_retry = False

        while connection_attempt_count < WiiFitBoard.maximum_connect_retry_count:
            #Warn the user to press the button
            logging.warning("Press Red Sync Button in Battery Compartment of Balance Board...")
            time.sleep(1)
            try:
                connection_attempt_count += 1
                self._receive_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
                self._control_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
                time.sleep(1)
                self._receive_socket.connect((self._bluetooth_address, 0x13))
                self._control_socket.connect((self._bluetooth_address, 0x11))
                time.sleep(1)

                if self._receive_socket and self._control_socket:
                    logging.debug(self.name + ' sockets created')
                    self.__calibrate()
                    logging.debug(self.name + ' calibration received')
                    useExt = ["00", WII_COMMAND_REGISTER, "04", "A4", "00", "40", "00"]
                    self.__send_command(useExt)
                    logging.debug(self.name + ' use ext port sent')
                    self.__set_reporting_type()
                    logging.debug(self.name + ' continuous reporting sent')
                    self._connection_success = True
                    connection_retry = False
                    self.__set_button_led(True)
                    logging.debug(self.name + ' set led sent')

            except Exception as ex:
                #Report errors
                logging.debug("Error communicating with balance board, trying again... (" + str(connection_attempt_count) + "/" + str(WiiFitBoard.maximum_connect_retry_count) + ")")
                logging.debug(ex)
                self._receive_socket = None
                self._control_socket = None
                time.sleep(2)
                connection_retry = True
                pass

            if not connection_retry:
                # exit loop
                break

            time.sleep(2)

        logging.debug('Connection success')
        self.__set_status(WIIFIT_STATUS_CONNECTED)

        # end loop

        if connection_retry:
            #Report and fail gracefully
            self.__set_status(WIIFIT_STATUS_DISCONNECTED)
            raise WiiFitBoardNotConnected('Bluetooth connection failed.', self._bluetooth_address)

        #Report success
        logging.debug("Balance board paired")


    def update(self):
        '''Update data from WFB'''
        if self.status != WIIFIT_STATUS_CONNECTED:
            raise WiiFitBoardNotConnected()

        try:
            board_event = self.__receive()
        except Exception as ex:
            logging.debug(ex)
            return

        with self._board_event_lock:

            if not board_event:
                return

            self._last_board_event = board_event


    def get_motion(self, motion_type):
        '''Get desired motion information based on last known WFB state. Not all motion types are supported'''
        if self.status != WIIFIT_STATUS_CONNECTED:
            raise WiiFitBoardNotConnected()

        if not isinstance(self._last_board_event,WiiFitBoardEvent):
            return ObjectMotion(self.name, motion_type, DDIR_STATIONARY)


        if motion_type == MTYPE_TANKSTEER:
            raise BadMotionTypeException('WiiBalanceBoard cannot produce MTYPE_TANKSTEER')

        with self._board_event_lock:

            board_event = self._last_board_event
            direction = DDIR_STATIONARY

            # No one on the Balance Board yet
            if not((board_event.topLeft < WiiFitBoard.minimum_active_mass)
                   and (board_event.topRight < WiiFitBoard.minimum_active_mass)
                   and (board_event.bottomLeft < WiiFitBoard.minimum_active_mass)
                   and (board_event.bottomRight < WiiFitBoard.minimum_active_mass)):

                logging.debug("TL: " + str(board_event.topLeft) + " TR: " + str(board_event.topRight) + " BL: " + str(board_event.bottomLeft) + " BR: " + str(board_event.bottomRight))

                rightside = float(board_event.topRight + board_event.bottomRight+1)
                leftside = float(board_event.topLeft + board_event.bottomLeft+1)
                frontside = float(board_event.topLeft + board_event.topRight+1)
                backside = float(board_event.bottomLeft + board_event.bottomRight+1)

                logging.debug('RS: ' + str(rightside) + ' LS: ' + str(leftside) + ' FS: ' + str(frontside) + ' BS: ' + str(backside))

                biasleft = False
                biasright = False
                biasahead = False
                biasreverse = False

                #Work out the users intention based on board state

                if rightside > leftside:
                    over = float(rightside / leftside)
                    logging.debug('r>l -> ' + str(over))
                    if (over < WiiFitBoard.maximum_lean_ratio) and (over > WiiFitBoard.minimum_lean_ratio_r):
                        biasright = True

                else:
                    over = float(leftside / rightside)
                    logging.debug('l>r -> ' + str(over))
                    if (over < WiiFitBoard.maximum_lean_ratio) and (over > WiiFitBoard.minimum_lean_ratio_l):
                        biasleft = True
                if frontside > backside:
                    over = float(frontside / backside)
                    logging.debug('f>b -> ' + str(over))
                    if (over < WiiFitBoard.maximum_lean_ratio) and (over > WiiFitBoard.minimum_lean_ratio_f):
                        biasahead = True
                else:
                    over = float(backside / frontside)
                    logging.debug('b>f -> ' + str(over))
                    if (over < WiiFitBoard.maximum_lean_ratio) and (over > WiiFitBoard.minimum_lean_ratio_b):
                        biasreverse = True

                if (not biasleft) and (not biasright) and (not biasahead) and (not biasreverse):
                    # stationary
                    direction = DDIR_STATIONARY
                if biasahead:
                    direction = DDIR_AHEAD
                if biasreverse:
                    direction = DDIR_REVERSE
                if biasleft:
                    direction = DDIR_LEFT
                    if biasahead:
                        direction = DDIR_AHEADLEFT
                    if biasreverse:
                        direction = DDIR_REVERSELEFT
                if biasright:
                    direction = DDIR_RIGHT
                    if biasahead:
                        direction = DDIR_AHEADRIGHT
                    if biasreverse:
                        direction = DDIR_REVERSERIGHT

                logging.debug(direction)

            return ObjectMotion(self.name, MTYPE_CARSTEER, direction,0.8)

                
    def __receive(self):
        '''Private method to cause data reception'''
        if self.status != WIIFIT_STATUS_CONNECTED:
            raise WiiFitBoardNotConnected()

        data = self._receive_socket.recv(23)
        intype = int(data.encode("hex")[2:4])
        if intype == WII_INPUT_STATUS:
            # TODO: Status input received. It just tells us battery life really
            self.__set_reporting_type()
        elif intype == WII_INPUT_READ_DATA:
            if self._calibration_requested:
                packetLength = (int(str(data[4]).encode("hex"), 16) / 16 + 1)
                self.__parse_calibration__response(data[7:(7 + packetLength)])

                if packetLength < 16:
                    self._calibration_requested = False
        elif intype == WII_EXTENSION_8BYTES:
            # self.processor.mass(self.createBoardEvent(data[2:12]))
            return self.__create_board_event(data[2:12])

        # self.status = "Disconnected"
        # self.disconnect()

    def disconnect(self):
        '''Disconnect gracefully if possible from the WFB'''
        if self.status != WIIFIT_STATUS_CONNECTED:
            raise WiiFitBoardNotConnected()

        self.__set_status(WIIFIT_STATUS_DISCONNECTING)
        try:
            self._receive_socket.close()
            self._receive_socket = None
        except:
            pass

        try:
            self._control_socket.close()
            self._control_socket = None
        except:
            pass

        self.__set_status(WIIFIT_STATUS_DISCONNECTED)

    def discover(self):
        '''Attempt automatic discover of WFB. UNTESTED'''
        address = None
        discovered_bluetooth_devices = bluetooth.discover_devices(duration=6, lookup_names=True)
        for bluetoothdevice in discovered_bluetooth_devices:
            if bluetoothdevice[1] == WIIFIT_BLUETOOTH_NAME:
                address = bluetoothdevice[0]
        return address

    def __create_board_event(self, bytes):
        '''Used to create an instance of the WFB event object with the raw data provided'''
        button_bytes = bytes[0:2]
        bytes = bytes[2:12]
        button_pressed = False
        button_released = False

        state = (int(button_bytes[0].encode("hex"), 16) << 8) | int(button_bytes[1].encode("hex"), 16)
        if state == WII_BUTTON_DOWN_MASK:
            button_pressed = True
            if not self._button_depressed:
                self._button_depressed = True

        if not button_pressed:
            if self._last_event.buttonPressed:
                button_released = True
                self._button_depressed = False
#                print "Button released"

        rawTR = (int(bytes[0].encode("hex"), 16) << 8) + int(bytes[1].encode("hex"), 16)
        rawBR = (int(bytes[2].encode("hex"), 16) << 8) + int(bytes[3].encode("hex"), 16)
        rawTL = (int(bytes[4].encode("hex"), 16) << 8) + int(bytes[5].encode("hex"), 16)
        rawBL = (int(bytes[6].encode("hex"), 16) << 8) + int(bytes[7].encode("hex"), 16)

        topLeft = self.__calc_mass(rawTL, WIIFIT_TOP_LEFT)
        topRight = self.__calc_mass(rawTR, WIIFIT_TOP_RIGHT)
        bottomLeft = self.__calc_mass(rawBL, WIIFIT_BOTTOM_LEFT)
        bottomRight = self.__calc_mass(rawBR, WIIFIT_BOTTOM_RIGHT)
        boardEvent = WiiFitBoardEvent(topLeft, topRight, bottomLeft, bottomRight, button_pressed, button_released)
        return boardEvent

    def __calc_mass(self, raw, pos):
        '''Form and approximation of the mass present on the WFB taking calibration data into account'''
        val = 0.0
        # calibration[0] is calibration values for 0kg
        # calibration[1] is calibration values for 17kg
        # calibration[2] is calibration values for 34kg
        try:
            if raw < self._calibration[0][pos]:
                return val
            elif raw < self._calibration[1][pos]:
                val = 17 * ((raw - self._calibration[0][pos]) / float((self._calibration[1][pos] - self._calibration[0][pos])))
            elif raw > self._calibration[1][pos]:
                val = 17 + 17 * ((raw - self._calibration[1][pos]) / float((self._calibration[2][pos] - self._calibration[1][pos])))
        except Exception as ex:
            logging.debug(self.name + ' -> ' + ex.message)
            pass

        return val

    def __get_button_led(self):
        '''Is the blue LED on or off'''
        return self._device_led

    def __parse_calibration__response(self, bytes):
        index = 0
        if len(bytes) == 16:
            for i in xrange(2):
                for j in xrange(4):
                    self._calibration[i][j] = (int(bytes[index].encode("hex"), 16) << 8) + int(bytes[index + 1].encode("hex"), 16)
                    index += 2
        elif len(bytes) < 16:
            for i in xrange(4):
                self._calibration[2][i] = (int(bytes[index].encode("hex"), 16) << 8) + int(bytes[index + 1].encode("hex"), 16)
                index += 2

    # Send <data> to the Wiiboard
    # <data> should be an array of strings, each string representing a single hex byte
    def __send_command(self, data):
        '''Send raw data to the WFB over Bluetooth'''
        # this gets used during connection stage for requesting calibration data and setting the led.
        if (self.status == WIIFIT_STATUS_DISCONNECTED) or (self.status == WIIFIT_STATUS_DISCONNECTING):
            raise WiiFitBoardNotConnected()

        data[0] = "52"

        senddata = ""
        for byte in data:
            byte = str(byte)
            senddata += byte.decode("hex")

        self._control_socket.send(senddata)

    def __set_button_led(self, light):
        '''Set the state of the blue LED on the WFB'''
        if light:
            val = "10"
        else:
            val = "00"

        message = ["00", WII_COMMAND_LIGHT, val]
        self.__send_command(message)
        self._device_led = light

    def __calibrate(self):
        '''This method is unreliable'''
        message = ["00", WII_COMMAND_READ_REGISTER, "04", "A4", "00", "24", "00", "18"]
        self.__send_command(message)
        self._calibration_requested = True

    def __set_reporting_type(self):
        bytearr = ["00", WII_COMMAND_REPORTING, WII_CONTINUOUS_REPORTING, WII_EXTENSION_8BYTES]
        self.__send_command(bytearr)

    def __wait(self, millis):
        time.sleep(millis / 1000.0)

    def __set_status(self, status):
        '''Private method used for status reports'''
        self.__status = status

    @property
    def status(self):
        '''Get status report'''
        return self.__status
