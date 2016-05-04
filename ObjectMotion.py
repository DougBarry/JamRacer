import math

DDIR_AHEAD=0
DDIR_AHEADLEFT=315
DDIR_LEFT=270
DDIR_REVERSELEFT=225
DDIR_REVERSE=180
DDIR_REVERSERIGHT=135
DDIR_RIGHT=90
DDIR_AHEADRIGHT=45
DDIR_STATIONARY=-1

MTYPE_UNDEFINED = -1
MTYPE_TANKSTEER = 3
MTYPE_COMPASS = 2
MTYPE_CARSTEER = 1


class BadMotionTypeException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)    

        
class ObjectMotion(object):
    '''Class used to define and describe how an object can or should move'''
    
    def __init__(self,sourceType,motionType,motionDirection,motionSpeed = -1):
        self.sType = sourceType
        self.mType = motionType
        self.mDirection = motionDirection
        self.mSpeed = motionSpeed
        
    @property
    def source_type(self):
        return self.sType
    
    @property
    def motion_type(self):
        return self.mType
        
    @property
    def direction(self):
        return self.mDirection
        
    @property
    def speed(self):
        return self.mSpeed

        
class AnalogMotionTranslator(object):
    """
    Defines 2 16 bit signed integers, where the desired speed is the magnitude, and the resultant vector defines the
    direction. This can be used for analogue actors and digital actors (with rounding and approximation of intention)
    Include appreciation of deadzones.

        ypos -
    xpos -.......+
             +
    """

    def __init__(self,deadzoneXneg, deadzoneXpos, deadzoneYneg, deadzoneYpos):
        self.deadzoneXneg = deadzoneXneg
        self.deadzoneXpos = deadzoneXpos
        self.deadzoneYneg = deadzoneYneg
        self.deadzoneYpos = deadzoneYpos

    def get_direction(self, motion_type, bias1, bias2):
        if motion_type == MTYPE_CARSTEER:
            motion_direction = self.get_digital_direction(bias1, bias2)
        elif motion_type == MTYPE_TANKSTEER:
            motion_direction0 = self.get_digital_direction(0, bias1)
            motion_direction1 = self.get_digital_direction(0, bias2)
            if motion_direction0 == motion_direction1:
                motion_direction = motion_direction0
            elif (motion_direction0 == DDIR_AHEAD) and (motion_direction1 == DDIR_REVERSE):
                motion_direction =  DDIR_RIGHT
            elif (motion_direction1 == DDIR_AHEAD) and (motion_direction0 == DDIR_REVERSE):
                motion_direction =  DDIR_LEFT
            elif (motion_direction0 == DDIR_STATIONARY) and (motion_direction1 == DDIR_AHEAD):
                motion_direction =  DDIR_AHEADLEFT
            elif (motion_direction1 == DDIR_STATIONARY) and (motion_direction0 == DDIR_AHEAD):
                motion_direction =  DDIR_AHEADRIGHT
            elif (motion_direction0 == DDIR_STATIONARY) and (motion_direction1 == DDIR_REVERSE):
                motion_direction =  DDIR_REVERSELEFT
            elif (motion_direction1 == DDIR_STATIONARY) and (motion_direction0 == DDIR_REVERSE):
                motion_direction =  DDIR_REVERSERIGHT
            else:
                motion_direction =  DDIR_STATIONARY
        elif motion_type == MTYPE_COMPASS:
            biasleft = False
            biasright = False
            biasahead = False
            biasreverse = False
            if bias1 < self.deadzoneXneg:
                biasleft = True
            elif bias1 > self.deadzoneXpos:
                biasright = True
            if bias2 < self.deadzoneYneg:
                biasahead = True
            elif bias2 > self.deadzoneYpos:
                biasreverse = True
            if (not biasleft) and (not biasright) and (not biasahead) and (not biasreverse):
                # stationary
                motion_direction = DDIR_STATIONARY
            else:
                motion_direction = (180-(round(math.degrees(math.atan2(bias1,bias2)))))
        else:
            motion_direction = DDIR_STATIONARY
            
        return motion_direction
    
    def get_digital_direction(self, xbias, ybias):
        biasleft = False
        biasright = False
        biasahead = False
        biasreverse = False
        if xbias < self.deadzoneXneg:
            biasleft = True
        elif xbias > self.deadzoneXpos:
            biasright = True
        if ybias < self.deadzoneYneg:
            biasahead = True
        elif ybias > self.deadzoneYpos:
            biasreverse = True

        direction = DDIR_STATIONARY

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

        return direction

