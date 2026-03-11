import pygame
import utilities

# A class for any clickable button 
class Button:
    def __init__(self, posX, posY, width, height, name, values, nameText, valueText):
        self.button = pygame.Rect(posX, posY, width, height)
        self.name = name
        self.values = values
        self.nameText = nameText
        self.valueText = valueText
        
        self.valueIndex = 0
        self.value = self.values[self.valueIndex]
        
    # Changes the buttons value to the next value on the list that is initialized
    def nextValue(self):
        self.valueIndex = (self.valueIndex + 1) % len(self.values)
        self.value = self.values[self.valueIndex]
    
    # Draws the button
    def draw(self, screen, color, textNameX, textNameY, textValuex, textValueY):
        pygame.draw.rect(screen, color, self.button)
        if self.nameText and self.valueText:
            utilities.Draw_text(self.name, utilities.FONT, utilities.BLACK, self.button.x + textNameX, self.button.y + textNameY)
            utilities.Draw_text(str(self.value), utilities.FONT, utilities.BLACK, self.button.x + textValuex, self.button.y + textValueY)
        elif self.nameText and not self.valueText:
            utilities.Draw_text(self.name, utilities.FONT, utilities.BLACK, self.button.x + textNameX, self.button.y + textNameY)
        elif not self.nameText and self.valueText:
            utilities.Draw_text(str(self.value), utilities.FONT, utilities.BLACK, self.button.x + textValuex, self.button.y + textValueY)

# Button storage
buttons = {
    "change view": Button((utilities.settingsTabX + 10), (utilities.settingsTabHeight - 145), 200, 25, "change view", utilities.VIEWS, True, True),
    "assign shuffle": Button((utilities.settingsTabX + 10), (utilities.settingsTabHeight - 95), 200, 25, "assign shuffle", utilities.SHUFFLES, True, True),
    "shuffle": Button((utilities.settingsTabX + 10), (utilities.settingsTabHeight - 60), 110, 50, "shuffle", [False, True], True, False),
    "reset": Button((utilities.settingsTabX + 130), (utilities.settingsTabHeight - 60), 110, 50, "reset", [False, True], True, False),
    "queue": Button((utilities.settingsTabX + 130), (utilities.settingsTabHeight - 190), 25, 25, "queue", [False, True], True, False),
    "remove": Button((utilities.settingsTabX + 190), (utilities.settingsTabHeight - 190), 25, 25, "remove", [False, True], True, False)
}