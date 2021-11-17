class Node:
    def __init__(self, server, id, outVertices = []):
        self.server = server
        self.id = id
        self.outVertices = outVertices 
    
    def connect(self, nxt_server, nxt_id):
        self.outVertices.append((nxt_server, nxt_id))
