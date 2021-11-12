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
            elif line[0] == "Node":
                line = line[1][:len(line[1]) - 1]
                message = Message("Node", message=line)
                self.message_queue.put(message)
            elif line[0] == "local":
                line = line[1][:len(line[1]) - 1]
                message = Message("local", message=line)
            elif line[0] == "connect":
                line = line[1][:len(line[1]) - 1]
                message = Message("connect", message=line)
            elif line[0] == "drop":
                line = line[1][:len(line[1]) - 1]
                message = Message("drop", message=line)


if __name__ == '__main__':
    server = Server(int(sys.argv[1]))
    server.start()
