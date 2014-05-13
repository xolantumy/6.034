import random
import time
import signal
import traceback
import sys
import bt_game
import bt_dumb_bot

def bt_time_machine(timeout):
    rows = 10
    cols = 9
    bot1 = bt_dumb_bot.BtDumbBot(True,'o','x')
    bot2 = bt_dumb_bot.BtDumbBot(False,'x','o')
    board = bt_game.BtBoard(rows,cols)
    signal.signal(signal.SIGALRM, signal_handler)
    N = []
    T = []
    for t in range(3):
        signal.alarm(timeout)
        start = time.time()
        total = 0
        n = 1
        try:
            for i in range(10**5):
                m = [ [-1,-1], [-1,-1] ]
                for r in range(rows):
                    for c in range(cols):
                        j = random.randint(1,10)
                        if j <= 6:
                            board.mat[r][c] = ' '
                        elif j <= 8:
                            board.mat[r][c] = 'x'
                        else:
                            board.mat[r][c] = 'o'
                        if board.mat[r][c] != ' ':
                            m = [ [r,c], [-1,-1] ]
                for r in range(rows):
                    for c in range(cols):
                        s = board.mat[r][c]
                        if s != ' ':
                            i = (s == 'o' and [1] or [-1])[0]
                            for j in [-1,0,1]:
                                bot = (s == 1 and [bot1] or [bot2])[0]
                                r2 = r + i
                                c2 = c + j
                                if bot.is_valid_move(board,[ [r,c], [r2,c2] ]):
                                    m = [ [r,c], [r2,c2] ]
                                    total += bot.score_move(board,m)
                n += 1
        except bt_game.TimeoutException:
            pass
        except Exception, msg:
            traceback.print_exc(file=sys.stdout)
            pass
        signal.alarm(0)
        end = time.time()
        N.append(n)
        T.append(end-start)
    #print "n = ",n," time = ",end-start
    n = 1.0*sum(N)/len(N)
    t = 1.0*sum(T)/len(T)
    return [n,t]

def signal_handler(signum,frame):
    #raise Exception("Time out [signum=%d,frame=%s]" % (signum,frame))
    raise bt_game.TimeoutException("Time out [signum=%d,frame=%s]" % (signum,frame))

if __name__ == '__main__':
    [n,s] = bt_time_machine(1)
    print n," ",s
