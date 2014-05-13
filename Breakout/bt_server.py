import sys
import socket
import thread
import threading
import random
import Queue
import logging
import time
import datetime
import string
import signal
import bt_game
import bt_protocol

class BtOnlineGame(bt_game.BtGame,threading.Thread):
    count = 0
    count_lock = threading.Lock()
    stats = []
    stats_lock = threading.Lock()
    def __init__(self, server_id, socket1, addr1, socket2, addr2, \
                 rows, cols, initn, sym1, sym2, timeout1, timeout2):
        self.server_id = server_id
        self.s1 = socket1
        self.a1 = addr1
        self.s2 = socket2
        self.a2 = addr2
        #self.rows = rows
        #self.cols = cols
        #self.sym1 = sym1
        #self.sym2 = sym2
        #self.timeout1 = timeout1
        #self.timeout2 = timeout2
        self._grace = 2
        BtOnlineGame.count_lock.acquire()
        BtOnlineGame.count += 1
        BtOnlineGame.count_lock.release()
        threading.Thread.__init__(self)
        bt_game.BtGame.__init__(self, rows, cols, initn, sym1, sym2, timeout1, timeout2)

    def get_client_id(self,s):
        s.sendall("i " + bt_protocol.eom)
        buf = ''
        while bt_protocol.eom not in buf:
            t = s.recv(64)
            if not t: raise Exception('client disconnected')
            if not buf and t and t[0] != 'i' : raise Exception('client violated id msg protocol')
            buf = buf + t
        a = buf.split()
        assert a[0] == 'i'
        return a[1]

    def send_board_to_all(self):
        eom = bt_protocol.eom
        board_msg = self.encode_board() + eom
        assert board_msg[-1] == eom
        self.s1.sendall(board_msg)
        self.s2.sendall(board_msg)

    def play_one_game(self,logfile):
        eom = bt_protocol.eom
        id1 = self.get_client_id(self.s1)
        id2 = self.get_client_id(self.s2)
        print "[BtOnlineGame] %s serving [%s] [%s]" % (BtServer.timestamp(),id1,id2)
        self._moves = []
        self._board = bt_game.BtBoard(self._rows,self._cols)
        self._board.new_game(self._sym1, self._sym2, self._init_rows)

        self._turn = self._sym1
        timeout = self._timeout1
        player = self.s1
        iteration = 1
        logfile.write("player 1 = [%s] %s %d\n" % (id1,self.a1[0],self.a1[1]))
        self.s1.sendall('n 1 o x' + eom)
        self.s1.sendall('a you are o' + eom)
        logfile.write("player 2 = [%s] %s %d\n" % (id2,self.a2[0],self.a2[1]))
        self.s2.sendall('n 0 x o' + eom)
        self.s1.sendall('a you are x' + eom)
        logfile.write("== starting game ==\n")
            
        while True:
            # send board to player
            self.send_board_to_all()
            
            # ask for move
            ask_move_msg = "m %d %s" % (self._timeout1, eom)
            ask_ok = player.sendall(ask_move_msg)
            assert ask_ok == None
            #nx = 128 - len(ask_move_msg) -1
            #if nx < 0: nx = 0
            #player.sendall("d " + "x"*nx + eom)
            
            # wait for move
            timeout_str = str(timeout + self._grace)
            logfile.write( BtServer.timestamp() + " asking move from player " + self._turn + " with timeout " + timeout_str + "\n")
            move_msg = ''
            start_time = time.time()
            player.settimeout(timeout+ self._grace)
            while eom not in move_msg:
                m = player.recv(128)
                if not m:
                    raise Exception("player %s disconnected" % self._turn)
                if not move_msg and m and m[0] != 'm':
                    raise Exception("player %s violated move message protocol" % self._turn)
                move_msg = move_msg + m
            player.settimeout(None)
            time_taken = time.time() - start_time
            logfile.write( BtServer.timestamp() + " got move message: " + move_msg + "\n")
            move = self.decode_move(move_msg)
            
            # annouce the move
            #self.s1.sendall("l %d %c %d %d %d %d %f %s" % \
            #                (iteration,self._turn,move[0][0],move[0][1],move[1][0],move[1][1],time_taken,eom))
            #self.s2.sendall("l %d %c %d %d %d %d %f %s" % \
            #                (iteration,self._turn,move[0][0],move[0][1],move[1][0],move[1][1],time_taken,eom))
            self.s1.sendall("l %d %c %d %d %d %d %s" % \
                            (iteration,self._turn,move[0][0],move[0][1],move[1][0],move[1][1],eom))
            self.s2.sendall("l %d %c %d %d %d %d %s" % \
                            (iteration,self._turn,move[0][0],move[0][1],move[1][0],move[1][1],eom))
            
            # make move if it's valid. otherwise other player wins
            self.add_move(move)
            logfile.write("%s iter %d %c moves %d %d => %d %d\n" % \
                          (BtServer.timestamp(), iteration, self._turn, move[0][0], move[0][1], move[1][0], move[1][1]))
            if self.is_valid_move(move):
                self.move(move)
                if self.is_game_over():
                    w = self.winner()
                    self.send_board_to_all()
                    self.s1.send('w %c %s' % (w,eom) )
                    self.s2.send('w %c %s' % (w,eom) )
                    logfile.write("%s winner = %s\n" % (BtServer.timestamp(),w))
                    break
            else:
                print "[BtOnlineGame] invalid move. terminating game",
                self.set_winner( (self._turn == self._sym1 and [self._sym2] or [self._sym1])[0] )
                winner_id = (self.winner() == self._sym1 and [id1] or [id2])[0]
                print "[BtOnlineGame] winner =", winner_id
                self.s1.send("a invalid move. immediate disqualification." + eom)
                self.s2.send("a invalid move. immediate disqualification." + eom)
                w = self.winner()
                self.s1.send('w %c %s' % (w,eom) )
                self.s2.send('w %c %s' % (w,eom) )
                break
            
            # switch player
            if self._turn == self._sym1:
                self._turn = self._sym2
                player = self.s2
                timeout = self._timeout2
            else:
                self._turn = self._sym1
                player = self.s1
                timeout = self._timeout1
            iteration += 1
            logfile.flush()
        # while
        logfile.flush()

    def run(self):
        eom = bt_protocol.eom
        try:
            #LOG_FILENAME = "logs/" + self.server_id + "-" + self.timestamp() + ".log"
            LOG_FILENAME = "../logs/" + self.server_id + "-" + BtServer.timestamp() + ".log"
            logfile = open(LOG_FILENAME,'a')
            self.play_one_game(logfile)
        except Exception, msg:
            print "[BtOnlineGame] exception:",msg
            try:
                self.s1.send("a unexpected exception (probably opponent disconnected.) disconnecting" + eom)
                self.s2.send("a unexpected exception (probably opponent disconnected.) disconnecting" + eom)
                logfile.close()
            except:
                pass
        try:
            # tell clients to close connection
            self.s1.send(eom)
            self.s2.send(eom)
            self.s1.close()
            self.s2.close()
            logfile.close()
        except:
            pass
        BtOnlineGame.count_lock.acquire()
        BtOnlineGame.count -= 1
        BtOnlineGame.count_lock.release()
        BtOnlineGame.stats_lock.acquire()
        while len(BtOnlineGame.stats) > 4:
            BtOnlineGame.stats.pop(-1)
        BtOnlineGame.stats.insert(0,str(datetime.datetime.now()))
        BtOnlineGame.stats_lock.release()
        print "[BtOnlineGame] game closed; count now %d" % (BtOnlineGame.count)

    def decode_move(self,m):
        a = m.split()
        assert a[0] == 'm'
        return [ [int(a[1]),int(a[2])], [int(a[3]),int(a[4])] ]

    def encode_board(self):
        m = "b %d %d " % (self._board.rows, self._board.cols)
        coord = {}
        count = {}
        for r in range(self._board.rows):
            for c in range(self._board.cols):
                x = self._board.mat[r][c]
                if x != ' ':
                    if x not in coord:
                        coord[x] = ''
                        count[x] = 0
                    t = "%d %d " % (r,c)
                    coord[x] = coord[x] + t
                    count[x] = count[x] + 1
        for k,v in coord.items():
            t = "%c %d " % (k,count[k])
            m = m + t + v
        return m
        
