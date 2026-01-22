import pygame
import random

pygame.init()
SCREEN_WIDTH = 1138
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
startDeck = []

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
    
    def draw(self, screen, color, textNameX, textNameY, textValuex, textValueY):
        pygame.draw.rect(screen, color, self.button)
        if self.nameText and self.valueText:
            Draw_text(self.name, sliderValueFont, (0, 0, 0), self.button.x + textNameX, self.button.y + textNameY)
            Draw_text(str(self.value), sliderValueFont, (0, 0, 0), self.button.x + textValuex, self.button.y + textValueY)
        elif self.nameText and not self.valueText:
            Draw_text(self.name, sliderValueFont, (0, 0, 0), self.button.x + textNameX, self.button.y + textNameY)
        elif not self.nameText and self.valueText:
            Draw_text(str(self.value), sliderValueFont, (0, 0, 0), self.button.x + textValuex, self.button.y + textValueY)
        

settings = {
    "shuffle": "riffleShuffle",
    "offset": 0.0,
    "accuracy": 0.0,
    "randomness": 0.0,
    "deckSize": 52,
    "inOutRand": "o"
}

shuffles = ["riffleShuffle", "cutDeck", "computer", "reverse"]

sliders = {
    "accuracy": Slider((settingsTabX + 10), 100, 200, 25, "accuracy"),
    "offset": Slider((settingsTabX + 10), 150, 200, 25, "offset"),
    #"randomness": Slider((settingsTabX + 10), 200, 200, 25, "randomness")
}

