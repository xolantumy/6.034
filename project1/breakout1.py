
from bt_game import BtBot
from bt_game import BtBoard
import random





        
class BreakoutBot1(BtBot):
    def __init__(self, first_player, my_sym, opp_sym):
        BtBot.__init__(self, first_player, my_sym, opp_sym)
        

    def spot_with_my_piece(self, board):
        [i, j] = [random.randint(0,9),random.randint(0,8)]
        while board.mat[i][j] != self._my_sym:
            [i, j] = [random.randint(0,9), random.randint(0,8)]
        spot = [i,j]
        return spot

    def pick_spot_and_move(self, board):
        valid_moves = (self._first_player \
              and [[ (1,-1), (1,0), (1,1) ]] \
              or [[ (-1,-1), (-1,0), (-1,1) ]])[0]
      
        spot = self.spot_with_my_piece(board)
        themove = random.choice(valid_moves)
        mmove = [[spot[0], spot[1]],
                 [themove[0]+spot[0], themove[1]+spot[1]]]
     
        while self.is_valid_move(board, mmove) == False:
            spot = self.spot_with_my_piece(board)
            themove = random.choice(valid_moves)
            mmove = [[spot[0], spot[1]],
                 [themove[0]+spot[0], themove[1]+spot[1]]]
        return (spot,[spot[0]+themove[0], spot[1]+themove[1]])
    
    def move(self, move, board):
        # AI-Complete Implementation Here
        (spot, mymove) = self.pick_spot_and_move(board)
        #set the move variable (absolute coordinates)
        #using the spot variable (absolute coordinates)
        #and the mymove variable (relative coordinates)

        r1 = spot[0]
        c1 = spot[1]
        r2 = mymove[0]
        c2 = mymove[1]
        
        self.assign_move(move, r1, c1, r2, c2)
        return move
