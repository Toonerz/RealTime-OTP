from src.messagedirector.MDParticipant import MDParticipant

class MDParticipantInterface:
    
    def __init__(self):
        self.registeredParticipants = {}
        self.potentialParticipants = []
        self.registeredClients = []

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
            new_client = MDParticipant(connection, channel)
            self.registeredClients.append(new_client)
        else:
            return
    
    def unregister_channel(self, connection, channel):
        if self.authenicateChannel(connection, channel) == True:
            del self.registeredParticipants[channel]
            print ("MDParticipantInterface: Un-Registered channel: %d" % channel) # DEBUG!
            for client in self.registeredClients:
                if client.channel == channel:
                    self.registeredClients.remove(client)
        else:
            return
