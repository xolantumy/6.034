import sys
import signal
import time
import copy
import random
import traceback

class TimeoutException(Exception):
    pass

class BtGame:
    def __init__(self, rows, cols, initn, sym1, sym2, timeout1, timeout2):
        assert sym1 != ' '
        assert sym2 != ' '
        self._timeout1 = timeout1
        self._timeout2 = timeout2
        self._rows = rows
        self._cols = cols
        self._init_rows = initn
        self._sym1 = sym1
        self._sym2 = sym2
        self._board = None
        self._winner = None
        self._moves = []

    def add_move(self,move): self._moves.append(move)

    def get_moves(self): return self._moves

    def set_winner(self,sym):
        self._winner = sym
        
    def move(self,move):
        self._board.move(move)

    def is_in_bounds(self,r,c):
        if r >= 0 and c >= 0 and r < self._rows and c < self._cols:
            return True
        else:
            return False

    def is_valid_move(self,move):
        r1 = move[0][0]
        c1 = move[0][1]
        r2 = move[1][0]
        c2 = move[1][1]
        if self.is_in_bounds(r1,c1) and self.is_in_bounds(r2,c2):
            # must be one move way
            s = (self._turn == self._sym1 and [1] or [-1])[0]
            if r2 - r1 == s and abs(c2 - c1) <= 1:
                if self._board.mat[r1][c1] != self._turn:
                    return False
                else:
                    if self._board.mat[r2][c2] != self._turn:
                        # must capture diagonally
                        if self._board.mat[r2][c2] != ' ':
                            if abs(r1-r2) == 1 and abs(c1 - c2) == 1:
                                return True
                            else:
                                return False
                        else:
                            return True
                    else:
                        return False
            else:
                return False
        else:
            return False
        
    def is_game_over(self):
        return self.winner() != None

    def set_turn(selfb,t):
        self._turn = t
    
    def board(self):
        return self._board

    def winner(self):
        if self._winner != None:
            return self._winner
        
        # check final row
        if [x for x in self._board.mat[0] if x == self._sym2]:
            self._winner = self._sym2
        else:
            if [x for x in self._board.mat[-1] if x == self._sym1]:
                self._winner = self._sym1
            else:
                # check if any surviving pawns
                if sum([row.count(self._sym2) for row in self._board.mat]) == 0:
                    self._winner = self._sym1
                else:
                    if sum([row.count(self._sym1) for row in self._board.mat]) == 0:
                        self._winner = self._sym2
        return self._winner

    def savelog(self, logfile, userid1, userid2, winner):
        logfile.write("==game== rows %d cols %d init_rows %d %s vs %s winner(0|1) %d\n" % \
                      (self._rows,self._cols,self._init_rows,userid1,userid2,winner) )
        logfile.write("%d moves\n" % len(self._moves))
        for m in self._moves:
            logfile.write("%d %d %d %d\n" % (m[0][0],m[0][1],m[1][0],m[1][1]))
        logfile.flush()

    def play(self, bot1, bot2, gui, verbose=2):
        if verbose: print "starting game..."
        self._moves = []
        self._board = BtBoard(self._rows,self._cols)
        self._board.new_game(self._sym1, self._sym2, self._init_rows)
        self._turn = self._sym1

        print "%s is playing %s" % (bot1.name(), self._sym1)
        print "%s is playing %s" % (bot2.name(), self._sym2)
        

        bot = bot1
        iteration = 0
        timeout = self._timeout1
        msg = ""
        game_over = False
        if verbose: gui.display_board(self._board)
        while not game_over:
            # get move
            move = [ [-1,-1], [-1,-1] ];

            # copy board since constant objects not supported
            board = copy.deepcopy(self._board)

            # set time limit and ask for move
            signal.alarm(timeout)
            start = time.time()
            #if True:
            try:
                bot.move(move,board)
            except TimeoutException:
                pass
            except Exception, msg:
                traceback.print_exc(file=sys.stdout)
                #print "Time out! [%d] seconds %s" % (timeout,msg)
                pass
            signal.alarm(0)
            time_taken = time.time() - start

            # move and update board
            self.add_move(move)
            if self.is_valid_move(move):
                self.move(move)
                msg = ""
            else:
                msg = "invalid move!"
                self.set_winner( (self._turn == self._sym1 and [self._sym2] or [self._sym1])[0] )

            if verbose:
                gui.log_move(iteration, self._turn, move, time_taken)
                gui.display_msg(msg)
                gui.display_board(self._board)

            # prep for next iteration
            game_over = self.is_game_over()
            # toggle
            if self._turn == self._sym1:
                self._turn = self._sym2
                bot = bot2
                timeout = self._timeout2
            else:
                self._turn = self._sym1
                bot = bot1
                timeout = self._timeout1
            iteration += 1
        # while not game_over
        
        if verbose: gui.display_winner(self.winner(),None);
        assert self._winner != None
        winner = (self.winner() == self._sym1 and [0] or [1])[0]
        if verbose > 1: self.savelog(sys.stdout, self._sym1, self._sym2, winner)
        #for i in range(len(self.get_moves())):
        #    c = (i % 2 == 0 and [self._sym1] or [self._sym2])[0]
        #    m = self._moves[i]
        #    print "%c %d %d => %d %d" % (c,m[0][0],m[0][1],m[1][0],m[1][1])
        return winner # 0 for first player

