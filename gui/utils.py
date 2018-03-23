import cfg

def msg(sock, message, channel):
    sock.sendto("PRIVMSG #{} :{}\r\n".format(channel, message).encode(), (cfg.HOST, cfg.PORT))