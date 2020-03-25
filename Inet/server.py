from socket import socket, AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET, \
    error as socketerror
import errno
from time import time, sleep
from protocol import pack_state, pack_msg, read_msg
from objects import Object, Collectable, ArrowShot, Character, BlockObject
from exceptions import ConnectionHungUp
import random

# Setting up some global variables
HOST = "127.0.0.1"
PORT = 5555
PLAYERS_COLOR = [ "GREEN", "WHITE" ]

# Height and width of the screen per lines
SCR_HEIGHT, SCR_WIDTH = 18, 60
# Top left and bottom right coordinates for the playground
box = [[3,3], [SCR_HEIGHT-3, SCR_WIDTH-3]]

SIMULATION_REFRESH_INTERVAL = 0.060
KEEP_ALIVE_TIMEOUT = 3

CHAR_SPEED = 4
ARROW_SHOT_SPEED = 18

class Client:
    """
    The client object which holds the attribute of a client connected to the
    server.
    """
    def __init__(self, socket, index, color):
        self.socket = socket
        self.index = index
        self.color = color
        self.send_queue = []
        self.recv_queue =  []
        self.recv_buff = b""
        self.char = None
        self.lastping = 0
        self.is_connected = True

class GameState:
    def __init__(self, box):
        self.message = ""
        self.objects = []
        self.chars = []
        self.box = box
        self.quit = False
    def mkblocks(self):
        blocks = []
        box = [[3,3], [SCR_WIDTH-3, SCR_HEIGHT-3]]
        for x in range(self.box[0][0], self.box[1][0]):
            for y in range(self.box[0][0], self.box[1][1]):
                if self.is_block_clear((x, y)):
                    blocks.append((x, y, "", " "))
        for obj in self.objects:
            blocks.append((obj.x, obj.y, obj.color, obj.symbol))
        return blocks
    def objects_at_pos(self, pos):
        return [ a for a in self.objects if a.get_pos() == pos ]
    def is_block_clear(self, pos):
        return len(self.objects_at_pos(pos)) == 0
    def rand_position(self):
       '''Function to create an object on coordinates which is clear'''
       trylen = 1000
       i = 0
       while True:
           pos = (random.randint(self.box[0][0]+1, self.box[1][0]-1),
                  random.randint(self.box[0][1]+1, self.box[1][1]-1))
           if self.is_block_clear(pos):
               break
           if i > trylen:
               raise RuntimeError("No more empty position left after {} tries".format(trylen))
           i += 1
       return pos

class GameHandler:
    def __init__(self, clients, gamestate):
        self.clients = clients
        self.gamestate = gamestate
    def update_state(self, clients=None):
        if clients is None:
            clients = self.clients
        for client in clients:
            msg = pack_msg("s", pack_state(self.gamestate.message, self.gamestate.mkblocks()))
            client.send_queue.append(msg)
    def on_before_move(self, obj, new_x, new_y):
        gamestate = self.gamestate
        newpos = (new_x, new_y)
        objects_at_newpos = gamestate.objects_at_pos(newpos)
        isclear = len(objects_at_newpos) == 0
        if isinstance(obj, Character):
            # check for char got shot, when user moves
            at_obj_list = [ a for a in objects_at_newpos if isinstance(a, ArrowShot) ]
            if len(at_obj_list) > 0 and len([a for a in at_obj_list if a.character == obj]) != len(at_obj_list):
                # at_obj_list[0].char != obj, meaning one cannot run into a shot
                self.on_char_got_shot(obj, at_obj_list[0])
            # check if collectable is ahead
            at_obj_list = [ a for a in objects_at_newpos if isinstance(a, Collectable) ]
            for collectable in at_obj_list:
                if collectable.name == "arrow":
                    obj.arrows += 1
                gamestate.objects.remove(collectable)
                isclear = True
        elif isinstance(obj, ArrowShot):
            # check for char got shot, when arrow moves
            at_obj_list = [ a for a in objects_at_newpos if isinstance(a, Character) ]
            if len(at_obj_list) > 0:
                self.on_char_got_shot(at_obj_list[0], obj)
            elif not isclear and obj in gamestate.objects:
                gamestate.objects.remove(obj)
        return isclear
    def on_char_got_shot(self, char, ashot):
        # game-over
        ashot.x = char.x
        ashot.y = char.y
        self.gamestate.objects.remove(char)
        self.gamestate.message = "Game-Over"
        self.update_state()
        game_communicate(self.clients)
        sleep(2)
        winner_list = [ a for a in self.clients if a.char == ashot.character ]
        loser_list = [ a for a in self.clients if a.char == char ]
        print("game-over")
        for winner in winner_list:
            msg = pack_msg("s", pack_state("You Won!", self.gamestate.mkblocks()))
            winner.send_queue.append(msg)
            print("winner: {}".format(winner.index))
        for loser in loser_list:
            msg = pack_msg("s", pack_state("You Lost!", self.gamestate.mkblocks()))
            loser.send_queue.append(msg)
            print("loser: {}".format(loser.index))
        game_communicate(self.clients)
        sleep(6)
        self.gamestate.quit = True
    def on_client_key (self, client, key):
        char = client.char
        if key in ["left","right","up","down"]:
            char.change_direction(key)
        elif key == "enter":
            if char.arrows > 0:
                char.arrows -= 1
                # shoot
                ashot = ArrowShot(char.x, char.y, "YELLOW", "X", char.direction, ARROW_SHOT_SPEED, char)
                ashot.move(ashot.direction)
                objects_at_newpos = self.gamestate.objects_at_pos(ashot.get_pos())
                if len([ a for a in objects_at_newpos if isinstance(a, BlockObject) ]) == 0:
                    self.gamestate.objects.append(ashot)



