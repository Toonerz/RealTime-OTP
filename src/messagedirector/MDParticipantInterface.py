from src.messagedirector.MDParticipant import MDParticipant

class MDParticipantInterface:
    
    def __init__(self):
        self.registeredParticipants = {}
        self.potentialParticipants = []

    def authenicateChannel(self, connection, channel):
		if channel in self.registeredParticipants:
			if self.registeredParticipants[channel] == connection:
				for potentials in self.potentialParticipants:
					if potentials == connection:
						self.potentialParticipants.remove(connection)
						return True
		else:
			return False
 
    def register_channel(self, connection, channel):
        if authenicateChannel(connection, channel) == True:
			return NotImplemented
		else:
			return NotImplemented
    
    def unregister_channel(self, connection, channel):
        if authenicateChannel(connection, channel) == False:
			return NotImplemented
		else:
			return NotImplemented
