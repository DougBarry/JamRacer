import pygame
import sys

class iRacerDisplay:
    # Define some colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    screen=None
    font=None

    def Setup(self):
        self.screen = pygame.display.set_mode((400,300))
        self.font = pygame.font.SysFont("Courier", 20)
        pygame.display.set_caption('Robotics multi in multi out')
        clock = pygame.time.Clock()

    def Draw(self):
        screen.fill(WHITE)
        DrawBorders()
        DrawBot1()
        DrawBot2()
        DrawBot3()
        DrawBot4()
        DrawLog()
        self.update()

    def LogMessage(self, text):
        print(text)

    def Update(self):
        pygame.display.update()
        
    def Clear(self, colour=WHITE):
        self.screen.fill(colour)
        self.Update()