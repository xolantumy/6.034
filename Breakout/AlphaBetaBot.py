import bt_game
from bt_game import BtBot
import copy

class SimpleAlphaBetaBot(BtBot):
    def __init__(self, first_player, my_sym, opp_sym):
        BtBot.__init__(self, first_player, my_sym, opp_sym)

    def result(self, move, board):
        # Don't change any code here.
        # You will use this function below in your max_value and min_value 
        # implementations. This safely copies the board and makes a move.
        newboard = copy.deepcopy(board)
        newboard.move(move)
        return newboard
    
    # YOUR EDITS GO BELOW ! YOUR EDITS GO BELOW ! YOUR EDITS GO BELOW !    
    # YOUR EDITS GO BELOW ! YOUR EDITS GO BELOW ! YOUR EDITS GO BELOW !    
    # -----------------------------------------------------------------
    # -- Your task: change the code with "TODO" markers below.
    # -- Your goal is to implement Alpha-Beta Pruning as outlined in class. 
    # -- The code stubs below match the algorithm provided in the book on p.170
    # -----------------------------------------------------------------
    # YOUR EDITS GO BELOW ! YOUR EDITS GO BELOW ! YOUR EDITS GO BELOW !    
    # YOUR EDITS GO BELOW ! YOUR EDITS GO BELOW ! YOUR EDITS GO BELOW !    

    def name(self):
        # TODO
        # --------------------------------------------------------------        
        # Return your name here
        return "Xola Ntumy"
    
    def move(self, move, board):
        # TODO
        # --------------------------------------------------------------        
        # Call alpha_beta_search and then use its results to assign a move
        # with the assign_move helper method on the base class.
        #
        # The game harness will automatically stop you after a fixed timeout.
        # Whatever move you have set when that occurs will be counted as
        # the move your bot will make. 
        #
        # Hint: here's your chance to do iterative deepening!
        for i in range(50):
            move = self.alpha_beta_search(board,i)
            #print move
            ##assign moves
        return move
        
    
    def alpha_beta_search(self, board, cutoff_depth):
        alpha = -float('inf')
        beta = float('inf')
        v = self.max_value(board, alpha, beta, cutoff_depth, 0)
        moves = self.possible_moves(board, self._first_player)
        for m in moves:
            if m == v:
                return v
        return
        
    def min_value(self, board, alpha, beta, cutoff_depth, current_depth):
        if self.cutoff_test(board, cutoff_depth, current_depth):
            return self.utility(board)
        v = float('inf')
        for move in self.possible_moves(board, self._first_player):
            ##cgange current depth
            v = min(v, self.max_value(self.result(move, board), alpha, beta, cutoff_depth, current_depth))
            if v <= alpha:
                return v
            beta = min(beta, v)

        return v
        
    def max_value(self, board, alpha, beta, cutoff_depth, current_depth):
        if self.cutoff_test(board, cutoff_depth, current_depth):
            return self.utility(board)
        v = -float('inf')
        for move in self.possible_moves(board, self._first_player):
            v = max(v, self.min_value(self.result(move, board), alpha, beta, cutoff_depth, current_depth))
            if v >= beta:
                return v
            alpha = max(alpha, v)

        return v
        
    def utility(self, board):
        # TODO
        # --------------------------------------------------------------
        # Implement the following utility function
        # If this board is a win for me, return 10000
        # Else, return number_my_pieces - number_opponent_pieces
        if board.winner(self._my_sym, self._opp_sym) == self._my_sym:
            return 10000
        else:
            num_my_sym = 0
            num_opp_sym = 0
            for i in range(len(board.cols)):
                for j in range(len(board.rows)):
                    if self.mat[i][j] == self._my_sym:
                        num_my_sym += 1
                    elif self.mat[i][j] == self._opp_sym:
                        num_opp_sym += 1

            return num_my_sym - num_opp_sym
                        
        
        
    def possible_moves(self, board, player):
        # TODO
        # --------------------------------------------------------------
        # Return a list of 2x2 arrays that represent all possible moves
        # given the current state of the board. This list should represent
        # ALL possible actions that the player specified by the "player"
        # variable could take given a particular board. 
        # Recall that these moves use absolute coordinates and 
        # must be legal according to the rules of the game.
        # 
        # Suggestion: pass in either self._opp_sym or self._my_sym
        # to specify the player.


        ##specify first-player
        possibleMoves = (player == self._my_sym\
              and [[ [[1],[-1]], [[1],[0]], [[1],[1]] ]] \
              or [[ [[-1],[-1]], [[-1],[0]], [[-1],[1]] ]])[0]
        
        player_pos = []
        possible_moves = []
        for row in range(board.rows):
            for col in range(board.cols):
                if board.mat[row][col] == player:
                    player_pos.append([row,col])
                    
        for (row,col) in player_pos:
            for move in possibleMoves:
                pos_move = [[row,col],[row+move[0][0], col+move[0][1]]]
                if self.is_valid_move(board, pos_move, player):
                    print pos_move
                    possible_moves.append(pos_move)

        return possible_moves
        
        
    def cutoff_test(self, board, cutoff_depth, current_depth):
        # TODO
        # --------------------------------------------------------------
        # See p. 173 of the book 
        # If depth > 2: return true
        # else:
        #    Return True if this board represents a win for me.
        #    False otherwise
        # 
        if current_depth > cutoff_depth:
            return True
        else:
            if board.winner(self._my_sym, self._opp_sym) == self._my_sym:
                return True
            else:
                return False


    




