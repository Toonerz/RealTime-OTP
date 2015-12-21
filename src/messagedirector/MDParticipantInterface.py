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
        if self.authenicateChannel(connection, channel) == False:
            self.registeredParticipants[channel] = connection
            print ("MDParticipantInterface: Registered channel: %d" % channel) # DEBUG!
        else:
            return NotImplemented
    
    def unregister_channel(self, connection, channel):
        if self.authenicateChannel(connection, channel) == True:
            del self.registeredParticipants[channel]
            print ("MDParticipantInterface: Un-Registered channel: %d" % channel) # DEBUG!
        else:
            return NotImplemented
