import scoring
import matplotlib.pyplot as plt
import shuffles
import pygame
import marker as m

# Screen dimensions
SCREEN_WIDTH = 1138
SCREEN_HEIGHT = 640

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# some commonly used colors
GREY = (135, 129, 128)
DARK_GREY = (59, 56, 55)
BLACK = (0, 0, 0)
LESS_BLACK = (20, 20, 20)
RED = (255, 0, 0)
LESS_RED = (255, 60, 60)
BACKGROUND_COLOR = (97, 125, 12)
SETTINGSTAB_COLOR = (50, 50, 50)

# Font for texts
FONT = pygame.font.SysFont("Arial", 20, False, False)

# Settings tab dimensions
settingsTabWidth = 250
settingsTabHeight = SCREEN_HEIGHT
settingsTabX = (SCREEN_WIDTH - settingsTabWidth)
settingsTabY = 0
settingsTab = pygame.Rect(settingsTabX, settingsTabY, settingsTabWidth, settingsTabHeight)


clock = pygame.time.Clock()
deckGenerated = False

deck = []           # THE deck in question
deckHistory = []    # Storage for all the deck states from the initial to the final. reseting the deck clears this
queue = []          # Queue for shuffles to be shuffled

# The different shuffles
SHUFFLES = ["Riffle Shuffle", 
            "Milk Shuffle", 
            "Overhand Shuffle", 
            "Monge Shuffle", 
            "Cut Deck", 
            "Reverse Cards", 
            "Computer Shuffle", 
            "Fisher-Yates Shuffle"]

# The different display modes
VIEWS = ["Suit", "Rank", "Order"]

# Spades, Diamonds, Clubs, Hearts
SUITS = ["S", "D", "C", "H"]
# Ace, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, Jack, Queen, King
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

# Current settings for the shuffle and the project
settings = {
    "shuffle": "Riffle Shuffle",
    "offset": 0.0,
    "accuracy": 0.0,
    "inOutRand": "o",
    "deckSize": 52,
    "displayType": "Suit"
}

# Simulates a given amount of trials of Fisher-Yates shuffle to score it with a chosen scoring method and get statistics of what score does a "perfect" shuffle get
def ExpectedIdealSimulator(n, trials=1000):
    initialDeck = list(range(n))
    total1 = 0
    
    values = []
    
    for _ in range(trials):
        shuffledDeck = shuffles.FisherYates(initialDeck)

        score = scoring.Score(shuffledDeck, initialDeck)
        score1 = score.edgePreservationScore
        total1 += score1
        values.append(score1)
    
    expectedMean = total1 / trials
    print(expectedMean)
    plt.hist(values, bins=50)
    plt.show()
    return

# Return the suit of the card from index
def CardSuit(c):
    c = c % 52
    return SUITS[c // 13]

# Return the rank of the card from index
def CardRank(c):
    c = c % 52
    return RANKS[c % 13]

# Return the color of the card from index
def CardColor(c):
    suit = CardSuit(c)
    if suit == "S" or suit == "C":
        color = "B"
    elif suit == "D" or suit == "H":
        color = "R"
    return color

# Function for drawing text
def Draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    SCREEN.blit(img, (x, y))

# Initializes deck to the start order
def InitializeDeck(n):
    deck = list(range(n))
    score = scoring.Score(deck, deck)
    
    deckHistory = [{
    "deck": deck.copy(),
    "shuffle": "initial",
    "settings": settings.copy(),
    "score": score
    }]
    
    UpdateQueuemarkers()
    
    return deck, deckHistory, score

# Queues a shuffle with the current settings to be shuffled next or after all the other shuffles in the queue
def QueueShuffle():
    queue.append({
        "shuffle": settings["shuffle"],
        "accuracy": settings["accuracy"],
        "offset": settings["offset"],
        "inOutRand": settings["inOutRand"]
    })
    
    UpdateQueuemarkers()
    
    print(len(queue))

# Removes the last shuffle in the queue from the queue
def RemoveShuffle():
    if not queue:
        return
    queue.pop()
    
    UpdateQueuemarkers()
    
    print(len(queue))

# Updates the queue markers
def UpdateQueuemarkers():
    if not queue:
        m.markers.clear()
        return
    
    m.markers.clear()
    
    x = settingsTabX + 10
    y = settingsTabHeight - 190
    width = 25
    height = 25
    dispalyAmount = 4
    
    for item in queue[:dispalyAmount]:
        
        if item["shuffle"] == "Riffle Shuffle":
            color = (255, 0, 38)
        elif item["shuffle"] == "Milk Shuffle":
            color = (242, 233, 234)
        elif item["shuffle"] == "Overhand Shuffle":
            color = (64, 64, 255)
        elif item["shuffle"] == "Monge Shuffle":
            color = (77, 175, 74)
        elif item["shuffle"] == "Cut Deck":
            color = (255, 255, 0)
        elif item["shuffle"] == "Reverse Cards":
            color = (138, 138, 138)
        elif item["shuffle"] == "Computer Shuffle":
            color = (82, 82, 82)
        elif item["shuffle"] == "Fisher-Yates Shuffle":
            color = (0, 0, 0)
        
        m.markers.append(m.Marker(item["shuffle"], color, x, y, width, height))
        
        x += width + 5
    