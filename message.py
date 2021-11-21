class Message:
    def __init__(self, tpe, message = "", sender = '', visited = set()):
        self.message = message
        self.sender = sender
        self.type = tpe
        self.stubs = set()
        self.scions = set()
        self.visited = visited
        self.target = ""
        self.reference_id = -1
