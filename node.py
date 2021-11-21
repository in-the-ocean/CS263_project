class Node:
    def __init__(self, server, nid, connected=True):
        self.server = server
        self.id = nid
        self.root = connected
        self.outVertices = []
        self.remote_copy = 0
    
    def removeNode(self):
        self.root = False

    def connect(self, nxt_server, nxt_id, reference_id = -1):
        self.outVertices.append((nxt_server, nxt_id, reference_id))

    def neighbours(self):
        return self.outVertices
    
    def isConnected(self):
        return self.root
