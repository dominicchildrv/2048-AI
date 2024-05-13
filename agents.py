import random
import pickle

class Agent:
    def get_move(self, game_state):
        raise NotImplementedError("This method should be overridden by subclasses.")
    

class GameStateFeatures:
    """
    Wrapper class around a game state where you can extract
    useful information 
    """

    def __init__(self, game_state):
        """
        Args:
            state: A given game state object
        """
        self.state = game_state

    def __eq__(self, other):

        if type(other) is type(self):
            return self.state == other.state
    
    def __hash__(self):

        return hash(self.state)
    
    def largest_in_corner(self):
        """Check if the largest tile is in the top left corner."""
        board = self.state.board
        max_tile = max(max(row) for row in board)
        corner = board[0][0]
        return max_tile == corner

    


class RandomAgent(Agent):
    def get_move(self, game_state):
        moves = game_state.valid_moves()
        if moves:
            return random.choice(moves)  # Return the move choice
        return None  # Return None if no moves are available
    

class LeftAgent(Agent):
    def get_move(self, game_state):
        moves = game_state.valid_moves()
        if moves:
            if 'left' in moves:
                return ('left')
            elif 'down' in moves:
                return ('down')
            elif 'right' in moves:
                return ('right')
            else:
                return ('up')
        return None  # Return None if no moves are available
    



