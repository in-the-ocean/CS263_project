import threading
import socket
import sys
import heapq
import queue
import time

from graph import Graph
from message import *


class Server:
    def __init__(self, pid):
        self.pid = pid
        self.message_queue = queue.Queue()
        self.graph = Graph(self.pid, self.message_queue)

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
            elif line[0] == "Node": # Node(id)
                line = line[1][:len(line[1]) - 1]
                message = Message("Node", message=line)
                self.message_queue.put(message)
            elif line[0] == "local_reference":
                try:
                    end_points = eval("(" + line[1])
                except:
                    print("invalid input")
                    continue
                message = Message("local_reference", message=end_points)
            elif line[0] == "connect":
                line = line[1][:len(line[1]) - 1]
                message = Message("connect", message=line)
            elif line[0] == "drop":
                line = line[1][:len(line[1]) - 1]
                message = Message("drop", message=line)


if __name__ == '__main__':
    server = Server(int(sys.argv[1]))
    server.start()
