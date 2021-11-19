class Message:
    def __init__(self, tpe, message = "", sender = ''):
        self.message = message
        self.sender = sender
        self.type = tpe
        self.stubs = set()
        self.scions = set()
        self.target = ""
