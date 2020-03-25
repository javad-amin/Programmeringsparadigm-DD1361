msgtype = "S"
oldmsg = "Hello world!"
msg = oldmsg[:3] 

msgbytes = bytes(msg, "utf8")
data = bytes("{}{:04x}".format(msgtype[0], len(msgbytes)), "ascii") + msgbytes

print(str(data, "utf-8"))
