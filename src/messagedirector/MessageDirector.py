from panda3d.core import *
from pandac.PandaModules import *
from direct.task.TaskManagerGlobal import *
from direct.task.Task import Task
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from src.messagedirector.MDParticipantInterface import MDParticipantInterface
from src.util.types import *

class MessageDirector(QueuedConnectionManager):
    
    def __init__(self, serveraddress, serverport):
        QueuedConnectionManager.__init__(self)
        self.serveraddress = serveraddress
        self.serverport = serverport
    
    def configure(self):
        self.cl = QueuedConnectionListener(self, 0)
        self.cr = QueuedConnectionReader(self, 0)
        self.cw = ConnectionWriter(self, 0)
        self.interface = MDParticipantInterface()
    
    def unconfigure(self):
        for participant in self.interface:
            self.cr.removeConnection(participant)
        self.closeConnection(self.tcp_socket)
        self.cl = self.cr = self.cw = self.interface = None
    
    def open_connection(self):
        self.tcp_socket = self.openTCPServerRendezvous(self.serverport, 1000)
        if self.tcp_socket:
            self.cl.addConnection(self.tcp_socket)
    
    def task_listner_poll(self, taskname):
        if self.cl.newConnectionAvailable():
            rendezvous = PointerToConnection()
            netAddress = NetAddress()
            newConnection = PointerToConnection()
            
            if self.cl.getNewConnection(rendezvous, netAddress, newConnection):
                newConnection = newConnection.p()
                self.interface.potentialParticipants.append(newConnection)
                self.cr.addConnection(newConnection)
        
        return Task.cont
    
    def task_reader_poll(self, taskname):
        if self.cr.dataAvailable():
            datagram = NetDatagram()
            if self.cr.getData(datagram):
                self.handle_datagram(datagram)
        
        return Task.cont
    
    def handle_datagram(self, datagram):
        self.connection = datagram.getConnection()
        if not self.connection:
            pass # TODO!
        
        di = PyDatagramIterator(datagram)
        if di.getUint8() == 1:
            self.handle_incoming(di)
        elif di.getUint8() == BAD_CHANNEL_ID:
            self.handle_bad_channel(di)
    
    def handle_incoming(self, di):
        sender = di.getUint64()
        reciever = di.getUint64()
        messageType = di.getUint16()
        
        if messageType == CONTROL_MESSAGE:
            return NotImplemented
        elif messageType == CONTROL_SET_CHANNEL:
            self.interface.register_channel(self.connection, reciever)
        elif messageType == CONTROL_REMOVE_CHANNEL:
            self.interface.unregister_channel(self.connection, reciever)
        elif messageType == CONTROL_SET_CON_NAME:
            return NotImplemented
        elif messageType == CONTROL_SET_CON_URL:
            return NotImplemented
        elif messageType == CONTROL_ADD_RANGE:
            return NotImplemented
        elif messageType == CONTROL_REMOVE_RANGE:
            return NotImplemented
        elif messageType == CONTROL_ADD_POST_REMOVE:
            return NotImplemented
        elif messageType == CONTROL_CLEAR_POST_REMOVE:
            return NotImplemented
        else:
            self.notify.debug("Recieved an invalid messageType: %d" % messageType)
            return
    
    def handle_bad_channel(self, di):
        return NotImplemented
