from array import array

# debugging flag
#debugging = True

#MAC_BT_WII_BALANCEBOARD_1 = "58:BD:A3:0E:50:65"
#MAC_BT_DAGUCAR_1 = "00:12:05:09:96:64"
#MAC_BT_SPHERO_1 = ""
#MAC_BT_PS3_CONTROLLER_1 = ""

class iRacerConfig:
    WiiBoards = ['58:BD:A3:0E:50:65']
    iRacers = ['00:12:05:09:96:64','00:12:05:09:92:72']
    # iracer work ['00:12:05:09:92:72']
    # iracer home ['00:12:05:09:96:64']
    Spheros = ['68:86:e7:00:dc:72']
    LegoNXTs = ['00:16:53:0E:92:16','00:16:53:07:20:F1','00:16:53:0D:6E:2D','00:16:53:0A:56:51']
    #tonys 00:16:53:07:20:F1
    #tonygrip 00:16:53:0A:56:51
    #alis '00:16:53:0D:6E:2D'
    #pats '00:16:53:0E:92:16'
    #nxt home ['00:16:53:07:64:B4']
    LegoEV3s = None

    controller_joystick_enabled = True
    controller_wiiboard_enabled = True

    actor_sphero_enabled = False
    actor_iracer_enabled = True
    actor_legonxt_enabled = True

#    def __init__(self):
#        DaguCars = array('c')
#        DaguCars.append('00:12:05:09:96:64')
#        Spheros = array('c')
#        Spheros.append('68:86:e7:00:dc:72')
#        WiiBoards = array('c')
#        WiiBoards.append('58:BD:A3:0E:50:65')

