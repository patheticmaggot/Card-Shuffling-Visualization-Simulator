import pygame
import utilities


class Slider:
    def __init__(self, posX, posY, width, height, name):
        self.slider = pygame.Rect(posX, posY, width, height)
        self.handle = pygame.Rect(posX, (posY - height * 0.04), height, (height * 1.16))
        self.minX = self.slider.x
        self.maxX = self.slider.x + self.slider.width - self.handle.width
        self.value = 0.0
        self.name = name
        
    def draw(self, screen, color1, color2):
        pygame.draw.rect(screen, color1, self.slider)
        pygame.draw.rect(screen, color2, self.handle)
        utilities.Draw_text(self.name, utilities.FONT, utilities.BLACK, (self.slider.x + 5), self.slider.y)
        utilities.Draw_text(str(int(self.value * 100)) + "%", utilities.FONT, utilities.BLACK, (self.slider.x + self.slider.width), self.slider.y)

sliders = {
    "accuracy": Slider((utilities.settingsTabX + 10), utilities.settingsTabHeight - 280, 200, 25, "accuracy"),
    "offset": Slider((utilities.settingsTabX + 10), utilities.settingsTabHeight - 240, 200, 25, "offset"),
}
