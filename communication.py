import socket
import threading
import time
import pickle

from message import Message

DELAY = 5


class ConnServer(threading.Thread):
    def __init__(self, conn_socket, pid, message_queue):
        super().__init__(daemon=True)
        self.conn_socket = conn_socket
        self.pid = pid
        self.message_queue = message_queue
    
    def run(self):
        while True:
            stream, addr = self.conn_socket.accept()
            respond_thread = ServerComm(stream, addr, self.pid, self.message_queue)
            respond_thread.start()
            print(f'connected to {addr}')

        
class ServerComm(threading.Thread):
    def __init__(self, stream, addr, pid, message_queue):
        super().__init__(daemon=True)
        self.stream = stream
        self.addr = addr
        self.pid = pid
        self.server_pid = None
        self.message_queue = message_queue

    def run(self):
        while True:
            byte_size = self.stream.recv(2)
            if not byte_size:
                return
            size = int.from_bytes(byte_size, byteorder='big')
            byte_message = self.stream.recv(size)
            if not byte_message:
                return
            message = pickle.loads(byte_message)
            if message.type == 'pid':
                self.server_pid = message.message
            else:
                self.message_queue.put(message)
                

def send(message, dst_sock):
    try:
        dst_sock.send(len(message).to_bytes(2, byteorder='big'))
        dst_sock.send(message)
    except:
        pass

