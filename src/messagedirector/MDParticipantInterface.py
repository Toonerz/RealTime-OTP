from src.messagedirector.MDParticipant import MDParticipant

class MDParticipantInterface:
    
    def __init__(self):
        self.registeredParticipants = {}
        self.potentialParticipants = []
    
    def register_channel(self, connection, channel):
        pass
    
    def unregister_channel(self, connection, channel):
        pass