class QLearnAgent(Agent):

    def __init__(self,
                 alpha: float = 0.2,
                 epsilon: float = 0.05,
                 gamma: float = 0.8,
                 maxAttempts: int = 30,
                 numTraining: int = 0):
        """
        These values are set to the default values above.

        Args:
            alpha: learning rate
            epsilon: exploration rate
            gamma: discount factor
            maxAttempts: How many times to try each action in each state
            numTraining: number of training episodes
        """
        super().__init__()
        self.alpha = float(alpha)
        self.epsilon = float(epsilon)
        self.gamma = float(gamma)
        self.maxAttempts = int(maxAttempts)
        self.numTraining = int(numTraining)
        # Count the number of games we have played
        self.episodesSoFar = 0

        self.qTable = {}
        self.previousState = []
        self.previousAction = []

    # Accessor functions for the variable episodesSoFar controlling learning
    def incrementEpisodesSoFar(self):
        self.episodesSoFar += 1

    def getEpisodesSoFar(self):
        return self.episodesSoFar

    def getNumTraining(self):
        return self.numTraining

    # Accessor functions for parameters
    def setEpsilon(self, value: float):
        self.epsilon = value

    def getAlpha(self) -> float:
        return self.alpha

    def setAlpha(self, value: float):
        self.alpha = value

    def getGamma(self) -> float:
        return self.gamma

    def getMaxAttempts(self) -> int:
        return self.maxAttempts
    
    def save_q_table(self, file_name):
        with open(file_name, 'wb') as file:
            pickle.dump(self.qTable, file)
        print(f"Q-table saved to {file_name}")

    def load_q_table(self, file_name):
        try:
            with open(file_name, 'rb') as file:
                self.qTable = pickle.load(file)
            print(f"Q-table loaded from {file_name}")
        except FileNotFoundError:
            print(f"No Q-table file found at {file_name}. Starting with an empty Q-table.")
            self.qTable = {}

    @staticmethod
    def computeReward(startState, endState):
        """
        Compute the reward, considering both the score and strategic tile placement.
        """
        # Basic reward for the score increase
        score_increase = endState.get_score() - startState.get_score()
        empty_tiles = sum(1 for row in endState.board for cell in row if cell == 0)

        # Additional reward if the largest number is in a corner
        if GameStateFeatures(endState).largest_in_corner():
            corner_bonus = startState.get_score() + 0.5 * score_increase
        else:
            corner_bonus = 0

        return score_increase + corner_bonus + (empty_tiles * 10)



    def getQValue(self,
                  state: GameStateFeatures,
                  action) -> float:
        """
        Args:
            state: A given state
            action: Proposed action to take

        Returns:
            Q(state, action)
        """
        "*** YOUR CODE HERE ***"
        return self.qTable.get((state, action), (0.0, 0))[0]

    

    def maxQValue(self, state: GameStateFeatures) -> float:
        """
        Args:
            state: The given state

        Returns:
            q_value: the maximum estimated Q-value attainable from the state
        """
        "*** YOUR CODE HERE ***"
        # Extract Q-values for the given state using list comprehension
        qValues = [qValue for (s, _), (qValue, _) in self.qTable.items() if s == state]

        # Return the maximum Q-value if any exist, otherwise return 0
        return max(qValues) if qValues else 0

        

    def learn(self,
              state: GameStateFeatures,
              action,
              reward: float,
              nextState: GameStateFeatures):
        """
        Performs a Q-learning update

        Args:
            state: the initial state
            action: the action that was took
            nextState: the resulting state
            reward: the reward received on this trajectory
        """
        # Directly compute the updated Q-value using the formula
        updatedQValues = (1 - self.alpha) * self.getQValue(state, action) + self.alpha * (reward + self.gamma * self.maxQValue(nextState))

        # Update the visit count, initializing if necessary
        _, visitCount = self.qTable.get((state, action), (0, 0))
        self.qTable[(state, action)] = (updatedQValues, visitCount + 1)

    def updateCount(self,
                    state: GameStateFeatures,
                    action):
        """
        Updates the stored visitation counts.

        Args:
            state: Starting state
            action: Action taken
        """
        # Increment the visit count for the state-action pair, initializing if it's not already in the Q-table
        qValue, times = self.qTable.get((state, action), (0, 0))
        self.qTable[(state, action)] = (qValue, times + 1)


    def getCount(self,
                 state: GameStateFeatures,
                 action) -> int:
        """
        Args:
            state: Starting state
            action: Action taken

        Returns:
            Number of times that the action has been taken in a given state
        """
        return self.qTable.get((state, action), (0.0, 0))[1] 

    def explorationFn(self,
                      utility: float,
                      counts: int) -> float:
        """
        Computes exploration function.
        Return a value based on the counts


        Args:
            utility: expected utility for taking some action a in some given state s
            counts: counts for having taken visited

        Returns:
            The exploration value
        """
        # Least-pick providing a stronger incentive for actions that have been taken less frequently
        # Constant C used to control the balance for explorationBonus
        C = 10
        explorationBonus = C / (counts + 1)
        return utility + explorationBonus

    def get_move(self, game_state):
        """
        Choose an action to take to maximise reward while
        balancing gathering data for learning


        Args:
            state: the current state

        Returns:
            The action to take
        """


        # The data we have about the state of the game
        moves = game_state.valid_moves()
        if moves:
            stateFeatures = GameStateFeatures(game_state)

            # Calculate reward between last state and current state
            if self.previousState:
                previousState = self.previousState[-1]
                previousAction = self.previousAction[-1]
                curReward = self.computeReward(previousState, game_state)
                # Update Q-Value
                self.learn(GameStateFeatures(previousState), previousAction, curReward, stateFeatures)


            # Decides whether to do exploration or exploitation using epsilon-greedy approach
            if random.random() < self.epsilon:
                action = random.choice(moves)
            else:
                # Calculates the best action based on q-values which are adjusted using the explorationFn
                adjustedQValues = {action: self.explorationFn(self.getQValue(stateFeatures, action), self.getCount(stateFeatures, action)) for action in moves}
                action = max(adjustedQValues, key=adjustedQValues.get)

            # Update counts and record the current state and action
            self.updateCount(stateFeatures, action)
            self.previousState.append(game_state)
            self.previousAction.append(action)

            return action
        
        return None  # Return None if no moves are available
    

    def final(self, state):
        """
        Handle the end of episodes, called by the game after a win or a loss.

        Args:
            state: the final game state
        """
        # Announce the game's completion and final score
        print(f"Game {self.getEpisodesSoFar() + 1} just ended!")
        print(f"Final score: {state.get_score()}")

        # If there was at least one move made, update the Q-values based on the final state
        if self.previousState:
            previousState, previousAction = self.previousState[-1], self.previousAction[-1]
            finalReward = self.computeReward(previousState, state)
            self.learn(GameStateFeatures(previousState), previousAction, finalReward, GameStateFeatures(state))

        # Prepare for the next episode
        self.previousState.clear()
        self.previousAction.clear()
        self.incrementEpisodesSoFar()

        # Check if the training phase is complete
        if self.getEpisodesSoFar() >= self.getNumTraining():
            msg = 'Training Done (turning off epsilon and alpha)'
            print('%s\n%s' % (msg, '-' * len(msg)))
            self.setAlpha(0)
            self.setEpsilon(0)


