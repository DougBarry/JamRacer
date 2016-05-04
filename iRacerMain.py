#!/usr/bin/env python

"""Simple user interface code to control Arexx Dagu i-racer using Raspberry Pi and Wii Balance Board for RaspberryJam at University of Greenwich Medway campus

Usage:
  $ python iracer_balance_board.py

"""

__author__ = 'bd59@gre.ac.uk (Doug Barry)'

import time
import pygame
from pygame.locals import *
from iRacerConfig import *
from InputWiiFitBoard import *
from OutputSphero import *
from OutputiRacer import *
from ObjectMotion import *
from InputXBox360Joypad import *
from Helpers import *
from iRacerDisplay import *
import logging
from iRacerJoystickHandler import *
from InputTrustUSBGamepad import *
from InputPyGameGenericJoystick import *
from OutputLegoMindstormsNXT import *

global app

class JamRacerApp(object):

    def __init__(self):
        self._mydisplay = None
        self._configuration = None
        self._joystick_handler = None

        self._controllers_wiifitboard = []
        self._controllers_joystick = []
        self._actors_sphero = []
        self._actors_iracer = []
        self._actors_legonxt = []
        self._actor_controller_connection = []

        self._time_since_robot_update = 0

    # Main method
    def main(self):
        logging.basicConfig(filename='iracer.log',level=logging.DEBUG)
        logging.info("Program startup")

        pygame.init()

        logging.info("Getting configuration")
        self._configuration = iRacerConfig.iRacerConfig()

        logging.info("Starting PyGame")
        self._mydisplay = iRacerDisplay()
        self._mydisplay.Setup()
        self._mydisplay.Update()

        logging.info("Initialise Controllers")
        # Prep/connect controllers/actors
        self.__initialise_controller_joystick()
        self.__initialise_controller_wiiboard()

        logging.info("Initialise Actors")
        self.__initialise_actor_sphero()
        self.__initialise_actor_iracer()
        self.__initialise_actor_legonxt()

        logging.info("Connecting actors to controllers")

        wiifitboard_num = 0
        joystick_num = 0

        logging.debug("Configuring iRacers")
        for iracer in self._actors_iracer:
            controller = None
            if len(self._controllers_wiifitboard) > 0:
                if wiifitboard_num < len(self._controllers_wiifitboard):
                    if self._controllers_wiifitboard[wiifitboard_num] is not None:
                        controller = self._controllers_wiifitboard[wiifitboard_num]
                        wiifitboard_num += 1
            if controller is None:
                if joystick_num < len(self._controllers_joystick):
                    if self._controllers_joystick[joystick_num] is not None:
                        controller = self._controllers_joystick[joystick_num]
                        joystick_num += 1
            if controller is not None:
                acc = ActorControllerConnection(iracer,controller,MTYPE_CARSTEER)
                self.__add_actor_controller_connection(acc)

        logging.debug("Configuring Spheros")
        for sphero in self._actors_sphero:
            controller = None
            if controller is None:
                if joystick_num < len(self._controllers_joystick):
                    if self._controllers_joystick[joystick_num] is not None:
                        controller = self._controllers_joystick[joystick_num]
                        joystick_num += 1
            if controller is not None:
                acc = ActorControllerConnection(sphero,controller,MTYPE_COMPASS)
                self.__add_actor_controller_connection(acc)

        logging.debug("Configuring LegoNXTs")
        for legonxt in self._actors_legonxt:
            controller = None
            if len(self._controllers_wiifitboard) > 0:
                if wiifitboard_num < len(self._controllers_wiifitboard):
                    if self._controllers_wiifitboard[wiifitboard_num] is not None:
                        controller = self._controllers_wiifitboard[wiifitboard_num]
                        wiifitboard_num += 1
            if controller is None:
                if joystick_num < len(self._controllers_joystick):
                    if self._controllers_joystick[joystick_num] is not None:
                        controller = self._controllers_joystick[joystick_num]
                        joystick_num += 1
            if controller is not None:
                acc = ActorControllerConnection(legonxt,controller,MTYPE_TANKSTEER)
                self.__add_actor_controller_connection(acc)

        logging.debug("Starting direct control mode")

        self._time_since_robot_update = current_milli_time()

        while True:

            self.__update_controller_wiifitboard()

            self.g_keys = pygame.event.get()

            for event in self.g_keys:
                if (event.type == KEYDOWN):
                    if (event.key == K_ESCAPE):
                        self.quit()
                        return

                elif (event.type == QUIT):
                    self.quit()
                    return

            # wiifit board has to be driven really fast to keep up with the data
            self.__update_controller_wiifitboard()


            if self._time_since_robot_update < (current_milli_time() - 100):
                self.__update_controller_joystick()

                for acc in self._actor_controller_connection:
                    motion = acc.controller.get_motion(acc.motion_type)
                    # logging.debug("Robot motion: motion_type=" + str(acc.motion_type) +" controller=" + acc.controller.name +" direction=" + str(motion.direction) + " speed=" + str(motion.speed))
                    acc.actor.output_motion(motion)

                self._mydisplay.Clear()
                self._mydisplay.Update()
                self._time_since_robot_update = current_milli_time()


        # we are leaving the program
        if self._configuration.actor_sphero_enabled:
            for sphero in self._actors_sphero:
                sphero.stop()

        if self._configuration.actor_iracer_enabled:
            for iracer in self._actors_iracer:
                iracer.stop()

    # end main
    def quit(self,message = ''):
        sys.exit(message)


    def __initialise_controller_joystick(self):
        if self._configuration.controller_joystick_enabled:
            try:
                self._joystick_handler = iRacerJoystickHandler()
                self._controllers_joystick = self._joystick_handler.joysticks
            except Exception as ex:
                self.controller_joystick_enabled = False
                logging.debug("No joysticks initialised")
                logging.debug(ex)
                pass
            else:
                self._configuration.controller_joystick_enabled = False


    def __initialise_controller_wiiboard(self):
        if self._configuration.controller_wiiboard_enabled:
            for bluetooth_address in self._configuration.WiiBoards:
                logging.info('Attempting to start Wii Fit Board controller with Bluetooth MAC Address %s' % bluetooth_address)
                try:
                    wiiboard = WiiFitBoard(bluetooth_address)
                    wiiboard.connect()
                    self._controllers_wiifitboard.append(wiiboard)
                except Exception as ex:
                    logging.info('Wii Fit Board connection failed to Bluetooth MAC Address %s' % bluetooth_address)
                    logging.debug(ex)
                    pass
            if len(self._controllers_wiifitboard) == 0:
                logging.info("Wii Fit Board controllers disabled")
                self.controller_wiiboard_enabled = False


    def __initialise_actor_sphero(self):
        if self._configuration.actor_sphero_enabled:
            for bluetooth_address in self._configuration.Spheros:
                logging.info('Attempting to start Sphero robot with Bluetooth MAC Address %s' % bluetooth_address)
                try:
                    sphero = Sphero(bluetooth_address)
                    sphero.connect()
                    sphero.set_rgb(SpheroColour(0,64,0))
                    self._actors_sphero.append(sphero)
                except Exception as eargs:
                    logging.info('Sphero connection failed to Bluetooth MAC Address %s' % bluetooth_address)
                    pass
            if len(self._actors_sphero) == 0:
                logging.info("Sphero actors disabled")
                self._configuration.actor_sphero_enabled = False

    def __initialise_actor_iracer(self):
        if self._configuration.actor_iracer_enabled:
            for bluetooth_address in self._configuration.iRacers:
                logging.info('Attempting to start iRacer robot with Bluetooth MAC Address %s' % bluetooth_address)
                try:
                    iracer = iRacer(bluetooth_address)
                    iracer.connect()
                    self._actors_iracer.append(iracer)
                except Exception as eargs:
                    logging.info('iRacer connection failed to Bluetooth MAC Address %s' % bluetooth_address)
                    logging.debug(eargs)
                    pass
            if len(self._actors_iracer) == 0:
                logging.info("iRacer actors disabled")
                self._configuration.actor_iracer_enabled = False

    def __initialise_actor_legonxt(self):
        if self._configuration.actor_legonxt_enabled:
            for bluetooth_address in self._configuration.LegoNXTs:
                logging.debug('Attempting to start LegoNXT robot with Bluetooth MAC Address %s' % bluetooth_address)
                try:
                    legonxt = LegoNXT(bluetooth_address)
                    legonxt.connect(MTYPE_CARSTEER)
                    legonxt.test_motors_quick()
                    self._actors_legonxt.append(legonxt)
                except Exception as ex:
                    logging.debug('LegoNXT connection failed to Bluetooth MAC Address %s' % bluetooth_address)
                    logging.debug(ex)
                    pass
            if len(self._actors_legonxt) == 0:
                logging.info('LegoNXT actors disabled')
                self._configuration.actor_legonxt_enabled = False

    def __update_controller_wiifitboard(self):
        if self._configuration.controller_wiiboard_enabled:
            for wiifitboard in self._controllers_wiifitboard:
                wiifitboard.update()

    def __update_controller_joystick(self):
        if self._configuration.controller_joystick_enabled:

            for joystick in self._controllers_joystick:
                joystick.update()

    def __add_actor_controller_connection(self, actor_controller_connection):
        logging.info("Adding actor<-controller connection. A:" + actor_controller_connection.actor.name + " C:" + actor_controller_connection.controller.name)
        self._actor_controller_connection.append(actor_controller_connection)


class ActorControllerConnection(object):
    def __init__(self, actor, controller, motion_type):
        self._actor = actor
        self._controller = controller
        self._motion_type = motion_type

    @property
    def actor(self):
        return self._actor

    @property
    def controller(self):
        return self._controller

    @property
    def motion_type(self):
        return self._motion_type



app = JamRacerApp()
app.main()
