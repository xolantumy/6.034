import signal
import copy
import random
import time
import bt_game

class BtDumbBot(bt_game.BtBot):
    def __init__(self, first_player, my_sym, opp_sym):
        bt_game.BtBot.__init__(self, first_player, my_sym, opp_sym)

    def score_move(self, board, move):
        # pre: move is valid
        r1 = move[0][0]
        c1 = move[0][1]
        r2 = move[1][0]
        c2 = move[1][1]
        ind = (self._first_player and [-1] or [0])[0]

        #print "r1 %d c1 % r2 %d c2 %d me [%s] opp [%s]"% (r1,c1,r2,c2,self._my_sym,self._opp_sym)
        if (self._first_player and [r2 == board.rows-1] or [r2 == 0])[0]:
            return float('inf') # i win

        t = (self._first_player and [r2] or [board.rows-1-r2])[0]
        q = (not self._first_player and [r2] or [board.rows-1-r2])[0]
        score = t # closer to target zone, higher the score
        if board.mat[r2][c2] == self._opp_sym:
            score += q # capture

        mmm = (self._first_player and [((1,1),(1,-1))] or [((-1,1),(-1,-1))])[0]
        kill_zone = 0
        for mm in mmm:
            r3 = r2 + mm[0]
            c3 = c2 + mm[1]
            if r3 >= 0 and r3 < board.rows and c3 >= 0 and c3 < board.cols:
                if board.mat[r3][c3] == self._opp_sym:
                    kill_zone += 1
            if kill_zone > 0:
                score -= t # if can be captured, negate it
        return score

    def move(self, move, board):
        # get inverted list
        l = {}
        for r in range(board.rows):
            for c in range(board.cols):
                sym = board.mat[r][c]
                pos = (r,c)
                if sym in l:
                    l[sym].append(pos)
                else:
                    l[sym] = [pos]

        # look one step ahead and pick the "best" move
        best_score = - float('inf')
        mm = self._first_player \
              and [ (1,-1), (1,0), (1,1) ] \
              or [ (-1,-1), (-1,0), (-1,1) ]
        
        random.shuffle(l[self._my_sym])
        #print l[self._my_sym]
        for pos in l[self._my_sym]:
            #print "examining options for %d %d %c" % (pos[0],pos[1],self._my_sym)
            random.shuffle(mm)
            for m in mm:
                r = pos[0] + m[0]
                c = pos[1] + m[1]
                if self.is_valid_move(board,[pos,[r,c]]):
                    b = copy.deepcopy(board)
                    score = self.score_move( b, (pos,(r,c)) )
                    #b.move((pos,(r,c)))
                    #score = self.score_board(b)
                    #print "%s: move (%d,%d) => (%d,%d) scores %f" % (self._my_sym,pos[0],pos[1],r,c,score)
                    if score > best_score:
                        #print "  %s updating move to (%d,%d) => (%d,%d) with score %5.2f => %5.2f" % (self._my_sym,pos[0],pos[1],r,c,best_score,score)
                        move[0][0] = pos[0]
                        move[0][1] = pos[1]
                        move[1][0] = r
                        move[1][1] = c
                        best_score = score
        # for pos
        #print "all moves considered"
        #print "dumbbot sleeping..."
        #time.sleep(5)
