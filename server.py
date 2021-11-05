import threading
import socket
import sys
import heapq
import queue
import time

from message import *


class Server:
    def __init__(self, pid, recover = False):
        self.pid = pid
        self.message_queue = queue.Queue()

    def start(self):
        while True:
            line = sys.stdin.readline().strip().split("(")
            if not line:
                continue
            if line[0] == "exit" or line[0] == "e":
                message = Message("exit")
                self.message_queue.put(message)
                # self.join()
                sys.exit()
            elif line[0] == "connect":
                # self.connect()
            elif line[0] == 'startCollection':
                message = Message("collect")
                self.message_queue.put(message)

if __name__ == '__main__':
    server = Server(int(sys.argv[1]))
    server.start()
