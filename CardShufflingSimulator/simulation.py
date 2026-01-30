import pygame
import random
import math
import matplotlib.pyplot as plt

pygame.init()
SCREEN_WIDTH = 1138
SCREEN_HEIGHT = 640
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shuffling simulator")

GREY = (135, 129, 128)
DARK_GREY = (59, 56, 55)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
FONT = pygame.font.SysFont("Arial", 20)


settingsTabWidth = 250
settingsTabHeight = SCREEN_HEIGHT
settingsTabX = (SCREEN_WIDTH - settingsTabWidth)
settingsTabY = 0
settingsTab = pygame.Rect(settingsTabX, settingsTabY, settingsTabWidth, settingsTabHeight)


clock = pygame.time.Clock()

deckGenerated = False
deck = []
startDeck = []

SHUFFLES = ["riffleShuffle", "cutDeck", "computer", "reverse", "fisherYates"]
SUITS = ["S", "D", "C", "H"]

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
        Draw_text(self.name, FONT, BLACK, (self.slider.x + 5), self.slider.y)
        Draw_text(str(int(self.value * 100)) + "%", FONT, BLACK, (self.slider.x + self.slider.width), self.slider.y)

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
            Draw_text(self.name, FONT, BLACK, self.button.x + textNameX, self.button.y + textNameY)
            Draw_text(str(self.value), FONT, BLACK, self.button.x + textValuex, self.button.y + textValueY)
        elif self.nameText and not self.valueText:
            Draw_text(self.name, FONT, BLACK, self.button.x + textNameX, self.button.y + textNameY)
        elif not self.nameText and self.valueText:
            Draw_text(str(self.value), FONT, BLACK, self.button.x + textValuex, self.button.y + textValueY)

