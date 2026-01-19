import pygame
import random
import string

pygame.init()
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shuffling simulator")

GREY = (135, 129, 128)
DARK_GREY = (59, 56, 55)
sliderNameFont = pygame.font.SysFont("Arial", 20)
sliderValueFont = pygame.font.SysFont("Arial", 20)


settingsTabWidth = 250
settingsTabHeight = SCREEN_HEIGHT
settingsTabX = (SCREEN_WIDTH - settingsTabWidth)
settingsTabY = 0
settingsTab = pygame.Rect(settingsTabX, settingsTabY, settingsTabWidth, settingsTabHeight)

clock = pygame.time.Clock()

deckGenerated = False
deck = []

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
        Draw_text(self.name, sliderNameFont, (0, 0, 0), (self.slider.x + 5), self.slider.y)
        Draw_text(str(int(self.value * 100)) + "%", sliderValueFont, (0, 0, 0), (self.slider.x + self.slider.width), self.slider.y)

class Button:
    def __init__(self, posX, posY, width, height, name, values, nameText, valueText):
        self.button = pygame.Rect(posX, posY, width, height)
        self.name = name
        self.values = values
        self.nameText = nameText
        self.valueText = valueText
        
        self.valueIndex = 0
        self.value = self.values[self.valueIndex]
    
    def nextValue(self):
        self.valueIndex = (self.valueIndex + 1) % len(self.values)
        self.value = self.values[self.valueIndex]
    
    def draw(self, screen, color):
        pygame.draw.rect(screen, color, self.button)
        if self.nameText and self.valueText:
            Draw_text(self.name, sliderValueFont, (0, 0, 0), self.button.x + 5, self.button.y - 25)
            Draw_text(str(self.value), sliderValueFont, (0, 0, 0), self.button.x + 5, self.button.y)
        elif self.nameText and not self.valueText:
            Draw_text(self.name, sliderValueFont, (0, 0, 0), self.button.x + 5, self.button.y)
        elif not self.nameText and self.valueText:
            Draw_text(str(self.value), sliderValueFont, (0, 0, 0), self.button.x + 5, self.button.y)
        

settings = {
    "shuffle": "riffleShuffle",
    "offset": 0.0,
    "accuracy": 0.0,
    "randomness": 0.0,
    "deckSize": 52,
    "inOutRand": "o"
}

shuffles = ["riffleShuffle", "cutDeck", "computer"]

sliders = {
    "accuracy": Slider((settingsTabX + 10), 100, 200, 25, "accuracy"),
    "offset": Slider((settingsTabX + 10), 150, 200, 25, "offset"),
    "randomness": Slider((settingsTabX + 10), 200, 200, 25, "randomness")
}

buttons = {
    "shuffle": Button((settingsTabX + 50), (settingsTabHeight - 75), 75, 50, "shuffle", [False, True], True, False),
    "assignShuffle": Button((settingsTabX + 50), (settingsTabY + 25), 100, 25, "assignShuffle", shuffles, True, True)
}


def Draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    SCREEN.blit(img, (x, y))

def GenDeck(n):
    deck = list(range(n))
    return deck

def DisplayDeck(deck):
    
    n = len(deck)
    
    
    for i, c in enumerate(deck):
        cardWidth = 100
        cardHeight = 30
        buffX = 10
        buffY = 10
        xPos = buffX
        
        if cardHeight * n > SCREEN_HEIGHT:
            cardHeight = SCREEN_HEIGHT // n
        
        if n == 1:
            yPos = (SCREEN_HEIGHT - cardHeight) // 2
            color = 0
        else:
            yPos = SCREEN_HEIGHT - (cardHeight * i) - buffY - cardHeight
            color = int(c * 250 / n)
            
            
        rect = pygame.Rect(xPos, yPos, cardWidth, cardHeight)
        pygame.draw.rect(SCREEN, (color, color, color), rect)
    
    return

def ShuffleWithSettings(deck, settings):
    if settings["shuffle"] == "cutDeck":
        return CutDeck(deck, settings["offset"], settings["randomness"])

    elif settings["shuffle"] == "riffleShuffle":
        return RiffleShuffle(deck, settings["offset"], settings["accuracy"], settings["inOutRand"])

    elif settings["shuffle"] == "computer":
        return ComputerRandomShuffle(deck)

    else:
        print("Unknown shuffle")
        return deck

def ComputerRandomShuffle(deck):
    shuffledDeck = random.sample(deck, len(deck))
    return shuffledDeck

