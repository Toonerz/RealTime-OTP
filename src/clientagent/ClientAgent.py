from panda3d.core import *
from pandac.PandaModules import *
from direct.task.TaskManagerGlobal import *
from direct.task.Task import Task
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from src.util.types import *

class ClientAgent(QueuedConnectionManager):
    
    def __init__(self, server_address, server_port, client_address, client_port):
        QueuedConnectionManager.__init__(self)
        self.server_address = server_address
        self.server_port = server_port
        self.client_address = client_address
        self.client_port = client_port
    
    def configure(self):
        self.cl = QueuedConnectionListener(self, 0)
        self.cr = QueuedConnectionReader(self, 0)
        self.cw = ConnectionWriter(self, 0)
        self.our_channel = CLIENT_AGENT_CHANNEL
        self.open_connection()
    
    def unconfigure(self):
        for participant in self.interface:
            self.cr.removeConnection(participant)
        self.closeConnection(self.tcp_socket)
        self.closeConnection(self.tcp_conn)
        self.cl = self.cr = self.cw = self.tcp_socket = self.tcp_conn = None

    def register_for_channel(self, channel):
        datagram = PyDatagram()
        datagram.addServerHeader(CLIENT_AGENT_CHANNEL, channel, CONTROL_SET_CHANNEL)
        self.cw.send(datagram, self.tcp_conn)
	
    def unregister_for_channel(self, channel):
        datagram = PyDatagram()
        datagram.addServerHeader(CLIENT_AGENT_CHANNEL, channel, CONTROL_REMOVE_CHANNEL)
        self.cw.send(datagram, self.tcp_conn)

    def open_connection(self):
        self.tcp_socket = self.openTCPServerRendezvous(self.server_port, 1000)
        if self.tcp_socket:
            self.cl.addConnection(self.tcp_socket)

        self.run_connection()
    
    def run_connection(self):
        self.tcp_conn = self.openTCPClientConnection(self.client_address, self.client_port, 3000)
        if self.tcp_conn:
			self.cl.addConnection(self.tcp_conn)
			self.register_for_channel(self.our_channel)
		
        taskMgr.add(self.task_reader_poll_reciever, "task reader reciever")
    
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

    """ This task handles incoming data for the clientagent """
    def task_reader_poll_reciever(self, taskname):
        if self.cr.dataAvailable():
            datagram = NetDatagram()
            if self.cr.getData(datagram):
                self.handle_datagram_reciever(datagram)
        
        return Task.cont

    def handle_datagram_reciever(self, datagram):
        self.connection = datagram.getConnection()
        if not self.connection:
            pass # TODO!
        
        di = PyDatagramIterator(datagram)
        print di.getUint16()