def init_gamestate (gamestate, clients):
    box = gamestate.box
    # Adding the borders to list of blocking objects
    for x in range(box[1][0]-box[0][0]+1):
        # borders in X axis
        top_block = BlockObject(x+box[0][0], box[0][1], "BLUE", "#")
        bottom_block = BlockObject(x+box[0][0], box[1][1], "BLUE", "#")
        gamestate.objects.append(top_block)
        gamestate.objects.append(bottom_block)
    for y in range(1, box[1][1]-box[0][0]):
        left_block = BlockObject(box[0][0], y+box[0][1], "BLUE", "#")
        right_block = BlockObject(box[1][0], y+box[0][1], "BLUE", "#")
        gamestate.objects.append(left_block) #Top
        gamestate.objects.append(right_block) #Bottom
    # create few random blocks
    for x in range(50):
        pos = gamestate.rand_position()
        block = BlockObject(pos[0], pos[1], "BLUE", "#")
        gamestate.objects.append(block)
    # create ammo
    for x in range(5):
        pos = gamestate.rand_position()
        obj = Collectable(pos[0], pos[1], "YELLOW", ">", "arrow")
        gamestate.objects.append(obj)
    # client
    for client in clients:
        pos = gamestate.rand_position()
        client.char = Character(pos[0], pos[1], client.color, 'ö', None, CHAR_SPEED, 0)
        gamestate.objects.append(client.char)
        gamestate.chars.append(client.char)

def game_apply_clients_request(clients, gamehandler, waiting_clients):
    ctime = time()
    for client in clients:
        while len(client.recv_queue):
            msgtype, data = client.recv_queue.pop(0)
            if msgtype == "k":
                key = str(data, "utf8")
                gamehandler.on_client_key(client, key)
            elif msgtype == "p":
                client.lastping = ctime
        if ctime - client.lastping > KEEP_ALIVE_TIMEOUT:
            waiting_clients.append(client.index)

def game_communicate(clients):
    """
    For each connected client sends and recieves evertything.
    """
    try:
        # send and recv all
        for client in clients:
            if client.is_connected:
                client_send_queue(client)
                client_recv_requests(client)
    except (ConnectionHungUp, BrokenPipeError, ConnectionResetError):
        print("Connection hung up, client: {}".format(client.index))
        client.socket.close()
        client.is_connected = False

