import pygame
import utilities as uti

# A class for the queue markers
class Marker:
    def __init__(self, name, color, posX, posY, width, height):
        self.marker = pygame.Rect(posX, posY, width, height)
        self.name = name
        self.color = color
        self.posX = posX
        self.posY = posY
        self.width = width
        self.height = height
    
    # Draw maker
    def Draw(self, screen, color, name):
        pygame.draw.rect(screen, color, self.marker)
        uti.Draw_text(name[0], uti.FONT, uti.BLACK, self.posX, self.posY)

# Marker storage    
markers = []