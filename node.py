class Node:
    def __init__(self, server, id, connected=True, outVertices = []):
        self.server = server
        self.id = id
        self.root = connected
        self.outVertices = outVertices
    
    def removeNode(self):
        self.root = False

    def connect(self, nxt_server, nxt_id):
        self.outVertices.append((nxt_server, nxt_id))

    def neighbours(self):
        return self.outVertices
    
    def isConnected(self):
        return self.root
