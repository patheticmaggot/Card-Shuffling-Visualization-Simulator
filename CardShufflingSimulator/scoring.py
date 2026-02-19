import utilities

class Score:
    def __init__(self, 
                 shuffledDeck, 
                 initialDeck, 
                 eps=1e-9, 
                 w_abs=0.25, 
                 w_rel=0.25, 
                 w_order=0.25, 
                 w_cons = 0.25, 
                 w_lipa = 0.25, 
                 w_rank = 0.25,
                 w_suit = 0.25,
                 w_color = 0.25,
                 w_TRank = 0.25,
                 #w_copa = 0.25,
                 w_supa = 0.25
                 ):
        
        self.shuffledDeck = shuffledDeck
        self.initialDeck = initialDeck
        self.eps = eps

        # weights
        self.w_abs = w_abs
        self.w_rel = w_rel
        self.w_order = w_order
        self.w_cons = w_cons
        self.w_lipa = w_lipa
        self.w_reank = w_rank
        self.w_suit = w_suit
        self.w_color = w_color
        self.w_TRank = w_TRank
        #self.w_copa = w_copa
        self.w_supa = w_supa

        # compute individual scores
        self.absoluteDistanceScore = self._absolute_distance_score()
        self.relativeDistanceScore = self._relative_distance_score()
        self.orderScore = self._order_score()
        self.consecutiveTrendScore = self._consecutive_trend_score()
        self.linearPatternScore = self._linear_pattern_score()
        self.repeatingRankScore = self._repeating_rank_score()
        self.repeatingSuitScore = self._repeating_suit_score()
        self.repeatingColorScore = self._repeating_color_score()
        self.trendingRankScore = self._trending_rank_score()
        #self.colorPatternScore = self._color_pattern_score()
        self.suitPatternScore = self._suit_pattern_score()

        # compute total score
        self.totalScore = self._total_score()
        self.humanScore = self._human_score()

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
        self.linearPatternScore
        ]


        weights = [
        self.w_abs,
        self.w_rel,
        self.w_order,
        self.w_cons,
        self.w_lipa
        ]


        eps = self.eps
        num = 0.0
        den = 0.0


        for s, w in zip(scores, weights):
            s = max(s, eps) # estää nollan ja logiikka-ongelmat
            num += w * (s ** p) # painotettu potenssi
            den += w


        return (num / den) ** (1 / p)
    
    def _human_score(self, p=-6):
        
        scores = [
            self.repeatingRankScore,
            self.repeatingSuitScore,
            self.repeatingColorScore,
            self.trendingRankScore,
            #self.colorPatternScore,
            self.suitPatternScore
        ]
        
        weights = [
            self.w_reank,
            self.w_suit,
            self.w_color,
            self.w_TRank,
            #self.w_copa,
            self.w_supa
        ]
        
        eps = self.eps
        num = 0.0
        den = 0.0
        
        for s, w in zip(scores, weights):
            s = max(s, eps)
            num += w * (s ** p)
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
        streakLengthExponent = 2.0
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
                    total_score += (streak - streakCutOff) ** streakLengthExponent
                streak = 1

            prev_dir = curr_dir
         
        # handle final streak
        if streak > streakCutOff:
            total_score += (streak - streakCutOff) ** streakLengthExponent
        

        maxTrend = (n - 1 - streakCutOff) ** streakLengthExponent
        shape = 15.0
        trendScore = (1 - total_score / maxTrend) ** shape
        
        return trendScore
    
    def _linear_pattern_score(self):
        
        """
        Scores how much the deck exhibits linear patterns e.g every 3rd card the card number rises by 4 for the whole deck then score = 0.
        
        - Scores the shuffled deck on its own doesnt care what the initial deck was
        - Looks trough every step height between 1 and n/2 (ascending/descending) for every step length that consist of at least 4 steps
        - Longer continuous patterns contribute more weight with minimum length being 3 step trend and maximum the whole deck
        - Returns score in [0, 1]
        - 0 = Atleast one pattern of the checked step sizes (example: every 4th card is going [1, 3, 5, 7, 9...] through the whole deck)
        - 1 = none of the patterns tried have a rising or decending pattern for more than 3 cards
        """
        
        n = len(self.initialDeck)
        if n < 2: 
            return 0.0
        
        scores = []
        minStepLength = 1
        
        for stepLength in range(minStepLength, n - 1):
            
            positions = range(0, n, stepLength)
            steppedValues = [self.shuffledDeck[i] for i in positions]
            numberOfSteps = len(steppedValues)
            streakLengthExponent = 2.0
            streakCutOff = 2
            maxStepHeight = int(n / 2)
            
            scoresH = []
            
            if numberOfSteps < 4:
                continue
            
            for stepHeight in range(1, maxStepHeight):
                
                total_score = 0.0
                streak = 0
                prev_dir = 0
                
                for i in range(numberOfSteps - 1):
                    
                    diff = steppedValues[i + 1] - steppedValues[i]

                    if diff == stepHeight:
                        curr_dir = 1
                    elif diff == -stepHeight:
                        curr_dir = -1
                    else:
                        curr_dir = 0

                    if curr_dir != 0 and curr_dir == prev_dir:
                        streak += 1
                    else:
                        if streak > streakCutOff:
                            total_score += (streak - streakCutOff) ** streakLengthExponent
                        streak = 0

                    prev_dir = curr_dir
                
                # handle final streak
                if streak > streakCutOff:
                    total_score += (streak - streakCutOff) ** streakLengthExponent
                

                maxTrend = (numberOfSteps - 1 - streakCutOff) ** streakLengthExponent
                shape = 15.0
                trendScore = (1 - total_score / maxTrend) ** shape
                scoresH.append(trendScore)
                #print("L: " + str(stepLength) + " H: " + str(stepHeight) + " = Score: " + str(trendScore))
            scores.append(min(scoresH))
            #print("L: "+ str(stepLength) + " : " + str(min(scoresH)))
        score = min(scores)
        #print(score)
        return score

    def _repeating_rank_score(self):
        
        lastRank = None
        totalRepeats = 0
        
        for c in self.shuffledDeck:
            currentRank = utilities.CardRank(c)
            if currentRank == lastRank:
                totalRepeats += 1
            lastRank = currentRank
        
        n = len(self.shuffledDeck)
        r = len(utilities.RANKS)
        
        base = n // r
        remainder = n % r

        # Compute theoretical maximum repeats
        maxRepeats = (remainder * base + (r - remainder) * (base - 1))
    
        rawScore = 1 - (totalRepeats / maxRepeats)
        #targetScore = 0.923  # Checked with 100 000 shuffles of Fisher-Yates and got the average score of "0.9231405128213228"
        
        #score = 1 - abs(rawScore - targetScore) / targetScore
        
        return rawScore #score
    
    def _repeating_suit_score(self):
    
        lastSuit = None
        totalRepeats = 0
        
        for c in self.shuffledDeck:
            currentSuit = utilities.CardSuit(c)
            if currentSuit == lastSuit:
                totalRepeats += 1
            lastSuit = currentSuit
        
        n = len(self.shuffledDeck)
        s = len(utilities.SUITS)
        
        base = n // s
        remainder = n % s

        # Compute theoretical maximum repeats
        maxRepeats = (remainder * base + (s - remainder) * (base - 1))

        rawScore = 1 - (totalRepeats / maxRepeats)
        targetScore = 0.75   # Checked with 100 000 shuffles of Fisher-Yates and got the average score of "0.7502385416666635"
        
        score = 1 - abs(rawScore - targetScore) / targetScore
        
        return score
    
    def _repeating_color_score(self):
    
        lastColor = None
        currentColor = None
        totalRepeats = 0
        
        for c in self.shuffledDeck:
            
            currentColor = utilities.CardColor(c)
            
            if currentColor == lastColor:
                totalRepeats += 1
            lastColor = currentColor
        
        n = len(self.shuffledDeck)
        s = 2   # Colors
        
        base = n // s
        remainder = n % s

        # Compute theoretical maximum repeats
        maxRepeats = (remainder * base + (s - remainder) * (base - 1))

        rawScore = 1 - (totalRepeats / maxRepeats)
        targetScore = 0.5   # Checked with 100 000 shuffles of Fisher-Yates and got the average score of "0.5000056000000025"
        
        score = 1 - abs(rawScore - targetScore) / targetScore
        
        return score
    
    def _trending_rank_score(self):
        
        n = len(self.initialDeck)
        if n < 2:
            return 0.0

        streakLengthExponent = 2.0
        streakCutOff = 2
        
        total_score = 0.0
        streak = 0
        prev_dir = 0

        for i in range(n - 1):
            
            currentCardRank = utilities.RANKS.index(utilities.CardRank(self.shuffledDeck[i]))
            nextCardRank = utilities.RANKS.index(utilities.CardRank(self.shuffledDeck[i + 1]))
            
            diff = nextCardRank - currentCardRank

            if diff > 0:
                curr_dir = 1
            elif diff < 0:
                curr_dir = -1
            else:
                curr_dir = prev_dir

            if curr_dir == prev_dir:
                streak += 1
            else:
                if streak > streakCutOff:
                    total_score += (streak - streakCutOff) ** streakLengthExponent
                streak = 1

            prev_dir = curr_dir
         
        # handle final streak
        if streak > streakCutOff:
            total_score += (streak - streakCutOff) ** streakLengthExponent
        

        shape = 15.0
        maxTrend = (n - 1 - streakCutOff) ** streakLengthExponent
        
        rawScore = (1 - total_score / maxTrend) ** shape
        
        targetScore = 0.79  # Checked with 100 000 shuffles of Fisher-Yates and got the average score of "0.7900041300991113"
        
        score = 1 - abs(rawScore - targetScore) / targetScore
        
        return score
    """
    def _color_pattern_score(self):
        
        n = len(self.initialDeck)
        if n < 2: 
            return 0.0
        
        scores = []
        minStepLength = 2
        maxStepLength = 10
        
        for stepLength in range(minStepLength, maxStepLength):
            
            positions = range(0, n, stepLength)
            steppedValues = [self.shuffledDeck[i] for i in positions]
            numberOfSteps = len(steppedValues)
            streakLengthExponent = 2.0
            streakStart = 2
            
            if numberOfSteps < 4:
                continue
                
            total_score = 0.0
            streak = 0
            
            for i in range(numberOfSteps - 1):
                
                curr_col = CardColor(steppedValues[i])
                next_col = CardColor(steppedValues[i + 1])
                
                sameColor = curr_col == next_col
                
                if sameColor:
                    streak += 1
                else:
                    if streak > streakStart:
                        total_score += (streak - streakStart) ** streakLengthExponent
                    streak = 0
            
            # handle final streak
            if streak > streakStart:
                total_score += (streak - streakStart) ** streakLengthExponent
            

            if stepLength == 1:
                maxTrend = 2 * ((n/2 - 1) - streakStart) ** streakLengthExponent
            else:
                maxTrend = ((numberOfSteps - 1) - streakStart) ** streakLengthExponent
                
            shape = 1.0
            trendScore = (1 - total_score / maxTrend) ** shape
            scores.append(trendScore)
            
            #print("L: "+ str(stepLength) + " : " + str(trendScore))
            
        score = min(scores)
        #print(score)
        return score
    """
    def _suit_pattern_score(self):
        
        n = len(self.initialDeck)
        if n < 2: 
            return 0.0
        
        scores = []
        minStepLength = 2
        maxStepLength = 11
        
        for stepLength in range(minStepLength, maxStepLength):
            
            positions = range(0, n, stepLength)
            steppedValues = [self.shuffledDeck[i] for i in positions]
            numberOfSteps = len(steppedValues)
            streakLengthExponent = 2.0
            streakStart = 2
            
            if numberOfSteps < 4:
                continue
                
            total_score = 0.0
            streak = 0
            
            for i in range(numberOfSteps - 1):
                
                curr_suit = utilities.CardSuit(steppedValues[i])
                next_suit = utilities.CardSuit(steppedValues[i + 1])
                
                sameSuit = curr_suit == next_suit
                
                if sameSuit:
                    streak += 1
                else:
                    if streak > streakStart:
                        total_score += (streak - streakStart) ** streakLengthExponent
                    streak = 0
            
            # handle final streak
            if streak > streakStart:
                total_score += (streak - streakStart) ** streakLengthExponent
            

            if stepLength == 1:
                maxTrend = 4 * ((numberOfSteps/4 - 1) - streakStart) ** streakLengthExponent
            elif stepLength == 2:
                maxTrend = 2 * ((numberOfSteps/2 - 1) - streakStart) ** streakLengthExponent
            else:
                maxTrend = ((numberOfSteps - 1) - streakStart) ** streakLengthExponent
                
            shape = 1.0
            trendScore = (1 - total_score / maxTrend) ** shape
            scores.append(trendScore)
            
            #print("L: "+ str(stepLength) + " : " + str(trendScore))
            
        score = min(scores)
        #print(score)
        return score        
    