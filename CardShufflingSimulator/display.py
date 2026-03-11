import utilities
import pygame


# Displays the chosen displaytype
def DisplayDeckHistory(deckHistory, DisplayType):
    
    xPos = 10
    gapWidth = 0
    historySize = len(deckHistory)
    gapAmount = historySize - 1
    displayArea = utilities.SCREEN_WIDTH - utilities.settingsTabWidth - xPos
    
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

# Displays the deck as black-white gradient with same ranks being the same color
def DisplayByRank(deck, xPos, width):
        
    n = len(deck)
    
    
    for i, c in enumerate(deck):
        cardWidth = width
        cardHeight = 30
        buffX = xPos
        buffY = 10
        xPos = buffX
        color = (0, 0, 0)
        
        
        if cardHeight * n > utilities.SCREEN_HEIGHT:
            cardHeight = utilities.SCREEN_HEIGHT // n
        
        if n == 1:
            yPos = (utilities.SCREEN_HEIGHT - cardHeight) // 2
        
        else:
            
            index = utilities.RANKS.index(utilities.CardRank(c))
            shade = (12 - index) * 20
            color = (shade, shade, shade)
                
            yPos = utilities.SCREEN_HEIGHT - (cardHeight * i) - buffY - cardHeight
            
            
        rect = pygame.Rect(xPos, yPos, cardWidth, cardHeight)
        pygame.draw.rect(utilities.SCREEN, color, rect)
    
    return

# Displays the deck as 2 different shades of red and black for the 4 suits
def DisplayBySuit(deck, xPos, width):
    
    n = len(deck)
    
    
    for i, c in enumerate(deck):
        cardWidth = width
        cardHeight = 30
        buffX = xPos
        buffY = 10
        xPos = buffX
        color = (0, 0, 0)
        
        
        if cardHeight * n > utilities.SCREEN_HEIGHT:
            cardHeight = utilities.SCREEN_HEIGHT // n
        
        if n == 1:
            yPos = (utilities.SCREEN_HEIGHT - cardHeight) // 2
        
        else:
            if utilities.CardSuit(c) == "S":
                color = utilities.BLACK
            elif utilities.CardSuit(c) == "D":
                color = utilities.LESS_RED
            elif utilities.CardSuit(c) == "C":
                color = utilities.LESS_BLACK
            elif utilities.CardSuit(c) == "H":
                color = utilities.RED
                
            yPos = utilities.SCREEN_HEIGHT - (cardHeight * i) - buffY - cardHeight
            
            
        rect = pygame.Rect(xPos, yPos, cardWidth, cardHeight)
        pygame.draw.rect(utilities.SCREEN, color, rect)
    
    return

# Displays the deck as one continuous gradient from black to white
def DisplayByOrder(deck, xPos, width):
    
    n = len(deck)
    
    
    for i, c in enumerate(deck):
        cardWidth = width
        cardHeight = 30
        buffX = xPos
        buffY = 10
        xPos = buffX
        
        if cardHeight * n > utilities.SCREEN_HEIGHT:
            cardHeight = utilities.SCREEN_HEIGHT // n
        
        if n == 1:
            yPos = (utilities.SCREEN_HEIGHT - cardHeight) // 2
            color = 0
        else:
            yPos = utilities.SCREEN_HEIGHT - (cardHeight * i) - buffY - cardHeight
            color = int(c * 250 / n)
            
            
        rect = pygame.Rect(xPos, yPos, cardWidth, cardHeight)
        pygame.draw.rect(utilities.SCREEN, (color, color, color), rect)
    
    return
