from game import Game
from agents import QLearnAgent

if __name__ == "__main__":
    num_episodes = 10
    q_agent = QLearnAgent()
    q_agent.load_q_table('q_table.pkl')  # Load the Q-table if it exists
    
    for episode in range(num_episodes):
        print(f"Starting Episode {episode + 1}")
        game = Game(4, 2048, q_agent)
        game.play()

        if (episode + 1) % 100 == 0:  # Save every 100 episodes
            q_agent.save_q_table('q_table.pkl')
    
    # Ensure the final Q-table is saved
    q_agent.save_q_table('q_table.pkl')