class BtTextGui:
    def display_winner(self,winner,me):
        print "gameover: player %s won!" % winner
        if me != None:
            if winner == me:
                print "you won!"
            else:
                print "you lost!"

    def display_board(self,board):
        # print board
        print "  ",
        for x in range(board.cols):
            print "%c" % "_",
        print "\n",
        for r in range(board.rows)[::-1]:
            rr = r % 10
            print "%d|" % rr,
            for c in range(board.cols):
                entry = board.mat[r][c]
                print "%c" % entry,
            print "|\n",
        print "  ",
        for x in range(board.cols):
            xx = x % 10
            print "%d" % xx,
        print "\n"

    def log_move(self,iteration,player_sym,move,time_taken):
        if time_taken != None:
            print "move #%d: %s [%d,%d] => [%d,%d] (took %f secs)" \
                  % (iteration,player_sym,move[0][0],move[0][1],move[1][0],move[1][1],time_taken)
        else:
            print "move #%d: %s [%d,%d] => [%d,%d]" \
                  % (iteration,player_sym,move[0][0],move[0][1],move[1][0],move[1][1])
            
    def display_msg(self,msg):
        if msg:
            print msg 
        
class BtBoard:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        # first index is row. second one column
        mat = [[' ' for col in range(cols)] for row in range(rows)]
        self.mat = mat

    def new_game(self, sym1, sym2, n):
        # first player occupies first two rows (i.e. lowest two row indices)
        for r in range(n): self.mat[r] = [sym1 for x in self.mat[r]]
        # second player last two rows
        for r in range(-n,0): self.mat[r] = [sym2 for x in self.mat[r]]

    def move(self,move):
        # assume move is valid
        i = move[0][0]
        j = move[0][1]
        r = move[1][0]
        c = move[1][1]
        beforeR = self.mat[r][c]
        self.mat[r][c] = self.mat[i][j]
        before = self.mat[i][j]
        self.mat[i][j] = ' '

    def winner(self, sym1, sym2):
        # check final row
        if [x for x in self.mat[0] if x == sym2]:
            return sym2
        else:
            if [x for x in self.mat[-1] if x == sym1]:
                return sym1
            else:
                # check if any surviving pawns
                if sum([row.count(sym2) for row in self.mat]) == 0:
                    return sym1
                else:
                    if sum([row.count(sym1) for row in self.mat]) == 0:
                        return sym2
        return None

class BtBot:
    def __init__(self, first_player, my_sym, opp_sym):
        self._first_player = first_player
        self._my_sym = my_sym
        self._opp_sym = opp_sym

    def get_my_sym(self):
        return self._my_sym

    def name(self):
        return "Anonymous Bot"

    def is_valid_move(self,board,move):
        r1 = move[0][0]
        c1 = move[0][1]
        r2 = move[1][0]
        c2 = move[1][1]
        if r1 >= 0 and r1 < board.rows and c1 >= 0 and c1 < board.cols \
           and r2 >= 0 and r2 < board.rows and c2 >= 0 and c2 < board.cols:
            # must be one move way
            s = (self._first_player and [1] or [-1])[0]
            if r2 - r1 == s and abs(c2 - c1) <= 1:
                if board.mat[r1][c1] != self._my_sym:
                    return False
                else:
                    if board.mat[r2][c2] != self._my_sym:
                        # must capture diagonally
                        if board.mat[r2][c2] != ' ':
                            if abs(r1-r2) == 1 and abs(c1 - c2) == 1:
                                return True
                            else:
                                return False
                        else:
                            return True
                    else:
                        return False
            else:
                return False
        else:
            return False

    def move(self, move, board):
        raise Exception("abstract virtual method BtBot::move() not implemented")

    def assign_move(self,move,r1,c1,r2,c2):
        move[0][0] = r1
        move[0][1] = c1
        move[1][0] = r2
        move[1][1] = c2






class HumanBtBot(BtBot):
    def __init__(self, first_player, my_sym, opp_sym):
        BtBot.__init__(self, first_player, my_sym, opp_sym)

    def move(self, move, board):
        m = raw_input("enter move> ").split()
        move[0][0] = int(m[0])
        move[0][1] = int(m[1])
        move[1][0] = int(m[2])
        move[1][1] = int(m[3])


class BtRandomBot(BtBot):
    def __init__(self, first_player, my_sym, opp_sym):
        BtBot.__init__(self, first_player, my_sym, opp_sym)

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

        mm = (self._first_player \
              and [[ (1,-1), (1,0), (1,1) ]] \
              or [[ (-1,-1), (-1,0), (-1,1) ]])[0]
        
        random.shuffle(l[self._my_sym])
        score = -float('inf')
        for pos in l[self._my_sym]:
            random.shuffle(mm)
            for m in mm:
                r = pos[0] + m[0]
                c = pos[1] + m[1]
                if self.is_valid_move(board,[pos,[r,c]]):
                    # win
                    if self._first_player:
                        if r == board.rows-1:
                            self.assign_move(move, pos[0], pos[1], r, c)
                            return None
                    else:
                        if r == 0:
                            self.assign_move(move, pos[0], pos[1], r, c)
                            return None
                    # capture
                    if board.mat[r][c] == self._opp_sym and score < 1:
                        self.assign_move(move, pos[0], pos[1], r, c)
                        score = 1
                    # any valid move
                    if score < 0:
                        self.assign_move(move, pos[0], pos[1], r, c)
                        score = 0