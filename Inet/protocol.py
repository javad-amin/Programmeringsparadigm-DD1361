import socket

def read_msg (recv):
    """
      Reads a single message.
      Parameter recv is a function which recieves bytes from the socket.
      Return value contains msgtype, the message and received size.
    """
    # Head size 1 byte message type and 4 bytes is the size of the msg in hex string.
    HEAD_SIZE = 5
    buff = recv(HEAD_SIZE)
    # We make sure that we read at least 5 bytes
    while len(buff) < HEAD_SIZE:
        buff += recv(HEAD_SIZE - len(buff))
    # We parse the msg head
    msgtype, msgsize = unpack_msg_head(buff)
    buff = b""
    while len(buff) < msgsize:
        buff += recv(msgsize - len(buff))
    return (msgtype, buff, HEAD_SIZE + msgsize)


def pack_msg (msgtype, msg):
    """
    Packs a message recieved from the server/client. Parameters msgtype and
    msg are of type string and the function convert them into bytes.
    The return value contains starts with one byte as msgtype followed by the
    length of the message which is 4 bytes and the msg itself.
    """
    msgbytes = bytes(msg, "utf8")
    return bytes("{}{:04x}".format(msgtype[0], len(msgbytes)), "ascii") + msgbytes



def unpack_msg_head (data):
    """
    It unpacks a message head. Parameter data is of type bytes.
    The return value is a tuple containing msgtype, msgsize.
    """
    if len(data) != 5:
        raise ValueError("input data should be more than five characters")
    msgtype = str(data[:1], "ascii")
    msgsize = int(str(data[1:5], "ascii"), 16) # convert hex to int
    return (msgtype, msgsize)

def pack_state (message, blocks):
    """
    Pack state returns a string representing state of the game.
    A message and a list containing the state of the game is received by the
    function. msg followed  a seperator "#@#@#" and then the state of the game
    is added. We convert our list into a string in order to send it.
    Example output : 0|0|X|BLUE, 0|RED, X|BLUE
    """
    return message + "#@#@#" + ",".join(map(lambda a: "|".join(map(str, a)), blocks))

def unpack_state (data):
    """
    Parses state of the game.
    Receives data as bytes and returns  
    """
    data = str(data, "utf-8")
    try:
        msgendidx = data.index("#@#@#")
        message = data[0:msgendidx]
        data = data[msgendidx+5:]
    except ValueError:
        message = ""
    return (message, tuple() if len(data) == 0 else tuple(map(lambda a: tuple(a.split("|")), data.split(","))))
