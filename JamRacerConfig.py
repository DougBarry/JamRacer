from array import array

# debugging flag
#debugging = True

class JamRacerConfig:
    '''Configuration of various inputs and outputs and which are enabled on start'''
    WiiBoards = ['58:BD:A3:0E:50:65']
    iRacers = ['00:12:05:09:96:64','00:12:05:09:92:72']
    Spheros = ['68:86:e7:00:dc:72']
    LegoNXTs = ['00:16:53:0E:92:16','00:16:53:07:20:F1','00:16:53:0D:6E:2D','00:16:53:0A:56:51']

    controller_joystick_enabled = True
    controller_wiiboard_enabled = True

    actor_sphero_enabled = False
    actor_iracer_enabled = True
    actor_legonxt_enabled = True

