import scoring
import matplotlib.pyplot as plt
import shuffles
import pygame

SCREEN_WIDTH = 1138
SCREEN_HEIGHT = 640

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

GREY = (135, 129, 128)
DARK_GREY = (59, 56, 55)
BLACK = (0, 0, 0)
LESS_BLACK = (20, 20, 20)
RED = (255, 0, 0)
LESS_RED = (255, 60, 60)
BACKGROUND_COLOR = (97, 125, 12)
SETTINGSTAB_COLOR = (50, 50, 50)
FONT = pygame.font.SysFont("Arial", 20, False, False)


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

VIEWS = ["Suit", "Rank", "Order"]

SUITS = ["S", "D", "C", "H"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

settings = {
    "shuffle": "Riffle Shuffle",
    "offset": 0.0,
    "accuracy": 0.0,
    "deckSize": 52,
    "inOutRand": "o",
    "displayType": "Suit"
}

def ExpectedIdealSimulator(n, trials=1000):
    initialDeck = list(range(n))
    total1 = 0
    
    values = []
    
    for _ in range(trials):
        shuffledDeck = shuffles.FisherYates(initialDeck)

        score = scoring.Score(shuffledDeck, initialDeck)
        score1 = score.repeatingColorScore
        total1 += score1
        values.append(score1)
    
    expectedMean = total1 / trials
    print(expectedMean)
    plt.hist(values, bins=50)
    plt.show()
    return

def CardSuit(c):
    c = c % 52
    return SUITS[c // 13]

def CardRank(c):
    c = c % 52
    return RANKS[c % 13]

def CardColor(c):
    suit = CardSuit(c)
    if suit == "S" or suit == "C":
        color = "B"
    elif suit == "D" or suit == "H":
        color = "R"
    return color

def Draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    SCREEN.blit(img, (x, y))

def InitializeDeck(n):
    deck = list(range(n))
    startDeck = deck.copy()
    score = scoring.Score(deck, deck)
    
    deckHistory = [{
    "deck": deck.copy(),
    "shuffle": "initial",
    "settings": settings.copy(),
    "score": score
    }]
    
    
    return deck, startDeck, deckHistory, score