def game_worker(clients):
    # init game
    gamestate = GameState(box)
    init_gamestate(gamestate, clients)
    gamehandler = GameHandler(clients, gamestate)
    print("starting countdown")
    # countdown
    gamestate.message = "Ready!"
    gamehandler.update_state()
    game_communicate(clients)
    sleep(1)
    for i in range(3):
        gamestate.message = str(3 - i)
        gamehandler.update_state()
        game_communicate(clients)
        sleep(1)
    # simulation starts here
    lasttime = time()
    print("simulation started")
    while not gamestate.quit:
        waiting_clients = []
        # apply players given keys
        disconnected_clients = [ a.index for a in clients if not a.is_connected ]
        if len(disconnected_clients) > 0:
            messages = "\n".join(map(lambda client: "${}$Player {} have disconnected!"\
                .format(client.color, client.index) \
                if client.index in disconnected_clients else \
                "${}$Player {},  Arrows {}".format(client.color, client.index, client.char.arrows), clients))
            gamestate.message = messages
            gamehandler.update_state([a for a in clients if a.index not in disconnected_clients])
            game_communicate(clients)
            print("one client did disconnect")
            sleep(6)
            break # exit game if a client has disconnected
        game_apply_clients_request(clients, gamehandler, waiting_clients)
        # wait for left behind clients
        while len(waiting_clients) > 0:
            messages = "\n".join(map(lambda client: "${}$Waiting for player {}"\
                .format(client.color, client.index) \
                if client.index in waiting_clients else \
                "${}$Player {},  Arrows {}".format(client.color, client.index, client.char.arrows), clients))
            gamestate.message = messages
            gamehandler.update_state([a for a in clients if a.index not in waiting_clients])
            game_communicate(clients)
            # sleep for one second
            sleep(1)
            # re-evaluate waiting clients & re-apply players given keys
            waiting_clients = []
            game_apply_clients_request(clients, gamehandler, waiting_clients)
        # perform a step
        ctime = time()
        timediff = ctime - lasttime
        # update all objects
        for obj in gamestate.objects:
            if gamestate.quit:
                break
            obj.update(timediff, gamehandler)
        # read msgs again
        messages = "\n".join(map(lambda client: "${}$Player {},  Arrows {}".format(client.color, client.index, client.char.arrows), clients))
        gamestate.message = messages
        gamehandler.update_state()
        game_communicate(clients)
        # sleep until next refresh
        if timediff < SIMULATION_REFRESH_INTERVAL:
            sleep(SIMULATION_REFRESH_INTERVAL - timediff)
        lasttime = ctime

def client_recv_requests(client):
    # socket_recv will hold a buff in case msg
    # has received partially
    received_buff = client.recv_buff
    def socket_recv (size):
        nonlocal received_buff
        if len(received_buff) >= size:
            buff = received_buff[0:size]
            received_buff = received_buff[size:]
            return buff
        buff = client.socket.recv(size - len(received_buff))
        if size > 0 and len(buff) == 0:
            raise ConnectionHungUp()
        client.recv_buff += buff
        return received_buff + buff
    try:
        while True:
            msg = read_msg(socket_recv)
            if msg[0] == "l": # log some text
                print("log from client {}: {}".format(client.index, str(msg[1], "utf8")))
            else:
                client.recv_queue.append(msg)
            received_size = msg[2]
            client.recv_buff = client.recv_buff[received_size:]
    except socketerror as e:
        # raise only of exception is not (partial data send)
        err = e.args[0]
        # if errno is one of the below thenn we skip the exception.
        if err != errno.EAGAIN and err != errno.EWOULDBLOCK:
            raise


def client_send_queue(client):
    """
    For a given client it sends everything that is in send_queue of that client.
    """
    while len(client.send_queue) > 0:
        msg = client.send_queue.pop(0)
        client.socket.send(msg)

def main():
    """
    Main server function, sets up server socket and listens for connections
    from clients.
    """
    server = socket(AF_INET, SOCK_STREAM)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server.bind((HOST, PORT)) # Binding the connection to server address
    server.listen(2) # Listenning for client connections
    clients = []
    gamestarted = False
    print("Server started, waiting for a connection...")
    while len(clients) < 2:
        newsocket, addr = server.accept()
        # Setting socket to non-blocking as we are going to have two active
        # sockets. Setting it to non-blocking it allows to continue
        # game simulation even if one party has disconnected or has delay.
        newsocket.setblocking(False)
        print("client connected: {}".format(addr))
        index = len(clients) + 1
        color = PLAYERS_COLOR[index-1]
        client = Client(newsocket, index, color)
        clients.append(client)
        if len(clients) < 2:
            message = "Waiting for the other player"
            client.send_queue.append(pack_msg("s", pack_state(message, [])))
            game_communicate(clients)
    print("game started")
    gamestarted = True
    for client in clients:
        # send start trigger
        client.send_queue.append(pack_msg("g", ""))
    game_communicate(clients)
    game_worker(clients)

main()
