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
        self.open_connection()
    
    def unconfigure(self):
        for participant in self.interface:
            self.cr.removeConnection(participant)
        self.closeConnection(self.tcp_socket)
        self.cl = self.cr = self.cw = self.tcp_socket = self.interface = None
    
    def open_connection(self):
        self.tcp_socket = self.openTCPServerRendezvous(self.serverport, 1000)
        if self.tcp_socket:
            self.cl.addConnection(self.tcp_socket)

        taskMgr.add(self.task_listner_poll, "poll listener")
        taskMgr.add(self.task_reader_poll, "poll reader")
    
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
        connection = datagram.getConnection()
        if not connection:
            pass # TODO!
        
        di = PyDatagramIterator(datagram)
        if di.getUint8() == 1:
            self.handle_incoming(di, connection, datagram)
        elif di.getUint8() == BAD_CHANNEL_ID:
            self.handle_bad_channel(di)
    
    def handle_incoming(self, di, connection, datagram):
        reciever_channel = di.getUint64()
        sender_channel = di.getUint64()
        message_type = di.getUint16()

        print sender_channel, reciever_channel, message_type
        
        if message_type == CONTROL_MESSAGE:
            self.route_message(di, datagram, reciever_channel, sender_channel)
        elif message_type == CONTROL_SET_CHANNEL:
            self.interface.register_channel(connection, reciever_channel)
        elif message_type == CONTROL_REMOVE_CHANNEL:
            self.interface.unregister_channel(connection, reciever_channel)
        elif message_type == CONTROL_SET_CON_NAME:
            return NotImplemented
        elif message_type == CONTROL_SET_CON_URL:
            return NotImplemented
        elif message_type == CONTROL_ADD_RANGE:
            return NotImplemented
        elif message_type == CONTROL_REMOVE_RANGE:
            return NotImplemented
        elif message_type == CONTROL_ADD_POST_REMOVE:
            return NotImplemented
        elif message_type == CONTROL_CLEAR_POST_REMOVE:
            return NotImplemented
        else:
            self.notify.debug("Recieved an invalid message_type: %d" % message_type)
            return
    
    def route_message(self, di, datagram, reciever_channel, sender_channel): 
        dg = PyDatagram()
        dg.addUint64(reciever_channel)
        dg.addUint64(sender_channel)
        dg.addUint16(di.getUint16())
        dg.appendData(di.getRemainingBytes())
        self.cw.send(dg, self.interface.registeredParticipants[reciever_channel])
        dg.clear()
    
    def handle_bad_channel(self, di):
        return NotImplemented
