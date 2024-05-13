import random

class Game:
    def __init__(self, dim: int, goal: int, agent= None) -> None:
        self.dim = dim
        self.goal = goal
        self.board = [[0] * self.dim for _ in range(self.dim)]
        self.score = 0
        self.agent = agent
        self.initialize_game()

    def initialize_game(self):
        """ Initialize a new game by adding two tiles to the board """
        self.add_new_tile()
        self.add_new_tile()

    def add_new_tile(self):
        empty_cells = [(r, c) for r in range(self.dim) for c in range(self.dim) if self.board[r][c] == 0]
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.board[r][c] = random.choices([2, 4], weights=(90, 10), k=1)[0]

    def print_board(self):
        """ Print the current state of the board in a readable format. """
        for row in self.board:
            print("\t".join(f"{cell or '_':>4}" for cell in row))
        print()

    def compress(self, row):
        """ Compress the non-zero elements of the board toward the front (left for rows) """
        return [num for num in row if num != 0]

    def merge(self, row, update_score=True):
        for i in range(len(row) - 1):
            if row[i] == row[i + 1]:
                if update_score:
                    self.score += row[i] * 2
                row[i] *= 2
                row[i + 1] = 0
        return row

    def move_left(self, update_score=True):
        moved = False
        for i in range(self.dim):
            original_row = self.board[i].copy()
            compressed_row = self.compress(original_row)
            merged_row = self.merge(compressed_row, update_score)
            merged_and_compressed_row = self.compress(merged_row)
            self.board[i] = merged_and_compressed_row + [0] * (self.dim - len(merged_and_compressed_row))
            if original_row != self.board[i]:
                moved = True
        return moved
    
    def move_down(self, update_score=True):
        self.board = self.rotate_board(self.board)
        moved = self.move_left(update_score)
        for _ in range(3):
            self.board = self.rotate_board(self.board)
        return moved

    def move_up(self, update_score=True):
        for _ in range(3):
            self.board = self.rotate_board(self.board)
        moved = self.move_left(update_score)
        self.board = self.rotate_board(self.board)
        return moved

    def move_right(self, update_score=True):
        self.board = self.rotate_board(self.board)
        self.board = self.rotate_board(self.board)
        moved = self.move_left(update_score)
        self.board = self.rotate_board(self.board)
        self.board = self.rotate_board(self.board)
        return moved


    def check_win(self):
        """ Check if the player has reached the goal """
        return any(any(x >= self.goal for x in row) for row in self.board)

    def check_game_over(self):
        """ Check if no moves are possible """
        return not self.move_possible()
    
    def move_possible(self):
        """ Check if any moves are possible by simulating moves in all four directions. """
        original_board = [row[:] for row in self.board]
        for move_func in [self.move_left, self.move_right, self.move_up, self.move_down]:
            self.board = [row[:] for row in original_board]  # Reset board to original before testing each move
            if self.simulate_move(move_func):
                self.board = original_board  # Reset board to original after testing
                return True
        self.board = original_board  # Reset board to original if no moves are possible
        return False



    def simulate_move(self, move_func):
        original_board = [row[:] for row in self.board]
        move_func(update_score=False)  # Pass False to avoid updating score
        changed = self.board != original_board
        self.board = original_board  # Reset board after simulation
        return changed


    def rotate_board(self, board: list):
        """ Rotate the given board 90 degrees clockwise. """
        return [list(row) for row in zip(*reversed(board))]
    
    def reset_game(self):
        """ Resets the game to the initial state """
        self.board = [[0] * self.dim for _ in range(self.dim)]
        self.score = 0
        self.initialize_game()


    def play(self):
        """ Plays a single game until game over """
        while not self.check_game_over():

            if self.agent:
                move_choice = self.agent.get_move(GameState(self.board, self.score, self.dim))
                if move_choice:
                    move_func = getattr(self, f'move_{move_choice}', None)
                    if move_func and move_func():
                        self.add_new_tile()
                    else:
                        print("Invalid move returned by agent. Game over.")
                        break
                else:
                    print("No valid moves available. Game over.")
                    break
            else:
                self.print_board()
                print(f"Score: {self.score}")
                dir_input = input("Use 'w', 'a', 's', 'd' to move up, left, down, right: ").lower()
                move_func = {'w': self.move_up, 'a': self.move_left, 's': self.move_down, 'd': self.move_right}.get(dir_input)
                if move_func and move_func():
                    self.add_new_tile()
                else:
                    print("Invalid move. Try again.")
                    continue

            if self.check_win():
                self.print_board()
                print("Congratulations! You've won the game!")
                break

        if self.agent:
            self.agent.final(GameState(self.board, self.score, self.dim))

        self.print_board()
        print("Game Over!")
        print(f"Final Score: {self.score}")



class GameState:

    def __init__(self, board: list, score: int, dim: int) -> None:
        
        self.board = [row[:] for row in board] #Deep copy
        self.score = score
        self.dim = dim


    def add_new_tile(self):
        empty_cells = [(r, c) for r in range(self.dim) for c in range(self.dim) if self.board[r][c] == 0]
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.board[r][c] = random.choices([2, 4], weights=(90, 10), k=1)[0]

    def compress(self, row):
        """ Compress the non-zero elements of the board toward the front (left for rows) """
        return [num for num in row if num != 0]

    def merge(self, row, update_score=True):
        for i in range(len(row) - 1):
            if row[i] == row[i + 1]:
                if update_score:
                    self.score += row[i] * 2
                row[i] *= 2
                row[i + 1] = 0
        return row

    def move_left(self, update_score=True):
        moved = False
        for i in range(self.dim):
            original_row = self.board[i].copy()
            compressed_row = self.compress(original_row)
            merged_row = self.merge(compressed_row, update_score)
            merged_and_compressed_row = self.compress(merged_row)
            self.board[i] = merged_and_compressed_row + [0] * (self.dim - len(merged_and_compressed_row))
            if original_row != self.board[i]:
                moved = True
        return moved
    
    def move_down(self, update_score=True):
        self.board = self.rotate_board(self.board)
        moved = self.move_left(update_score)
        for _ in range(3):
            self.board = self.rotate_board(self.board)
        return moved

    def move_up(self, update_score=True):
        for _ in range(3):
            self.board = self.rotate_board(self.board)
        moved = self.move_left(update_score)
        self.board = self.rotate_board(self.board)
        return moved

    def move_right(self, update_score=True):
        self.board = self.rotate_board(self.board)
        self.board = self.rotate_board(self.board)
        moved = self.move_left(update_score)
        self.board = self.rotate_board(self.board)
        self.board = self.rotate_board(self.board)
        return moved
    
    def rotate_board(self, board: list):
        """ Rotate the given board 90 degrees clockwise. """
        return [list(row) for row in zip(*reversed(board))]
    
    def simulate_move(self, move_func):
        original_board = [row[:] for row in self.board]
        move_func(update_score=False)  # Pass False to avoid updating score
        changed = self.board != original_board
        self.board = original_board  # Reset board after simulation
        return changed
    
    def valid_moves(self):
        """Return a list of valid moves and their functions."""
        moves = []
        for direction, func in [('left', self.move_left), ('right', self.move_right), ('up', self.move_up), ('down', self.move_down)]:
            original_board = [row[:] for row in self.board]  # Preserve original board
            if func(update_score=False):
                moves.append(direction)
            self.board = original_board  # Reset the board
        return moves

    
    def get_score(self):

        return self.score







                



