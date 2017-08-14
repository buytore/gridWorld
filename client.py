#!/usr/bin/env python
# client.py

import config as cfg
import sys
import socket

"""
def main(elems):
    e = tuple(map(int, elems))

    try:
        for e in elems:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = socket.gethostname()
            client.connect((host, cfg.PORT))
            client.send(e)
            client.shutdown(socket.SHUT_RDWR)
            client.close()
    except Exception as msg:
        print msg
"""

def main(elems):
    e = str(tuple(map(int, elems)))
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        client.connect((host, cfg.PORT))
        client.send(e)
        client.shutdown(socket.SHUT_RDWR)
        client.close()
    except Exception as msg:
        print msg

#########################################################

if __name__ == "__main__":
    #main(sys.argv[1:])
    main(sys.argv[1:])