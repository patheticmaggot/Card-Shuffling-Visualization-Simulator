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
LESS_BLACK = (20, 20, 20)
RED = (255, 0, 0)
LESS_RED = (255, 60, 60)
BACKGROUND_COLOR = (97, 125, 12)
SETTINGSTAB_COLOR = (50, 50, 50)
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
deckHistory = []

SHUFFLES = ["Riffle Shuffle", 
            "Milk Shuffle", 
            "Overhand Shuffle", 
            "Over-Under Shuffle", 
            "Cut Deck", 
            "Reverse Cards", 
            "Computer Shuffle", 
            "Fisher-Yates Shuffle"]

SUITS = ["S", "D", "C", "H"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

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
    def __init__(self, 
                 shuffledDeck, 
                 initialDeck, 
                 eps=1e-9, 
                 w_abs=0.25, 
                 w_rel=0.25, 
                 w_order=0.25, 
                 w_cons = 0.25, 
                 w_step = 0.25, 
                 w_rank = 0.25,
                 w_suit = 0.25,
                 w_color = 0.25
                 ):
        
        self.shuffledDeck = shuffledDeck
        self.initialDeck = initialDeck
        self.eps = eps

        # weights
        self.w_abs = w_abs
        self.w_rel = w_rel
        self.w_order = w_order
        self.w_cons = w_cons
        self.w_step = w_step
        self.w_reank = w_rank
        self.w_suit = w_suit
        self.w_color = w_color

        # compute individual scores
        self.absoluteDistanceScore = self._absolute_distance_score()
        self.relativeDistanceScore = self._relative_distance_score()
        self.orderScore = self._order_score()
        self.consecutiveTrendScore = self._consecutive_trend_score()
        self.steppedTrendScore = self._stepped_trend_score()
        self.consecutiveRankScore = self._consecutive_rank_score()
        self.consecutiveSuitScore = self._consecutive_suit_score()
        self.consecutiveColorScore = self._consecutive_color_score()

        # compute total score
        self.totalScore = self._total_score()

    # ---------- total score ----------
    def _total_score(self, p=-6):
        """
        Combines the other scores to one score.
        
        - Total score gets punished hard if one score is bad
        - p determines how hard small scores punish the total
        - The scores have tunable weights to contol their importance
        - Returns score in [0, 1]
        - 0 = Atleast one of the scores in 0
        - 1 = All of the scores are 1
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
        
        - Scores the shuffled deck compared to the initial deck
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
        
        - Scores the shuffled deck compared to the initial deck
        - Weighted on how far the neighbour card is from the original spot as the originals neighbour
        - k determines how far away do we chack the neighbours
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
        
        - Scores the shuffled deck compared to the initial deck
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
    
    
    def _consecutive_trend_score(self):
        """
        Scores how strongly the deck exhibits long increasing or decreasing trends.
        
        - Scores the shuffled deck on its own doesnt care what the initial deck was
        - Any step size allowed to the same direction (ascending/descending) 
        - Longer continuous trends contribute more weight with minimum length being 2 step trend
        - Shape variable determines how exponentially punishing longer trends are
        - Returns score in [0, 1]
        - 0 = whole deck is ascending or descending
        - 1 = after every card the trend direction changes
        """
        n = len(self.initialDeck)
        if n < 2:
            return 0.0

        total_score = 0.0
        streakLengthExponent = 1.1
        streak = 0
        streakCutOff = 2
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
            else:
                if streak > streakCutOff:
                    total_score += streakLengthExponent ** (streak - streakCutOff)
                streak = 1

            prev_dir = curr_dir
         
        # handle final streak
        if streak > streakCutOff:
            total_score += streakLengthExponent ** (streak - streakCutOff)
        

        maxTrend = streakLengthExponent ** (n - 1 - streakCutOff)
        shape = 4.0
        trendScore = (1 - total_score / maxTrend) ** shape
        
        return trendScore
    
    def _stepped_trend_score(self):
        
        """
        Scores how much the deck avoids rising or decending patterns every other, every 3rd, every 4th etc. card.
        
        - Scores the shuffled deck on its own doesnt care what the initial deck was
        - Looks at only a step size of 1 (ascending/descending) 
        - Longer continuous patterns contribute more weight with minimum length being 2 step trend
        - The smaller the jump over cards is the more its weght on the final score. every other weighing the most
        - Returns score in [0, 1]
        - 0 = Atleast one pattern between every other to every n:th spans the whole deck lenght 
            (example: every 4th card is going [1, 2, 3, 4, 5...] through the whole deck)
        - 1 = none of the patterns we try to search for have a rising nor decending pattern for more than 2 cards
        """
        
        n = len(self.shuffledDeck)
        product = 1.0
        
        maxStep = int(n/2)
        
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
    
    def _consecutive_rank_score(self):
        
        lastRank = None
        totalRepeats = 0
        
        for c in self.shuffledDeck:
            currentRank = CardRank(c)
            if currentRank == lastRank:
                totalRepeats += 1
            lastRank = currentRank
        
        n = len(self.shuffledDeck)
        r = len(RANKS)
        
        base = n // r
        remainder = n % r

        # Compute theoretical maximum repeats
        maxRepeats = (remainder * base + (r - remainder) * (base - 1))
    
        raw = 1 - (totalRepeats / maxRepeats)
        #target = 0.923  # Checked with 100 000 shuffles of Fisher-Yates and got the average score of "0.9231405128213228"
        
        #score = 1 - abs(raw - target) / target
        
        return raw #score
    
    def _consecutive_suit_score(self):
    
        lastSuit = None
        totalRepeats = 0
        
        for c in self.shuffledDeck:
            currentSuit = CardSuit(c)
            if currentSuit == lastSuit:
                totalRepeats += 1
            lastSuit = currentSuit
        
        n = len(self.shuffledDeck)
        s = len(SUITS)
        
        base = n // s
        remainder = n % s

        # Compute theoretical maximum repeats
        maxRepeats = (remainder * base + (s - remainder) * (base - 1))

        raw = 1 - (totalRepeats / maxRepeats)
        target = 0.75   # Checked with 100 000 shuffles of Fisher-Yates and got the average score of "0.7502385416666635"
        
        score = 1 - abs(raw - target) / target
        
        return score
    
    def _consecutive_color_score(self):
    
        lastColor = None
        currentColor = None
        totalRepeats = 0
        
        for c in self.shuffledDeck:
            
            currentSuit = CardSuit(c)
            if currentSuit == "S" or currentSuit == "C":
                currentColor = "B"
            elif currentSuit == "D" or currentSuit == "H":
                currentColor = "R"
            
            if currentColor == lastColor:
                totalRepeats += 1
            lastColor = currentColor
        
        n = len(self.shuffledDeck)
        s = 2   # Colors
        
        base = n // s
        remainder = n % s

        # Compute theoretical maximum repeats
        maxRepeats = (remainder * base + (s - remainder) * (base - 1))

        raw = 1 - (totalRepeats / maxRepeats)
        target = 0.5   # Checked with 100 000 shuffles of Fisher-Yates and got the average score of "0.5000056000000025"
        
        score = 1 - abs(raw - target) / target
        
        return score
    
settings = {
    "shuffle": "Riffle Shuffle",
    "offset": 0.0,
    "accuracy": 0.0,
    "deckSize": 52,
    "inOutRand": "o"
}

sliders = {
    "accuracy": Slider((settingsTabX + 10), settingsTabHeight - 220, 200, 25, "accuracy"),
    "offset": Slider((settingsTabX + 10), settingsTabHeight - 180, 200, 25, "offset"),
}

buttons = {
    "shuffle": Button((settingsTabX + 20), (settingsTabHeight - 75), 75, 50, "shuffle", [False, True], True, False),
    "assign shuffle": Button((settingsTabX + 10), (settingsTabHeight - 120), 200, 25, "assign shuffle", SHUFFLES, True, True),
    "reset": Button((settingsTabX + 150), (settingsTabHeight - 75), 75, 50, "reset", [False, True], True, False)
}


def ExpectedIdealSimulator(n, trials=1000):
    initialDeck = list(range(n))
    total1 = 0
    
    values = []
    
    for _ in range(trials):
        shuffledDeck = FisherYates(initialDeck)

        score = Score(shuffledDeck, initialDeck)
        total1 += score.consecutiveColorScore
        values.append(score.consecutiveColorScore)
        
    plt.hist(values, bins=50)
    plt.show()
    expectedMean = total1 / trials
    return expectedMean

def CardSuit(n):
    n = n % 52
    return SUITS[n // 13]

def CardRank(n):
    n = n % 52
    return RANKS[n % 13]

def Draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    SCREEN.blit(img, (x, y))

def InitializeDeck(n):
    deck = list(range(n))
    startDeck = deck.copy()
    score = Score(deck, deck)
    
    deckHistory = [{
    "deck": deck.copy(),
    "shuffle": "initial",
    "settings": settings.copy(),
    "score": score
    }]
    
    
    return deck, startDeck, deckHistory, score


def DisplayDeckHistory(deckHistory, DisplayType):
    
    xPos = 10
    gapWidth = 0
    historySize = len(deckHistory)
    gapAmount = historySize - 1
    displayArea = SCREEN_WIDTH - settingsTabWidth - xPos
    
    if historySize * 100 + gapAmount * gapWidth + xPos > displayArea:
        width = (displayArea - gapAmount * gapWidth) // historySize
    else:
        width = 100
    
    for i in deckHistory:
        if DisplayType == "Order":
            DisplayByOrder(i["deck"], xPos, width)
        elif DisplayType == "Suit":
            DisplayBySuit(i["deck"], xPos, width)
        elif DisplayType == "Rank":
            DisplayByRank(i["deck"], xPos, width)
        
        xPos += (width + gapWidth)
        
    return

def DisplayByRank(deck, xPos, width):
        
    n = len(deck)
    
    
    for i, c in enumerate(deck):
        cardWidth = width
        cardHeight = 30
        buffX = xPos
        buffY = 10
        xPos = buffX
        color = (0, 0, 0)
        
        
        if cardHeight * n > SCREEN_HEIGHT:
            cardHeight = SCREEN_HEIGHT // n
        
        if n == 1:
            yPos = (SCREEN_HEIGHT - cardHeight) // 2
        
        else:
            
            index = RANKS.index(CardRank(c))
            shade = (12 - index) * 20
            color = (shade, shade, shade)
                
            yPos = SCREEN_HEIGHT - (cardHeight * i) - buffY - cardHeight
            
            
        rect = pygame.Rect(xPos, yPos, cardWidth, cardHeight)
        pygame.draw.rect(SCREEN, color, rect)
    
    return

def DisplayBySuit(deck, xPos, width):
    
    n = len(deck)
    
    
    for i, c in enumerate(deck):
        cardWidth = width
        cardHeight = 30
        buffX = xPos
        buffY = 10
        xPos = buffX
        color = (0, 0, 0)
        
        
        if cardHeight * n > SCREEN_HEIGHT:
            cardHeight = SCREEN_HEIGHT // n
        
        if n == 1:
            yPos = (SCREEN_HEIGHT - cardHeight) // 2
        
        else:
            if CardSuit(c) == "S":
                color = BLACK
            elif CardSuit(c) == "D":
                color = LESS_RED
            elif CardSuit(c) == "C":
                color = LESS_BLACK
            elif CardSuit(c) == "H":
                color = RED
                
            yPos = SCREEN_HEIGHT - (cardHeight * i) - buffY - cardHeight
            
            
        rect = pygame.Rect(xPos, yPos, cardWidth, cardHeight)
        pygame.draw.rect(SCREEN, color, rect)
    
    return

def DisplayByOrder(deck, xPos, width):
    
    n = len(deck)
    
    
    for i, c in enumerate(deck):
        cardWidth = width
        cardHeight = 30
        buffX = xPos
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


def Shuffle(deck, settings, deckHistory):
    
    startDeck = deckHistory[0]["deck"].copy()
    
    if settings["shuffle"] == "Cut Deck":
        shuffledDeck = CutDeck(deck, settings["offset"], settings["accuracy"])
        score = Score(shuffledDeck, startDeck)
        shuffle = "Cut Deck"
        
    elif settings["shuffle"] == "Riffle Shuffle":
        shuffledDeck = RiffleShuffle(deck, settings["offset"], settings["accuracy"], settings["inOutRand"])
        score = Score(shuffledDeck, startDeck)
        shuffle = "Riffle Shuffle"
        
    elif settings["shuffle"] == "Computer Shuffle":
        shuffledDeck = ComputerRandomShuffle(deck)
        score = Score(shuffledDeck, startDeck)
        shuffle = "Computer Shuffle"
        
    elif settings["shuffle"] == "Reverse Cards":
        shuffledDeck = ReverseDeck(deck)
        score = Score(shuffledDeck, startDeck)
        shuffle = "Reverse Cards"
        
    elif settings["shuffle"] == "Fisher-Yates Shuffle":
        shuffledDeck = FisherYates(deck)
        score = Score(shuffledDeck, startDeck)
        shuffle = "Fisher-Yates Shuffle"
        
    elif settings["shuffle"] == "Milk Shuffle":
        shuffledDeck = MilkShuffle(deck, settings["accuracy"])
        score = Score(shuffledDeck, startDeck)
        shuffle = "Milk Shuffle"
        
    elif settings["shuffle"] == "Overhand Shuffle":
        shuffledDeck = OverhandShuffle(deck, settings["accuracy"])
        score = Score(shuffledDeck, startDeck)
        shuffle = "Overhand Shuffle"
        
    elif settings["shuffle"] == "Over-Under Shuffle":
        shuffledDeck = OverUnderShuffle(deck, settings["accuracy"], settings["inOutRand"])
        score = Score(shuffledDeck, startDeck)
        shuffle = "Over-Under Shuffle"
        
    else:
        shuffledDeck = deck
        score = Score(shuffledDeck, startDeck)
        shuffle = "Unknown shuffle"
    
    
    deckHistory.append({
        "deck": shuffledDeck.copy(),
        "shuffle": shuffle,
        "settings": settings.copy(),
        "score": score
    })
    return shuffledDeck, score


def MilkShuffle(deck, accuracy):
    
    accuracy = max(0.0, min(1.0, accuracy))
    initialDeck = deck[:]
    shuffledDeck = []
    
    decay_rate = 0.6
    base = 1 - decay_rate * accuracy
    k = 4
    s = 0.1
    startAccuracy = accuracy * s + (accuracy ** k) * (1 - s)
    
    while initialDeck:
        
        clump = []
        endingChance = 0
        cardsTaken = 0
        
        while random.random() > endingChance:
            endingChance = accuracy * (1 - (1 - startAccuracy) * (base ** cardsTaken))
            
            clump.append(initialDeck.pop(0))
            cardsTaken += 1
            
            if not initialDeck:
                endingChance = 1
                
        shuffledDeck.extend(clump)
        
        
        if not initialDeck:
            break
        
        
        
        clump = []
        endingChance = 0
        cardsTaken = 0
        
        while random.random() > endingChance:
            endingChance = accuracy * (1 - (1 - startAccuracy) * (base ** cardsTaken))
            
            clump.append(initialDeck.pop())
            cardsTaken += 1
            
            if not initialDeck:
                endingChance = 1
                
        shuffledDeck.extend(reversed(clump))
        
    return shuffledDeck

def OverhandShuffle(deck, accuracy):
    
    accuracy = max(0.0, min(1.0, accuracy))
    initialDeck = deck[:]
    shuffledDeck = []
    
    decay_rate = 0.6
    base = 1 - decay_rate * accuracy
    k = 4
    s = 0.1
    startAccuracy = accuracy * s + (accuracy ** k) * (1 - s)
    
    while initialDeck:
        
        clump = []
        endingChance = 0
        cardsTaken = 0
        
        while random.random() > endingChance:
            endingChance = accuracy * (1 - (1 - startAccuracy) * (base ** cardsTaken))
            
            clump.append(initialDeck.pop())
            cardsTaken += 1
            
            if not initialDeck:
                endingChance = 1
        
        shuffledDeck.extend(reversed(clump))
    
    return shuffledDeck

def OverUnderShuffle(deck, accuracy, inOutRand):
    
    accuracy = max(0.0, min(1.0, accuracy))
    initialDeck = deck[:]
    shuffledDeck = []
    
    if (inOutRand == "i"):
        useTop = True
    elif (inOutRand == "o"):
        useTop = False
    else:
        useTop = random.choice([True, False])
        
    decay_rate = 0.6
    base = 1 - decay_rate * accuracy
    k = 4
    s = 0.1
    startAccuracy = accuracy * s + (accuracy ** k) * (1 - s)
    
    while initialDeck:
        
        clump = []
        endingChance = 0
        cardsTaken = 0
        
        
        while random.random() > endingChance:
            endingChance = accuracy * (1 - (1 - startAccuracy) * (base ** cardsTaken))
            
            clump.append(initialDeck.pop())
            cardsTaken += 1
            
            if not initialDeck:
                endingChance = 1
        
        if useTop:
            shuffledDeck.extend(reversed(clump))
        else:
            shuffledDeck[0:0] = reversed(clump)
        
        useTop = not useTop
            
        
    
    return shuffledDeck

def RiffleShuffle(deck, offset, accuracy, inOutRand):
    """
    Offset: 0.5 = deck split in 2 equal halves, Accuracy: 0.0 = deck cut point completly random 
    and one half will go as a whole first then the other as  whole, 1.0 = deck cut point is exact 
    and the halves will deposit exactly one card one after the other
    """
    
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
                
    #print("Offset: " + str(offset))        
    return shuffledDeck

def CutDeck(deck, offset, accuracy):
    """
    Offset: 0.5 = deck split in 2 equal halves, Accuracy will decrease radially from the offset 
    point from 1 untill completly random at 0
    """
    
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

def ComputerRandomShuffle(deck):
    shuffledDeck = random.sample(deck, len(deck))
    return shuffledDeck

def ReverseDeck(deck):
    reversedDeck = deck[::-1]
    return reversedDeck


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

deck, startDeck, deckHistory, score = InitializeDeck(settings["deckSize"])
deckGenerated = True

running = True
while running:

    clock.tick(60)
    SCREEN.fill(BACKGROUND_COLOR)
    pygame.draw.rect(SCREEN, SETTINGSTAB_COLOR, settingsTab)
    
    mouse_held = pygame.mouse.get_pressed()
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                if not deckGenerated:
                    deck, startDeck, deckHistory, score = InitializeDeck(settings["deckSize"])
                    deckGenerated = True
                deck, score = Shuffle(deck, settings, deckHistory)

            elif event.key == pygame.K_r:
                deck, startDeck, deckHistory, score = InitializeDeck(settings["deckSize"])
                deckGenerated = True

            elif event.key == pygame.K_q:
                running = False
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for button in buttons.values():
                    if button.button.collidepoint(event.pos):
                        if button.name == "shuffle":
                            if button.value == False:
                                deck, score = Shuffle(deck, settings, deckHistory)
                                button.value = True
                        elif button.name == "assign shuffle":
                            button.nextValue()
                            settings["shuffle"] = button.value
                            print("Selected shuffle: " + str(button.value))
                        elif button.name == "reset":
                            if button.value == False:
                                deck, startDeck, deckHistory, score = InitializeDeck(settings["deckSize"])
                                deckGenerated = True
                                button.value = True
                                #print(ExpectedIdealSimulator(52, 100000))
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if buttons["shuffle"].value == True:
                    buttons["shuffle"].value = False
                    buttons["shuffle"].valueIndex = 1
                elif buttons["reset"].value == True:
                    buttons["reset"].value = False
                    buttons["reset"].valueIndex = 1
    
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
        elif button.name == "reset":
            if button.value == False:
                button.draw(SCREEN, GREY, 10, 10, 0, 0)
            else:
                button.draw(SCREEN, DARK_GREY, 10, 15, 0, 0)
        else:
            button.draw(SCREEN, GREY, 0, -25, 5, 0)
            
    Draw_text(str(int(score.absoluteDistanceScore * 100)) + "% :Absolut distance score", FONT, BLACK, settingsTabX + 10, settingsTabY + 10)
    Draw_text(str(int(score.relativeDistanceScore * 100)) + "% :Relative distance score", FONT, BLACK, settingsTabX + 10, settingsTabY + 30)
    Draw_text(str(int(score.orderScore * 100)) + "% :Order score", FONT, BLACK, settingsTabX + 10, settingsTabY + 50)
    
    Draw_text(str(int(score.consecutiveTrendScore * 100)) + "% :Consecutive trend score", FONT, BLACK, settingsTabX + 10, settingsTabY + 90)
    Draw_text(str(int(score.steppedTrendScore * 100)) + "% :Stepped trend score", FONT, BLACK, settingsTabX + 10, settingsTabY + 110)
    Draw_text(str(int(score.consecutiveRankScore * 100)) + "% :Consecutive rank score", FONT, BLACK, settingsTabX + 10, settingsTabY + 130)
    Draw_text(str(int(score.consecutiveSuitScore * 100)) + "% :Consecutive suit score", FONT, BLACK, settingsTabX + 10, settingsTabY + 150)
    Draw_text(str(int(score.consecutiveColorScore * 100)) + "% :Consecutive color score", FONT, BLACK, settingsTabX + 10, settingsTabY + 170)
    
    Draw_text(str(int(score.totalScore * 100)) + "% :Total score", FONT, BLACK, settingsTabX + 10, settingsTabY + 210)
    
    #DisplayByRank(deck, 300)
    #DisplayBySuit(deck, 150)
    #DisplayByOrder(deck, 10)
    
    DisplayDeckHistory(deckHistory, "Order")
    
    pygame.display.flip()
    
    
            
pygame.quit()