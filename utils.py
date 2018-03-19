import cfg

def msg(sock, message):
    sock.sendto("PRIVMSG #{} :{}\r\n".format(cfg.CHANNEL, message).encode(), (cfg.HOST, cfg.PORT))