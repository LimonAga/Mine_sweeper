import random

class Minesweeper:
    def __init__(self, size, mine_count):
        self.row_count, self.col_count = size[0], size[1]
        self.mine_count = mine_count
        self.board = [[0 for _ in range(self.col_count)] for _ in range(self.row_count)] #contains mines and numbers
        self.player_board = [['?' for _ in range(self.col_count)] for _ in range(self.row_count)] # board to be drawn

    def get_neighbours(self, row, col):
        '''Returns all avaible neigbour cells.'''
        offsets = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        neighbours = []
        for neighbour in offsets:
            x, y = row + neighbour[0], col + neighbour[1] #look for the neighbour coordinates
            if not self.is_valid(x, y):
                continue #skip this cell if it's not on the board
            neighbours.append((x,y))
        return neighbours

    def place_mines(self, row, col):
        '''Places mines on the board randomly. Never places a mine to the given starting position.'''
        empty_cells = [(row,col)]+self.get_neighbours(row, col)

        while self.mine_count:
            #  generate random mine coordinates
            row, col = random.randint(0, self.row_count - 1), random.randint(0, self.col_count - 1)

            # place mines if they are not in the starting position
            if not self.is_bomb(row,col) and (row,col) not in empty_cells:
                self.board[row][col] = 'b'
                self.mine_count -= 1

        # Place numbers after the mines
        self.place_numbers()

    def place_numbers(self):
        '''Places all the numbers.'''
        for row in range(self.row_count):
            for col in range(self.col_count):
                if self.is_bomb(row, col): 
                    continue #if it's a mine skip this cell

                # Count the mines in the neighbour cells and place the number
                count = 0
                neighbours = self.get_neighbours(row, col)
                for neighbour in neighbours:
                    if self.is_bomb(neighbour[0], neighbour[1]): count += 1
                self.board[row][col] = count

    def reveal(self, row, col):
        """Reveals the content of a cell and updates the player's board.
        Returns 'lost' if a bomb is revealed."""

        if self.is_bomb(row, col): # Check for the lose
            return 'lost'

        elif self.is_unknown(row, col): # If cell is unknown, reveal all connected empty cells and numbers.
            cells = [(row, col)]
            while cells:
                cell = cells.pop()
                neighbours = self.get_neighbours(cell[0], cell[1])

                if self.board[cell[0]][cell[1]] == 0:# Look all nearby empty cells
                    for neighbour in neighbours:
                        row, col = neighbour[0], neighbour[1]

                        if self.is_unknown(row, col) and not self.is_bomb(row, col):
                            self.player_board[row][col] = self.board[row][col]

                            if self.board[row][col] == 0 and (row,col) not in cells:
                                cells.append((row,col))
                            else:
                                self.player_board[row][col] = self.board[row][col]
                else:
                    self.player_board[row][col] = self.board[row][col]

        # Easy flagging and revailing when clicked on a number.
        elif self.player_board[row][col] in range(1, 9):
            # Lose the game if adjacent flags are wrong
            if self.show_remaining(row,col) == 'lost':
                return 'lost'
            else:
                self.flag_remaining(row, col)

    def show_remaining(self, row, col):
        """Reveals remaining adjacent cells if the correct number of flags is placed."""
        neighbours = self.get_neighbours(row, col)
        flags = 0
        for cell in neighbours:
            if self.is_flag(cell[0], cell[1]): flags += 1

        if flags == self.board[row][col]:
            for cell in neighbours:
                row, col = cell[0], cell[1]

                if not self.is_flag(row, col):
                    if self.is_bomb(row, col): 
                        return 'lost' # Lose the game if player has flagged incorrectly

                    elif self.board[row][col] == 0: 
                        self.reveal(row, col)
                    self.player_board[row][col] = self.board[row][col]

    def flag_remaining(self, row, col):
        """Flags remaining safe cells if the sum of adjacent unknown cells and adjacent flags 
        is equal to the number indicated in the current cell."""
        remaining = 0
        neighbours = self.get_neighbours(row, col)
        for cell in neighbours:
            # Count the cells that are either flagged or unknown
            if self.player_board[cell[0]][cell[1]] in ['f', '?']: remaining += 1

        if remaining == self.player_board[row][col]:
            for cell in neighbours:
                if self.is_unknown(cell[0], cell[1]):
                    self.flag(cell[0], cell[1])

    def is_bomb(self, row, col):
        '''Check if the given cell is a bomb.'''
        return self.board[row][col] == 'b'

    def is_flag(self, row, col):
        '''Check if the given cell is flagged.'''
        return self.player_board[row][col] == 'f'

    def is_unknown(self, row, col):
        '''Check if the given cell is unkown.'''
        return self.player_board[row][col] == '?'

    def is_win(self):
        '''Check if the player has won the game.'''
        for row in range(self.row_count):
            for col in range(self.col_count):
                if self.is_unknown(row, col) and not self.is_bomb(row, col):
                    return False
        return True

    def flag(self, row, col):
        '''Flags or unflags the given cell.'''
        if self.is_unknown(row, col): # Flag
            self.player_board[row][col] = 'f'

        elif self.is_flag(row, col): # Unflag
            self.player_board[row][col] = '?'

    def is_valid(self, x, y):
        '''Check for boundaries.'''
        return (0 <= x < self.row_count and 0 <= y < self.col_count)

    def get_remaining_mines(self,mines):
        """Calculate the number of remaining mines based on flagged cells."""
        count = 0
        for row in range(self.row_count):
            for col in range(self.col_count):
                if self.is_flag(row, col): count += 1
        return mines - count    

    def solve(self):
        """Automatically flags and reveals cells. Only makes guaranteed moves."""
        for row_index, row in enumerate(self.player_board):
            for col_index, _ in enumerate(row):
                if self.player_board[row_index][col_index] in range(1, 9):
                    self.flag_remaining(row_index, col_index)
                    self.show_remaining(row_index, col_index)
