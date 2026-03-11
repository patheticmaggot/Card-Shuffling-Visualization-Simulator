import utilities

# A class to score a given deck for its shuffleness with either comparing to the original deck or just by the shuffled deck
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
                 w_supa = 0.25,
                 w_edge = 0.25
                 ):
        
        self.shuffledDeck = shuffledDeck
        self.initialDeck = initialDeck
        self.eps = eps  # Small number to not get 0

        # weights
        self.w_abs = w_abs      # Absolute distance weight
        self.w_rel = w_rel      # Realtive distance weight
        self.w_order = w_order  # Order weight
        self.w_cons = w_cons    # Consecutive trend weight
        self.w_lipa = w_lipa    # Linear pattern weight
        self.w_rank = w_rank    # Repeating rank weight
        self.w_suit = w_suit    # Reapeating suit weight
        self.w_color = w_color  # Repeating color weight
        self.w_TRank = w_TRank  # Trending rank weight
        #self.w_copa = w_copa   # Color pattern weight
        self.w_supa = w_supa    # Suit pattern weight
        self.w_edge = w_edge    # Edge preservation weight

        # Compute individual scores
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
        
        self.edgePreservationScore = self._edge_preservation_score()

        # Compute combined scores
        self.totalScore = self._total_score()
        self.humanScore = self._human_score()


    # ---------- combined scores ----------
    
    # Edge preservation is in both since it is and "under the hood" score and an intuitive score for humans.
    
    def _total_score(self, p=-6):
        """
        Combining the scores that compare to the original deck or use things not seen by humans to score the deck (what happens under the hood)
        
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
        self.linearPatternScore,
        self.edgePreservationScore
        ]


        weights = [
        self.w_abs,
        self.w_rel,
        self.w_order,
        self.w_cons,
        self.w_lipa,
        self.w_edge
        ]


        eps = self.eps
        num = 0.0
        den = 0.0

        
        for s, w in zip(scores, weights):
            s = max(s, eps)
            num += w * (s ** p)
            den += w


        return (num / den) ** (1 / p)
    
    # Combining scores that are intuitive for humans like colors ranks and suits and also edge most cards since you can remember what was on top or bottom.
    def _human_score(self, p=-6):
        
        """
        Combining scores that are intuitive for humans like colors ranks and suits and also edge most cards.
        
        - Human score gets punished hard if one score is bad
        - p determines how hard small scores punish the total
        - The scores have tunable weights to contol their importance
        - Returns score in [0, 1]
        - 0 = Atleast one of the scores in 0
        - 1 = All of the scores are 1
        """
        
        scores = [
            self.repeatingRankScore,
            self.repeatingSuitScore,
            self.repeatingColorScore,
            self.trendingRankScore,
            #self.colorPatternScore,
            self.suitPatternScore,
            self.edgePreservationScore
        ]
        
        weights = [
            self.w_rank,
            self.w_suit,
            self.w_color,
            self.w_TRank,
            #self.w_copa,
            self.w_supa,
            self.w_edge
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
    
    def _edge_preservation_score(self):
        
        """
        Scores how much the edge most cards have moved from their initial position with top and bottom card having the most importance
        
        - Score is and average of the weighted worst offender and the weighted mean of the other edge cards
        - Returns score in [0, 1]
        - 0 = cards on the same spots as in the original deck
        - 1 = all of the edge cards are atleast 6 cards away from their original position 
        """
        
        n = len(self.initialDeck)   # Initial decks length
        
        # Create a dictionary to get the indexes of the shuffled numbers in the shuffled deck
        position = {card: i for i, card in enumerate(self.shuffledDeck)}

        totalDistance = 0
        totalWeight = 0
        trackDistance = 6
        
        worstDistance = 0
        
        for i, card in enumerate(self.initialDeck):
            distance = min(abs(i - position[card]), trackDistance)
            invDistance = 1 - (distance / trackDistance)
            
            weight = 1 / (min((i + 1), (n + 1) - (i + 1)))
            totalDistance += invDistance * weight
            totalWeight += weight
            
            worstDistance = max(invDistance * weight, worstDistance)

        meanDistance = totalDistance / totalWeight
        
        meanScore = 1 - meanDistance
        worstScore = 1 - worstDistance
        
        # Half of the score comes from the average from cards weighted to the sides and the other half from the worst offender (usually a top or bottom card not moving at all)
        edgePreservationScore = 0.5 * meanScore + 0.5 * worstScore 
        
        return edgePreservationScore
    
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
        - 1 = The ideal expectation for a randomly shuffled deck (half of them have changed)
        
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
        - Longer continuous trends contribute more weight with minimum length being 3 step trend
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
        Scores how much the deck exhibits linear patterns e.g. every 3rd card the card number rises by 4 for the whole deck then score = 0.
        
        - Scores the shuffled deck on its own doesnt care what the initial deck was
        - Looks trough every step height (ascending/descending) for every step length that consist of at least 4 steps
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
        
        """
        Scores how much ranks repeat after eachother.
        
        - Scores the shuffled deck on its own doesnt care what the initial deck was
        - Checks every pair and scores how many pairs are the same rank.
        - Returns score in [0, 1]
        - 0 = all of the same rank are next to eachother e.g. "1,1,1,1,A,A,A,A,6,6,6,6"
        - 1 = none of the same 4 ranks are next to each other
        """
        
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
        
        """
        Scores how much suit repeats after eachother
        
        - Scores the shuffled deck on its own doesnt care what the initial deck was
        - Checks every pair and scores how many pairs are the same suit.
        - Returns score in [0, 1]
        - 0 = all of the 13 of same suit are next to eachother e.g. "...H,H,H,H,H,H,S,S,S,S,S,S,S,..."
        - 1 = the amount of suits that are not next to eachother is closest to 0.75 percent of the deck
        """
        
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
        
        """
        Scores how much the 2 colors repeat after eachother.
        
        - Scores the shuffled deck on its own doesnt care what the initial deck was
        - Checks every pair and scores how many pairs are the same color.
        - Returns score in [0, 1]
        - 0 = all of the same color cards are next to eachother e.g. first the reds then the blacks
        - 1 = half of the colors repeat half dont
        """
        
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
        
        """
        Scores how much the ranks exhibit rising and decending trends
        
        - Scores the shuffled deck on its own doesnt care what the initial deck was
        - Any step size is counted (ascending/descending)
        - longer trends contribute more weight.
        - Returns score in [0, 1]
        - 0 = the whole deck is a rising or decending trend of the ranks (card being the same rank as the previous still contributes to the trend)
        - 1 = the deck has 79 percent of the pairs changing direction
        """
        
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
    # Ture random shows too much patterns for this to work
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
        
        """
        Scores how much the suits exhibit linear patterns e.g. every 3rd card the card suit is the same
        
        - Scores the shuffled deck on its own doesnt care what the initial deck was
        - Looks trough every step length that consist of at least 4 steps
        - Longer continuous patterns contribute more weight with minimum length being 3 step trend and maximum the whole deck (or with step=2 half deck one trend and other half the other trend)
        - Returns score in [0, 1]
        - 0 = Atleast one pattern goes trough the whole deck or with step size 2 half and half
        - 1 = none of the patterns tried have a pattern for more than 3 cards
        """
        
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
    