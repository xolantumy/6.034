import socket
import sys
import signal
import datetime
import string
import time
import random
import traceback
import StringIO
import bt_game
import bt_dumb_bot
import bt_smart_bot
import bt_protocol

class BtClient:
    def __init__(self,id,BotClass):
        self.id = id
        self.board = None
        self.bot = None
        self.BotClass = BotClass
        self.gui = bt_game.BtTextGui()

    def log(self,x):
        if False:
            print "[%s] " % self.id,
            print x

    def timestamp(self):
        return string.replace(str(datetime.datetime.now()), ' ', '_')

    def play(self,host,port):
        eom = bt_protocol.eom
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.log("connecting to server..")
            s.connect((host,port))
            s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 0) 
            self.log("connected to %s %d" % (host,port))
        except Exception,msg:
            print msg
            print "can't connect to server"
            return None
        
        buf = ''
        try:
        #if True:
            while True:
                assert eom not in buf
                while eom not in buf:
                    x = s.recv(1024)
                    if len(x) == 0: raise Exception("[%s] server closed connection" % self.timestamp())
                    buf = buf + x
                while buf and eom in buf:
                    i = string.find(buf,eom)
                    m = buf[0:i+1]
                    buf = buf[i+1::]

                    # protocol here
                    m0 = m[0]
                    ml = len(m)
                    if ml > 40:
                        ml = 40
                        self.log("mesg (%d) is %s..." % (ml,m[0:ml]))
                    else:
                        self.log("mesg (%d) is [%s]" % (ml,m))
                        
                    if m0 == eom: # disconnect
                        raise Exception("disconnecting")
                    elif m0 == 'm':
                        s.sendall(self.move(m) + " " + eom)
                    elif m0 == 'w':
                        self.display_winner(m)
                    elif m0 == 'l':
                        self.display_last_move(m)
                    elif m0 == 'n':
                        self.new_game(m)
                    elif m0 == 'b':
                        self.set_board(m)
                        self.gui.display_board(self.board)
                    elif m0 == 'a':
                        self.announce(m)
                    elif m0 == 'd':
                        pass # discard
                    elif m0 == 'i':
                        s.sendall("i %s %s" % (self.id, eom)) # send userid
                    else:
                        self.log("ignoring unknown header %s" % m0)
                        pass
                # while eom not in buf
            # while True
        except Exception,msg:
            fp = StringIO.StringIO()
            traceback.print_exc(file=fp)
            self.log(fp.getvalue())
            self.log("caught Exception")
            self.log(msg)
        self.log("closing connection")
        s.close()
        self.log("connection closed.")

    def announce(self,msg):
        assert msg[-1] == bt_protocol.eom
        msg = msg[0:-1]
        assert msg[0] == 'a'
        self.gui.display_msg(msg[2::])

    def display_winner(self,msg):
        assert msg[-1] == bt_protocol.eom
        msg = msg[0:-1]
        a = msg.split()
        assert a[0] == 'w'
        winner = a[1]
        self.gui.display_winner(winner,self.bot.get_my_sym())

    def set_board(self,msg):
        assert msg[-1] == bt_protocol.eom
        msg = msg[0:-1]
        tokens = msg.split()
        header = tokens.pop(0)
        assert header == 'b'

        rows = int(tokens.pop(0))
        cols = int(tokens.pop(0))
        self.board = bt_game.BtBoard(rows, cols)

        sym1 = tokens.pop(0)
        num1 = int(tokens.pop(0))
        for i in range(num1):
            r = int(tokens.pop(0))
            c = int(tokens.pop(0))
            self.board.mat[r][c] = sym1

        if tokens:
            sym2 = tokens.pop(0)
            num2 = int(tokens.pop(0))
            for i in range(num2):
                r = int(tokens.pop(0))
                c = int(tokens.pop(0))
                self.board.mat[r][c] = sym2

    def show_winner(self,msg):
        header = msg[0]
        assert header == 'w'
        winner = msg[2]
        if winner != ' ':
            self.gui.show_winner(winner)
    
    def move(self,msg):
        assert msg[-1] == bt_protocol.eom
        msg = msg[0:-1]
        tokens = msg.split()
        header = tokens.pop(0)
        assert header == 'm'
        timeout = int(tokens.pop(0))
        move = [ [-1,-1], [-1,-1] ]
        self.log("timeout is %d" % timeout)
        signal.alarm(timeout)
        try:
            self.bot.move(move,self.board)
            #move = [ [-1,-1], [-1,-1] ]
            #time.sleep(10)
        except bt_game.TimeoutException:
            pass
        except Exception,msg: # timeout
            traceback.print_exc(file=sys.stdout)
            #print "[BtClient] exception caught:", msg
            pass 
        signal.alarm(0)
        self.log("propose move %d %d => %d %d" % (move[0][0],move[0][1],move[1][0],move[1][1]))
        s = "m %d %d %d %d" % (move[0][0],move[0][1],move[1][0],move[1][1])
        self.log("sending: %s" % s)
        return s

    def new_game(self,msg):
        assert msg[-1] == bt_protocol.eom
        msg = msg[0:-1]
        tokens = msg.split()
        header = tokens.pop(0)
        assert header == 'n'
        first_player = (tokens.pop(0) == '1' and [True] or [False])[0]
        my_sym = tokens.pop(0)
        opp_sym = tokens.pop(0)
        self.bot = self.BotClass(first_player, my_sym, opp_sym)
        
    def display_last_move(self,msg):
        assert msg[-1] == bt_protocol.eom
        msg = msg[0:-1]
        tokens = msg.split()
        header = tokens.pop(0)
        assert header == 'l'
        iteration = int(tokens.pop(0))
        player_sym = tokens.pop(0)
        r1 = int(tokens.pop(0))
        c1 = int(tokens.pop(0))
        r2 = int(tokens.pop(0))
        c2 = int(tokens.pop(0))
        #time_taken = float(tokens.pop(0))
        time_taken = None
        move = ((r1,c1), (r2,c2))
        self.gui.log_move(iteration, player_sym, move, time_taken)

def signal_handler(signum,frame):
    #raise Exception("BtClient Time out [signum=%d,frame=%s]" % (signum,frame))
    raise bt_game.TimeoutException("Time out [signum=%d,frame=%s]" % (signum,frame))

if __name__ == '__main__':
    signal.signal(signal.SIGALRM, signal_handler)
    userid = sys.argv[1]
    host = sys.argv[2]
    port = int(sys.argv[3])
    #BotClass = bt_game.BtRandomBot
    #BotClass = bt_dumb_bot.BtDumbBot
    BotClass = bt_smart_bot.BtSmartBot
    client = BtClient(userid,BotClass)
    client.play(host,port)
