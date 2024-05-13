from game import Game
from agents import RandomAgent

if __name__ == "__main__":
    random_agent = RandomAgent()
    game = Game(4, 2048, random_agent)
    game.play()
