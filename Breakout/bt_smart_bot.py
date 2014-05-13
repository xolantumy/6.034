import signal
import bt_game

class BtSmartBot(bt_game.BtBot):
    def __init__(self, first_player, my_sym, opp_sym):
        bt_game.BtBot.__init__(self, first_player, my_sym, opp_sym)

    def move(self, move, board):
        """
        Notes:  
        1 You just need to code this function.  Probably the easiest way to
          understand the data structures is to look at BtRandomBot in bt_game.py
        
        2 variable 'move':
          a) Please UPDATE (not assign) this variable like this:
             move[0][0] = old row
             move[0][1] = old column
             move[1][0] = new row
             move[1][1] = new column
          
             (rant: python, java, etc try to abstract away the notion of
              pointers, but in reality, we can't do away with it....)
          
          b) Once time is up, the caller will use whatever it is there
          
          c) It is initialized to an invalid value [ [-1,-1], [-1,-1] ].
             You'll be disqualified if you propose an invalid move, but
             you can easily check if your move is valid with

                self.is_valid_move(self,board,move)

        3 board 'variable':
          a) board.rows = number of rows
             board.cols = number of colums
             board.mat  = list of list of characters (i.e. a 2-d array)

             board.mat[r][c] gives the contents of cell at row r column c.
             It can take three possible values
             i)   ' ': empty space
             ii)  self._my_sym: character denoting your pawn
             iii) self._opp_sym: character denoting your opponent's pawn

             r ranges from 0 to (board.rows-1), likewise for c

             If self._first_player is true, then your goal is to move a
             pawn to row (board.rows-1).  Otherwise, advance to row 0

             
          b) You can modify it if you wish because the caller has made a copy
        """
        raise Exception("Please remove this exception and implement your function here")
    
