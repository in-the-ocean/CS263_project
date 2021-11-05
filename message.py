class Message:
    def __init__(self, tpe, message = "", sender = '', client_idx = -1):
        self.message = message
        self.sender = sender
        self.type = tpe
        self.client_idx = client_idx
