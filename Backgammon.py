import copy


class Cell:
    def __init__(self, color, num):
        self.color = color
        self.num = num

    def __str__(self):
        return '(' + self.color + ":" + str(self.num) + ')'

    def reduce(self):
        self.num = self.num - 1
        if self.num == 0:
            self.color = "NONE"

    def increase(self, color):
        if self.color == "NONE":
            self.color = color
            self.num = 1
        else:
            self.num = self.num + 1

    def __eq__(self, other):
        if not isinstance(other, Cell):
            return False
        return self.color == other.color and self.num == other.num


class Backgammon:
    def __init__(self):
        board = [None] * 26
        for i in range(0, 26):
            if i == 1:
                board[i] = Cell("BLACK", 2)
            elif i == 6:
                board[i] = Cell("WHITE", 5)
            elif i == 8:
                board[i] = Cell("WHITE", 3)
            elif i == 12:
                board[i] = Cell("BLACK", 5)
            elif i == 13:
                board[i] = Cell("WHITE", 5)
            elif i == 17:
                board[i] = Cell("BLACK", 3)
            elif i == 19:
                board[i] = Cell("BLACK", 5)
            elif i == 24:
                board[i] = Cell("WHITE", 2)
            else:
                board[i] = Cell("NONE", 0)
        self.board = board
        self.curr_player = "BLACK"
        self.jail = {"BLACK": 0, "WHITE": 0}

    def __key(self):
        return str(self)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Backgammon):
            return self.__key() == other.__key()
        return NotImplemented

    def __str__(self):
        ret = ""
        for cell in self.board:
            ret += str(cell) + ","
        ret += str(self.jail)
        return ret

    __repr__ = __str__

    def can_move(self, cell, color):
        if cell.color == color or cell.color == "NONE":
            return True
        elif cell.num <= 1:
            return True
        else:
            return False

    def get_board_after_move(self, from_ind, to_ind):
        new_board = copy.deepcopy(self)
        from_cell, to_cell = new_board.board[from_ind], new_board.board[to_ind]
        if to_cell.color == from_cell.color or to_cell.color == "NONE":
            to_cell.increase(from_cell.color)
        else:
            new_board.jail[to_cell.color] += 1
            to_cell.color = from_cell.color
        from_cell.reduce()
        return new_board

    def is_in_house(self, color):
        if color == "WHITE":
            start, end = 0, 7
        else:
            start, end = 19, 26
        sum = 0
        for i in range(start, end):
            cell = self.board[i]
            if cell.color == color:
                sum += cell.num
        return sum == 15

    def is_win(self, color):
        if color == "WHITE":
            return self.board[0].num == 15
        else:
            return self.board[25].num == 15

    def get_moves(self, dice1, dice2, color):
        curr_boards = [self]
        curr_boards = set(curr_boards)
        if dice1 == dice2:
            for i in range(4):
                new_boards = set()
                for board in curr_boards:
                    boards = set(board.do_one_move(dice1, color))
                    new_boards = new_boards.union(boards)
                if len(new_boards) == 0:
                    return curr_boards
                curr_boards = new_boards
            return curr_boards
        first_move = set(self.do_one_move(dice1, color))
        first_second = set()
        if len(first_move) > 0:
            for board in first_move:
                boards = set(board.do_one_move(dice2, color))
                first_second = first_second.union(boards)
        second_move = set(self.do_one_move(dice2, color))
        second_first = set()
        if len(second_move) > 0:
            for board in second_move:
                boards = set(board.do_one_move(dice1, color))
                second_first = second_first.union(boards)
        all_boards = first_second.union(second_first)
        if len(all_boards) == 0:
            return curr_boards
        return all_boards

    def do_one_move(self, dice, color):
        boards = []
        adjuster = dice
        if color == "WHITE":
            adjuster = 25 - dice
        if self.jail[color] > 0:
            if self.can_move(self.board[adjuster], color):
                board = copy.deepcopy(self)
                if board.board[adjuster].color != "NONE" and board.board[adjuster].color != color:
                    prev_color = board.board[adjuster].color
                    board.board[adjuster].reduce()
                    board.jail[prev_color] += 1
                board.board[adjuster].increase(color)
                board.jail[color] -= 1
        else:
            if color == "WHITE":
                dice = -dice
            for (i, cell) in enumerate(self.board):
                if cell.color == color:
                    if self.is_in_house(color):
                        if 25 >= i + dice >= 0:
                            if self.can_move(self.board[i + dice], color):
                                boards.append(self.get_board_after_move(i, i + dice))
                        else:
                            no_prev = True
                            if color == "WHITE":
                                for j in range(i + 1, 7):
                                    cell = self.board[j]
                                    if cell.color == color and cell.num > 0:
                                        no_prev = False
                                        break
                                if no_prev:
                                    board = copy.deepcopy(self)
                                    board.board[i].reduce()
                                    board.board[0].increase(color)
                            else:
                                for j in range(19, i - 1):
                                    cell = self.board[j]
                                    if cell.color == color and cell.num > 0:
                                        no_prev = False
                                        break
                                if no_prev:
                                    board = copy.deepcopy(self)
                                    board.board[i].reduce()
                                    board.board[25].increase(color)
                    else:
                        if 24 >= i + dice >= 1 and self.can_move(self.board[i + dice], color):
                            boards.append(self.get_board_after_move(i, i + dice))
        return boards
