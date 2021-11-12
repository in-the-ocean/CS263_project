class Node:
	def __init__(self, server, id, linkage = []):
		self.server = server
		self.id = id
		self.linkage = linkage
	def connect(self, nxt_server, nxt_id):
		self.linkage.append((nxt_server, nxt_id))
