import pygame
from InputTrustUSBGamepad import *

class iRacerJoystickHandler(object):

    def __init__(self):
        pygame.joystick.init()

        self.joysticks = []

        if pygame.joystick.get_count() > 0:
            # Enumerate joysticks
            logging.debug("Found " + str(pygame.joystick.get_count()) + " input devices")

            for index in range(0, pygame.joystick.get_count()):
                this_joystick = pygame.joystick.Joystick(index)
                this_joystick.init()
                joyname = this_joystick.get_name()
                logging.info("Found input device: " + joyname)
                if 'ragon' in joyname:
                    self.joysticks.append(TrustUSBJoypadController(this_joystick, "Trust USB Gamepad (" + joyname + ")"))
                else:
                    self.joysticks.append(PyGameJoystickController(this_joystick, joyname))
        else:
            raise JoystickNotConnectedException("No joysticks are attached")