buttons = {
    "shuffle": Button((settingsTabX + 10), (settingsTabHeight - 75), 75, 50, "shuffle", [False, True], True, False),
    "assignShuffle": Button((settingsTabX + 10), (settingsTabY + 25), 100, 25, "assignShuffle", shuffles, True, True),
    "resetDeck": Button((settingsTabX + 150), (settingsTabY + 25), 25, 25, "resetDeck", [False, True], True, False)
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
        return CutDeck(deck, settings["offset"], settings["accuracy"])

    elif settings["shuffle"] == "riffleShuffle":
        return RiffleShuffle(deck, settings["offset"], settings["accuracy"], settings["inOutRand"])

    elif settings["shuffle"] == "computer":
        return ComputerRandomShuffle(deck)
    elif settings["shuffle"] == "reverse":
        return ReverseDeck(deck)
    else:
        print("Unknown shuffle")
        return deck

def AnalyzeRandomness(shuffledDeck, initialDeck):

    absolutDistanceScore = AbsolutDistanceScore(shuffledDeck, initialDeck)
    orderScore = OrderScore(shuffledDeck, initialDeck)
    relativeDistanceScore = RelativeDistanceScore(shuffledDeck, initialDeck)
    print("0=bad 1=good")
    print("absolute distance score: ", absolutDistanceScore)
    print("order score: ", orderScore)
    print("relative distance score: ", relativeDistanceScore)
    
    return

# How close the shuffled card is to 1/3 of the distance away from original position (the ideal distance for randomness).
# 1 = 1/3 away on average, 0 = exact same positions. maximum distance is achieved by reversing cards.
def AbsolutDistanceScore(shuffledDeck, initialDeck):
    n = len(initialDeck)
    
    position = {card: i for i, card in enumerate(shuffledDeck)}
    
    totalDistance = 0
    
    for i, card in enumerate(initialDeck):
        totalDistance += abs(i - position[card])
        
    meanDistance = totalDistance / n
    expectedIdeal = n / 3
    absolutDistanceScore = 1 - abs(meanDistance - expectedIdeal) / expectedIdeal
    
    return absolutDistanceScore

def RelativeDistanceScore(shuffledDeck, initialDeck, k=6):
    n = len(initialDeck)
    position = {card: i for i, card in enumerate(shuffledDeck)}

    total = 0
    weightSum = 0

    for i, card in enumerate(initialDeck):
        for d in range(1, k + 1):
            for j in (i - d, i + d):
                if 0 <= j < n:
                    weight = 1 / d
                    total += weight * abs(abs(position[card] - position[initialDeck[j]]) - d)
                    weightSum += weight

    meanRelativeDistance = total / weightSum
    expectedIdeal = n / 3

    relativeDistanceScore = 1 - abs(meanRelativeDistance - expectedIdeal) / expectedIdeal
    #relativeDistanceScore = min(1.0, relativeDistanceScore)
    return relativeDistanceScore

def OrderScore(shuffledDeck, initialDeck):
    n = len(initialDeck)
    position = {card: i for i, card in enumerate(shuffledDeck)}

    preserved = 0
    totalPairs = n * (n - 1) // 2

    for i in range(n):
        for j in range(i + 1, n):
            if position[initialDeck[i]] < position[initialDeck[j]]:
                preserved += 1

    fraction = preserved / totalPairs
    expectedIdeal = 1/2
    orderScore = 1 - abs(fraction - expectedIdeal) / expectedIdeal
    
    return orderScore

def ComputerRandomShuffle(deck):
    shuffledDeck = random.sample(deck, len(deck))
    return shuffledDeck

def ReverseDeck(deck):
    reversedDeck = deck[::-1]
    return reversedDeck

# Offset: 0.5 = deck split in 2 equal halves, Accuracy: 0.0 = deck cut point completly random 
# and one half will go as a whole first then the other as  whole, 1.0 = deck cut point is exact 
# and the halves will deposit exactly one card one after the other
def RiffleShuffle(deck, offset, accuracy, inOutRand):
    n = len(deck)
    
    offset = max(0.0, min(1.0, offset))
    accuracy = max(0.0, min(1.0, accuracy))
    
    # Make the accuracy of the cut index to change between 90-100 accuracy since since the cut is ment to be done exactly at the middle
    cutIndex = CutIndex(n, offset, (0.90 + 0.10 * accuracy))
    
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
    cardsSinceSwitch = 0
    
    while ti < len(top) or bi < len(bottom):

        # Change the deck half if the other is empty
        if useTop and ti >= len(top):
            useTop = False
            cardsSinceSwitch = 0
        elif not useTop and bi >= len(bottom):
            useTop = True
            cardsSinceSwitch = 0

        # Shuffle a card 
        if useTop and ti < len(top):
            shuffledDeck.append(top[ti])
            ti += 1
        elif not useTop and bi < len(bottom):
            shuffledDeck.append(bottom[bi])
            bi += 1
        
        decay_rate = 0.6
        base = 1 - decay_rate * accuracy
        k = 4   # Changes the shape of the curve that decides how low the switch_chance starts with 0 cards since switch
        s = 0.1 # Multiplies the "0 cards since switch" swich_chancees starting chance.
        startAccuracy = accuracy * s + (accuracy ** k) * (1 - s)
        switch_chance = accuracy * (1 - (1 - startAccuracy) * (base ** cardsSinceSwitch))
        
        # Decide whether to change deck half
        if random.random() < switch_chance:
            useTop = not useTop
            cardsSinceSwitch = 0
        else:
            cardsSinceSwitch += 1
                
    print("Offset: " + str(offset))        
    return shuffledDeck

# Offset: 0.5 = deck split in 2 equal halves, Accuracy will decrease radially from the offset 
# point from 1 untill completly random at 0
def CutDeck(deck, offset, accuracy):
    n = len(deck)
    
    offset = max(0.0, min(1.0, offset))
    accuracy = max(0.0, min(1.0, accuracy))
    
    cutIndex = CutIndex(n, offset, accuracy)
    
    print("Cut index: " + str(cutIndex))
    top = deck[:cutIndex]
    bottom = deck[cutIndex:]
    
    cutDeck = bottom + top
    
    return cutDeck

def CutIndex(n, offset, accuracy):
    targetCut = offset * n

    idealRadius = (1 - accuracy) * (n / 2)

    # Initial bounds
    low = targetCut - idealRadius
    high = targetCut + idealRadius

    # Redistribute range to the higher side if hitting the lower bound
    if low < 0:
        high += -low
        low = 0

    # Redistribute range to the lower side if hitting the higher bound
    if high > n:
        low -= (high - n)
        high = n

    low = max(0, low)
    high = min(n, high)

    cutIndex = int(random.uniform(low, high))
    
    return cutIndex

deck = GenDeck(settings["deckSize"])
startDeck = deck
deckGenerated = True

running = True
while running:

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
                    startDeck = deck
                    deckGenerated = True
                deck = ShuffleWithSettings(deck, settings)
                AnalyzeRandomness(deck, startDeck)

            elif event.key == pygame.K_r:
                deck = GenDeck(settings["deckSize"])
                startDeck = deck
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
                                AnalyzeRandomness(deck, startDeck)
                                button.value = True
                        elif button.name == "assignShuffle":
                            button.nextValue()
                            settings["shuffle"] = button.value
                            print("Selected shuffle: " + str(button.value))
                        elif button.name == "resetDeck":
                            if button.value == False:
                                deck = GenDeck(settings["deckSize"])
                                startDeck = deck
                                deckGenerated = True
                                button.value = True
                         
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if buttons["shuffle"].value == True:
                    buttons["shuffle"].value = False
                    buttons["shuffle"].valueIndex = 1
                elif buttons["resetDeck"].value == True:
                    buttons["resetDeck"].value = False
                    buttons["resetDeck"].valueIndex = 1
    
    if mouse_held[0]:
        for slider in sliders.values():
            if slider.slider.collidepoint(mouse_x, mouse_y):
                slider.handle.x = max(slider.minX, min(slider.maxX, mouse_x - slider.handle.width // 2))
                slider.value = (slider.handle.x - slider.minX) / (slider.maxX - slider.minX)
                settings[slider.name] = slider.value

    for slider in sliders.values():
        slider.draw(SCREEN, GREY, DARK_GREY)
    
    for button in buttons.values():
        if button.name == "shuffle":
            if button.value == False:
                button.draw(SCREEN, GREY, 10, 10, 0, 0)
            else:
                button.draw(SCREEN, DARK_GREY, 10, 15, 0, 0)
        elif button.name == "resetDeck":
            if button.value == False:
                button.draw(SCREEN, GREY, 0, -25, 0, 0)
            else:
                button.draw(SCREEN, DARK_GREY, 0, 0, 0, 0)
        else:
            button.draw(SCREEN, GREY, 0, -25, 5, 0)
            
    DisplayDeck(deck)
    pygame.display.flip()
    
    
            
pygame.quit()