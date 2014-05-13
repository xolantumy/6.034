#!/usr/bin/python

import signal
import math
import random
import bt_game
import bt_dumb_bot
import bt_smart_bot
import bt_time_machine
import breakout1





def signal_handler(signum,frame):
    #raise Exception("Time out [signum=%d,frame=%s]" % (signum,frame))
    raise bt_game.TimeoutException("Time out [signum=%d,frame=%s]" % (signum,frame))

def play_one_game():
    bot_vs_bot = True
    symbols = 'ox'
    init_rows = 2
    rows = 10
    cols = 9
    #bot_timeout = 1
    [n,s] = bt_time_machine.bt_time_machine(1)
    print "n = ",n," s = ",s
    bot_timeout = max(int(math.ceil(3000.0/n)),1)
    print "setting timeout = %d seconds" % bot_timeout

    bot1 = breakout1.BreakoutBot1( True, symbols[0], symbols[1] )
    #bot1 = bt_dumb_bot.BtDumbBot( True, symbols[0], symbols[1] )
    #bot1 = bt_smart_bot.BtSmartBot( True, symbols[0], symbols[1] )

    #bot2 = BtRandomBot( False, symbols[1], symbols[0] )
    bot2 = bt_dumb_bot.BtDumbBot( False, symbols[1], symbols[0] )
    #bot2 = bt_smart_bot.BtSmartBot( False, symbols[1], symbols[0] )

    human = bt_game.HumanBtBot( False, symbols[0], symbols[1] )
    signal.signal(signal.SIGALRM, signal_handler)
    game = ( \
        bot_vs_bot \
        and [bt_game.BtGame(rows, cols, init_rows, symbols[0], symbols[1], bot_timeout, bot_timeout)] \
        or  [bt_game.BtGame(rows, cols, init_rows, symbols[0], symbols[1], 0, bot_timeout)] \
        )[0]
    gui = bt_game.BtTextGui()
    winner = -1
    if bot_vs_bot:
        winner = game.play(bot1, bot2, gui)
    else:
        print "format for move input: \"row1 col1 row2 col2\""
        print "  e.g. \"1 2 3 3\" (without quotes) means row 1 col 2 to row 3 col 3]"
        winner = game.play(human, bot2, gui)
    #print winner

if __name__ == '__main__':
    play_one_game()