class Score:
    def __init__(self, shuffledDeck, initialDeck, eps=1e-9, w_abs=0.25, w_rel=0.25, w_order=0.25, w_cons = 0.25, w_step = 0.25):
        self.shuffledDeck = shuffledDeck
        self.initialDeck = initialDeck
        self.eps = eps

        # weights
        self.w_abs = w_abs
        self.w_rel = w_rel
        self.w_order = w_order
        self.w_cons = w_cons
        self.w_step = w_step

        # compute individual scores
        self.absoluteDistanceScore = self._absolute_distance_score()
        self.relativeDistanceScore = self._relative_distance_score()
        self.orderScore = self._order_score()
        self.consecutiveTrendScore = self._consecutive_trend_score()
        self.steppedTrendScore = self._stepped_trend_score()

        # compute total score
        self.totalScore = self._total_score()

    # ---------- total score ----------
    def _total_score(self, p=-6):
        """
        Soft-min power mean aggregation.


        p -> -inf : lähestyy min(scoret)
        p = -1..-10: kuinka rankaiseva pieniä arvoja kohtaan
        """


        scores = [
        self.absoluteDistanceScore,
        self.relativeDistanceScore,
        self.orderScore,
        self.consecutiveTrendScore,
        self.steppedTrendScore
        ]


        weights = [
        self.w_abs,
        self.w_rel,
        self.w_order,
        self.w_cons,
        self.w_step
        ]


        eps = self.eps
        num = 0.0
        den = 0.0


        for s, w in zip(scores, weights):
            s = max(s, eps) # estää nollan ja logiikka-ongelmat
            num += w * (s ** p) # painotettu potenssi
            den += w


        return (num / den) ** (1 / p)

    # ---------- component scores ----------
    
    def _absolute_distance_score(self):
        
        """
        Scores how close to the ideal distance away the cards are frm their original position in the initial deck
        
        - Expected ideal checked with simulations to be "n / 3"
        - Returns score in [0, 1]
        - 0 = cards on the same spots as in the original deck
        - 1 = cards on average "n / 3" distance away from the original position
        """
        
        n = len(self.initialDeck)   # Initial decks length
        
        # Create a dictionary to get the indexes of the shuffled numbers in the shuffled deck
        position = {card: i for i, card in enumerate(self.shuffledDeck)}

        # Add up every distence between the initial position of the card and the shuffled position of that same card
        totalDistance = 0
        for i, card in enumerate(self.initialDeck):
            totalDistance += abs(i - position[card])

        meanDistance = totalDistance / n    # Calculate mean
        expectedIdeal = n / 3               # Use a precalculated expected ideal of the perfect shuffle as a standard for the score
        absoluteDistanceScore = 1 - abs(meanDistance - expectedIdeal) / expectedIdeal # Score between 0 and 1. 1 = closest to ideal
        
        return absoluteDistanceScore

    def _relative_distance_score(self, k=6):
        
        """
        Scores every card on how far their neighbours have moved from their original neighbour spots
        
        - Weighted on how far the neighbour card is from the original
        - k determines how far away do we chack the neighbours scores
        - Returns score in [0, 1]
        - 0 = every neighbour is on their original spot compared to the original
        - 1 = Weighted neighbour distances on average are as close to the ideal expected distance tested with perfect shuffling
        - Expected ideal checked with simulations to be "n / 3.357" for deck size 52 (bigger deck apraches to 3)
        """
        
        n = len(self.initialDeck)   # Initial decks length
        
        # Create a dictionary to get the indexes of the shuffled numbers in the shuffled deck
        position = {card: i for i, card in enumerate(self.shuffledDeck)}

        total = 0
        weightSum = 0

        # Iterate through every card in initial deck
        for i, card in enumerate(self.initialDeck):
            for d in range(1, k + 1):       # Iterate trough every distance from the initial card between 1 card away to k cards away
                for j in (i - d, i + d):    # Iterate trough the 2 dirctions for the distance
                    if 0 <= j < n:          # Check to not go out of bounds
                        weight = 1 / d      # Assign a weight to the card by how far it is from the original in the initial deck
                        
                        # Get the absolute distance between the original card in the shuffled deck, 
                        # with the closest cards to it now in the shuffled deck. Then taking into account 
                        # the distance to the orginal card and multipying that value with the weight it got 
                        # from how far it is from the original card and adding that to the total
                        total += weight * abs(abs(position[card] - position[self.initialDeck[j]]) - d)
                        weightSum += weight # Adding up weights to use that instad of n to get accurate weights

        
        meanRelativeDistance = total / weightSum    # Geting the weighted mean of the relative distances
        expectedIdeal = n / 3.357                   # Using a precalculated expected ideal of the perfect shuffle as a standard for the score
        relativeDistanceScore = 1 - abs(meanRelativeDistance - expectedIdeal) / expectedIdeal   # Score between 0 and 1. 1 = closest to ideal

        return relativeDistanceScore

    def _order_score(self):
        
        """
        Scores how much the cards have changed sides on average
        
        - Returns score in [0, 1]
        - 0 = everything is in their original place or reversed.
        - 1 = The ideal expectation for a randomly shuffled deck
        
        """
        
        n = len(self.initialDeck)
        position = {card: i for i, card in enumerate(self.shuffledDeck)}

        preserved = 0
        totalPairs = n * (n - 1) // 2

        for i in range(n):
            for j in range(i + 1, n):
                if position[self.initialDeck[i]] < position[self.initialDeck[j]]:
                    preserved += 1

        fraction = preserved / totalPairs
        expectedIdeal = 0.5

        return 1 - abs(fraction - expectedIdeal) / expectedIdeal
    
    def _consecutive_trend_score(self, shape=8.0):
        """
        Scores how strongly the deck exhibits long increasing or decreasing trends.
        
        - Any step size allowed to the same direction (ascending/descending) 
        - Longer continuous trends contribute more weight starting from 2 steps (singles are not counted)
        - Shape determines how exponentially punnnishing longer trends are
        - Returns score in [0, 1]
        - 0 = whole deck is escending or descending
        - 1 = every card changes trend diretion
        """
        n = len(self.initialDeck)
        if n < 2:
            return 0.0

        total_score = 0.0
        streakCutoff = 1
        streak = 0
        prev_dir = 0

        for i in range(n - 1):
            diff = self.shuffledDeck[i + 1] - self.shuffledDeck[i]

            if diff > 0:
                curr_dir = 1
            elif diff < 0:
                curr_dir = -1
            else:
                curr_dir = 0

            if curr_dir != 0 and curr_dir == prev_dir:
                streak += 1
            elif curr_dir != 0:
                streak = 1
            else:
                streak = 0

            prev_dir = curr_dir
            
            if streak > streakCutoff:
                total_score += streak


        maxTrend = sum(i for i in range(streakCutoff + 1, n))
        
        trendScore = (1 - total_score / maxTrend) ** shape
        
        return trendScore
    
    def _stepped_trend_score(self):
        
        n = len(self.shuffledDeck)
        product = 1.0
        
        maxStep = int(n)
        
        for step in range(2, maxStep - 1):
            
            weight = 1.0 / (step - 1)
                
            positions = range(0, n, step)
            steppedValues = [self.shuffledDeck[i] for i in positions]

            stepN = len(steppedValues)
            
            if stepN < 3:
                continue
            
            ascendingPairs = 0
            descendingPairs = 0
            
            for i in range(stepN - 1):
                if steppedValues[i + 1] == steppedValues[i] + 1:
                    ascendingPairs += 1
                elif steppedValues[i + 1] == steppedValues[i] - 1:
                    descendingPairs += 1

            ascendingFraction = ascendingPairs / (stepN - 1)
            descendingFraction = descendingPairs / (stepN - 1)
            
            product *= (1.0 - ascendingFraction) ** weight
            product *= (1.0 - descendingFraction) ** weight
            
        score = product
        
        return score
    """
    def modulo_ordered(deck, mod):
        groups = {}
        for card in deck:
            groups.setdefault(card % mod, []).append(card)
        return any(group == sorted(group) for group in groups.values())
    """