class BtServer:
    @staticmethod
    def timestamp():
        return string.replace(str(datetime.datetime.now()), ' ', '-')
    
    def __init__(self, server_id, rows, cols, initn):
        self.singles = []
        self.singles_lock = threading.Lock()
        self.MAX_GAMES = 50
        self.WAITLIST_LIMIT = 20
        self.server_id = server_id
        self.rows = rows
        self.cols = cols
        self.initn = initn
        self.total_connections = 0
        self.dropped_connections = 0

    def run(self,port):
        m = BtServer.MatchMaker(self.server_id, self.rows, self.cols, self.initn, self.singles, self.singles_lock, self.MAX_GAMES)
        m.start()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('',port))
        s.listen( self.WAITLIST_LIMIT )
        print "[BtServer] starting server in port %d" % port
        try:
            while True:
                (client,addr) = s.accept()
                print "[BtServer] %s: connection from (%s,%d)" % (BtServer.timestamp(),addr[0],addr[1])
                client.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 0)
                print "[BtServer] singles qsize = %d BtOnlineGames.count = %d" % (len(self.singles),BtOnlineGame.count)
                self.total_connections += 1
                if len(self.singles) < self.WAITLIST_LIMIT:
                    try:
                        m = str(BtOnlineGame.stats)
                        client.sendall('a last few games ended on ' + m + bt_protocol.eom)
                        client.sendall("a waiting list size %d %s" % (len(self.singles), bt_protocol.eom))
                        client.sendall("a # of games now %d %s" % (BtOnlineGame.count, bt_protocol.eom))
                        client.sendall('a waiting...' + bt_protocol.eom)
                        self.singles_lock.acquire()
                        self.singles.append([client,addr])
                        self.singles_lock.release()
                    except Exception,msg:
                        print msg
                        try:
                            client.close()
                        except: pass
                    #print "[BtServer] queuing connection"
                else:
                    try:
                        client.sendall('a server busy. please come back later.' + bt_protocol.eom)
                        client.send(bt_protocol.eom)
                        client.close()
                    except Exception,msg:
                        print msg
                    print "[BtServer] dropping connection"
                    self.dropped_connections += 1
                drop_rate = 1.0 * self.dropped_connections / self.total_connections
                print "[BtServer] drop rate = %d / %d = %f" % (self.dropped_connections,self.total_connections,drop_rate)
                sys.stdout.flush()
        except KeyboardInterrupt:
            s.close()

    class MatchMaker(threading.Thread):
        def __init__(self, server_id, rows, cols, initn, singles, singles_lock, max_games):
            self.server_id = server_id
            self.singles = singles
            self.singles_lock = singles_lock
            self.MAX_GAMES = max_games
            self.rows = rows
            self.cols = cols
            self.initn = initn
            threading.Thread.__init__(self)

        def first_two_singles_alive(self):
            # pre: single list short
            self.singles_lock.acquire()
            i = 0
            j = 0
            while i < len(self.singles):
                (s,a) = self.singles[i]
                alive = True
                try:
                    single_alive = s.sendall('i ' + bt_protocol.eom)
                    if single_alive != None:
                        raise Exception("[MatchMaker] dropping dead connection")
                    buf = ''
                    while bt_protocol.eom not in buf:
                        t = s.recv(32)
                        if not t: raise Exception("[MatchMaker] connection dropped")
                        if not buf and t[0] != 'i': raise Exception("[MatchMaker] invalid id msg protocol")
                        buf = buf + t
                except Exception,msg:
                    alive = False
                if not alive:
                    # purge
                    print "[MatchMaker] %s dropping dead or illegal single: [%d] %s %d" % (BtServer.timestamp(),j,a[0],a[1])
                    self.singles.pop(i)
                    try: s.close()
                    except: pass
                else:
                    if j == 1 and i == 1:
                        # first two singles alive
                        self.singles_lock.release()
                        return True
                    i = i + 1
                j = j + 1
                
            self.singles_lock.release()
            return False

        def run(self):
            print "[MatchMatcher] started"
            while True:
                if BtOnlineGame.count >= self.MAX_GAMES or not self.first_two_singles_alive():
                    time.sleep(1)
                    continue

                print "[MatchMaker] singles qsize = %d BtOnlineGame.count = %d" \
                      % (len(self.singles), BtOnlineGame.count)

                p = []
                self.singles_lock.acquire()
                assert len(self.singles) >= 2
                p.append( self.singles.pop(0) )
                p.append( self.singles.pop(0) )
                self.singles_lock.release()
                #print "[MatchMaker] creating game"                    
                random.shuffle(p)
                s1 = p[0][0]
                a1 = p[0][1]
                s2 = p[1][0]
                a2 = p[1][1]
                g = BtOnlineGame(self.server_id,s1,a1,s2,a2,self.rows,self.cols,self.initn,'o','x',1,1)
                #print "[MatchMaker] starting game"
                sys.stdout.flush()
                g.start()
# class BtServer

if __name__ == '__main__':
    rows = 10
    cols = 9
    initn = 2 # number of rows of pawns
    server_id = "bvb-%d-%d" % (rows,cols)
    s = BtServer(server_id, rows, cols, initn)
    s.run(int(sys.argv[1]))