def RiffleShuffle(deck, offset, accuracy, inOutRand):
    n = len(deck)
    
    offset = max(0.0, min(1.0, offset))
    accuracy = max(0.0, min(1.0, accuracy))
    
    cutIndex = int(offset * n)
    
    top = deck[cutIndex:]
    bottom = deck[:cutIndex]
    
    ti = 0  # Top half Index
    bi = 0  # Bottom half Index
    
    if (inOutRand == "i"):
        useTop = True
    elif (inOutRand == "o"):
        useTop = False
    else:
        useTop = random.choice([True, False])
    
    shuffledDeck = []

    while ti < len(top) or bi < len(bottom):

        # Change the deck half if the other is empty
        if useTop and ti >= len(top):
            useTop = False
        elif not useTop and bi >= len(bottom):
            useTop = True

        # Move a card to the shuffled 
        if useTop and ti < len(top):
            shuffledDeck.append(top[ti])
            ti += 1
        elif not useTop and bi < len(bottom):
            shuffledDeck.append(bottom[bi])
            bi += 1

        # Decide whether to change deck half
        if random.random() < accuracy:
            useTop = not useTop
    print(offset)        
    return shuffledDeck

def CutDeck(deck, offset, randomness):
    n = len(deck)
    
    offset = max(0.0, min(1.0, offset))
    randomness = max(0.0, min(1.0, randomness))
    
    targetCut = offset * n
    randomCut = random.randint(1, n - 1)
    
    cutIndex = int((1 - randomness) * targetCut + randomness * randomCut)
    print(cutIndex)
    top = deck[:cutIndex]
    bottom = deck[cutIndex:]
    
    cutDeck = bottom + top
    
    return cutDeck


deck = GenDeck(settings["deckSize"])
deckGenerated = True

running = True
while running:
    """
    controls = input("Do a shuffle(s), Reset the deck(r), Quit(q)")
    
    if (controls == "s"):
        if (not deckGenerated):
            size = int(input("How many cards do you want in your deck?: "))
            deck = GenDeck(size)
            deckGenerated = True
        shuffle = input("Choose a shuffle type. (Cut(c), Riffle Shuffle(r), Computer shuffle(computer))")
        deck = ShuffleWithSettings(deck, shuffle)
    
    elif (controls == "r"):
        size = int(input("How many cards do you want in your deck?: "))
        deck = GenDeck(size)
        deckGenerated = True
    
    elif (controls == "q"):
        running = False
        
    else:
        print("Worng input.")
    """
    clock.tick(60)
    SCREEN.fill((97, 125, 12))
    pygame.draw.rect(SCREEN, (50, 50, 50), settingsTab)
    
    mouse_held = pygame.mouse.get_pressed()
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                if not deckGenerated:
                    deck = GenDeck(settings["deckSize"])
                    deckGenerated = True
                deck = ShuffleWithSettings(deck, settings)

            elif event.key == pygame.K_r:
                deck = GenDeck(settings["deckSize"])
                deckGenerated = True

            elif event.key == pygame.K_q:
                running = False
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for button in buttons.values():
                    if button.button.collidepoint(event.pos):
                        if button.name == "shuffle":
                            if button.value == False:
                                deck = ShuffleWithSettings(deck, settings)
                                button.value = True
                        elif button.name == "assignShuffle":
                            button.nextValue()
                            settings["shuffle"] = button.value
                            print(button.value)
                      
                        
                """           
                if shuffleButton.collidepoint(event.pos):
                    if shuffleButtonValue == False:
                        if not deckGenerated:
                            deck = GenDeck(settings["deckSize"])
                            deckGenerated = True
                        deck = ShuffleWithSettings(deck, settings)
                        shuffleButtonValue = True
                """         
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if buttons["shuffle"].value == True:
                    buttons["shuffle"].value = False
                    buttons["shuffle"].valueIndex = 1
    
    if mouse_held[0]:
        for slider in sliders.values():
            if slider.slider.collidepoint(mouse_x, mouse_y):
                slider.handle.x = max(slider.minX, min(slider.maxX, mouse_x - slider.handle.width // 2))
                slider.value = (slider.handle.x - slider.minX) / (slider.maxX - slider.minX)
                settings[slider.name] = slider.value
    """
    if shuffleButtonValue == False:
        pygame.draw.rect(SCREEN, GREY, shuffleButton)
    else:
        pygame.draw.rect(SCREEN, DARK_GREY, shuffleButton)
    """
    for slider in sliders.values():
        slider.draw(SCREEN, GREY, DARK_GREY)
    
    for button in buttons.values():
        if button.name == "shuffle":
            if button.value == False:
                button.draw(SCREEN, GREY)
            else:
                button.draw(SCREEN, DARK_GREY)
        else:
            button.draw(SCREEN, GREY)
    """
    pygame.draw.rect(SCREEN, GREY, accuracySlider)
    pygame.draw.rect(SCREEN, DARK_GREY, accuracySliderHandle)
    """
    DisplayDeck(deck)
    pygame.display.flip()
    
    
            
pygame.quit()