settings = {
    "shuffle": "riffleShuffle",
    "offset": 0.0,
    "accuracy": 0.0,
    "randomness": 0.0,
    "deckSize": 52,
    "inOutRand": "o"
}

sliders = {
    "accuracy": Slider((settingsTabX + 10), 100, 200, 25, "accuracy"),
    "offset": Slider((settingsTabX + 10), 150, 200, 25, "offset"),
    #"randomness": Slider((settingsTabX + 10), 200, 200, 25, "randomness")
}

buttons = {
    "shuffle": Button((settingsTabX + 10), (settingsTabHeight - 75), 75, 50, "shuffle", [False, True], True, False),
    "assignShuffle": Button((settingsTabX + 10), (settingsTabY + 25), 100, 25, "assignShuffle", SHUFFLES, True, True),
    "resetDeck": Button((settingsTabX + 150), (settingsTabY + 25), 25, 25, "resetDeck", [False, True], True, False)
}

def expectedIdealSimulator(n, trials=1000):
    initialDeck = list(range(n))
    total1 = 0
    power = 1.5
    
    values = []
    
    for _ in range(trials):
        shuffledDeck = FisherYates(initialDeck)

        
        
        if n < 2:
            return 0.0

        trendScore = 0.0

        streak = 0
        prev_dir = 0

        for i in range(n - 1):
            diff = shuffledDeck[i + 1] - shuffledDeck[i]

            if diff > 0:
                curr_dir = 1
            elif diff < 0:
                curr_dir = -1
            else:
                curr_dir = 0

            if curr_dir != 0 and curr_dir == prev_dir:
                streak += 1
            elif curr_dir != 0:
                streak = 1
            else:
                streak = 0

            prev_dir = curr_dir
            if streak > 1:
                trendScore += streak ** power
            
        #expectedIdeal = 90
        #trendScore1 = 1 - abs(trendScore - expectedIdeal) / expectedIdeal
        values.append(trendScore)
        
        total1 += trendScore
        
        
        print(trendScore)
        
    plt.hist(values, bins=50)
    plt.show()
    expectedMean = total1 / trials
    return expectedMean

