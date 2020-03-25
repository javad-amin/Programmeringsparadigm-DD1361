import random
import curses
from protocol import unpack_state, pack_msg, read_msg
from time import sleep, time
from socket import socket, AF_INET, SOCK_STREAM, SO_REUSEADDR, \
    error as socketerror
import errno
import traceback
from exceptions import ConnectionHungUp

CONNECT_ADDR = ("127.0.0.1", 5555)

rate = 0.050
# Height and width of the screen per lines
SCR_HEIGHT, SCR_WIDTH = 18, 60
# Top left and bottom right coordinates for the playground
box = [[3,3], [SCR_HEIGHT-3, SCR_WIDTH-3]]
colorsattrmap = { }
curseskeymap = {
    curses.KEY_DOWN : "down",
    curses.KEY_UP : "up",
    curses.KEY_LEFT : "left",
    curses.KEY_RIGHT : "right",
    curses.KEY_ENTER : "enter",
}
conn = None
recv_buff = b""

def curses_get_protocol_key (key):
    if key in curseskeymap:
        return curseskeymap[key]
    if key in [10, 13]:
        return "enter"
    return None

def connect_to_server(addr):
    conn = socket(AF_INET, SOCK_STREAM)
    conn.connect(addr)
    return conn

def render_blocks (stdscr, message, blocks):
    try:
        for x, y, color, symbol in blocks:
            try:
                x = int(x)
                y = int(y)
            except ValueError:
                continue
            if x < 0 or x > SCR_WIDTH or y < 0 or y > SCR_HEIGHT:
                continue
            colorattr = colorsattrmap.get(color, None)
            if colorattr != None:
                stdscr.attron(colorattr) # Set player color for drawing
            # Draw block
            stdscr.addstr(y, x, symbol[0] if len(symbol) > 0 else " ")
            if colorattr != None:
                stdscr.attroff(colorattr) # Set player color for drawing
    except:
        raise ValueError("Invalid blocks given by server\n{}".format(traceback.format_exc()))

    # Print number of arrows
    maxlines = 2
    y = 0
    for line in message.split("\n"):
        if y >= maxlines:
            break
        startx = SCR_WIDTH//2 - len(line)//2
        colorattr = None
        if line.startswith("$"):
            try:
                idx = line[1:].index("$")
                color = line[1:idx+1]
                colorattr = colorsattrmap.get(color, None)
                if colorattr != None:
                    line = line[idx+2:]
            except ValueError:
                pass
        # insert empty space, to wipe existing state
        if startx > 0:
            stdscr.addstr(y, 0, " " * startx)
        if SCR_WIDTH - startx - len(line) > 0:
            stdscr.addstr(y, startx + len(line), " " * (SCR_WIDTH + startx - len(line)))
        # write line with color if given
        if colorattr != None:
            stdscr.attron(colorattr)
        stdscr.addstr(y, startx, line)
        if colorattr != None:
            stdscr.attroff(colorattr)
        y += 1

def init_scr(stdscr):
    global colorsattrmap
    # init screen
    curses.curs_set(0)
    curses.resizeterm(SCR_HEIGHT, SCR_WIDTH)
    # init colors
    cidx = 1
    for color in ("RED", "BLUE", "YELLOW", "GREEN", "WHITE"):
        curses.init_pair(cidx, getattr(curses, "COLOR_" + color), curses.COLOR_BLACK)
        colorsattrmap[color] = curses.color_pair(cidx)
        cidx += 1

def conn_recv(size):
    global recv_buff
    buff = conn.recv(size)
    if size > 0 and len(buff) == 0:
        raise ConnectionHungUp()
    recv_buff += buff
    size = min(len(recv_buff), size)
    buff = recv_buff[:size]
    recv_buff = recv_buff[size:]
    return buff

def main(stdscr):
    global conn
    init_scr(stdscr)
    conn = connect_to_server(CONNECT_ADDR)
    conn.setblocking(0)
    stdscr.nodelay(1)
    quit = False
    lasttime = time()
    started = False
    while not quit:
        # non-blocking input
        key = stdscr.getch()
        # exit at next cycle when q has pressed
        if key in (b"q"[0], b"Q"[0]):
            quit = True
        if started:
            pkey = curses_get_protocol_key(key)
            if pkey is not None:
                # send key
                conn.send(pack_msg("k", pkey))
        # recv a message
        try:
            msgtype, data, _ = read_msg(conn_recv)
            if msgtype == "s": # state
                message, blocks = unpack_state(data)
                render_blocks(stdscr, message, blocks)
                conn.send(pack_msg("p", ""))
            elif msgtype == "g":
                # trigger for start of game
                started = True
                conn.send(pack_msg("p", ""))
        except socketerror as e:
           # raise only of exception is not (partial data send)
           err = e.args[0]
           if err != errno.EAGAIN and err != errno.EWOULDBLOCK:
               raise
        # sleep if needed, to preserve certain refresh rate
        ctime = time()
        if ctime - lasttime < rate:
            sleep(rate - (ctime - lasttime))
        lasttime = ctime


curses.wrapper(main)
