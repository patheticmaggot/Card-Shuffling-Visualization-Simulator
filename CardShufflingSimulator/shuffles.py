import random
import scoring
import utilities as uti


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


# ---------- shuffles ----------

# Shuffling the deck with current settings
def Shuffle(deck, settings, deckHistory):
    
    startDeck = deckHistory[0]["deck"].copy()
    
    if uti.queue:
        shuffle = uti.queue[0]["shuffle"]
        print("\nShuffle from queue: " + str(shuffle))
        accuracy = uti.queue[0]["accuracy"]
        print("accuracy: " + str(accuracy))
        offset = uti.queue[0]["offset"]
        print("offset: " + str(offset))
        inOutRand = uti.queue[0]["inOutRand"]
        
        uti.queue.append(uti.queue.pop(0))
        print("\nNext in queue:" + str(uti.queue[0]["shuffle"]))
        uti.UpdateQueuemarkers()
    else:
        shuffle = settings["shuffle"]
        accuracy = settings["accuracy"]
        offset = settings["offset"]
        inOutRand = settings["inOutRand"]
    
    
    
    if shuffle == "Cut Deck":
        shuffledDeck = CutDeck(deck, offset, accuracy)
        score = scoring.Score(shuffledDeck, startDeck)
    elif shuffle == "Riffle Shuffle":
        shuffledDeck = RiffleShuffle(deck, offset, accuracy, inOutRand)
        score = scoring.Score(shuffledDeck, startDeck)
    elif shuffle == "Computer Shuffle":
        shuffledDeck = ComputerRandomShuffle(deck)
        score = scoring.Score(shuffledDeck, startDeck)
    elif shuffle == "Reverse Cards":
        shuffledDeck = ReverseDeck(deck)
        score = scoring.Score(shuffledDeck, startDeck)
    elif shuffle == "Fisher-Yates Shuffle":
        shuffledDeck = FisherYates(deck)
        score = scoring.Score(shuffledDeck, startDeck)
    elif shuffle == "Milk Shuffle":
        shuffledDeck = MilkShuffle(deck, accuracy)
        score = scoring.Score(shuffledDeck, startDeck)
    elif shuffle == "Overhand Shuffle":
        shuffledDeck = OverhandShuffle(deck, accuracy)
        score = scoring.Score(shuffledDeck, startDeck)
    elif shuffle == "Monge Shuffle":
        shuffledDeck = MongeShuffle(deck, accuracy, inOutRand)
        score = scoring.Score(shuffledDeck, startDeck)
    else:
        shuffledDeck = deck
        score = scoring.Score(shuffledDeck, startDeck)
    
    
    deckHistory.append({
        "deck": shuffledDeck.copy(),
        "shuffle": shuffle,
        "settings": settings.copy(),
        "score": score
    })
    
    
    
    return shuffledDeck, score

# A shuffle where you take clumps from the top and the bottom
def MilkShuffle(deck, accuracy):
    
    """
    Accuracy: 1.0 = take exactly one card from the top and one from the bottom and put them on top of the new deck.
    Accuracy: 0.0 = take all the cards and put them in the new deck (nothing happens)
    """
    
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

# A shuffle wher you take clumps from the top only
def OverhandShuffle(deck, accuracy):
    """
    Accuracy: 1.0 = take exactly 1 card from the top and put it on top of the new deck (results in a reversed deck)
    Accuracy: 0.0 = take the whole deck and put it in the new deck (nothing happens)
    """
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

# A shuffle where you take clumps from the top and alternate with putting the clumps on the bottom and top of the new deck
def MongeShuffle(deck, accuracy, inOutRand):
    #(if I've forgotten somewhere a "Over-Under Shuffle" name that is the same as Monge shuffle)
    """
    Accuracy: 1.0 = take exactly 1 card from the top and alternate with putting it on top or on the bottom
    Accuracy: 0.0 = take every card from the top (nothing happens)
    inOutRand: "i" = start with puting the card on top, "o" = start with puting the card on teh bottom. (something else = random)
    """
    
    accuracy = max(0.0, min(1.0, accuracy))
    initialDeck = deck[:]
    shuffledDeck = []
    
    if accuracy == 1.0:
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

# A shuffle where you split the deck in half and then riffle the parts back together like a zipper
def RiffleShuffle(deck, offset, accuracy, inOutRand):
    """
    Offset: 0.5 = deck split in 2 equal halves
    Accuracy: 0.0 = deck cut point completly random and one half will go as a whole first then the other as a whole
    Accuracy: 1.0 = deck cut point is exact and the halves will deposit exactly one card one after the other
    InOutRand: "i" = start with the top half, "o" = start with the bottom half. (something else = random)
    """
    
    n = len(deck)
    
    offset = max(0.0, min(1.0, offset))
    accuracy = max(0.0, min(1.0, accuracy))
    
    # Make the accuracy of the cut index to change between 90-100 accuracy since since the cut is ment to be done exactly at the middle
    cutIndex = CutIndex(n, offset, (0.90 + 0.10 * accuracy))
    #print("Cut index: " + str(cutIndex))
    top = deck[cutIndex:]
    bottom = deck[:cutIndex]
    
    ti = 0  # Top half Index
    bi = 0  # Bottom half Index
    
    if accuracy == 1.0:
        
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

# Cutting the deck from some point and exchanging those parts places
def CutDeck(deck, offset, accuracy):
    """
    Offset: 0.5 = deck split in 2 equal halves, 
    Accuracy: 1.0 = cut exactly at offset
    Accuracy: 0.0 = cut completly at random
    """
    
    n = len(deck)
    
    offset = max(0.0, min(1.0, offset))
    accuracy = max(0.0, min(1.0, accuracy))
    
    cutIndex = CutIndex(n, offset, accuracy)
    
    #print("Cut index: " + str(cutIndex))
    top = deck[:cutIndex]
    bottom = deck[cutIndex:]
    
    cutDeck = bottom + top
    
    return cutDeck


# ---------- testing shuffles ----------

# Supposedly the best computer generated shuffle of cards
def FisherYates(deck):
    n = len(deck)
    shuffledDeck = list(deck)
    for i in range(n - 1, 0, -1):
        j = random.randint(0, i)  # 0 ≤ j ≤ i
        shuffledDeck[i], shuffledDeck[j] = shuffledDeck[j], shuffledDeck[i]
    
    return shuffledDeck

# Simple computer generated shuffle
def ComputerRandomShuffle(deck):
    shuffledDeck = random.sample(deck, len(deck))
    return shuffledDeck

# Reversing the order of the deck
def ReverseDeck(deck):
    reversedDeck = deck[::-1]
    return reversedDeck