def cardSuit(n):
    return SUITS[n // 13]

def Draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    SCREEN.blit(img, (x, y))

def GenDeck(n):
    deck = list(range(n))
    return deck

def DisplayBySuit(deck):
    
    n = len(deck)
    
    
    for i, c in enumerate(deck):
        cardWidth = 100
        cardHeight = 30
        buffX = 150
        buffY = 10
        xPos = buffX
        color = (0, 0, 0)
        #RGBvalue = #int(c * 250) // (n*4)
        
        
        if cardHeight * n > SCREEN_HEIGHT:
            cardHeight = SCREEN_HEIGHT // n
        
        if n == 1:
            yPos = (SCREEN_HEIGHT - cardHeight) // 2
        
        else:
            if cardSuit(c) == "S":
                color = BLACK
            elif cardSuit(c) == "D":
                color = RED
            elif cardSuit(c) == "C":
                color = BLACK
            elif cardSuit(c) == "H":
                color = RED
                
            yPos = SCREEN_HEIGHT - (cardHeight * i) - buffY - cardHeight
            
            
        rect = pygame.Rect(xPos, yPos, cardWidth, cardHeight)
        pygame.draw.rect(SCREEN, color, rect)
    
    return

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
    elif settings["shuffle"] == "fisherYates":
        return FisherYates(deck)
    else:
        print("Unknown shuffle")
        return deck
"""
def AnalyzeRandomness(shuffledDeck, initialDeck):
    absoluteDistanceScore = AbsoluteDistanceScore(shuffledDeck, initialDeck)
    relativeDistanceScore = RelativeDistanceScore(shuffledDeck, initialDeck)
    orderScore = OrderScore(shuffledDeck, initialDeck)
    
    return

# How close the shuffled card is to 1/3 of the distance away from original position (the ideal distance for randomness).
# 1 = 1/3 away on average, 0 = exact same positions. maximum distance is achieved by reversing cards.
def AbsoluteDistanceScore(shuffledDeck, initialDeck):
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
"""
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

def FisherYates(deck):
    n = len(deck)
    shuffledDeck = list(deck)
    for i in range(n - 1, 0, -1):
        j = random.randint(0, i)  # 0 ≤ j ≤ i
        shuffledDeck[i], shuffledDeck[j] = shuffledDeck[j], shuffledDeck[i]
    
    return shuffledDeck
    

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
randomnessScore = Score(deck, deck)
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
                #AnalyzeRandomness(deck, startDeck)
                randomnessScore = Score(deck, startDeck)

            elif event.key == pygame.K_r:
                deck = GenDeck(settings["deckSize"])
                startDeck = deck
                randomnessScore = Score(deck, startDeck)
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
                                #AnalyzeRandomness(deck, startDeck)
                                randomnessScore = Score(deck, startDeck)
                                button.value = True
                                randomnessScore._stepped_trend_score()
                        elif button.name == "assignShuffle":
                            button.nextValue()
                            settings["shuffle"] = button.value
                            print("Selected shuffle: " + str(button.value))
                        elif button.name == "resetDeck":
                            if button.value == False:
                                deck = GenDeck(settings["deckSize"])
                                startDeck = deck
                                randomnessScore = Score(deck, startDeck)
                                deckGenerated = True
                                button.value = True
                                #print("expectedIdeal: " + str(expectedIdealSimulator(52, 10000)))
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
            
    Draw_text("Total score: " + str(int(randomnessScore.totalScore * 100)) + "%", FONT, BLACK, settingsTabX + 10, settingsTabY + 300)
    Draw_text("Absolut distance score: " + str(int(randomnessScore.absoluteDistanceScore * 100)) + "%", FONT, BLACK, settingsTabX + 10, settingsTabY + 320)
    Draw_text("Relative distance score: " + str(int(randomnessScore.relativeDistanceScore * 100)) + "%", FONT, BLACK, settingsTabX + 10, settingsTabY + 340)
    Draw_text("Order score: " + str(int(randomnessScore.orderScore * 100)) + "%", FONT, BLACK, settingsTabX + 10, settingsTabY + 360)
    Draw_text("Consecutive trend score: " + str(int(randomnessScore.consecutiveTrendScore * 100)) + "%", FONT, BLACK, settingsTabX + 10, settingsTabY + 380)
    Draw_text("Stepped trend score: " + str(int(randomnessScore.steppedTrendScore * 100)) + "%", FONT, BLACK, settingsTabX + 10, settingsTabY + 400)
    
    DisplayBySuit(deck)
    DisplayDeck(deck)
    pygame.display.flip()
    
    
            
pygame.quit()